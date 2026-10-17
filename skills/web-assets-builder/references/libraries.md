# Libraries — verified CDN URLs

Every URL below was checked live (HTTP 200). Use them **exactly** — a 404 CDN URL fails
silently and leaves the asset unstyled.

Rules:
- Absolute `https://` only. No relative paths, no npm, no bundler.
- Put every `<script src>` **before** the inline `<script>` that uses it.
- Pin versions (as below). Unpinned `@latest` can break an asset that worked yesterday.
- Don't load a library you don't use — each one costs load time inside the preview.

---

## Core

### Tailwind CSS (utility classes — the default choice)

```html
<script src="https://cdn.tailwindcss.com/3.4.17"></script>
```

This is the **v3 Play CDN** (pinned). It compiles classes in the browser, so it must
finish before the page paints — keeping it in `<head>` is correct. Arbitrary values
(`h-[320px]`, `w-[42%]`) work. Configure the theme inline if you need brand colours:

```html
<script src="https://cdn.tailwindcss.com/3.4.17"></script>
<script>
  tailwind.config = {
    theme: { extend: { colors: { brand: { DEFAULT: '#6d28d9', hover: '#5b21b6' } } } }
  };
</script>
```

> Note: the Play CDN is a browser compiler and logs a "not for production" console
> warning. That is expected and harmless here — the asset is a self-contained preview
> document, not a served website.

If you prefer plain CSS, skip Tailwind entirely and use the copy-paste stylesheet in
`references/design-system.md` § 4. Fewer moving parts, faster preview.

### Alpine.js (light interactivity: toggles, tabs, small state)

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
```

`defer` is required. `x-data` on a container, `x-model`, `x-show`, `x-text`, `@click`.
Prefer Alpine over hand-written DOM wiring for anything with more than two state values.

---

## Charts

### ECharts (default for dashboards — richest, best-looking defaults)

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
```

```html
<div id="chart" style="width:100%;height:320px;"></div>
<script>
  const chart = echarts.init(document.getElementById('chart'));
  chart.setOption({
    grid: { left: 8, right: 8, top: 24, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar'], axisLine: { lineStyle: { color: '#e4e4e7' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f0f2' } } },
    series: [{ type: 'line', smooth: true, data: [120, 200, 150], areaStyle: { opacity: .12 },
               itemStyle: { color: '#6d28d9' } }]
  });
  window.addEventListener('resize', () => chart.resize());
</script>
```

**Always** give the container an explicit height, and **always** wire `resize` (or a
`ResizeObserver`) — a chart in a zero-height or never-resized container renders blank.

### Chart.js (simpler charts, smaller)

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
```

```html
<canvas id="c" height="140"></canvas>
<script>
  new Chart(document.getElementById('c'), {
    type: 'bar',
    data: { labels: ['A','B','C'], datasets: [{ label: 'Units', data: [12,19,7],
            backgroundColor: '#6d28d9', borderRadius: 6 }] },
    options: { responsive: true, maintainAspectRatio: false,
               plugins: { legend: { display: false } },
               scales: { y: { grid: { color: '#f0f0f2' } } } }
  });
</script>
```

Wrap a `maintainAspectRatio:false` canvas in a fixed-height parent.

### D3 (only for genuinely custom visualisations)

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
```

Prefer ECharts unless you need a layout ECharts cannot express.

---

## Tables

### Grid.js (sortable/searchable/paginated grid)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/gridjs@6.2.0/dist/theme/mermaid.min.css">
<script src="https://cdn.jsdelivr.net/npm/gridjs@6.2.0/dist/gridjs.umd.js"></script>
```

```html
<div id="grid"></div>
<script>
  new gridjs.Grid({
    columns: ['Name', 'Units', 'Revenue'],
    data: [['Alpha', 120, '$4,200'], ['Beta', 98, '$3,100']],
    search: true, sort: true, pagination: { limit: 10 }
  }).render(document.getElementById('grid'));
</script>
```

### SortableJS (drag-and-drop reordering)

```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js"></script>
```

```html
<script>Sortable.create(document.getElementById('list'), { animation: 150 });</script>
```

For a plain static table, write semantic `<table>` + CSS (see `design-system.md`) — a grid
library is overkill.

---

## Icons

Two mechanisms. **Pick one and load the matching asset** — mixing them is the most common
icon bug.

### A. Icon font (recommended — one CSS file, no JS)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lucide-static@0.454.0/font/lucide.css">
```

```html
<i class="icon-trending-up" aria-hidden="true"></i>
<span class="icon-house"></span>
```

Icons come from `::before` content, so size them with `font-size` (or a width/height +
`font-size` pair). Decorative icons get `aria-hidden="true"`; icon-only buttons get
`aria-label`. Browse names at <https://lucide.dev/icons>.

### B. Inline SVG (when you need `currentColor` control or zero extra requests)

Copy the path straight from <https://lucide.dev/icons>:

```html
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M3 17l6-6 4 4 8-8"/>
  <path d="M17 7h4v4"/>
</svg>
```

This inherits `color`, needs no network, and never 404s. Best choice for a handful of icons.

> **Do not** use `data-lucide="…"` unless you also load the lucide **script** *and* call
> `lucide.createIcons()` — the static font package ships no JS. A bare `data-lucide`
> attribute renders nothing.

---

## Animation & effects

### anime.js

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js"></script>
```

### canvas-confetti (celebrations — use sparingly)

```html
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
<script>confetti({ particleCount: 90, spread: 70, origin: { y: .7 } });</script>
```

Respect `prefers-reduced-motion` and never auto-fire an effect that blocks the user.

---

## Mermaid (a diagram inside an HTML asset)

Only needed when a diagram must live *inside* a dashboard. For a diagram the user just
wants to read, emit a ```` ```mermaid ```` block in chat instead — no skill needed.

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
```

```html
<div class="mermaid">
flowchart TD
    A[Start] --> B{Valid?}
    B -->|Yes| C[Process]
    B -->|No| D[Reject]
</div>
<script>
  mermaid.initialize({ startOnLoad: true, theme: 'neutral', securityLevel: 'strict' });
</script>
```

`securityLevel: 'strict'` is required — it sanitises node labels. Load mermaid **before**
the markup it renders, or call `mermaid.run()` after `DOMContentLoaded`.

---

## Data & formatting helpers

```html
<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>   <!-- CSV parse -->
<script src="https://cdn.jsdelivr.net/npm/dayjs@1.11.13/dayjs.min.js"></script>          <!-- dates -->
<script src="https://cdn.jsdelivr.net/npm/marked@14.1.3/marked.min.js"></script>         <!-- markdown -> html -->
```

For a handful of dates or a number format, prefer `Intl` — no dependency:

```js
new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(42300);
new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date());
```

---

## Tooltips

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tippy.js@6.3.7/dist/tippy.css">
<script src="https://cdn.jsdelivr.net/npm/tippy.js@6.3.7/dist/tippy.umd.min.js"></script>
<script>tippy('[data-tip]', { content: el => el.dataset.tip });</script>
```

Prefer the native `title` attribute for one or two tooltips — no dependency at all.

---

## 3D / creative

```html
<!-- three.js ships ESM only in modern versions; use the module build: -->
<script type="module">
  import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js';
</script>
```

```html
<script src="https://cdn.jsdelivr.net/npm/roughjs@4.6.6/bundled/rough.js"></script>
```

3D and hand-drawn styles are heavy; use them only when the request is explicitly about
the visual style, and keep the scene small.

---

## Choosing

| Need | Use |
|---|---|
| Dashboard with several charts | ECharts |
| One simple chart | Chart.js |
| Interactive table with search/sort | Grid.js |
| Drag-and-drop ordering | SortableJS |
| Toggles, tabs, small state | Alpine.js |
| Lots of markup with utility classes | Tailwind |
| A few icons | Inline SVG |
| Many icons | lucide icon font |
| Diagram inside an asset | mermaid |
| Diagram the user just wants to read | ```` ```mermaid ```` block in chat — no library |

Do not load three charting libraries "just in case". Every extra script delays the preview.
