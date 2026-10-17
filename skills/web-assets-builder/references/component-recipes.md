# Component Recipes

Copy-paste HTML/CSS for the pieces that appear in almost every asset. Each is
self-contained: paste it into the blueprint shell, keep the class names, swap the
content. Tokens come from `design-system.md`.

Assumes the Tailwind Play CDN (`https://cdn.tailwindcss.com/3.4.17`) in `<head>`,
and the lucide icon font (`class="icon-…"`) for icons.

---

## KPI card

```html
<div class="bg-white p-5 rounded-xl border border-[#e4e4e7] shadow-sm">
  <div class="flex items-start justify-between">
    <span class="text-xs font-semibold uppercase tracking-wider text-[#6b6b75]">Revenue</span>
    <span class="w-7 h-7 grid place-items-center rounded-md bg-[#ede9fe] text-[#6d28d9]">
      <i class="icon-trending-up text-sm" aria-hidden="true"></i>
    </span>
  </div>
  <p class="mt-2 text-[28px] font-bold leading-none" style="font-variant-numeric:tabular-nums">€284,900</p>
  <p class="mt-2 text-xs font-semibold text-emerald-600">
    ▲ 8.4% <span class="font-normal text-[#6b6b75]">vs last quarter</span>
  </p>
</div>
```

**With a sparkline** — pair the value with a 48px chart (see `chart-recipes.md`):

```html
<div class="bg-white p-5 rounded-xl border border-[#e4e4e7] shadow-sm">
  <div class="text-xs font-semibold uppercase tracking-wider text-[#6b6b75]">Revenue</div>
  <div class="mt-2 flex items-end justify-between gap-3">
    <p class="text-[28px] font-bold leading-none" style="font-variant-numeric:tabular-nums">€284,900</p>
    <div id="spark" style="width:96px;height:44px"></div>
  </div>
</div>
```

Always `tabular-nums` on numbers, and always a `<span>` for the comparison
context — a bare "+8.4%" with no baseline means nothing.

---

## Card grid

```html
<div class="grid gap-4" style="grid-template-columns:repeat(auto-fit,minmax(210px,1fr))">
  <div class="bg-white p-5 rounded-xl border border-[#e4e4e7] shadow-sm">…</div>
  <div class="bg-white p-5 rounded-xl border border-[#e4e4e7] shadow-sm">…</div>
</div>
```

`auto-fit` + `minmax` is responsive with no media queries. Use it instead of
`grid-cols-4` unless you specifically need a fixed column count.

---

## Buttons

```html
<button type="button" class="px-4 py-2 rounded-lg bg-[#6d28d9] text-white text-sm font-semibold
        hover:bg-[#5b21b6] transition-colors focus:outline-none focus-visible:ring-2
        focus-visible:ring-[#6d28d9] focus-visible:ring-offset-2">Primary</button>

<button type="button" class="px-4 py-2 rounded-lg border border-[#e4e4e7] bg-white text-sm font-semibold
        hover:bg-[#f4f4f5] transition-colors focus:outline-none focus-visible:ring-2
        focus-visible:ring-[#6d28d9]">Secondary</button>

<button type="button" aria-label="Delete row" class="p-2 rounded-md border border-[#e4e4e7] bg-white
        hover:bg-[#f4f4f5] transition-colors">
  <i class="icon-trash-2 text-sm" aria-hidden="true"></i>
</button>
```

Icon-only buttons **must** have `aria-label`. Always `type="button"` — inside a
form the default is `submit`.

---

## Segmented control

```html
<div role="tablist" aria-label="Time range" class="inline-flex gap-0.5 p-0.5 bg-[#f0f0f2] rounded-lg">
  <button role="tab" type="button" aria-selected="true"
          class="px-3 py-1.5 text-xs font-semibold rounded-md bg-white shadow-sm transition-colors">Week</button>
  <button role="tab" type="button" aria-selected="false"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors">Month</button>
</div>
```

Wire it: on click, set `aria-selected` on the chosen button and remove it from the
others, **and** change the visual class. A control that toggles appearance but not
state is the classic dead-UI bug — see "Wiring" below.

---

## Tabs (real panels)

```html
<div class="border-b border-[#e4e4e7] flex gap-5" role="tablist">
  <button role="tab" type="button" data-tab="overview" aria-selected="true"
          class="pb-2.5 text-sm font-semibold border-b-2 border-[#6d28d9] text-[#18181b]">Overview</button>
  <button role="tab" type="button" data-tab="detail" aria-selected="false"
          class="pb-2.5 text-sm font-medium border-b-2 border-transparent text-[#6b6b75] hover:text-[#18181b]">Detail</button>
</div>
<div data-panel="overview" class="pt-4">…</div>
<div data-panel="detail" class="pt-4 hidden">…</div>
```

---

## Form field

```html
<div>
  <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-[#6b6b75] mb-2">
    Work email
  </label>
  <input id="email" type="email" required placeholder="you@company.com"
         class="w-full px-3 py-2.5 text-sm rounded-lg border border-[#e4e4e7] bg-white
                placeholder:text-[#9ca3af] focus:outline-none focus-visible:ring-2
                focus-visible:ring-[#6d28d9]">
  <p class="mt-1.5 text-xs text-[#6b6b75]">We'll only use this for account notices.</p>
</div>
```

Every input needs a `<label for>`. Placeholders are not labels — they vanish on
input and fail screen readers.

---

## Range slider with live value

```html
<label for="budget" class="flex items-center justify-between text-xs font-semibold
       uppercase tracking-wider text-[#6b6b75] mb-2">
  <span>Budget</span>
  <span class="normal-case tracking-normal text-sm font-semibold text-[#18181b]"
        style="font-variant-numeric:tabular-nums" id="budget-out">€25,000</span>
</label>
<input id="budget" type="range" min="1000" max="200000" step="1000" value="25000"
       class="w-full cursor-pointer" style="accent-color:#6d28d9">
```

---

## Badge / status pill

```html
<span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700">Active</span>
<span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-sky-50 text-sky-700">Trial</span>
<span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700">Past due</span>
<span class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[#f0f0f2] text-[#6b6b75]">Churned</span>
```

Map status → colour in one object so the mapping stays consistent:

```js
var STATUS = {
  'Active':   'bg-emerald-50 text-emerald-700',
  'Trial':    'bg-sky-50 text-sky-700',
  'Past due': 'bg-amber-50 text-amber-700'
};
// fallback so an unexpected status never renders unstyled
var cls = STATUS[row.status] || 'bg-[#f0f0f2] text-[#6b6b75]';
```

---

## Table (static)

```html
<div class="bg-white rounded-xl border border-[#e4e4e7] shadow-sm overflow-hidden">
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <caption class="sr-only">Revenue by channel</caption>
      <thead class="bg-[#fafafa]">
        <tr class="text-left text-[11px] uppercase tracking-wider text-[#6b6b75]">
          <th scope="col" class="px-5 py-3 font-semibold">Channel</th>
          <th scope="col" class="px-5 py-3 font-semibold text-right">Revenue</th>
        </tr>
      </thead>
      <tbody style="font-variant-numeric:tabular-nums">
        <tr class="border-t border-[#e4e4e7] hover:bg-[#fafafa] transition-colors">
          <td class="px-5 py-3 font-medium text-[#18181b]">Enterprise</td>
          <td class="px-5 py-3 text-right text-[#6b6b75]">€142,400</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

Right-align numbers, `tabular-nums`, `scope="col"` on headers, wrap in
`overflow-x-auto` so narrow previews scroll instead of clipping.

---

## Empty state

```html
<div class="py-12 text-center">
  <div class="w-10 h-10 mx-auto grid place-items-center rounded-full bg-[#f0f0f2] text-[#9ca3af]">
    <i class="icon-inbox text-lg" aria-hidden="true"></i>
  </div>
  <p class="mt-3 font-semibold">No data yet</p>
  <p class="mt-1 text-xs text-[#6b6b75]">Adjust the filters above to see results.</p>
</div>
```

Every data-driven view needs one. A blank region reads as broken, not as empty.

---

## Loading skeleton

```html
<div class="animate-pulse space-y-3" aria-hidden="true">
  <div class="h-4 w-1/3 rounded bg-[#f0f0f2]"></div>
  <div class="h-3 w-full rounded bg-[#f0f0f2]"></div>
  <div class="h-3 w-5/6 rounded bg-[#f0f0f2]"></div>
</div>
```

Only for a genuinely async load. A static asset should not fake latency.

---

## Toast / inline alert

```html
<div role="status" class="flex items-start gap-2.5 p-3.5 rounded-lg border border-emerald-200 bg-emerald-50">
  <i class="icon-circle-check text-emerald-600 text-sm mt-0.5" aria-hidden="true"></i>
  <p class="text-sm text-emerald-800">Saved to your workspace.</p>
</div>
```

`role="status"` for confirmations, `role="alert"` for errors. Never rely on
colour alone — the icon and the wording carry the meaning.

---

## Modal / dialog

```html
<div id="modal" class="hidden fixed inset-0 z-50 bg-black/40 grid place-items-center p-4"
     role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="bg-white rounded-2xl shadow-lg p-6 max-w-sm w-full">
    <h2 id="modal-title" class="text-base font-semibold">Confirm deletion</h2>
    <p class="mt-2 text-sm text-[#6b6b75]">This cannot be undone.</p>
    <div class="mt-5 flex justify-end gap-2">
      <button type="button" data-close class="px-3.5 py-2 rounded-lg border border-[#e4e4e7] bg-white text-sm font-semibold hover:bg-[#f4f4f5]">Cancel</button>
      <button type="button" class="px-3.5 py-2 rounded-lg bg-[#dc2626] text-white text-sm font-semibold hover:bg-red-700">Delete</button>
    </div>
  </div>
</div>
```

Use the native `<dialog>` element when you can — you get focus trapping and Esc
handling for free. If you hand-roll it, you must: move focus in on open, return it
on close, and handle Esc.

---

## Progress bar

```html
<div class="h-2 rounded-full bg-[#f0f0f2] overflow-hidden" role="progressbar"
     aria-valuenow="68" aria-valuemin="0" aria-valuemax="100" aria-label="Onboarding progress">
  <div class="h-full rounded-full bg-[#6d28d9]" style="width:68%"></div>
</div>
```

---

## Kbd hint

```html
<kbd class="px-1.5 py-0.5 rounded border border-[#e4e4e7] bg-[#fafafa] text-[11px] font-mono text-[#6b6b75]">⌘K</kbd>
```

---

## Wiring: making controls actually work

The most common quality failure in a generated asset is a **dead control** — a
button or tab that looks interactive and does nothing. If you render a control,
wire it. Minimum viable patterns:

```js
// Tabs / segmented control — swap selection AND panel
document.querySelectorAll('[role="tab"]').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('[role="tab"]').forEach(function (b) {
      var on = b === btn;
      b.setAttribute('aria-selected', String(on));
      b.classList.toggle('bg-white', on);
      b.classList.toggle('shadow-sm', on);
    });
    document.querySelectorAll('[data-panel]').forEach(function (p) {
      p.classList.toggle('hidden', p.dataset.panel !== btn.dataset.tab);
    });
  });
});

// Modal open/close
function openModal() { document.getElementById('modal').classList.remove('hidden'); }
function closeModal() { document.getElementById('modal').classList.add('hidden'); }
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeModal();
});

// Filter + re-render — one function is the single source of truth
function render() { /* read state, write DOM */ }
document.getElementById('search').addEventListener('input', debounce(function (e) {
  state.query = e.target.value;
  render();
}, 120));

function debounce(fn, ms) {
  var t; return function () { var a = arguments, s = this;
    clearTimeout(t); t = setTimeout(function () { fn.apply(s, a); }, ms); };
}
```

Rules:
- **One `render()` per view.** Scattered direct DOM writes drift out of sync.
- **Debounce text input** (≈120ms); do not debounce clicks.
- **Escape any user/data string inserted as HTML**:
  ```js
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  ```
  Prefer `textContent` over `innerHTML` wherever the value is not markup.
- **If you can't wire it, don't render it.** A static label beats a dead button.
