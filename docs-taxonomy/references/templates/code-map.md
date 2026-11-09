---
title: Code map
type: reference
audience: [human, agent]
status: stable
stale_after: {{YYYY-MM-DD}}
---

# Code map

> Where each part of {{Project}} lives in the repository, and which file to open to change it.

Files and symbols are cited in backticks with the symbol named. {{With a site: never as a
link, which breaks on the site.}}

## Packages

One row per package, in the order a {{request}} crosses them. The rule column carries the
layer invariant that applies, where one does.

| Package | What it holds | Rule |
| --- | --- | --- |
| `{{src/package/}}` | {{One to three sentences naming the main files and their key symbols: `router.py` `route_request` dispatches each request.}} | {{Never imports `src/other/`. / No I/O. / —}} |

## I want to change…

Each row gives the file to open, the symbol or key to edit, the page to read first, and what
guards the change. Rows come from questions people asked; a row nobody needs is noise to
keep true.

### {{Fixed texts}}

| I want to change… | File | Symbol or key | Read | Guarded by |
| --- | --- | --- | --- | --- |
| {{the welcome message}} | `{{src/path/file.py}}` | `{{WELCOME}}` | {{[the deep dive](../explanation/feature.md)}} | `{{tests/path/test_file.py}}` |

### {{Rules and thresholds}}

| I want to change… | File | Symbol or key | Read | Guarded by |
| --- | --- | --- | --- | --- |
| {{when X triggers}} | `{{src/path/file.py}}` | `{{THRESHOLD}}` | {{[the deep dive](../explanation/feature.md)}} | `{{tests/path/test_file.py}}` |
