#!/usr/bin/env python3
"""Static validator for chat-delivered HTML assets (web-assets-builder).

Checks the failure modes that make a generated asset render blank, unstyled, or
broken inside the platform's sandboxed preview iframe. No third-party deps.

Usage:
    python validate_asset.py path/to/asset.html [--offline] [--quiet]

Exit codes:
    0  no errors (warnings may be present)
    1  at least one ERROR
    2  bad usage / unreadable file

--offline skips the HTTP HEAD/GET reachability check on CDN URLs.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# ── the platform's contract ─────────────────────────────────────────────────
# A fenced ```html block with fewer than this many lines is NOT hoisted into the
# preview dock; it renders in the chat's inline code previewer, which blocks all
# CDN loads. Assets below the threshold look unstyled. (client: ARTIFACT_THRESHOLD)
MIN_HOISTED_LINES = 5

# The artifact-preview endpoint rejects bodies above this size, and the client
# silently falls back to a stricter renderer with CDNs blocked.
MAX_BYTES = 2_000_000

# Tag names that never need a closing tag.
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

# Leftover scaffolding that means the asset is not finished. Deliberately
# anchored to avoid the legitimate `placeholder="…"` input attribute and
# ordinary prose use of the word.
PLACEHOLDER_PATTERNS = [
    (re.compile(r"lorem ipsum", re.I), "Lorem ipsum placeholder text"),
    (re.compile(r"\bTODO\b(?!\s*[:=]\s*['\"]?)"), "TODO marker"),
    (re.compile(r"\bFIXME\b"), "FIXME marker"),
    (re.compile(r"\{\{\s*[\w.\-\[\]]{1,40}\s*\}\}"), "unfilled {{template}} placeholder"),
    (re.compile(r"\bPLACEHOLDER[-_ ]?(?:TEXT|CONTENT|VALUE|HERE|DATA)\b", re.I),
     "PLACEHOLDER marker"),
    (re.compile(r"your[-_ ](?:api[-_ ]?)?key\b", re.I), "placeholder API key"),
    (re.compile(r"\bCHANGEME\b"), "CHANGEME marker"),
]

# Sample/placeholder values the bundled templates ship with. Only a warning:
# copying a template without replacing its demo numbers is the common failure.
SAMPLE_DATA_PATTERNS = [
    (re.compile(r"\$128,400|\$42,300"), "template sample revenue value"),
    (re.compile(r"Acme Corp|Globex|Initech|Umbrella Health|Soylent Foods|Hooli"),
     "template sample company name"),
    (re.compile(r"\bexample\.com\b"), "example.com placeholder"),
]

# Library -> the global its script defines. Used to catch "used but not loaded"
# and "loaded after use" ordering bugs.
LIBRARY_GLOBALS = {
    "echarts": re.compile(r"\becharts\s*\."),
    "Chart": re.compile(r"\bnew\s+Chart\s*\("),
    "mermaid": re.compile(r"\bmermaid\s*\.\s*(?:initialize|run)\b"),
    "gridjs": re.compile(r"\bnew\s+gridjs\s*\."),
    "Sortable": re.compile(r"\bSortable\s*\.\s*create\b"),
    "confetti": re.compile(r"\bconfetti\s*\("),
    "d3": re.compile(r"\bd3\s*\.\s*select\b"),
    "Papa": re.compile(r"\bPapa\s*\.\s*parse\b"),
    "dayjs": re.compile(r"\bdayjs\s*\("),
    "marked": re.compile(r"\bmarked\s*\("),
    "tippy": re.compile(r"\btippy\s*\("),
    "anime": re.compile(r"\banime\s*\("),
    "rough": re.compile(r"\brough\s*\.\s*svg\b"),
}

# Markers that identify which CDN script provides which global.
LIBRARY_URL_MARKERS = {
    "echarts": "echarts",
    "Chart": "chart.js",
    "mermaid": "mermaid",
    "gridjs": "gridjs",
    "Sortable": "sortablejs",
    "confetti": "canvas-confetti",
    "d3": "/d3@",
    "Papa": "papaparse",
    "dayjs": "dayjs",
    "marked": "marked",
    "tippy": "tippy",
    "anime": "animejs",
    "rough": "roughjs",
}


class AssetParser(HTMLParser):
    """Collects structure, external resources and inline script/style bodies."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.unbalanced: list[str] = []
        self.scripts: list[dict] = []       # {src, line, inline, text}
        self.stylesheets: list[dict] = []   # {href, line}
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.attrs_seen: list[tuple[str, dict, int]] = []
        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_body = False
        self.has_title = False
        self._in_script: dict | None = None
        self._in_style = False
        self._script_buf: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        d = {k.lower(): (v or "") for k, v in attrs}
        self.attrs_seen.append((tag, d, line))

        if tag == "html":
            self.has_html = True
        elif tag == "head":
            self.has_head = True
        elif tag == "body":
            self.has_body = True
        elif tag == "title":
            self.has_title = True

        if tag == "script":
            entry = {"src": d.get("src", ""), "line": line, "inline": not d.get("src"),
                     "text": "", "type": d.get("type", "")}
            self.scripts.append(entry)
            if not d.get("src"):
                self._in_script = entry
                self._script_buf = []
        elif tag == "style":
            self._in_style = True
        elif tag == "link":
            rel = d.get("rel", "").lower()
            if "stylesheet" in rel:
                self.stylesheets.append({"href": d.get("href", ""), "line": line})
            else:
                self.links.append({"href": d.get("href", ""), "line": line, "rel": rel})
        elif tag == "img":
            self.images.append({"src": d.get("src", ""), "line": line})

        if tag not in VOID_TAGS:
            self.stack.append((tag, line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            if self._in_script is not None:
                self._in_script["text"] = "".join(self._script_buf)
            self._in_script = None
            self._script_buf = []
        elif tag == "style":
            self._in_style = False

        if tag in VOID_TAGS:
            return
        # Pop to the matching opener; anything skipped was never closed.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for orphan, line in self.stack[i + 1:]:
                    self.unbalanced.append(
                        f"<{orphan}> opened at line {line} is never closed")
                del self.stack[i:]
                return
        self.unbalanced.append(f"</{tag}> at line {self.getpos()[0]} has no opening tag")

    def handle_data(self, data: str) -> None:
        if self._in_script is not None:
            self._script_buf.append(data)


def check_url_reachable(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """HEAD (falling back to GET) so we can prove a CDN URL actually resolves."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "ajelix-asset-validator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 400, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):  # some CDNs reject HEAD; retry with GET
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "ajelix-asset-validator/1.0"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return 200 <= r.status < 400, f"HTTP {r.status}"
            except Exception as e2:  # noqa: BLE001
                return False, f"HTTP {getattr(e2, 'code', '?')}"
        return False, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - network varies; report, don't crash
        return False, f"{type(e).__name__}: {e}"


def strip_js_comments(src: str) -> str:
    """Remove // and /* */ comments (string-literal aware) so commented-out
    example code is not mistaken for real library usage."""
    out: list[str] = []
    i, n = 0, len(src)
    quote: str | None = None
    while i < n:
        ch = src[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(src[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'`":
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            end = src.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def validate(path: Path, offline: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    # ── size / hoisting contract ────────────────────────────────────────────
    if len(raw) > MAX_BYTES:
        errors.append(
            f"asset is {len(raw):,} bytes — over the {MAX_BYTES:,}-byte preview limit; "
            "the preview silently degrades and CDN scripts stop loading")
    if len(lines) < MIN_HOISTED_LINES:
        errors.append(
            f"asset is only {len(lines)} lines — below the {MIN_HOISTED_LINES}-line "
            "hoist threshold, so it renders in the inline previewer with CDNs blocked")

    parser = AssetParser()
    parser.feed(text)
    parser.close()

    # ── document shape ──────────────────────────────────────────────────────
    if not parser.has_doctype:
        errors.append("missing <!DOCTYPE html> — the fence body is served as a whole "
                      "document; without a doctype it renders in quirks mode")
    for present, tag in ((parser.has_html, "<html>"), (parser.has_head, "<head>"),
                         (parser.has_body, "<body>")):
        if not present:
            errors.append(
                f"missing {tag} — a bare fragment has nowhere to put <style>/<script> "
                "and renders unstyled in the preview")
    if not parser.has_title:
        warnings.append("no <title> — set one for the browser tab and preview header")
    if parser.has_html and not re.search(r"<html[^>]*\blang\s*=", text, re.I):
        warnings.append("<html> has no lang attribute (accessibility)")

    for problem in parser.unbalanced:
        errors.append(f"unbalanced markup: {problem}")
    for tag, line in parser.stack:
        errors.append(f"<{tag}> opened at line {line} is never closed")

    # ── external resources ──────────────────────────────────────────────────
    external: list[tuple[str, str, int]] = []   # (kind, url, line)
    for s in parser.scripts:
        if s["src"]:
            external.append(("script", s["src"], s["line"]))
    for s in parser.stylesheets:
        external.append(("stylesheet", s["href"], s["line"]))
    for i in parser.images:
        external.append(("image", i["src"], i["line"]))

    for kind, url, line in external:
        if url.startswith(("data:", "blob:")):
            continue
        if url.startswith("//"):
            warnings.append(f"line {line}: protocol-relative {kind} URL '{url}' — "
                            "use an explicit https:// URL")
            continue
        if not url.startswith(("http://", "https://")):
            errors.append(
                f"line {line}: {kind} '{url}' is not an absolute URL — the preview "
                "document has no workspace access, so relative/local paths never resolve")
            continue
        if url.startswith("http://"):
            warnings.append(f"line {line}: {kind} uses insecure http:// — prefer https://")
        if kind in ("script", "stylesheet") and "latest" in url:
            warnings.append(f"line {line}: unpinned '{url}' — pin a version so the "
                            "asset does not break when the package publishes")

    if not offline:
        seen: dict[str, tuple[bool, str]] = {}
        for kind, url, line in external:
            if not url.startswith(("http://", "https://")) or url in seen:
                continue
            ok, detail = check_url_reachable(url)
            seen[url] = (ok, detail)
            if not ok:
                errors.append(f"line {line}: {kind} URL is unreachable ({detail}): {url}")

    # ── library usage vs loading, and load order ────────────────────────────
    # Commented-out example code is NOT usage: strip JS comments before matching,
    # or a blueprint whose snippet is commented out reports a missing library.
    inline_scripts = [dict(s, text=strip_js_comments(s["text"]))
                      for s in parser.scripts if s["inline"] and s["text"].strip()]
    all_script_src = " ".join(s["src"].lower() for s in parser.scripts if s["src"])
    all_text = text

    for lib, usage in LIBRARY_GLOBALS.items():
        used = any(usage.search(s["text"]) for s in inline_scripts)
        if not used:
            continue
        marker = LIBRARY_URL_MARKERS[lib]
        if marker not in all_script_src:
            errors.append(
                f"code uses `{lib}` but no matching <script src> is loaded "
                f"(expected a URL containing '{marker}')")
            continue
        # load order: the library script must come before the inline script using it
        lib_line = min((s["line"] for s in parser.scripts
                        if s["src"] and marker in s["src"].lower()), default=None)
        use_line = min((s["line"] for s in inline_scripts if usage.search(s["text"])),
                       default=None)
        if lib_line is not None and use_line is not None and lib_line > use_line:
            errors.append(
                f"`{lib}` is used at line {use_line} but its <script src> is loaded at "
                f"line {lib_line} — the library must load first")

    # lucide: data-lucide needs the JS, not the font
    if re.search(r"data-lucide\s*=", all_text):
        has_lucide_js = re.search(r"lucide[^\"']*\.js|lucide@[\d.]+/dist", all_script_src)
        if not has_lucide_js:
            errors.append(
                "`data-lucide` is used but the lucide script is not loaded — the static "
                "icon font ships no JS. Either load the lucide JS and call "
                "lucide.createIcons(), or switch to class=\"icon-…\" with the font CSS, "
                "or inline the SVG")
        elif not re.search(r"createIcons\s*\(", all_text):
            errors.append("lucide is loaded but `lucide.createIcons()` is never called, "
                          "so `data-lucide` elements render empty")

    # alpine
    if re.search(r"\bx-data\s*=", all_text) and "alpinejs" not in all_script_src:
        errors.append("`x-data` is used but Alpine.js is not loaded "
                      "(expected a URL containing 'alpinejs')")
    for s in parser.scripts:
        if s["src"] and "alpinejs" in s["src"].lower() and "defer" not in _attrs_of(parser, s):
            warnings.append(f"line {s['line']}: Alpine should be loaded with `defer`")

    # tailwind
    if "cdn.tailwindcss.com" in all_script_src and not re.search(
            r"class\s*=\s*[\"'][^\"']*\b(?:bg|text|p|m|flex|grid|rounded|border)-", all_text):
        warnings.append("Tailwind is loaded but no utility classes were found in markup")

    # ── placeholders ────────────────────────────────────────────────────────
    for pattern, label in PLACEHOLDER_PATTERNS:
        for m in pattern.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            errors.append(f"line {line}: leftover {label} — the asset is not finished")
            break
    for pattern, label in SAMPLE_DATA_PATTERNS:
        if pattern.search(text):
            warnings.append(f"{label} — replace with real data or label it clearly as sample")

    # ── hygiene ─────────────────────────────────────────────────────────────
    if re.search(r"</script>", _inside_js_strings(inline_scripts)):
        errors.append("a literal `</script>` appears inside a JS string — write it as "
                      "`<\\/script>` or the document is truncated there")

    if re.search(r"<script[^>]*\bsrc=[^>]*>\s*[^<\s]", text, re.I):
        warnings.append("a <script src> tag has inline content; the browser ignores it")

    if not re.search(r"viewport", text, re.I):
        warnings.append("no <meta name=\"viewport\"> — the asset will not scale on mobile")

    if re.search(r"\bheight\s*:\s*(?:0|auto)\b", text) and re.search(
            r"echarts\.init|new\s+Chart\s*\(", text):
        warnings.append("a chart container may have no explicit height — charts in a "
                        "zero/auto-height parent render blank")

    if (re.search(r"echarts\.init", text) and
            not re.search(r"resize|ResizeObserver", text)):
        warnings.append("ECharts is initialised without a resize handler — the chart "
                        "will not adapt when the preview panel is resized")

    return errors, warnings


def _attrs_of(parser: AssetParser, script: dict) -> str:
    for tag, d, line in parser.attrs_seen:
        if tag == "script" and line == script["line"]:
            return " ".join(f"{k}" for k in d)
    return ""


def _inside_js_strings(inline_scripts: list[dict]) -> str:
    """JS string literals only — so a real `</script>` terminator is not flagged."""
    out: list[str] = []
    for s in inline_scripts:
        for m in re.finditer(r"""(['"`])(?:\\.|(?!\1).)*\1""", s["text"], re.S):
            out.append(m.group(0))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, help="HTML asset to validate")
    ap.add_argument("--offline", action="store_true",
                    help="skip CDN reachability checks")
    ap.add_argument("--quiet", action="store_true", help="print only problems")
    args = ap.parse_args()

    if not args.path.is_file():
        print(f"ERROR: not a file: {args.path}", file=sys.stderr)
        return 2

    try:
        errors, warnings = validate(args.path, args.offline)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: validator failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"validating {args.path}  "
              f"({args.path.stat().st_size:,} bytes, "
              f"{len(args.path.read_text(encoding='utf-8', errors='replace').splitlines())} lines)")
        if args.offline:
            print("(offline: CDN reachability not checked)")

    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"WARN:  {w}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        print("Fix every ERROR before emitting the asset.")
        return 1
    print("OK — safe to emit as a ```html block.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
