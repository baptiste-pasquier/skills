---
title: Issue conventions
type: conventions
audience: [agent, human]
status: stable
stale_after: {{YYYY-MM-DD}}
---

# Issue conventions

**Scope: the GitHub issues of `{{owner/repo}}`.**

Every issue carries three things: a **type**, one or two **area** labels, and a
**priority**. {{The rationale is in [ADR NNNN](../journal/decisions/NNNN-classify-issues-by-type-area-and-priority.md).}}

{{PICK ONE of the two tables below, and delete the other with this line — see the skill's
references/issues.md. The first needs the organisation's issue types and `Priority` issue
field; the second is the fallback when either is missing.}}

| Axis | Mechanism | Cardinality |
| --- | --- | --- |
| What kind of work | Issue type (organisation-level) | exactly one |
| Where in the code | `area:*` label | one or two |
| How much it hurts | `Priority` issue field (organisation-level) | exactly one while open |

| Axis | Mechanism | Cardinality |
| --- | --- | --- |
| What kind of work | `type:bug`, `type:feature` or `type:task` label | exactly one |
| Where in the code | `area:*` label | one or two |
| How much it hurts | `priority:urgent`, `priority:high`, `priority:medium` or `priority:low` label | exactly one while open |

Every open issue is unbuilt work: there is no `backlog` label. {{Every label is an `area:*`
label / Every label is a `type:*`, `area:*` or `priority:*` label}}{{, apart from the ones a
bot applies: Dependabot's `dependencies`}} — do not create another kind.

## Type

Pick the type from what {{the product}} does **today**, not from the size of the fix.

| Type | When |
| --- | --- |
| Bug | Something {{the product}} already does, it does wrong — even when the fix is a redesign |
| Feature | Something {{the product}} does not do yet: a spec line never built, or a change of behaviour someone asked for |
| Task | No user-visible change: tech debt, tests, tooling, docs, an investigation |

The test is whether the behaviour exists. {{One example of each side, from this repo's
issues — or delete this sentence.}} A security gap is a Bug.

## Area

One label is required; add a second only when the fix must touch both. `area:security` does
not count toward that limit.

| Label | Covers |
| --- | --- |
| {{`area:<name>`}} | {{the modules, paths or subsystems it covers}} |
| {{`area:ci-cd`, for example}} | {{the work that touches no product code: workflows, tooling, docs}} |
| `area:security` | Secrets, exposure, personal data — added on top of the area where the fix lands, whenever the issue is a security gap |

A new area is a new label and a new row here, in the same PR.

## Priority

Set it from the impact on the end user or on the team, not from the effort.

| Priority | When |
| --- | --- |
| Urgent | Harm in production **now**: personal data or a secret leaking, the service down. Drop current work |
| High | On a nominal path, the user gets a wrong result or is stuck. Or a security gap reachable today, or a team workflow blocked |
| Medium | Wrong or degraded on a secondary path, or a missing capability with a workaround |
| Low | A latent risk never observed, tech debt, polish |

A closed issue keeps no priority requirement.

## Body

Write the issue in {{language}}. State the observed problem or the missing capability, its
impact, and what "done" means. Cite files as backticked paths, and link the
`docs/journal/solutions/` entry or the pull request that surfaced it.

## Commands

`gh issue list` stops at 30 results unless given `--limit`.

{{PICK ONE of the two subsections below, the one matching the table above. Delete the other,
heading included, and this line.}}

### With the organisation's issue types and `Priority` field

Create — `gh` sets the type and labels, but not the priority:

```bash
gh issue create --type Bug --label area:{{name}} --title "…" --body-file body.md
```

Set the priority. `gh` has no flag for issue fields, so the call goes through GraphQL:

```bash
gh api graphql \
  -f query='mutation($issue: ID!, $option: ID!) {
    setIssueFieldValue(input: {issueId: $issue, issueFields: [
      {fieldId: "{{PRIORITY_FIELD_ID}}", singleSelectOptionId: $option}]}) { issue { number } }
  }' \
  -f issue="$(gh issue view 123 --json id --jq .id)" \
  -f option={{HIGH_OPTION_ID}}
```

| Priority | Option ID |
| --- | --- |
| Urgent | `{{URGENT_OPTION_ID}}` |
| High | `{{HIGH_OPTION_ID}}` |
| Medium | `{{MEDIUM_OPTION_ID}}` |
| Low | `{{LOW_OPTION_ID}}` |

Read and filter:

```bash
gh issue list --limit 200                       # all unbuilt work
gh issue list --limit 200 --search "type:Bug field.priority:High"
gh issue list --limit 200 --label area:{{name}}
gh issue edit 123 --type Task                   # change the type
```

Audit — each command prints the open issues the convention was not applied to, and prints
nothing when it holds:

```bash
gh issue list --limit 200 --search "no:field.priority" --json number --jq '.[].number'
gh issue list --limit 200 --json number,issueType,labels --jq '.[]
  | [.labels[].name | select(startswith("area:") and . != "area:security")] as $areas
  | select(.issueType == null or ($areas | length) < 1 or ($areas | length) > 2)
  | .number'
```

### With labels only

Create — every axis is a label:

```bash
gh issue create --label type:bug --label area:{{name}} --label priority:high \
  --title "…" --body-file body.md
```

Read and filter:

```bash
gh issue list --limit 200                       # all unbuilt work
gh issue list --limit 200 --label type:bug --label priority:high
gh issue list --limit 200 --label area:{{name}}
gh issue edit 123 --remove-label type:bug --add-label type:task   # change the type
```

Audit — prints the open issues without exactly one type, exactly one priority, and one or
two areas besides `area:security`; prints nothing when the convention holds:

```bash
gh issue list --limit 200 --json number,labels --jq '.[]
  | [.labels[].name] as $names
  | select(
      ([$names[] | select(startswith("type:"))] | length) != 1
      or ([$names[] | select(startswith("priority:"))] | length) != 1
      or ([$names[] | select(startswith("area:") and . != "area:security")] | length
          | . < 1 or . > 2))
  | .number'
```
