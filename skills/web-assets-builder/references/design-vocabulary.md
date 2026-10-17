# Design Vocabulary

When the user asks for a *style* — "make it look brutalist", "editorial", "like a
fintech dashboard", "glassmorphic" — these are the concrete CSS signatures behind
those words. Pick the closest, apply the signature, then keep the structure from
the relevant template.

Two rules before you use any of this:

1. **A style is a set of decisions, not a filter.** Choosing "editorial" means a
   serif display face, tight measure, generous leading, near-monochrome palette —
   not just changing a colour. Half-applying a style looks worse than not trying.
2. **Legibility beats the aesthetic.** Whatever you pick: body text ≥ 13px,
   contrast ≥ 4.5:1, focus states visible, and never put text on a busy gradient
   without a scrim.

---

## The axes that define any style

Almost every "style" is a position on these five axes. Decide all five and the
style falls out:

| Axis | Range | Effect |
|---|---|---|
| **Density** | airy ←→ dense | Spacing scale, line-height, how much fits per screen |
| **Contrast** | low (grey-on-grey) ←→ high (black/white) | Perceived authority; low = calm, high = editorial |
| **Radius** | 0 (sharp) ←→ 999px (pill) | Sharp = serious/technical, round = friendly/consumer |
| **Elevation** | flat (borders) ←→ layered (shadows) | Flat = modern/technical, layered = familiar/soft |
| **Chroma** | monochrome ←→ one accent ←→ multi | One accent is almost always the strongest choice |

Write the five down before you write CSS. It prevents the "everything at once"
look that reads as generic.

---

## Styles with concrete signatures

### Swiss / International (grid, neutrality)
The safe default for anything data-related.

```css
--bg:#ffffff; --ink:#111; --muted:#666; --line:#e5e5e5; --accent:#e00;
font-family: 'Inter', system-ui, sans-serif;
font-size: 13px; line-height: 1.5;
/* 12-col grid, generous margins, left-aligned everything, no centring */
/* One red accent used sparingly. Rules (1px lines) instead of cards. */
h1 { font-size: 40px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.05; }
```
Density airy · contrast high · radius 0 · elevation flat · chroma one accent.

### Editorial (magazine, long-form)
For reports and anything with prose.

```css
font-family: 'Source Serif 4', Georgia, serif;   /* display + body */
--measure: 62ch;                                  /* reading width, never wider */
line-height: 1.7; font-size: 17px;                /* body prose is bigger */
h1 { font-size: clamp(32px, 6vw, 56px); letter-spacing: -0.02em; }
/* drop caps, pull quotes, generous vertical rhythm (32–48px), asymmetric layout */
```
Density airy · contrast high · radius 0 · elevation flat · chroma none.

### Brutalist / neo-brutalist
Loud on purpose. Use only when asked.

```css
--bg:#fff; --ink:#000; --accent:#ff5c00;
font-family: ui-monospace, 'JetBrains Mono', monospace;   /* or a heavy grotesk */
border: 3px solid #000; border-radius: 0;
box-shadow: 6px 6px 0 #000;                                /* hard offset, never blurred */
text-transform: uppercase; letter-spacing: 0.04em;
/* no gradients, no transparency, no subtle greys — everything is a decision */
```
Density dense · contrast max · radius 0 · elevation hard-shadow · chroma 1–2 loud.

### Glassmorphic / aurora
Dark, layered, translucent. High visual payoff, easy to make unreadable.

```css
--bg:#06050a; --accent:#8f7bff;
background:
  radial-gradient(900px 420px at 20% -10%, rgba(143,123,255,.28), transparent 70%),
  radial-gradient(700px 380px at 85% 10%, rgba(80,200,255,.16), transparent 70%),
  #06050a;
.card {
  background: rgba(255,255,255,.045);
  border: 1px solid rgba(255,255,255,.09);
  backdrop-filter: blur(12px);
  border-radius: 16px;
}
h1 { font-size: clamp(40px, 7vw, 84px); letter-spacing: -0.04em; line-height: 1.02; color: #fff; }
```
**Always put a scrim behind text on a gradient.** `backdrop-filter` is expensive —
use it on a handful of elements, not every card.
Density airy · contrast high-on-dark · radius large · elevation glow · chroma 1–2.

### Terminal / technical
For developer-facing tools, logs, config.

```css
--bg:#0d1117; --ink:#c9d1d9; --accent:#58a6ff; --ok:#3fb950;
font-family: ui-monospace, 'JetBrains Mono', Consolas, monospace;
font-size: 13px; line-height: 1.55;
border-radius: 6px;                        /* small, not pill */
/* monospace everywhere, including headings; thin borders; no shadows */
/* green/amber/red for state, exactly like a terminal */
```
Density dense · contrast high · radius small · elevation flat · chroma semantic.

### Soft / consumer
Friendly, rounded, low-contrast. Good for onboarding, empty states.

```css
--bg:#fafafa; --ink:#18181b; --muted:#6b6b75; --accent:#6d28d9;
border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,.06);
font-size: 15px; line-height: 1.6;
/* pill buttons, soft shadows, pastel tints (accent at 8% opacity), lots of padding */
```
Density airy · contrast medium · radius large · elevation soft · chroma one + tints.

### Dashboard / data-dense (the Ajelix house style)
For KPI views — see `design-system.md` for the full token set.

```css
--bg:#fafafa; --surface:#fff; --line:#e4e4e7; --accent:#6d28d9;
border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.05);
font-size: 13px; font-variant-numeric: tabular-nums;   /* numbers must align */
/* cards on a wash, 1px hairlines, uppercase micro-labels, one accent */
```
Density dense · contrast medium · radius medium · elevation hairline · chroma 1 + semantics.

---

## Typography pairings

Never ship a default browser font. Load from a CDN or use the system stack.

| Style | Display | Body |
|---|---|---|
| Swiss / dashboard | Inter, system-ui | Inter, system-ui |
| Editorial | Source Serif 4 / Playfair | Source Serif 4 / Georgia |
| Brutalist | Archivo Black / heavy grotesk | JetBrains Mono |
| Technical | JetBrains Mono | JetBrains Mono |
| Soft / consumer | Inter, system-ui | Inter, system-ui |

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
```

Always give a real fallback in the stack — the preview can be offline.

**Display type rules** (what separates designed from default):
- Tighten tracking as size grows: `-0.02em` at 32px, `-0.045em` at 80px.
- Tighten leading on display: `1.0`–`1.1`, never the body's `1.5`.
- Body text wants the opposite: `1.6`–`1.7` leading, and a measure of 60–70ch.
- One weight jump is enough. `700` display + `400` body beats five weights.

---

## Motion

```css
--dur-fast:100ms; --dur-base:180ms; --ease:cubic-bezier(.16,1,.3,1);
transition: transform var(--dur-base) var(--ease), opacity var(--dur-base) var(--ease);
```

- Animate **`transform` and `opacity` only**. Animating `width`/`height`/`top`
  forces layout on every frame.
- Enter animations: 180–320ms. Anything longer feels broken on repeat use.
- Hover feedback: ≤120ms.
- Always honour `prefers-reduced-motion`:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { animation-duration:.01ms !important; transition-duration:.01ms !important; }
  }
  ```
- **Never animate content into an invisible default state.** Start visible, and
  let JS add the hidden state — a failed observer must not blank the page.

---

## Colour discipline

- **One accent.** Everything else is a neutral ramp. Two accents fight.
- Build the ramp from one hue: `50/100/300/500/700/900`. Don't hand-pick greys.
- Semantic colours are separate from the accent and reserved:
  `#059669` success · `#d97706` warning · `#dc2626` error.
- Check contrast: body text ≥ 4.5:1, large display text ≥ 3:1, borders ≥ 3:1 if
  they carry meaning. Dark mode is not "invert" — re-pick, because saturated
  colours vibrate on black (lighten them).
- **Never encode meaning in colour alone.** Pair with an icon, arrow, or word.

---

## Layout

```css
.wrap { max-width: 1140px; margin-inline: auto; padding-inline: clamp(20px, 4vw, 44px); }
.grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); }
```

- `clamp()` for fluid type and gutters beats breakpoint soup.
- `auto-fit` + `minmax` is responsive with zero media queries.
- Establish a spacing scale (`4 8 12 16 24 32 48 64`) and use only those values.
- Vertical rhythm: one large gap between sections, one small gap inside them.
- Whitespace is the cheapest quality signal. When in doubt, add more.

---

## What makes output look generic

Avoid these — they are the tells:

| Tell | Instead |
|---|---|
| Centred everything | Left-align body; centre only the hero |
| Three equal cards in a row, always | Vary emphasis; one card can be larger |
| Purple-to-pink gradient on a white page | One accent, used sparingly |
| `border-radius: 8px` on everything | Pick a radius scale and commit |
| Shadows on every element | Hairlines, or shadow on one layer only |
| Placeholder lorem / `$42,300` | Real data, or clearly labelled sample |
| All text the same size | 3–4 distinct sizes, one display size |
| Every section the same height | Vary rhythm; let one section breathe |
| Icons from three different sets | One icon set, one stroke weight |
| Default browser font | Load a font, or use a deliberate system stack |
