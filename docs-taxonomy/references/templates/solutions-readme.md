# `journal/solutions/` — what broke, and what the measurement said

One entry per problem solved. **Append-only**: an entry is dated and never rewritten. If a
later change supersedes it, write a new entry and link back.

Path: `journal/solutions/<category>/<kebab-case-slug>.md`

Categories in use: {{`logic-errors`, `deployment`}}. Add a category only when an entry does
not fit an existing one.

**Read this store before implementing a fix** in a documented area. It exists so the same
wall is not hit twice.

**Never** narrate an incident in `explanation/`, `how-to/`, `reference/` or
`conventions/`. Write it here and leave the distilled rule plus a link — see
[`../../conventions/documentation.md`](../../conventions/documentation.md).

## Frontmatter

{{Keep whatever schema the project's artifact writer already uses. The two-track schema
below is the compound-engineering `ce-compound` one - if that plugin is installed, do not
invent a second schema, it will keep writing its own.}}

Two tracks, keyed on `problem_type`. Both require `title`, `date`, `category`, `module`,
`problem_type`, `component`, `severity`, `tags`.

**Bug track** — `build_error`, `test_failure`, `runtime_error`, `performance_issue`,
`database_issue`, `security_issue`, `ui_bug`, `integration_issue`, `logic_error`.
Also requires `symptoms`, `root_cause`, `resolution_type`.

**Knowledge track** — `best_practice`, `documentation_gap`, `workflow_issue`,
`developer_experience`, `architecture_pattern`, `design_pattern`, `tooling_decision`,
`convention`. Also requires `applies_when`.

`component` and `root_cause` are open vocabularies with a **corpus-first** rule: reuse the
spelling an existing entry in that area already uses rather than inventing a new one. That
is what stops tag sprawl.

Add `last_updated: YYYY-MM-DD` whenever you touch an existing entry.

## Body

```markdown
## Problem
## Symptoms
## What Didn't Work
## Solution
## Why This Works
## Prevention
## Related Issues        (optional)
```

`What Didn't Work` and `Prevention` are the two sections that pay for the entry. A write-up
with only `Problem` and `Solution` is a commit message.

Write `Prevention` as durable rules aimed at a future reader, not as a summary of this fix.

## Example

{{Name the best existing entry here once one exists - a bug-track write-up with a measured
root cause and prevention rules written as durable rules, not as a summary of the fix. A
template with no worked example gets filled in badly.}}
