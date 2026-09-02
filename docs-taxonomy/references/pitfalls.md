# Pitfalls

Every entry here cost real time on a real repo. Read before building the gate.

## Gating

### A gate must depend on the change under review

This is the rule the others follow from. If a check can fail on a commit that did not touch
the thing being checked, it is not a gate — it is a random CI outage.

**Two ways this gets violated, both tempting:**

**A shared staleness date.** Frontmatter with `stale_after`, all docs given the same date
because they were written the same day. On that date every unrelated PR goes red with no
code change. Fix: make expiry a **warning**, and stagger the dates by folder so reviews
spread over months.

**A check against external state.** "The committed `BACKLOG.md` must match the issue
tracker." Issues change asynchronously from commits, so a teammate opening an issue fails
the next unrelated PR. Fix: gate on a property of the **diff** instead — the generated
header is present, or the file regenerates identically.

### A hard size cap is the wrong unit

Tempting, because the drift *is* growth. But a cap blocks a legitimate addition to a
reference table, and a doc is illegible because of how its paragraphs are built, not how
many there are.

Warn on size, and gate on shape instead:

- **one claim per paragraph** — the mechanism, not a proxy for it. A single-claim paragraph
  is individually replaceable, so the next writer edits it; a multi-claim paragraph resists
  that, so the next writer appends a third claim.
- **banned incident narration** in `reference/` and `conventions/` — this fails, and it
  targets the observed failure mode.
- a **PR-template checkbox** for what was removed.

### A rulebook trips its own rules

`conventions/documentation.md` documents the banned filler phrases and the incident-narration
markers — so a naive checker flags the file that defines them.

Fix: write every rule term in **backticks**, and have the checker strip inline code before
matching. Better markdown anyway. Watch out: a backtick span **cannot break across lines**,
so reflow before wrapping.

### Heuristic markers need anchoring, and some need dropping

Two that bite:

| Marker | Problem | Fix |
| --- | --- | --- |
| `used to` | Also means "used for": *"field names used to build citations"* | Anchor to a state verb: `used to (be\|have\|fire\|return\|...)` |
| `no longer` | Reads equally as incident narration and as current behaviour: *"the value is no longer valid"* | **Drop it.** Too ambiguous to gate on. |

Same for language detection. Do **not** flag single function words — `plus`, `la`, `des`
occur in English. **Score per line** and require ~4 distinct markers. One hit proves nothing;
four are conclusive.

### Compute line numbers on the file, not the stripped body

If you strip fenced blocks before scanning, your line numbers point at the wrong lines and
every report is a wild goose chase. Iterate the real lines, track fence state, strip inline
code **per line**. Add the frontmatter offset so numbers match the file.

### An indented code fence is still a fence

`^```` misses a fence nested in a list item — the natural shape in a how-to. Its contents
then get scanned as prose, and there is **no way to comply**. Match `raw.lstrip()`, in both
the fence tracker and the code-stripper.

### `datetime` subclasses `date`

`isinstance(x, date)` is true for a `datetime`. YAML parses `2027-03-02 00:00` as a
`datetime`, so the isinstance guard passes it and the comparison then raises `TypeError`.
Normalise with `.date()` first.

### Check position when the rule says "opens with"

`"**Scope:" in body` is satisfied by a line on page two. If the stated rule is *opens with*,
check the first paragraph or two.

## Instructions

### The agent instructions file is usually a cause

Bullets shaped "use and update `docs/<file>` whenever X changes" are instructions to
**append to a named file**. Point at directories, and add "if the change taught you
something, add a journal entry — do not narrate it in the reference".

### An overstated rule is worse than no rule

If the instructions say narration is banned in four folders and the checker bans it in two,
an agent will move prose **out of `explanation/`, where it belonged**. State exactly what
fails, and keep the two in sync. Prefer generating the list from the code, or at least
diffing them when either changes.

### Malformed tables mislead silently

A three-column header with rows that fill only two columns renders with the content under
the wrong heading. Nobody notices in a diff. Render or eyeball every table in an
always-loaded instructions file.

## Moving

### Install the gate before moving content

With an allowlist so it passes on the old tree, then drop the allowlist at the end. A gate
added after the restructure never gets added — the energy is spent by then.

### Use `git mv`

Renames stay renames in the diff, history is preserved, and review is possible. A
delete-plus-add of a 300-line file is unreviewable.

### The references that break are not in `docs/`

A rename breaks, silently: generator **output paths** and their docstrings, test docstrings
and assertions, CI steps, the root `README.md`, source-file comments, and every relative
link whose **depth changed**. Grep the whole repo for the old paths and re-grep at the end.

A link checker validates **targets, not labels**: a link whose visible text still says
`old-name.md` while pointing at `new-name.md` passes, and lies to the reader. Grep for stale label text separately.

### A frozen record's metadata is not frozen

Journal entries keep their prose as written, including now-wrong claims — they are records.
But a dead `origin:` pointer or a broken link is not a record of anything. Repoint the
metadata, leave the prose.

### Verify each gate actually fails

Seed one violation per rule, confirm it fails with an accurate line number, remove it. Then
write those as tests **in both directions** — the false-positive cases (`used to build`
passing) matter as much as the true ones.

## Tooling assessed

| Considered | Verdict |
| --- | --- |
| **Diátaxis** | Adopt. The compass is the one framework piece that works at paragraph scale. Gives no maintenance mechanism — supply your own. |
| **MADR 4.0.0** | Adopt for `journal/decisions/`. `NNNN-title-with-dashes.md`. |
| **arc42** | Skip. Twelve mandatory sections invite the empty-section sprawl being fixed. |
| **llms.txt** | Skip for a repo. Specified for websites, and an agent with Glob/Grep gains nothing. Ship it only if `docs/` is published. |
| **mkdocs `--strict`** | Its `validation.nav.omitted_files` orphan gate is the one genuinely useful off-the-shelf check, and it is five lines against `docs/README.md`. Skip the site build unless you already publish. |
| **Vale, markdownlint, lychee** | Fine for hygiene. None can check frontmatter against a folder, which is the core rule. |
| **A single repo script** | What to actually build. Every rule that matters is repo-specific. |
