# {{Project}} documentation

Start here. This file is the map, and it carries the one rule for deciding where a new
paragraph goes.

## Two axes

**Lifecycle first.** Is this text *maintained*, or is it a *dated record*?

- The folders below the line are **maintained**. They are edited, pruned, and kept true.
  They are the sources of truth.
- `journal/` is **append-only**. Entries are dated, never revised, and **never cited as
  truth**. A maintained doc may link a journal entry; a journal entry never governs code.

**Then, for maintained text, the [Diátaxis](https://diataxis.fr/) quadrant.**

| Folder | The question it answers | Shape |
| --- | --- | --- |
| [`explanation/`](explanation/) | *Why does it work this way?* | Narrative allowed. Human-first. |
| [`how-to/`](how-to/) | *How do I reach this goal?* | Numbered steps. |
| [`reference/`](reference/) | *What is true?* | Tables and contracts. No narrative. |
| [`conventions/`](conventions/) | *What must I do when I write?* | Imperative, checkable. Agent-first. |
| [`journal/`](journal/) | *What happened, and what did we decide?* | Dated records. |

{{There is no `tutorials/` folder. Diátaxis's fourth quadrant is real, but nothing here is
a tutorial yet, and it warns against empty quadrants. When one is written, it gets its
folder.}}

## Where does this paragraph go?

The **Diátaxis compass**, two questions in order. It works at paragraph scale, which is the
scale at which docs actually drift.

| The content… | …serves the reader… | …belongs in |
| --- | --- | --- |
| informs **action** | **applying** a skill (working) | `how-to/` |
| informs **action** | **acquiring** a skill (studying) | a tutorial — we have none, so `how-to/` |
| informs **cognition** | **applying** a skill (working) | `reference/` |
| informs **cognition** | **acquiring** a skill (studying) | `explanation/` |

Four extensions, for text that is not about the product:

| The paragraph… | goes to | never to |
| --- | --- | --- |
| tells a future writer or agent what to do | `conventions/` | `explanation/` |
| recounts what was tried, what failed, what was measured | `journal/solutions/` | anywhere maintained |
| records a choice between options | `journal/decisions/` | `explanation/` |
| names something not built yet | {{the issue tracker}} | prose, anywhere |

**The rule that keeps this from sprawling:** a maintained doc states the rule **once** and
links the journal entry for the evidence. It does not retell the story.

Full rules, including how to write the sentence itself:
[`conventions/documentation.md`](conventions/documentation.md).

## The index

Every maintained doc appears here. A doc missing from this list fails CI.

### `explanation/`

- {{[`name.md`](explanation/name.md) — one line}}

### `how-to/`

- {{[`name.md`](how-to/name.md) — one line}}

### `reference/`

- {{[`name.md`](reference/name.md) — one line}}

### `conventions/`

- [`documentation.md`](conventions/documentation.md) — where a paragraph goes, and how to
  write it. Governs the prose in `docs/`
- {{[`name.md`](conventions/name.md) — governs {{what}}}}

### `journal/`

- [`decisions/`](journal/decisions/) — one architectural choice per entry, MADR format.
  An accepted decision is never edited
- [`solutions/`](journal/solutions/) — what broke, what was tried, what the measurement
  said. Read the relevant category before implementing a fix
- [`plans/`](journal/plans/) — shipped implementation plans, kept for provenance
- [`ideation/`](journal/ideation/) — requirements exploration that fed a plan

Templates: [`solutions/README.md`](journal/solutions/README.md),
[`decisions/README.md`](journal/decisions/README.md).

## Not in this tree

| What | Where | Why |
| --- | --- | --- |
| {{Prompt text / generated code / secrets}} | {{path}} | {{why docs only point at it}} |
| Unbuilt work | {{BACKLOG.md or the tracker}} | {{how it is maintained}} |
| {{An external docs mirror}} | {{where}} | Owned outside this repo |
| {{An autonomous sub-project's docs}} | {{path}} | Its own conventions; these rules do not apply |

## What CI enforces

`scripts/check_docs.py` runs in pre-commit and in CI. It fails on:

1. a file whose `type` does not match its folder, or a file in an unknown folder
2. missing or invalid frontmatter
3. a relative link that does not resolve
4. a maintained doc missing from the index above
5. {{prose in the wrong language, outside a code fence}}
6. past-tense incident narration in `reference/` or `conventions/`
7. a banned filler phrase
8. a filename that is not kebab-case, or an ADR not named `NNNN-with-dashes.md`
9. a `conventions/` file that does not open with a `Scope:` line
10. {{`BACKLOG.md` with its generated header removed}}

It **warns**, without failing, on two things: a maintained doc past {{150}} prose lines
(`reference/`: {{250}}), and a `stale_after` date that has passed. Neither fails, because
neither depends on the change being reviewed — an expiry would otherwise redden every
unrelated PR on the day it fires.

{{Two rules are enforced outside the checker: a hand edit to `BACKLOG.md` is caught at
commit time by `scripts/check_backlog_staging.sh`, not in CI where nothing is staged; and
the review rule below is a checkbox in the PR template.}}
