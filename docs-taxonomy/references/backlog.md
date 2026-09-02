# Backlog: where unbuilt work lives

The diagnosis will have found "not yet implemented" items buried in prose. They need a
home, and the tracker is always the source of truth. The only real question is whether a
tracked mirror in `docs/` is worth its refresh mechanism.

## The rule, whichever option is chosen

State it in the instructions file and in `conventions/documentation.md`:

> **Never write a backlog, TODO or "future work" section under `docs/`.** Open an issue.

A `TODO` comment in a source file is fine, and a doc may point at one. What is banned is a
**list of unbuilt work in prose**, because nothing ever prunes it.

## Options

| Option | Gets you | Costs |
| --- | --- | --- |
| **Tracker only** | One source of truth, zero machinery | Invisible to an agent reading the repo without a tool call. Needs an instructions rule: "list the open issues before planning." |
| **Generated mirror in `docs/BACKLOG.md`** | An agent sees unbuilt work with no tool call, offline | A generator, and a refresh mechanism — see the trap below |
| **Hand-maintained file** | Nothing | Becomes the dumping ground it replaced |
| **Source `TODO` comments only** | Each item next to its code | No overview; items with no obvious code home have nowhere to go |

## The mirror, if chosen

- **Only labelled issues.** One label (`backlog`) keeps bug reports and support noise out.
  A second family (`area:*`) gives the generator a "where" — a title alone does not tell an
  agent which module to open.
- **Deterministic ordering** (by issue number). Otherwise every run diffs for nothing.
- **A generated header** naming the generator and the refresh command.
- **Track the file.** Gitignoring it removes the only reason it exists.

## The trap: how the mirror gets refreshed

The obvious design — a workflow that regenerates and commits — **fails on any protected
default branch.**

Check first, before building it:

```bash
gh api repos/<owner>/<repo>/rulesets 2>/dev/null | \
  python3 -c "import json,sys; [print(r['name'], r.get('source_type'), r.get('source')) for r in json.load(sys.stdin)]"
gh api repos/<owner>/<repo>/rulesets/<id> 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print([r['type'] for r in d['rules']], 'bypass:', d.get('bypass_actors'))"
```

If a `pull_request` rule is present with no bypass actors, a bot push cannot land. And note
**an organization-level ruleset cannot be overridden by a repo-level bypass** — check
`source_type`.

Then the options are:

| Option | Verdict |
| --- | --- |
| **Bot commits the refresh** | Only if the branch is unprotected, or a bypass actor already exists |
| **Bot opens a PR per change** | Clears the rule, but needs a human approval **every time**. More review burden than the staleness it removes. |
| **Add a bot bypass to the ruleset** | Works, but widens who may write to the default branch without review — for one generated convenience file. Disproportionate, and on an org ruleset it is not even the repo owner's call. |
| **Report, do not commit** | **Recommended under protection.** A daily job regenerates, diffs, and fails with the diff when stale. A red scheduled run means "run `make sync-backlog`". Holds `contents: read`. |

With report-only, trigger on **cron plus dispatch, not per issue event** — six event types
would each turn red for the same fact until someone synced.

**Never make it a check on pull requests.** Issues change asynchronously from commits, so
that fails unrelated PRs. What *can* be a PR gate are properties of the diff:

- the generated header is still present (a checker rule);
- the file regenerates identically (a pre-commit hook that regenerates and compares — and
  passes when the tracker is unreachable, rather than blocking a commit for being offline).

## Say what the mirror is

In `conventions/documentation.md`, plainly: the mirror is as fresh as the last refresh, the
tracker is correct either way, so a stale mirror is an out-of-date convenience and never a
wrong answer. That sentence is what stops someone treating the lag as a bug.
