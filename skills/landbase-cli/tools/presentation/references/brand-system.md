# Landbase Brand System

Full CSS token system, component patterns, and layout rules. Load this when
generating any Landbase-branded HTML.

## CSS Custom Properties

```css
:root {
  /* ── Core brand ── */
  --teal: #00a09a; /* primary brand, links, icons, eyebrow text */
  --green: #59e395; /* highlight, gradient end, emphasis, stat numbers */
  --green-mid: #4dc8a4; /* gradient midpoint, button gradient end */

  /* ── Dark surfaces ── */
  --dark: #0c2e34; /* primary dark background (page, hero, nav, footer) */
  --dark-card: #102e36; /* elevated surfaces on dark */
  --dark-raised: #132e35; /* slightly raised surfaces */
  --dark-border: #1c464c; /* primary borders on dark */
  --dark-border-2: #143840; /* secondary/subtle borders on dark */

  /* ── Text on dark ── */
  --muted-text: rgba(255, 255, 255, 0.45);
  --subtle-text: rgba(255, 255, 255, 0.25);

  /* ── Light surfaces ── */
  --surface: #f2f5f4;
  --surface-2: #eaf0ee;
  --white: #ffffff;
  --border: #dce8e5;

  /* ── Text on light ── */
  --ink: #0b1c1a;
  --ink-mid: #345450;
  --ink-muted: #628480;

  /* ── Radii ── */
  --r-page: 12px;
  --r-content: 16px;
  --r-card: 10px;
  --r-panel: 14px;
  --r-btn: 8px;
  --r-pill: 4px;
  --r-tag: 6px;
  --r-circle: 50%;

  /* ── Font stacks ── */
  --sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --mono: "SF Mono", "Fira Code", ui-monospace, monospace;
}
```

### Opacity patterns (dark backgrounds)

| Element          | Background               | Border                   |
| ---------------- | ------------------------ | ------------------------ |
| Teal-tinted card | `rgba(0,160,154,0.08)`   | `rgba(0,160,154,0.18)`   |
| Teal-strong card | `rgba(0,160,154,0.12)`   | `rgba(0,160,154,0.25)`   |
| Neutral card     | `rgba(255,255,255,0.04)` | `rgba(255,255,255,0.08)` |
| Neutral subtle   | `rgba(255,255,255,0.06)` | `rgba(255,255,255,0.10)` |
| Green badge      | `rgba(89,227,149,0.08)`  | `rgba(89,227,149,0.22)`  |

### Data-viz supplementary (use sparingly, not in headlines)

- Good/positive → `var(--green)` (#59e395)
- Bad/negative → `#fe6060`
- Warn → `#ffa600`

---

## Gradients

```css
/* Primary text gradient — accent words in headlines */
background: linear-gradient(90deg, #00a09a, #59e395);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;

/* Section title gradient (light backgrounds) */
background: linear-gradient(90deg, #00a09a, #4dc8a4);

/* Button / badge gradient */
background: linear-gradient(135deg, #00a09a, #4dc8a4);

/* Dark card gradient */
background: linear-gradient(145deg, #0e3038, #091e23);

/* Teal glow (radial, behind hero) */
background: radial-gradient(
  circle,
  rgba(0, 160, 154, 0.14) 0%,
  transparent 60%
);

/* Dot grid overlay */
background-image: radial-gradient(rgba(0, 160, 154, 0.07) 1px, transparent 1px);
background-size: 26px 26px;

/* Accent gradient bar (top of cards) — 2.5px via ::before */
background: linear-gradient(90deg, #00a09a, #59e395);
```

**Gradient text:**

```css
.grad {
  background: linear-gradient(90deg, var(--teal), var(--green-mid));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

On dark backgrounds, use `var(--teal)` → `var(--green)` for a brighter range.

---

## Typography

```html
<link
  href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap"
  rel="stylesheet"
/>
```

`html { font-size: 13.5px; }` — all sizing in rem.

| Element          | Size         | Weight  | Letter-spacing | Line-height |
| ---------------- | ------------ | ------- | -------------- | ----------- |
| Hero headline    | 2.9rem       | 900     | -0.045em       | 1.03        |
| Section h2       | 1.5rem       | 800     | -0.03em        | 1.18        |
| Column title     | 1rem–1.15rem | 700     | -0.015em       | 1.3         |
| Body             | 0.81–0.9rem  | 400     | —              | 1.68–1.72   |
| Eyebrow / label  | 0.6–0.62rem  | 600–700 | 0.14–0.18em    | —           |
| Stat number      | 2.1rem       | 900     | -0.045em       | 1           |
| Stat description | 0.67rem      | 400     | —              | 1.5         |

---

## Visual Design Patterns

### Noise texture

```css
.noise::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,..."); /* fractalNoise SVG filter */
  pointer-events: none;
  z-index: 0;
  opacity: 0.03;
}
```

### Dot grid

```css
.dot-grid {
  background-image: radial-gradient(
    rgba(0, 160, 154, 0.07) 1px,
    transparent 1px
  );
  background-size: 26px 26px;
}
```

### Strikethrough (before/after)

```html
<span class="strike-wrap"><span class="strike-line"></span>weeks</span>
```

```css
.strike-wrap {
  position: relative;
  color: rgba(255, 255, 255, 0.25);
}
.strike-line {
  position: absolute;
  left: -4px;
  right: -4px;
  top: 50%;
  transform: translateY(-50%) rotate(-2deg);
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
```

### Vignette

```css
background: radial-gradient(
  ellipse 100% 100% at 50% 50%,
  transparent 40%,
  rgba(0, 0, 0, 0.5) 100%
);
```

### Box shadows

```css
/* Page container */
box-shadow:
  0 0 0 1px rgba(255, 255, 255, 0.06),
  0 40px 120px rgba(0, 0, 0, 0.4);
/* Dark cards */
box-shadow:
  0 24px 64px rgba(0, 0, 0, 0.45),
  0 0 0 1px rgba(255, 255, 255, 0.04);
/* CTA buttons */
box-shadow: 0 4px 20px rgba(0, 160, 154, 0.25);
/* Light cards */
box-shadow: 0 6px 24px rgba(0, 160, 154, 0.1);
```

---

## One-Pager Components

### Layout

- Single HTML file, all CSS in `<style>`, Inter from Google Fonts CDN
- Max-width: `920px` (one-pager) or `1200px` (landing page)
- Section padding: `80px 0` desktop, `48px 0` mobile
- CSS Grid for cards: `repeat(auto-fit, minmax(240px, 1fr))`

### Hero

```html
<section class="hero noise dot-grid">
  <div class="teal-glow"></div>
  <div class="wrap">
    <div class="eyebrow">[EYEBROW]</div>
    <h1>[LINE_1]<br /><span class="grad">[ACCENT]</span></h1>
    <p class="sub">[SUBHEADLINE]</p>
    <a class="cta" href="#cta">[CTA] →</a>
  </div>
</section>
```

```css
.hero {
  position: relative;
  background: var(--dark);
  color: #fff;
  padding: 120px 0 96px;
  overflow: hidden;
}
.teal-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 50% 40%,
    rgba(0, 160, 154, 0.14) 0%,
    transparent 60%
  );
  pointer-events: none;
}
.hero .wrap {
  position: relative;
  z-index: 2;
  max-width: 920px;
  margin: 0 auto;
  padding: 0 24px;
}
.eyebrow {
  color: var(--teal);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
h1 {
  font-size: 2.9rem;
  font-weight: 900;
  letter-spacing: -0.045em;
  line-height: 1.03;
  margin: 16px 0 20px;
  max-width: 600px;
}
.sub {
  color: var(--muted-text);
  font-size: 0.9rem;
  line-height: 1.72;
  max-width: 560px;
}
```

### Stats row

```css
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 32px;
}
.stat .num {
  color: #fff;
  font-size: 2.1rem;
  font-weight: 900;
  letter-spacing: -0.045em;
  line-height: 1;
}
.stat .desc {
  color: var(--muted-text);
  font-size: 0.67rem;
  line-height: 1.5;
  margin-top: 8px;
}
```

### CTA button

```css
.cta {
  display: inline-block;
  padding: 14px 32px;
  border-radius: var(--r-btn);
  background: linear-gradient(135deg, #00a09a, #4dc8a4);
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  box-shadow: 0 4px 20px rgba(0, 160, 154, 0.25);
  text-decoration: none;
  width: fit-content;
}
```

### Cards on light

```css
.card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 24px;
  position: relative;
  transition: box-shadow 0.2s;
}
.card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2.5px;
  background: linear-gradient(90deg, #00a09a, #59e395);
  border-radius: var(--r-card) var(--r-card) 0 0;
}
.card:hover {
  box-shadow: 0 6px 24px rgba(0, 160, 154, 0.1);
}
.card h3 {
  color: var(--ink);
  font-size: 1rem;
  font-weight: 700;
}
.card p {
  color: var(--ink-mid);
  font-size: 0.81rem;
  line-height: 1.68;
  margin-top: 8px;
}
```

### Cards on dark

```css
.dark-card {
  background: rgba(0, 160, 154, 0.08);
  border: 1px solid rgba(0, 160, 154, 0.18);
  border-radius: var(--r-card);
  padding: 24px;
}
.dark-card h3 {
  color: #fff;
  font-size: 0.84rem;
  font-weight: 700;
}
.dark-card p {
  color: var(--muted-text);
  font-size: 0.76rem;
  line-height: 1.6;
  margin-top: 6px;
}
```

### Messaging slots (one-pager)

- **Hero:** `[EYEBROW]`, `[HEADLINE]`, `[ACCENT]` (gradient), `[SUBHEADLINE]`
- **Stats:** 3–4 × `[NUM]` / `[DESC]`
- **Problem:** `[TAG]`, `[TITLE]`, `[BODY]` (2–3 sentences)
- **Solution:** `[TAG]`, `[TITLE]` + `[ACCENT]`, 3 steps
- **How It Works:** up to 5 items with `[NAME]` / `[DESC]`
- **Case Studies:** 4 cards — company, challenge, result, 3 metric pills,
  testimonial
- **Capabilities:** 6 stat cards with `[STAT]` / `[LABEL]` / `[DESC]`
- **Why Switch:** 3 before-after cards with strikethrough
- **Built For:** 3 persona cards
- **Footer:** `[CTA_TEXT]`, `[EMAIL_OR_URL]`

### Ad specs (optional)

Portrait 1080×1350 (Meta) · Square 1080×1080 (Meta/LinkedIn). Dark background,
teal glow, compact CTA.

### Print styles (one-pager)

```css
@media print {
  @page {
    size: 1000px 5000px;
    margin: 0;
  }
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .grad {
    background: none !important;
    -webkit-text-fill-color: #00a09a !important;
  }
}
```

---

## Presentation Mode Components

### Slide system

```css
body {
  background: var(--surface-2);
  scroll-snap-type: y mandatory;
}
.slide {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  scroll-snap-align: start;
  padding: 40px 24px;
}
.slide-inner {
  max-width: 880px;
  background: var(--white);
  border-radius: var(--r-content);
  box-shadow:
    0 24px 64px rgba(0, 0, 0, 0.12),
    0 0 0 1px var(--border);
  overflow: hidden;
}
.slide-stripe {
  height: 4px;
  background: linear-gradient(90deg, #00a09a, #59e395);
}
.slide-body {
  padding: 48px 56px 52px;
}
h2 {
  color: var(--ink);
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.18;
}
.s-label {
  color: var(--teal);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
```

### Cover slide

- `.slide.cover-slide { padding: 0; }`, `.slide-inner` uses `var(--dark)`
  background
- Teal glow + dot grid overlays
- `.cover-tag`:
  `background: rgba(89,227,149,0.08); border: 1px solid rgba(89,227,149,0.22); color: var(--green);`
- `.cover-title`: 2rem, weight 800, white, `.grad` span for accent
- `.cover-stats`:
  `background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08);`

### Print/PDF (CRITICAL)

```css
@media print {
  @page {
    size: 11in 8.5in;
    margin: 0.25in;
  }
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .slide {
    width: 10.5in;
    height: 8in;
    min-height: 8in;
    max-height: 8in;
    overflow: hidden;
    break-after: page;
    page-break-after: always;
    display: flex;
    align-items: stretch;
  }
  .slide-inner {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .slide-body {
    flex: 1;
  }
  .slide-stripe,
  .slide-footer {
    flex-shrink: 0;
  }
}
```

Use `height/max-height: 8in` — never `min-height` alone (causes overflow). Cover
slide: `justify-content: center`, no border.

### Stat cards

```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="number grad">4,260</div>
    <div class="label">Description</div>
  </div>
</div>
```

`.grad` (default) · `.good` (green) · `.bad` (#fe6060)

### Tables

```html
<table>
  <thead>
    <tr>
      <th>Header</th>
      <th class="num">Number</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Item</strong></td>
      <td class="num good">+40</td>
    </tr>
    <tr class="total-row">
      <td><strong>Total</strong></td>
      <td class="num"><strong>100</strong></td>
    </tr>
  </tbody>
</table>
```

Uppercase headers, 2px `var(--dark)` bottom border, alternating rows
`rgba(0,160,154,0.04)`.

### Callouts

```html
<div class="callout teal">
  <p><strong>Key point:</strong> Text.</p>
</div>
```

`.teal` (default) · `.success` (green border) · `.dark` (dark bg, white text)

### Tier badges

```html
<span class="tier a">A</span>
<!-- green -->
<span class="tier b">B</span>
<!-- teal -->
<span class="tier c">C</span>
<!-- green-mid -->
<span class="tier d">D</span>
<!-- #ffa600 -->
<span class="tier e">E</span>
<!-- #fe6060 -->
```

### Flow diagram

```html
<div class="flow">
  <div class="flow-step">Step 1</div>
  <span class="flow-arrow">→</span>
  <div class="flow-step">Step 2</div>
</div>
```

### Bar chart

```html
<div class="bar-chart">
  <div class="bar-row">
    <div class="bar-label"><span class="tier a">A</span></div>
    <div class="bar-track">
      <div
        class="bar-fill"
        style="width:55%; background: linear-gradient(90deg, #00a09a, #59e395);"
      >
        236
      </div>
    </div>
    <div class="bar-val">55%</div>
  </div>
</div>
```

### Signal grid

```html
<div class="signal-grid">
  <div class="signal-box">
    <h3>Category</h3>
    <div class="pts">+8 pts each</div>
    <div class="tags"><span class="tag">keyword</span></div>
  </div>
  <div class="signal-box negative">
    <h3>Negative</h3>
    <div class="pts">−10 pts each</div>
  </div>
</div>
```

### Simplified slide pattern (data reports / internal decks)

```html
<div class="slide">
  <div class="slide-header">
    <h1>Title</h1>
    <div class="sub">Context</div>
  </div>
  <!-- stats, ctx paragraph, tables, callouts -->
  <div class="footer">Landbase · Report Name · Date</div>
</div>
```

```css
.slide-header {
  background: var(--dark);
  color: #fff;
  padding: 24px 32px 18px;
  border-radius: var(--r-card);
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.slide-header::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00a09a, #59e395);
}
.slide-header h1 {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.03em;
}
.ctx {
  font-size: 0.75rem;
  color: var(--ink-muted);
  line-height: 1.6;
  margin-bottom: 12px;
}
.footer {
  position: absolute;
  bottom: 16px;
  left: 56px;
  right: 56px;
  font-size: 9px;
  color: var(--ink-muted);
  text-align: center;
  border-top: 1px solid var(--border);
  padding-top: 8px;
}
```

Use simplified pattern for internal data reports. Use full component system for
external/executive decks.
