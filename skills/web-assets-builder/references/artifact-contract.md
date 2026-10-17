# Artifact Contract — how the platform renders your HTML

Everything here is verified against the shipping platform. Read it once; it prevents the
failure modes that make an asset look broken.

## 1. Delivery channel

| Stage | What happens |
|---|---|
| You emit ```` ```html title="…" ```` | The chat client hoists any fenced block with **≥ 5 lines** out of the message and replaces it with a clickable **artifact chip** labelled with your `title="…"`. |
| User clicks the chip | The preview dock opens beside the chat and renders your document in a sandboxed `<iframe>`. |
| Sandbox | The frame is an **opaque origin**: scripts run, but the document has no access to the app's cookies, storage, or DOM. |
| CDN scripts | **Load normally** — the preview is served as its own document with its own policy, not as an inline fragment of the app. |
| Save to workspace | The user can persist the asset as a real `.html` file; it then previews through the same path. |

### Consequences you must design around

- **Fence body must be a complete document.** `<html>`, `<head>`, `<body>`. A fragment
  has nowhere to put `<style>`/`<script>` and renders unstyled.
- **≥ 5 lines.** Below that the block is *not* hoisted; it renders in the chat's inline
  code-block previewer, which is a different sandbox that **blocks all CDN loads**. Short
  assets look broken. Always emit a full document so you are comfortably over the line.
- **No local files, no relative URLs.** The document has no workspace access. Every
  asset must be inline or an absolute `https://` CDN URL. `<img src="./logo.png">` and
  `fetch('/api/…')` will not work.
- **No app CSS or fonts.** Style everything yourself.

## 2. Failure modes (in the order they actually bite)

| Symptom | Cause | Fix |
|---|---|---|
| Renders as unstyled text | Fragment instead of a document; or the block was under 5 lines | Emit a complete `<!DOCTYPE html>` document |
| Charts/cards have no styling | A CDN script or stylesheet URL 404s | Use the pinned URLs in `references/libraries.md` — all verified |
| Blank page, no error visible | Unclosed `<script>` or unbalanced tag swallowing the rest of the document | Run `scripts/validate_asset.py` |
| Library `X is not defined` | Your init script ran before the library script | Put all `<script src>` **before** your inline init script, at the end of `<body>` |
| Icons show as empty boxes / missing | `data-lucide="…"` needs the lucide **script** + `lucide.createIcons()`; the icon *font* uses `class="icon-…"` — different mechanisms | Pick one, load the matching CDN asset |
| Tailwind classes do nothing | Tailwind's browser build must load **before** the markup is styled — it is fine in `<head>`, but a wrong/404 URL is silent | Use the pinned URL; verify with the validator |
| Looks fine locally, blank in chat | You used a relative path or a local file | Inline it, or use a CDN URL |

## 3. Non-negotiable output rules

1. **One asset per fence.** Do not emit two ```` ```html ```` blocks for one request.
2. **Never write the asset as a file** with `bash`/`write_file`. Chat is the channel.
   (Writing a *scratch copy* to validate it is fine — see below — but the deliverable is
   the chat block.)
3. **No placeholder data.** Use the user's real numbers. If you have none, use clearly
   labelled sample data that is obviously illustrative (`Sample data` badge), never
   fabricated specifics presented as real.
4. **Escape correctly.** A literal `</script>` inside a JS string breaks the document.
   Write `<\/script>` in JS strings.
5. **Self-contained.** No build step, no npm, no bundler.

## 4. Validate before emitting

The validator is a fast static check for exactly the failure modes above:

```bash
mkdir -p /mnt/workspace/.workspace
cat > /mnt/workspace/.workspace/asset.html <<'HTML'
<!DOCTYPE html>
...your document...
HTML

python /mnt/workspace/.ajelix/skills/web-assets-builder/scripts/validate_asset.py \
  /mnt/workspace/.workspace/asset.html
```

It reports ERRORs (fix all) and WARNs (judgement). It checks:

- `<!DOCTYPE html>` present, `<html>`/`<head>`/`<body>` present
- balanced tags, unclosed `<script>`/`<style>`
- every external `<script src>` / `<link href>` returns HTTP 200
- libraries referenced by your code are actually loaded (`echarts`/`Chart`/`mermaid`/
  `lucide`/`alpine`), and load **before** the code that uses them
- `data-lucide` used without the lucide script; `x-data` used without Alpine
- leftover placeholders (`Lorem ipsum`, `TODO`, `{{…}}`, `$42,300`)
- asset is comfortably ≥ 5 lines and non-trivial
- `<title>` present

Exit code 0 → safe to emit. Anything else → fix and re-run.

## 5. Size and performance

- Keep the document under **~2 MB**. Larger payloads are rejected by the preview
  endpoint and the asset silently falls back to a stricter renderer with CDNs blocked.
- Prefer ECharts or Chart.js over D3 for standard charts; use D3 only for genuinely
  custom visualisations.
- Do not embed base64 images over a few hundred KB. Prefer an inline SVG or a CSS shape.
- Virtualise or paginate tables above ~1,000 rows; do not render 10,000 DOM rows.
- Debounce expensive recomputation on input; keep interaction under one frame.
