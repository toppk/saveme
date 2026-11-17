# Horizon

A documentation theme: the future as the 1990s pictured it, taken at its
word. Clear skies, engineered surfaces, a sunrise on the horizon. Matte
colour, plain geometry, nothing glowing.

Horizon is three files and pandoc. There is no Node, no bundler and no site
generator.

| file | what it is |
|---|---|
| `horizon.css` | the whole look, driven by custom properties; light and dark ("night shift") |
| `template.html` | a pandoc HTML5 template: masthead, optional hero, sidebar, page, "on this page", pager |
| `horizon.js` | optional niceties: light/dark toggle, code language labels and copy buttons, heading anchors, contents highlighting |
| `horizon.lua` | a pandoc filter: scrolling tables, and boxes in `::: tier` rows |

## Using it in a project

1. Copy `site/theme/` into the project, and `site/build.sh` beside it.
2. Write `site/site.yaml`:

   ```yaml
   site-title: myproject
   site-tagline: one line about it
   site-logo: assets/logo.svg       # optional; also the favicon
   site-footer: 'MIT licensed · <a href="https://github.com/me/myproject">source</a>'
   llms: llms.txt                   # optional link in each page footer
   top-links:
     - label: Docs
       href: getting-started.html
     - label: GitHub
       href: https://github.com/me/myproject
   ```

3. List the pages in `build.sh`'s `pages=(…)` array as
   `name|Title|Group[|source path]`, in reading order. Groups become the
   sidebar's sections.
4. Write the pages in `site/pages/*.md`, then `site/build.sh _site`.
5. Publish with `.github/workflows/pages.yml` (pandoc in, `_site` out).

`build.sh` also copies each page's Markdown beside its HTML, adds
`llms-full.txt` (every page in one file) and copies `site/llms.txt`, so
agents can read the documentation as text.

## Page front matter

```yaml
---
title: Configuration              # the page's heading and <title>
eyebrow: Use                      # small label above the title
lede: One sentence under the title, larger.
description: For search engines and link previews.
---
```

The front page can have a hero instead of a title:

```yaml
---
title: Overview
hero: true
hero-eyebrow: What it is · where it runs
hero-title: The big promise.
hero-lede: Two or three sentences.
hero-links:
  - { label: Get started, href: getting-started.html, kind: primary }
  - { label: Read the API, href: api.html, kind: secondary }
---
```

## Components

Callouts are pandoc fenced divs:

```markdown
::: note
Plain information.
:::

::: tip
A better way.
:::

::: safety
A promise the software keeps (labelled "Promise").
:::

::: warning
Something that can go wrong.
:::

::: agent
Guidance for AI agents.
:::
```

Cards, in an auto-fitting grid:

```markdown
::: cards
::: card
[Label]{.label}

### Title

Text.
:::
:::
```

A stack diagram, as rows of boxes:

```markdown
::: stack
::: tier
[Client A]{.box}
[Client B]{.box}
:::

[protocol]{.wire}

::: tier
[server [what it does]{.small}]{.box .daemon}
:::
:::
```

Box variants: `.socket` (teal), `.daemon` (night sky), `.store` (sunrise).
Keys: `<kbd>Ctrl</kbd>`. Definition lists, tables and fenced code with a
language (`` ```python ``) are all styled.

## Making it yours

Every colour and font is a custom property at the top of `horizon.css`.
Override them in a small stylesheet loaded after it, or edit them in place:

```css
:root {
  --accent: #6b4fbb;           /* links in the sidebar, labels */
  --mark: #e2574c;             /* the current page, focus rings */
  --font-head: "Futura", sans-serif;
}
```

Michroma for labels, Jost for headings, IBM Plex Sans and Mono for text
and code. saveme serves them from `fonts/` (latin subsets, OFL) rather than
Google Fonts, so pages make no third-party requests. Each has a system
fallback.

## Design notes

- **Palette.** Sky (deep blues), orbit teal, sunrise orange and gold, on
  warm paper. No neon, no glow, no gradients on text.
- **The horizon.** Three stripes under the masthead (orange, gold, teal),
  repeated as the short rule above each section heading, the way an
  airliner's livery repeats.
- **Engineering paper.** A faint 28 px grid behind white panels: the page
  is a drawing on a drafting table.
- **Control-panel labels.** Wide capitals (Michroma) only for small labels:
  eyebrows, table headings, sidebar sections, code languages. Never for
  reading text.
- **Night shift.** Dark mode is the same sky after sunset, not an
  inversion. It follows the system setting until the reader picks one.
