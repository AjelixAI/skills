---
name: web-assets-builder
description: Builds self-contained interactive HTML assets — dashboards, calculators, tools, data tables, charts, reports, games, mockups. Use whenever the user wants to SEE something interactive or visual in chat. Provides the Ajelix design tokens, verified CDN libraries, copy-ready templates and chart/component recipes. NOT for diagrams — write a ```mermaid block directly, the platform renders it natively.
version: "2.0.0"
---

# Web Assets Builder

Build ONE self-contained HTML document, delivered as a single ```` ```html ```` fenced
block in your chat reply. The platform renders it in a live sandboxed preview.

## Scope

**This skill: interactive HTML/JS assets** — dashboards, calculators, tools, data
tables, charts, written reports with figures, games, mockups, UI concepts.

**Not this skill: diagrams.** Flowcharts, sequence/ER/class diagrams, mindmaps, Gantt —
write a ```` ```mermaid ```` fenced block directly in your reply. The platform renders it
natively; loading this skill for a diagram is wasted work.

**Not this skill: production websites.** A chat asset is a self-contained document in a
sandboxed frame — a working prototype, a pitch, or a mockup. It has no routing, no
backend, no build step, and cannot be deployed as-is. If the user wants a real site,
build the concept here and say plainly that it is a prototype.

A diagram *inside* a dashboard is fine — see `references/libraries.md` § Mermaid.

---

## How the platform renders your asset (read this first)

Your ```` ```html ```` block becomes a **chip** the user clicks to open a sandboxed
preview iframe. Three rules follow from how that iframe is built. Breaking them is the
single most common cause of an asset that looks broken to the user.

| Rule | Why |
|---|---|
| **≥ 5 lines of code** | Fences under 5 lines stay inline and render in a *different*, stricter preview that blocks CDNs. Short assets lose all styling. Always emit a full document. |
| **Complete `<!DOCTYPE html>` document** | The fence body is served as a whole document. A bare `<div>` fragment has no `<head>`, so no CSS/JS ever loads. |
| **Everything inline or from a CDN** | The document is an opaque-origin sandbox: no access to app CSS, fonts, or files. Relative paths and local files never resolve. Use absolute `https://` CDN URLs and inline `<style>`/`<script>`. |

**Write the asset in chat — never as a `.html` file.** Do not use `bash`/`write_file` to
produce something the user will view. The chat block *is* the delivery channel; the user
can save it to the workspace from the preview if they want a file.

### Title the asset

The fence info string after the language becomes the chip label:

````
```html title="Q3 Revenue Dashboard"
<!DOCTYPE html>
...
```
````

Use `title="..."`. Do **not** use ```` ```html [Name] ```` — the brackets render literally
in the chip label.

---

## Workflow

1. **Load only the references you need** — do not read them all:
   | File | Read when |
   |---|---|
   | `references/artifact-contract.md` | Always, on the first asset of a session — the rendering contract and failure modes |
   | `references/design-system.md` | Always — Ajelix tokens, typography, base stylesheet, layout rules |
   | `references/design-vocabulary.md` | The user names a style ("brutalist", "editorial", "clean"), or the asset is more visual than functional |
   | `references/libraries.md` | Choosing a CDN library; every URL is verified |
   | `references/chart-recipes.md` | Building any chart — copy-paste ECharts/Chart.js options |
   | `references/component-recipes.md` | Need a table, tabs, form, modal, empty state, or wiring patterns |
   | `references/master_blueprint.html` | Starting from scratch rather than from a template |
2. **Start from a template** when the asset is one of these shapes — they are complete
   working documents; replace the sample data, keep the shell:
   | Template | Use for |
   |---|---|
   | `templates/kpi_dashboard.html` | Multi-chart dashboards, KPI grids, CSV export |
   | `templates/report.html` | Written analysis with figures — summary → evidence → detail, print-ready |
   | `templates/data_table.html` | Searchable/sortable/paginated tables |
   | `templates/interactive_tool.html` | Calculators, generators, configurators, forms |
   | `templates/logic_game.html` | Games and playful interactive pieces |
3. **Build** the asset: one file, inline `<style>`, libraries from CDN, inline `<script>`
   at the end of `<body>`. Prefer a recipe from `chart-recipes.md`/`component-recipes.md`
   over inventing markup — they are already consistent with the design tokens.
4. **Decide the visual direction before writing CSS.** Name your position on the five
   axes in `design-vocabulary.md` (density, contrast, radius, elevation, chroma). An
   asset with no point of view reads as a generic template.
5. **Self-check before you emit** — run the validator (below). Do not skip this.
6. **Emit** one ```` ```html title="…" ```` block. No prose preamble inside the block.

### Self-check (run it — it takes seconds)

Write the document to the scratch dir, validate, then emit the same content in chat:

```bash
mkdir -p /mnt/workspace/.workspace
# ...write your document to /mnt/workspace/.workspace/asset.html...
python /mnt/workspace/.ajelix/skills/web-assets-builder/scripts/validate_asset.py \
  /mnt/workspace/.workspace/asset.html
```

The validator catches the failure modes that make assets render blank or unstyled:
missing DOCTYPE, unbalanced tags, unclosed `<script>`, CDN URLs that 404, script-before-
library ordering, `data-lucide` without the lucide script, and placeholder data left in.
Exit code 0 = safe to emit. Fix every ERROR before emitting; WARNs are judgement calls.

---

## Design principles

- **Match the platform.** Light theme by default: `#fafafa` page, `#ffffff` cards,
  `#e4e4e7` hairlines, `#18181b` ink, `#6b6b75` secondary, **`#6d28d9` violet** for
  primary actions. Full tokens + copy-paste CSS in `references/design-system.md`.
- **Have a point of view.** The default failure mode of a generated asset is that it
  looks like every other generated asset — centred text, three equal cards, rounded
  white boxes on grey. Decide density/contrast/radius/elevation/chroma up front
  (`references/design-vocabulary.md`) and commit to it.
- **Real data over placeholder.** If the user gave you numbers, use them. Never ship
  `Lorem ipsum` or fabricated metrics presented as real — the validator flags them.
- **Empty states.** Handle "no data" explicitly; a dashboard that renders blank reads
  as broken.
- **Fonts.** The sandbox can't reach the app's fonts. Use a deliberate system stack
  (`system-ui, -apple-system, 'Segoe UI', sans-serif`) or load a webfont from a CDN —
  never leave the browser default.
- **Responsive.** Use CSS grid/flex with `minmax()`/`clamp()`; charts must resize.
- **Accessible.** Real `<button>`/`<label>`; `aria-label` on icon-only controls; visible
  focus; ≥ 4.5:1 text contrast; never encode meaning in colour alone.
- **Wire what you render.** A control that looks interactive and does nothing is worse
  than a label. See `references/component-recipes.md` § Wiring.

### On seeking design inspiration

If `web_search` is enabled and the user asks for a specific visual direction you don't
have a pattern for, you may look it up — but know the limits: search returns **text
only** (no images, no rendered pages), so it gives you *vocabulary* (a style's name, its
palette, its reference points), never a layout to copy. Never present a look as
"researched" when you only read about it.

Prefer, in order:
1. `references/design-vocabulary.md` — concrete CSS signatures for the common styles.
2. `references/design-system.md` — the house style, when the asset represents Ajelix.
3. The templates and recipes — already consistent and already validated.
4. `web_search` — only to resolve a style name you don't recognise.

Never fetch or hotlink an image, screenshot, or font file you found while looking.

## Output format

````
```html title="Descriptive Name"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Descriptive Name</title>
  <!-- CDN stylesheets here (Tailwind, fonts, icon font) -->
  <style>/* your CSS */</style>
</head>
<body>
  <!-- content -->
  <!-- CDN scripts here -->
  <script>/* init at end of body */</script>
</body>
</html>
```
````
