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
