# Frontmatter schema

## Maintained docs (`explanation/`, `how-to/`, `reference/`, `conventions/`)

```yaml
---
title: {{Human title}}
type: {{explanation | how-to | reference | conventions}}   # must equal the parent folder
audience: [{{human, agent}}]                               # human | agent
status: stable                                             # draft | stable | deprecated
stale_after: {{YYYY-MM-DD}}                                # absolute expiry; WARNS, never fails
---
```

`type` matching its folder is the check that turns the routing rule into a gate. It is the
single most important field.

`stale_after` is an absolute expiry rather than a `last_reviewed` date on purpose: a review
date has to be remembered, an expiry announces itself. **Stagger the dates by folder** — all
docs sharing one date means one day where everything warns at once.

## `journal/solutions|specs|plans|ideation/`

Keep whatever schema the project's artifact writer already uses (the compound-engineering
`ce-compound` schema, if that plugin is installed). Do not impose a second one — the plugin
will keep writing its own.

A `superpowers` spec or plan carries **no** frontmatter of this schema, and needs none: the
gate asks a journal entry for no frontmatter at all. What it does ask of one is a `.md`
extension, a kebab-case filename (`NNNN-...` in `decisions/`), a resolvable link, its
language, no unreplaced `{{...}}`, and — if it declares a `category` — that the category be
its folder. The last three are the ones a pasted artifact can trip on.

## `journal/decisions/`

[MADR 4.0.0](https://adr.github.io/madr/):

```yaml
---
status: {{proposed | rejected | accepted | deprecated | superseded by ADR-NNNN}}
date: {{YYYY-MM-DD}}
decision-makers: [{{who}}]
consulted: [{{who}}]     # optional
informed: [{{who}}]      # optional
---
```
