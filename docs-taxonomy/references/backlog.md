# Backlog: where unbuilt work lives

The diagnosis will have found "not yet implemented" items buried in prose. They need a
home, and **the tracker is always the source of truth.** The only question is whether a
tracked mirror in `docs/` earns its keep.

## The rule, whichever option is chosen

State it in the instructions file and in `conventions/documentation.md`:

> **Never write a backlog, TODO or "future work" section under `docs/`.** Open an issue,
> and **link it** rather than describing the missing work.

A `TODO` comment in a source file is fine, and a doc may point at one. What is banned is a
**list of unbuilt work in prose**, because nothing ever prunes it.

## The decision rule: one question decides it

```
Can a workflow push to the default branch?
├── yes  →  mirror in docs/BACKLOG.md, refreshed automatically   (§ The mirror)
└── no   →  tracker only, `gh issue list` in the agents file      (§ Tracker only)
```

**A mirror is worth having only when nobody has to remember to refresh it.** That is the
whole of it. A mirror refreshed by hand — or by a job that only *reports* staleness — is a
cache of one command, and it costs a generator, a hook, a workflow, a gate rule and a
title-escaping contract to keep honest.

Put the question to the owner, then check rather than trust the answer. **Two APIs, not
one:** rulesets and classic branch protection are separate, and a repo protected the classic
way returns an empty ruleset list — indistinguishable from "nothing blocks a push" if you
only ask the first.

Do not send stderr to `/dev/null` here. A 403 from a token missing `administration:read`
reads exactly like "no protection", and that is the one mistake this check exists to
prevent.

```bash
REPO=<owner>/<repo>
BRANCH=$(gh repo view "$REPO" --json defaultBranchRef -q .defaultBranchRef.name)

# 1. Classic branch protection. 404 means none; 403 means you cannot tell.
gh api "repos/$REPO/branches/$BRANCH/protection" \
  --jq '{pr_required: (.required_pull_request_reviews != null),
         enforce_admins: .enforce_admins.enabled}'

# 2. Rulesets, and whose they are.
gh api "repos/$REPO/rulesets" --jq '.[] | {id, name, source_type, source}'

# 3. For each ruleset id from step 2:
gh api "repos/$REPO/rulesets/<id>" \
  --jq '{rules: [.rules[].type], bypass: .bypass_actors}'
```

Read it this way:

| What you see | What it means |
| --- | --- |
| step 1 returns 404, step 2 returns `[]` | Nothing blocks a push. **Ship the mirror.** |
| a `pull_request` rule, or `required_pull_request_reviews`, with no bypass actors | A bot push cannot land. **Tracker only.** |
| `source_type: Organization` | Not the repo owner's call to change — treat as final |
| a 403 on either call | You cannot answer the question. Ask someone who can, or assume protected |

`enforce_admins` matters too: without it, an admin token can push through classic
protection, but `GITHUB_TOKEN` is not an admin.

## Tracker only

The default under branch protection, and the simpler answer everywhere. No file, no
generator, no workflow. The agents file carries the commands instead:

```markdown
- **Never add a backlog, TODO or "future work" section under `docs/`.** Unbuilt work lives
  in the issue tracker and nowhere else — `gh issue list --label backlog` to read it,
  `gh issue create --label backlog` to add an item, and **link the issue** from the doc
  rather than describing the missing work.
```

Then, in the gate's CONFIGURATION block, turn the mirror off. **One setting**, because two
describing the same file could be set to disagree — and the half-configured state, where the
gate no longer checks a mirror it still tolerates, accepts a hand-written one forever:

```python
GENERATED_BACKLOG_HEADER = None      # no mirror; the root allowlist follows
```

**What this costs:** an agent that can read files but not run commands — a sandbox with no
`gh` credentials — sees the label name and the command, and stops there. If that case is
real for the project, grant the sandbox `gh` rather than reintroducing a cache.

**Do not gitignore a mirror as a middle ground.** It is the worst of the three: every ounce
of the complexity, none of the benefit. Some clones have the file and others do not, a stale
local copy is invisible to everyone but its owner, the gate still special-cases it, and an
agent that refreshes it produces a file absent from the diff — so no reviewer can see what
it claimed.

## The mirror

Only when the workflow below can actually push. Then:

- **Only labelled issues.** One label (`backlog`) keeps bug reports and support noise out.
  A second family (`area:*`) gives the generator a "where" — a title alone does not tell an
  agent which module to open.
- **Deterministic ordering** (by issue number). Otherwise every run diffs for nothing.
- **A generated header** naming the generator and the refresh command, plus a gate rule that
  fails when the header is gone.
- **Escape the issue title, and the area labels with it.** Both are written by anyone who
  can open an issue, and a title can be edited *after* a maintainer applied the label — so
  the text a triager approved is not the text landing in a file agents read as repository
  truth. Neutralise everything that changes the rendered **structure**: a newline (it ends
  the table, and the rest becomes markdown of its own — a heading, a list, an instruction
  addressed to an agent), `|`, `<` and `>` (no HTML tag renders, which also disarms `<!--`
  and `-->`), and `[` `]` (no title becomes a link pointing elsewhere). The trade-off,
  stated: intentional formatting in a title shows literally. That is the right way round —
  a tracker's titles are text, not markup.
- **Track the file.** Gitignoring it removes the only reason it exists.

### The workflow that keeps it fresh

Copy the SHAs from a workflow already in the repo rather than trusting the ones below —
a pinned digest here is a snapshot, and pinning is the point.

```yaml
name: Backlog mirror

on:
  issues:
    types: [opened, closed, reopened, labeled, unlabeled, edited]
  schedule:
    - cron: "0 6 * * *"      # catches whatever the events missed
  workflow_dispatch:

# Read-only by default; the one job that writes asks for it.
permissions:
  contents: read

# An issue rename during a labelling spree fires two runs that would push onto
# each other. Serialise, and do not cancel: the last run must be the last state.
concurrency:
  group: backlog-mirror
  cancel-in-progress: false

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # the push
      issues: read
    steps:
      - uses: actions/checkout@<sha>          # actions/checkout, pinned
        with:
          ref: <default-branch>
          # The push below uses GITHUB_TOKEN explicitly, so no credential needs
          # to stay behind in .git/config.
          persist-credentials: false
      - uses: actions/setup-python@<sha>      # actions/setup-python, pinned
        with:
          python-version-file: .python-version
      - run: python scripts/sync_backlog.py
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit when the mirror changed
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if git diff --quiet -- docs/BACKLOG.md; then
            echo "No change."; exit 0
          fi
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/BACKLOG.md
          git commit -m "docs: refresh the backlog mirror [skip ci]"
          git push "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}" \
            "HEAD:<default-branch>"
```

Seven details in there are not guessable, and each has a reason:

| Detail | Why |
| --- | --- |
| `[skip ci]` in the message | The refresh must not spend a CI run on a generated table |
| commit **only when changed** | Otherwise an empty commit lands on every issue event |
| `concurrency` without `cancel-in-progress` | Two issue events would otherwise push onto each other; cancelling would drop the newest state |
| `permissions` per **job**, `contents: read` at the top | The generator step has no reason to hold a write token |
| `persist-credentials: false` | Otherwise the token stays in `.git/config` for every later step |
| `GH_TOKEN` in `env`, never interpolated into a `run:` body | An issue title reaching a shell is an injection |
| actions pinned to a **SHA**, deps installed from the lockfile | The same supply-chain rule as every other workflow in the repo |

**Never make the mirror a check on pull requests.** Issues change asynchronously from
commits, so that fails unrelated PRs. What *can* gate a PR are properties of the diff: the
generated header is still present, and the file regenerates identically — a pre-commit hook
that regenerates and compares, and passes when the tracker is unreachable rather than
blocking a commit for being offline.

### If the push cannot land, do not fall back to report-only

The tempting fallback is a daily job that regenerates, diffs, and fails when stale — a red
scheduled run meaning "run `make sync-backlog`". It holds `contents: read` and clears the
protection rule.

It is not worth it. That design keeps the full apparatus — generator, tests, hook, workflow,
gate rule, escaping contract — and still needs a human to remember the refresh, which is the
thing the mirror existed to avoid. **Choose tracker-only instead.**

The other two fallbacks are worse. A bot PR per change needs a human approval every time,
which is more review burden than the staleness it removes. Adding a bot bypass to the
ruleset widens who may write to the default branch without review, for one generated
convenience file — and on an org-level ruleset it is not even the repo owner's call.

## Say what the mirror is

If a mirror ships, say plainly in `conventions/documentation.md`: the mirror is as fresh as
the last refresh, the tracker is correct either way, so a stale mirror is an out-of-date
convenience and never a wrong answer. That sentence is what stops someone treating the lag
as a bug.
