# Issues: where unbuilt work lives

The diagnosis will have found "not yet implemented" items buried in prose. They need a
home, and **the issue tracker is the only one.**

## The rule

State it in the instructions file and in `conventions/documentation.md`:

> **Never write a backlog, TODO or "future work" section under `docs/`.** Open an issue,
> and **link it** rather than describing the missing work.

A `TODO` comment in a source file is fine, and a doc may point at one. What is banned is a
**list of unbuilt work in prose**, because nothing ever prunes it.

## No copy of the tracker under `docs/`

Not a `BACKLOG.md`, not a generated table, not a gitignored local copy. `gh issue list`
reads the tracker directly, so a copy answers the same question with a delay — and every
way of keeping it fresh (a generator, a hook, a workflow that pushes to the default branch)
is machinery that exists only to shrink that delay. With no copy there is nothing to sync,
and nothing to be stale. The gate enforces it: a `BACKLOG.md` at the root of `docs/` fails
as a loose file.

**What this costs:** an agent that can read files but not run commands — a sandbox with no
`gh` credentials — cannot read the backlog. If that case is real for the project, grant the
sandbox `gh` rather than reintroducing a copy.

## The default: one `backlog` label

No convention beyond one label. The agents file carries the commands:

```markdown
- **Never add a backlog, TODO or "future work" section under `docs/`.** Unbuilt work lives
  in the issue tracker and nowhere else — `gh issue list --label backlog --limit 200` to read it,
  `gh issue create --label backlog` to add an item, and **link the issue** from the doc
  rather than describing the missing work.
```

Pass `--limit` to every `gh issue list` an agent is told to run: `gh` stops at 30 results
without it, silently, and an agent reads the truncated list as the whole backlog.

## The option: type, area and priority

Offer it when the backlog has outgrown one label — a few dozen open issues, or an agent that
must answer "what next?" and "where in the code?" from the tracker alone. The rulebook ships
as `templates/conventions-issues.md`, landing in `docs/conventions/issues.md`.

Every issue carries three things, **each axis on exactly one mechanism** so two can never
disagree:

| Axis | With the organisation's mechanisms | Fallback, labels only |
| --- | --- | --- |
| What kind of work — Bug, Feature, Task | issue type | `type:*` label |
| Where in the code | `area:*` label, one or two | same |
| How much it hurts — Urgent, High, Medium, Low | `Priority` issue field | `priority:*` label |

The `backlog` label goes: every open issue is unbuilt work, so `gh issue list --limit 200`
is the backlog. Two rules carry most of the value, and the template states both:

- **The type comes from whether the behaviour exists today**, not from the size of the fix.
  Something shipped and wrong is a Bug even when the fix is a redesign.
- **The priority comes from the impact** on the user or the team, not from the effort, so a
  cheap fix for a data leak and an expensive one rank the same.

### 1. Detect what the organisation provides

Issue types and issue fields exist only at organisation level. One read-only call answers
both, and returns the IDs the template needs. Every `gh` command here runs from a clone with
a GitHub remote; without one, set `OWNER` by hand and pass `-R <owner>/<repo>` to the others.

```bash
OWNER=$(gh repo view --json owner --jq .owner.login)
gh api graphql -f org="$OWNER" -f query='query($org: String!) {
  organization(login: $org) {
    issueTypes(first: 20) { nodes { name isEnabled } }
    issueFields(first: 20) {
      nodes { ... on IssueFieldSingleSelect { id name options { id name } } }
    }
  }
}'
```

Fields of another kind come back as `{}`, and other single-select fields (`Effort`) are
listed too: only the one named `Priority` matters.

| What you see | Variant |
| --- | --- |
| enabled issue types **and** a single-select field named `Priority` | The organisation's mechanisms. Copy the field `id` and the four option `id`s into the template |
| exit 1 with `NOT_FOUND` on `organization` — the owner is a user, not an organisation | Labels only |
| no enabled issue type, or no `Priority` field | Labels only |
| any other error, a 403 among them | You cannot tell. Fix the token or ask someone who can — never read an error as "absent" |

Both variants or neither: never mix the organisation's types with `priority:*` labels. One
rule per repo is what lets the audit be one command. If the organisation's type or priority
names differ from Bug, Feature, Task and Urgent to Low, use its names in the template's
tables.

### 2. Choose the areas

Derive them from the code layout and from the labels already in use
(`gh label list --limit 200`, `gh issue list --state all --limit 200 --json labels`), not
from a generic list. Each area names the paths or subsystems it covers.

- **Cover the work that touches no product code** — docs, CI, tooling — with an area of its
  own, such as `area:ci-cd`: every issue needs one, a Task included. Create only the areas
  the backlog needs; a new one is a label and a row, added when its first issue is.
- **`area:security` is the one area that is not a place.** It is added on top of the area
  where the fix lands, whenever the issue is a security gap, and does not count toward the
  limit of two. A login bug with no security impact is `area:auth` alone.

### 3. Write it down and wire it

In one PR:

1. `docs/conventions/issues.md` from the template, and its entry in `docs/README.md`.
2. An ADR in `journal/decisions/`, stating the three axes and the options set aside: with
   the organisation's mechanisms, everything as labels and a GitHub Project (its fields
   live outside the issue); with labels only, a GitHub Project, and the organisation's
   mechanisms as the move to make if the repo joins an organisation.
3. Every mention of the `backlog` label replaced — `grep -rni "backlog" AGENTS.md CLAUDE.md
   docs .claude .github`, then read each hit: a command wraps across lines, the compass row
   says "an issue labelled `backlog`", and an issue form or a workflow under `.github/` may
   apply the label. An issue form applies the new labels instead, or none. A command becomes a link to
   `docs/conventions/issues.md#commands`, where the commands are written once; the compass
   row becomes "an issue, classified per `docs/conventions/issues.md`".
4. The agents file gets the rule below, in the list of repo-wide conventions — not in the
   `## Documentation` section, since it governs the tracker, not `docs/`.

```markdown
- **Every issue you open or triage carries a type, one or two `area:*` labels, and a
  priority** — definitions and commands in
  [`docs/conventions/issues.md`](docs/conventions/issues.md). There is no `backlog` label:
  every open issue is unbuilt work.
```

### 4. Apply it to the existing issues

A convention the tracker does not follow on day one is not followed afterwards.

1. Create the labels: `gh label create <name> --description "<what it covers>"` for every
   area — and, with labels only, for the three `type:*` and four `priority:*` labels too.
2. Classify every **open** issue: one type, one or two areas, one priority. Convert the old
   labels before step 4 deletes them: `bug` becomes the Bug type (with labels only,
   `type:bug`), `enhancement` the Feature type (`type:feature`). Closed issues are left as
   they are — the audit reads open issues only.
3. Run the template's audit commands. Empty output means done.
4. Delete every label that is not one of the convention's kinds — `backlog`, the GitHub
   defaults (`bug`, `enhancement`, `question`, `good first issue`, …) — except the ones a bot
   applies (Dependabot's `dependencies`), which the convention then names. **Ask the owner
   first**: deleting a label strips it from every issue, and nothing brings it back.

Report what was applied in the PR description — counts per priority, labels created and
deleted — since none of it shows in the diff.

### What goes wrong

| Mistake | Consequence |
| --- | --- |
| `gh issue list` without `--limit` | Stops at 30, silently; the audit reports a clean tracker that is not |
| Running the audit in CI | An issue opened by a teammate fails an unrelated PR — see `pitfalls.md` |
| Expecting `gh` to set the priority | It has no flag for issue fields; the GraphQL mutation is in the template |
| Reading the priority in `gh issue list`'s default output | A field value does not show there; search with `field.priority:High` |
| The type from the size of the fix | A redesign of shipped behaviour filed as a Feature, and the Bug count lies |
