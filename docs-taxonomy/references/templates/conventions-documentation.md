---
title: Documentation conventions
type: conventions
audience: [agent, human]
status: stable
stale_after: {{YYYY-MM-DD}}
---

# Documentation conventions

**Scope: the prose in `docs/`. {{For MAX's prompt text, see [`prompting.md`](prompting.md).}}**

{{Those rule sets rhyme in places — both say to cut the filler — and they stay apart because
the reasons differ. A prompt is priced per token and subject to attention effects; a doc is
scanned by a person, so this file argues from what survives a reader who stops after one
sentence.}}

## Placement

The routing table lives in [`../README.md`](../README.md) and is not repeated here. Run the
compass on **the paragraph**, not on the file you happen to have open. That is what stops a
paragraph landing in a doc merely because that doc was already open.

### Never narrate an incident in a maintained doc

A passage that recounts a past attempt, a failure, or a measured symptom does not belong in
`how-to/`, `reference/` or `conventions/`. CI fails on one there.

`explanation/` is the exception, and CI only warns: explaining why the code is shaped this
way sometimes needs the attempt that failed. What still does not belong there is the **full
write-up** — symptoms, measurements, a traceback. That is a journal entry, and the
explanation links it.

`journal/` is exempt outright. Recording what failed is what it is for.

Markers: `used to`, `we tried`, `before this fix`, `an earlier version did X`,
`3 attempts out of 4`.

Write it as a [`journal/solutions/`](../journal/solutions/README.md) entry. Leave behind
**the distilled rule, one or two sentences, plus a link**.

This applies in every session, whether or not an artifact-writing plugin is running.

The reason is not tidiness. {{One lesson — {{the claim}} — reached three separate files,
each cross-linking the other two. Three copies drift, and a reader cannot tell which is
current. One entry, linked three times, cannot.}}

### What stays inline

A hard-won **invariant** is explanation, not an incident. It stays.

{{The counter-example to keep in mind: {{the invariant}} in
[`../explanation/{{doc}}.md`](../explanation/{{doc}}.md) reads like a bug story, because a
bug is how anyone finds it. It is not one. It is a standing property of the code that a
reader needs in order to work on it, so it stays inline.}}

The test: **would a reader who never saw the bug still need this to work on the code?** Yes
means it is explanation. No means it is a journal entry.

### A plugin's artifacts land in the journal

{{Delete this section if no artifact-writing plugin is installed.}}

A spec, a plan or a retrospective written by a plugin is a dated record, so it goes under
[`../journal/`](../journal/) and nowhere else — `journal/specs/` for an approved design,
`journal/plans/` for an implementation plan. The redirect is written in the agent
instructions file, which outranks a plugin skill's own hardcoded path.

Only the directory is ours. The artifact keeps the plugin's filename and frontmatter, and
nobody edits it afterwards: it is a record.

One rule the artifact must follow, because CI fails on it: **a path to a repo file is a
backticked path, not a markdown link**, unless it resolves from the artifact's own folder. A
plugin writes those links relative to the directory being worked on, and the link check
reads journal entries too. A plan names its spec as `../specs/<file>.md`.

### Never write a backlog

No TODO section, no "future work", no "not yet implemented" list anywhere in `docs/`, and
**link the issue** rather than describing the missing work.

{{PICK ONE — see the skill's references/issues.md. With the `backlog` label:

Unbuilt work lives in the issue tracker and nowhere else:

```bash
gh issue list --label backlog --limit 200    # what is known, wanted, and not built
gh issue create --label backlog              # add an item
```

With the issue convention:

Unbuilt work lives in the issue tracker and nowhere else — every open issue is unbuilt
work. How to open, classify and read one is in [`issues.md`](issues.md#commands).}}

There is deliberately no copy of the tracker under `docs/`: `gh` reads it directly, so a
copy only adds something to keep in sync.

A `TODO` comment in a source file is fine, and a doc may point at one. What is banned is a
**list of unbuilt work** inside prose, because nothing ever prunes it.

### Record a lasting choice as a decision

A library choice, a pattern, a schema shape with cross-cutting consequences: write an entry
in [`journal/decisions/`](../journal/decisions/README.md). An accepted decision is never
edited — a change adds a new entry marking the old one superseded.

### Read before you fix

Before implementing a fix or a non-obvious behaviour change, check
[`journal/solutions/`](../journal/solutions/) for an entry in the relevant category. That
store exists so the same wall is not hit twice.

## Prose

These rules govern documentation prose. They are what keeps a doc legible once the incident
narratives are gone.

### Lead with the conclusion

The rule or the fact leads the paragraph. Justification and mechanism follow. A reader who
stops after the first sentence still has the point.

### One claim per paragraph

A paragraph that argues two things splits into two.

This is the anti-accretion mechanism, and it is why the rule exists rather than a line
limit. A single-claim paragraph is individually replaceable: the next writer edits it or
deletes it. A multi-claim paragraph resists that, so the next writer appends a third claim,
and the paragraph grows instead of changing.

### No filler, no hedging

Every sentence carries a fact, a rule, or a pointer.

Banned openers, checked by CI: {{`it is worth mentioning that`, `it should be noted that`,
`it is important to note that`, `as mentioned previously`}}.

Delete a hedging adverb — `arguably`, `somewhat`, `possibly`. Uncertainty is different from
hedging: state it as a fact about what is known.

### Prefer a table to enumerative prose

Three or more cases in one sentence become a table. {{`reference/{{doc}}.md`'s parameter
tables are the pattern to copy.}}

## Language

**{{English}}.** All of `docs/`, the journal included, checked by CI. A generated file
under a maintained folder — an API spec, a fixture — is checked for its name and its links
only.

{{The exception: quoted prompt text and quoted user-facing labels, both inside code fences
or backticks. Business vocabulary keeps its name in running text — {{terms}} — because
renaming it would make the docs disagree with the code.}}

## Frontmatter

Every maintained doc:

```yaml
---
title: {{Title}}
type: {{folder name}}
audience: [{{agent}}]
status: stable
stale_after: {{YYYY-MM-DD}}
---
```

`stale_after` is an absolute date rather than a `last_reviewed` one on purpose: a review
date has to be remembered, and an expiry announces itself. When one fires, re-date the doc
or fix what drifted. It warns and never fails, because a shared expiry date would otherwise
redden every unrelated PR on one day.

`journal/` keeps {{its own schema}} instead.

## Every `conventions/` file states its scope

Line one of the body, before anything else: what artifact this file governs, and where the
neighbouring rules live. CI fails without it.

`conventions/` holds rules for unrelated artifacts — documentation prose, {{prompt text}},
and whatever comes next. A reader must never have to infer which.

## Review

**A pull request that adds prose to a maintained doc says what it removed, or why nothing
needed removing.** There is a checkbox in the PR template.

This is the compensation for the size check being a warning rather than a failure. Growth is
not the defect on its own; growth that nobody looked at is.
