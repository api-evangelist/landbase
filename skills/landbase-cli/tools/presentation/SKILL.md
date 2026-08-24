---
name: presentation
description:
  Generate HTML output using the Landbase visual identity. Default is a
  responsive one-pager. Switch to slide mode for presentations, slide decks, or
  PDF export.
when_to_use:
  when the user wants to generate a Landbase-branded HTML page, one-pager,
  landing page, slide deck, or PDF presentation — phrases like "make a
  one-pager", "create a presentation", "generate a slide deck", "build a landing
  page", "make this into slides", or when another skill produces output that
  needs a visual deliverable
version: 1.0.0
user-invocable: true
argument-hint: "[topic or description] [--presentation]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
model: sonnet
---

# Presentation

Read references/brand-system.md before generating any HTML. It contains the full
CSS token system, component patterns, and layout rules. Every color, gradient,
and component must come from that reference.

## Step 1 — Choose mode

**Default — one-pager:** user asks for a page, landing page, one-pager, or any
HTML output.

**Presentation mode:** user says "presentation", "slide deck", "slides", "PDF",
or "deck" — or passes `--presentation`.

## Step 2 — Collect inputs

Ask for or infer from context:

- **Topic or content** — what the page is about, or a file/data source to
  visualize
- **Logo** — if the user provides a path, embed it as base64:
  `base64 -i <path>`. White/reverse logo on dark backgrounds, positive/dark logo
  on light. Omit if unavailable.
- **Save location** — default to `[topic].html` in the current directory. For
  presentation mode also offer `[topic]-slides.html`.

## Step 3 — Generate HTML

Follow the brand system from references/brand-system.md exactly:

- All CSS custom properties from the `:root` block
- Inter font via Google Fonts CDN
- Section structure and component patterns appropriate to the mode

### One-pager section order

Pick what fits the topic — not every section is required. Alternate dark/light
sections for rhythm:

```
Nav (dark, sticky) · Hero · Stats row · Problem · Solution · How It Works
· Case Studies / Proof · Capabilities · Why Switch · Built For · CTA Footer
```

### Presentation mode rules

- One main idea per slide
- Use the slide system CSS from references/brand-system.md
- Apply print/PDF requirements — every slide gets `break-after: page`,
  `height/max-height: 8in`
- Cover slide: 3–4 headline stats, full bleed dark background
- For data reports and internal decks: use the simplified slide pattern
  (table-first, minimal decoration)
- For external/executive decks: use the full component system (cover slide,
  signal grids, bar charts)

## Step 4 — Save and confirm

Write the file to the agreed location. Tell the user the path.

For presentation mode: tell the user to open in a browser and use Print → Save
as PDF.

## Red Flags — STOP

- About to use colors, fonts, or components not in references/brand-system.md →
  read the reference first
- About to use `min-height` instead of `height/max-height` on slides → causes
  PDF overflow
- Generating presentation mode without `break-after: page` on every slide → PDF
  won't paginate
