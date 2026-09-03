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

Put the question to the owner, then check rather than trust the answer:

```bash
gh api repos/<owner>/<repo>/rulesets 2>/dev/null | \
  python3 -c "import json,sys; [print(r['name'], r.get('source_type'), r.get('source')) for r in json.load(sys.stdin)]"
gh api repos/<owner>/<repo>/rulesets/<id> 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print([r['type'] for r in d['rules']], 'bypass:', d.get('bypass_actors'))"
```

A `pull_request` rule with no bypass actors means a bot push cannot land. And
**an organization-level ruleset cannot be overridden by a repo-level bypass** — check
`source_type` before concluding the repo owner can fix it.

## Tracker only

The default under branch protection, and the simpler answer everywhere. No file, no
generator, no workflow. The agents file carries the commands instead:

```markdown
- **Never add a backlog, TODO or "future work" section under `docs/`.** Unbuilt work lives
  in the issue tracker and nowhere else — `gh issue list --label backlog` to read it,
  `gh issue create --label backlog` to add an item, and **link the issue** from the doc
  rather than describing the missing work.
```

Then, in the gate's CONFIGURATION block, turn the mirror's two rules off:

```python
ROOT_ALLOWED = {INDEX_NAME}          # no BACKLOG.md at the docs root
GENERATED_BACKLOG_HEADER = None      # no generated file to check
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
- **Escape the issue title.** A title is written by anyone who can open an issue, and can be
  edited *after* a maintainer applied the label — so the text a triager approved is not the
  text landing in a file agents read as repository truth. Collapse whitespace (a newline
  ends the table and lets the rest become markdown of its own), escape the cell separator,
  and neutralise HTML comment markers so a title cannot close the generated header.
- **Track the file.** Gitignoring it removes the only reason it exists.

### The workflow that keeps it fresh

```yaml
name: Backlog mirror

on:
  issues:
    types: [opened, closed, reopened, labeled, unlabeled, edited]
  schedule:
    - cron: "0 6 * * *"      # catches whatever the events missed
  workflow_dispatch:

permissions:
  contents: write            # the push
  issues: read

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          ref: <default-branch>
      - uses: actions/setup-python@v6
        with:
          python-version-file: .python-version
      - run: python scripts/sync_backlog.py
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit when the mirror changed
        run: |
          if git diff --quiet -- docs/BACKLOG.md; then
            echo "No change."; exit 0
          fi
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/BACKLOG.md
          git commit -m "docs: refresh the backlog mirror [skip ci]"
          git push
```

Four details in there are not guessable, and each has a reason:

| Detail | Why |
| --- | --- |
| `[skip ci]` in the message | The refresh must not spend a CI run on a generated table |
| commit **only when changed** | Otherwise an empty commit lands on every issue event |
| `GH_TOKEN` in `env`, never interpolated into the `run:` body | An issue title reaching a shell is an injection |
| pin the actions, install locked deps | The same supply-chain rule as every other workflow in the repo |

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
