# Ajelix UI Kit — design tokens for generated assets

The platform's own look, distilled to what an asset can use. The sandbox **cannot** reach
the app's CSS or fonts — copy the tokens you need into your document.

## 1. Palette

Light theme (default — the platform's default surface is light):

| Token | Value | Use |
|---|---|---|
| Page background | `#fafafa` | `body` |
| Card surface | `#ffffff` | cards, panels, tables |
| Hover wash | `#f4f4f5` | row hover, quiet button hover |
| Active tint | `#f0f0f2` | selected chips, segmented controls |
| Hairline | `#e4e4e7` | borders, dividers, table rules |
| Primary text | `#18181b` | headings, values |
| Secondary text | `#6b6b75` | labels, captions, table body |
| Tertiary text | `#9ca3af` | placeholder, disabled |
| **Brand primary** | `#6d28d9` | primary buttons, active states, focus rings |
| Primary hover | `#5b21b6` | button hover |
| Primary tint | `#ede9fe` | selected background, badge fill |
| Success | `#059669` | positive delta |
| Warning | `#d97706` | caution |
| Error | `#dc2626` | negative delta, destructive |

Semantic series colours for charts (use in this order, never more than 6):

```
#6d28d9  #0ea5e9  #059669  #d97706  #dc2626  #7c3aed
```

Dark theme (only if the user asks, or the asset is explicitly a dark UI):

| Token | Value |
|---|---|
| Page background | `#0c0d0f` |
| Card surface | `#17181c` |
| Hairline | `#27282d` |
| Primary text | `#ececee` |
| Secondary text | `#9a9ba4` |
| Brand primary | `#a78bfa` |

## 2. Type scale

```css
--fs-12: 12px;  /* micro labels, table meta — the floor, never go below */
--fs-13: 13px;  /* body, table cells */
--fs-14: 14px;  /* code */
--fs-15: 15px;  /* prose */
--fs-17: 17px;  /* section headings */
--fs-22: 22px;  /* page title */
--fs-28: 28px;  /* KPI value */
```

Font stack (no webfont needed):

```css
font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;  /* code/numbers */
```

Use `font-variant-numeric: tabular-nums` on any column of numbers and on KPI values —
misaligned digits are the most visible quality tell in a dashboard.

## 3. Shape, elevation, motion

```css
--radius-sm: 4px;    /* chips, badges      */
--radius-md: 6px;    /* buttons, inputs    */
--radius-lg: 10px;   /* inner panels       */
--radius-xl: 12px;   /* cards              */
--radius-2xl: 16px;  /* modals, sheets     */

--shadow-1: 0 1px 2px rgba(0,0,0,.05);
--shadow:   0 10px 25px -5px rgba(0,0,0,.05), 0 8px 10px -6px rgba(0,0,0,.05);

--dur-fast: 100ms;   /* hover, background fades */
--dur-base: 150ms;   /* dropdowns, presses      */
--ease-out: cubic-bezier(.16, 1, .3, 1);
```

Motion rule: transition colour/background/shadow only. Never animate `width`/`height`/
`top`/`left` — animate `transform`/`opacity`. Respect `prefers-reduced-motion`.

## 4. Base stylesheet (copy-paste)

```html
<style>
  :root {
    --bg:#fafafa; --surface:#ffffff; --wash:#f4f4f5; --tint:#f0f0f2;
    --border:#e4e4e7; --ink:#18181b; --muted:#6b6b75; --faint:#9ca3af;
    --primary:#6d28d9; --primary-hover:#5b21b6; --primary-tint:#ede9fe;
    --success:#059669; --warning:#d97706; --error:#dc2626;
    --radius-sm:4px; --radius-md:6px; --radius-xl:12px; --radius-2xl:16px;
    --shadow:0 10px 25px -5px rgba(0,0,0,.05), 0 8px 10px -6px rgba(0,0,0,.05);
    --shadow-1:0 1px 2px rgba(0,0,0,.05);
    --dur-fast:100ms; --dur-base:150ms; --ease-out:cubic-bezier(.16,1,.3,1);
  }
  * { box-sizing: border-box; }
  body {
    margin:0; background:var(--bg); color:var(--ink);
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    font-size:13px; line-height:1.5; -webkit-font-smoothing:antialiased;
  }
  .card { background:var(--surface); border:1px solid var(--border);
          border-radius:var(--radius-xl); box-shadow:var(--shadow-1); padding:20px; }
  .muted { color:var(--muted); }
  .kpi-value { font-size:28px; font-weight:700; font-variant-numeric:tabular-nums; letter-spacing:-.01em; }
  .kpi-label { font-size:12px; font-weight:600; text-transform:uppercase;
               letter-spacing:.04em; color:var(--muted); }
  .delta-up   { color:var(--success); }
  .delta-down { color:var(--error); }
  .btn {
    font:inherit; font-weight:600; font-size:13px; cursor:pointer;
    padding:8px 14px; border-radius:var(--radius-md); border:1px solid var(--border);
    background:var(--surface); color:var(--ink);
    transition: background var(--dur-fast) ease, border-color var(--dur-fast) ease;
  }
  .btn:hover { background:var(--wash); }
  .btn-primary { background:var(--primary); border-color:var(--primary); color:#fff; }
  .btn-primary:hover { background:var(--primary-hover); border-color:var(--primary-hover); }
  input, select, textarea {
    font:inherit; font-size:13px; padding:8px 10px; border-radius:var(--radius-md);
    border:1px solid var(--border); background:var(--surface); color:var(--ink);
  }
  input:focus-visible, select:focus-visible, textarea:focus-visible, .btn:focus-visible {
    outline:2px solid var(--primary); outline-offset:2px;
  }
  table { width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }
  th, td { padding:8px 12px; text-align:left; border-bottom:1px solid var(--border); }
  th { font-size:12px; font-weight:600; text-transform:uppercase;
       letter-spacing:.04em; color:var(--muted); }
  td { color:var(--muted); }
  td:first-child { color:var(--ink); }
  .grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); }
  @media (prefers-reduced-motion: reduce) {
    * { animation-duration:.01ms !important; transition-duration:.01ms !important; }
  }
</style>
```

## 5. Component recipes

### KPI card

```html
<div class="card">
  <div class="kpi-label">Total Revenue</div>
  <div class="kpi-value">$42,300</div>
  <div class="delta-up" style="font-size:12px;font-weight:600;">▲ 12.5% vs last month</div>
</div>
```

### Card grid

```html
<div class="grid">  <!-- auto-fit 220px — responsive with no media queries -->
  <div class="card">…</div>
  <div class="card">…</div>
</div>
```

### Segmented control

```html
<div role="tablist" style="display:inline-flex;gap:2px;padding:2px;background:var(--tint);border-radius:var(--radius-md);">
  <button role="tab" aria-selected="true" class="btn" style="background:var(--surface);box-shadow:var(--shadow-1);">Week</button>
  <button role="tab" aria-selected="false" class="btn" style="background:none;border-color:transparent;">Month</button>
</div>
```

### Empty state

```html
<div style="padding:48px 16px;text-align:center;color:var(--muted);">
  <div style="font-weight:600;color:var(--ink);margin-bottom:4px;">No data yet</div>
  <div style="font-size:12px;">Adjust the filters above to see results.</div>
</div>
```

## 6. Layout rules

- Content max-width `1200px`, centred, `padding:24px`.
- Card grid: `repeat(auto-fit, minmax(220px, 1fr))` — responsive by construction.
- Section rhythm: `24px` between blocks, `16px` inside a card.
- Never nest a card inside a card; use the `--wash` background for inner regions.
- Charts get an explicit height (`h-[320px]` / `height:320px`) — a chart in a zero-height
  parent renders blank. This is the most common chart bug.
