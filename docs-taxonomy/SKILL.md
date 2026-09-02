---
name: docs-taxonomy
description: Restructure a project's docs/ into a MECE, enforced taxonomy - Diátaxis quadrants plus an append-only journal - so humans and coding agents both have exactly one place to put each paragraph. Use when docs/ has drifted (agents appending paragraphs every PR, nothing ever pruned, retrospectives interleaved with explanation), when setting up docs/ on a new project, when asked to make documentation agent-readable or stop doc sprawl, or when asked where a doc belongs. Ships a diagnosis procedure, file templates, and a CI gate.
---

# docs-taxonomy

Documentation written by humans **and** coding agents drifts in one specific way: agents
append, and nothing prunes. Every PR that turns up a subtlety adds a paragraph to whatever
doc was open. After a few months no doc has a single subject, the same lesson is written
three times in three files, and nobody can tell which copy is current.

This skill fixes that structurally. Not with review discipline — review discipline is what
already failed.

## Route first

| Situation | Go to |
| --- | --- |
| `docs/` exists and has drifted | **Brownfield**, below. Diagnose before touching anything. |
| New project, or `docs/` is 1-2 files | **Greenfield**, below. Create almost nothing. |
| "Where does this paragraph go?" | [The routing rule](#the-routing-rule). Answer, do not restructure. |
| A gate is misfiring | `references/pitfalls.md` |

## The design, in one screen

**Two axes, and only two.**

**Axis 1 — lifecycle.** Is this text *maintained*, or is it a *dated record*? This is the
axis that governs behaviour: may I edit this, and may I cite it as truth?

**Axis 2 — the [Diátaxis](https://diataxis.fr/) quadrant**, for maintained text only.

```
docs/
├── README.md          the map + the routing rule. The only entry point.
│
├── explanation/       WHY it works this way.   Narrative allowed.
├── how-to/            HOW to reach a goal.     Numbered steps.
├── reference/         WHAT is true.            Tables, contracts. No narrative.
├── conventions/       WHAT YOU MUST DO.        Imperative, checkable. Agent-first.
│
├── BACKLOG.md         unbuilt work (see references/backlog.md)
│
└── journal/           DATED. Append-only. Never revised, never cited as truth.
    ├── decisions/     one architectural choice per entry (MADR)
    ├── solutions/     what broke, what was tried, what was measured
    ├── plans/         implementation plans, kept for provenance
    └── ideation/      requirements exploration that fed a plan
```

**`journal/` is the load-bearing idea.** It is where the append reflex goes to be harmless
— append-only *by design*. Without it, retrospective prose has no home and lands in
explanation docs, where it is never pruned. Nothing in `journal/` is a source of truth: a
maintained doc may link a journal entry, never the reverse.

**`conventions/` is a fifth folder, deliberately outside the compass.** The compass sorts
content by what a *reader of the product* needs; conventions target a *writer of the repo*.

**Create no empty quadrants.** Diátaxis says so and it matters: an empty folder is an
invitation to fill it with the wrong thing. Most repos have no tutorial — do not make
`tutorials/` until one exists.

## The routing rule

The **Diátaxis compass**, two questions in order. It works **at paragraph scale**, which is
the scale at which docs actually drift. Put it in `docs/README.md` and in the agent
instructions file, verbatim.

| The content… | …serves the reader… | …belongs in |
| --- | --- | --- |
| informs **action** | **applying** a skill (working) | `how-to/` |
| informs **action** | **acquiring** a skill (studying) | a tutorial (or `how-to/` if none) |
| informs **cognition** | **applying** a skill (working) | `reference/` |
| informs **cognition** | **acquiring** a skill (studying) | `explanation/` |

Four extensions, for text that is not about the product:

| The paragraph… | goes to | never to |
| --- | --- | --- |
| tells a future writer or agent what to do | `conventions/` | `explanation/` |
| recounts what was tried, what failed, what was measured | `journal/solutions/` | anywhere maintained |
| records a choice between options | `journal/decisions/` | `explanation/` |
| names something not built yet | the issue tracker | prose, anywhere |

**The corollary that kills duplication: a maintained doc states the rule once and links the
journal entry for the evidence.** It does not retell the story.

## Brownfield: diagnose, then move

**Do not restructure before measuring.** The numbers decide the scope, prove the problem to
whoever must approve the churn, and often reveal that one file is 80% of it.

### 1. Measure

Run every command in `references/diagnose.md`. It produces:

- the **append ratio** (lines added vs removed in `docs/` over the project's life) — the
  headline number;
- per-file commit counts and add/remove ratios — finds the one or two files that are the
  real problem;
- **duplicated lessons** — grep for the same claim across files, and the cross-link graph
  (a fully-connected graph means no hierarchy);
- buried backlog items, language mixing, broken links, prose-vs-code ratio per file.

Write the findings down as a numbered list before proposing anything. If the append ratio
is near 1:1 and no lesson is duplicated, **the docs are fine** — say so and stop.

### 2. Decide with the owner

Four questions have no default. Ask them (see `references/decisions.md` for the trade-offs):

1. **Language** — one language for all docs, or a stated boundary?
2. **Scope** — `docs/` only, or also co-located `README.md`s and sub-projects?
3. **Existing plans/specs** — delete, or move to `journal/` marked shipped?
4. **Backlog** — issue tracker only, a tracked mirror, or a generated file?

### 3. Move, in this order

1. Create the tree and `docs/README.md`. Write `conventions/documentation.md`.
2. **Install the gate before moving content**, with an allowlist so it passes on the old
   tree. A gate added afterwards never gets added.
3. `git mv` the dated records into `journal/`. Use `git mv` — renames preserve history and
   keep the diff reviewable.
4. Split the drifted docs. **For each, extract every incident narrative into a
   `journal/solutions/` entry and leave the distilled rule plus a link.** This is the bulk
   of the work and the whole point.
5. Fix every reference: code docstrings, generator output paths, tests, CI, the root
   `README.md`, relative-link depths. Then grep for the old paths repo-wide.
6. Rewrite the agent instructions file (see below).
7. Drop the allowlist. Write ADRs for the choices just made.

### 4. Extract the narratives

The rule, applied to every maintained doc:

> A passage that recounts a past attempt, a failure, or a measured symptom becomes its own
> `journal/solutions/` entry. What stays inline is the distilled one-to-two-sentence rule,
> plus a link.

Markers: `used to be`, `we tried`, `an earlier version`, `before this fix`,
`3 attempts out of 4`.

**Consolidate.** A lesson narrated in three files becomes **one** entry linked from three
places. That is usually the single biggest readability win.

**Know what stays.** A hard-won **invariant** is explanation, not an incident. The test:
*would a reader who never saw the bug still need this to work on the code?* Yes means it
stays. Put that counter-example in `conventions/documentation.md`, or the rule gets
over-applied and real explanation gets gutted.

## Greenfield: create almost nothing

Do **not** scaffold four empty folders. Create:

1. `docs/README.md` — the routing rule and an empty index. This alone prevents most drift.
2. `conventions/documentation.md` — the rules.
3. The gate (`scripts/check_docs.py` + pre-commit hook + a test).
4. The agent instructions section.

Folders appear when their first doc does. `journal/decisions/` is worth creating early — a
project makes decisions before it has explanations.

## The gate

`scripts/check_docs.py` in `references/` is a single dependency-light file. Copy it into the
project, edit the marked constants block, wire it two ways: a pre-commit hook, **and** a
test, so CI fails on a bad merge even if hooks were skipped.

**What must fail:**

| Check | Why it is the one that matters |
| --- | --- |
| `type` frontmatter ≠ its folder | Turns the compass from advice into a gate. The core check. |
| Incident narration in `reference/`/`conventions/` | Targets the observed failure mode directly. |
| Missing or invalid frontmatter | |
| A relative link that does not resolve | Catches renames and phantom files. |
| A maintained doc missing from the index | The orphan-file gate. |
| A file in an unknown folder, or a bad filename | |
| Language, if a language rule was chosen | Stops the rule eroding. |

**What must only warn:** document size, and staleness dates. Both, always.

**And the rule behind that:** a gate must depend on the change under review. A size cap
blocks a legitimate addition; a shared expiry date reddens every unrelated PR on the day it
fires. See `references/pitfalls.md` — this is the mistake most worth not repeating.

What carries the load instead of a size cap:

- **One claim per paragraph**, stated in `conventions/documentation.md`. A single-claim
  paragraph is individually replaceable, so the next writer edits it. A multi-claim
  paragraph resists that, so the next writer appends a third claim.
- The **banned incident narration**, which does fail.
- A **PR-template checkbox**: prose added to a maintained doc says what it removed, or why
  nothing needed removing.

**Verify each gate fails.** Seed a violation per rule, watch it fail with an accurate line
number, remove it. A gate nobody has seen fail is indistinguishable from no gate. Then
write those cases as tests, both directions — `used to build` must **not** be flagged as
incident narration.

## Rewire the agent instructions

The agent instructions file (`AGENTS.md`, `CLAUDE.md`, or both) is usually **itself a cause
of the drift.** Look for bullets shaped:

> "Use and update `docs/<file>` whenever X changes."

That is an instruction to append to a named file. Replace the whole section with a router:

1. The compass table, and a pointer to `docs/README.md`.
2. The gate list, split into **what fails** and **what is reviewed** — and make it match
   the code exactly. An overstated rule makes an agent move prose that belonged where it was.
3. One rule per trigger pointing at a **directory**, not a file: "when a tool changes,
   update `reference/tools.md`; if the change taught you something, add a
   `journal/solutions/` entry — do not narrate it in the reference".
4. "Before implementing a fix, check `journal/solutions/` for an entry in that area."
5. "Never write a backlog section under `docs/`."

Then move path-scoped rules **out** of the always-loaded file. In Claude Code,
`.claude/rules/*.md` with `paths:` frontmatter loads only when a matching file is read —
so prompt conventions load when a prompt is touched, not every session. Each rule file is
a 5-line pointer, never a copy; the rulebook stays in `docs/conventions/` where humans
read it.

**Every `conventions/` file opens with a one-line `Scope:` statement** naming the artifact
it governs, and the gate checks it. `conventions/` will hold rules for unrelated things —
docs prose, prompt text, commit messages — and a reader must never have to infer which.

## Compound-engineering and other artifact writers

If the project uses the compound-engineering plugin, it writes up to nine artifact folder
names (`solutions`, `plans`, `ideation`, `explainers`, `specs`, `personas`,
`pulse-reports`, `dogfood-reports`, `feedback-sweep`). At the root of `docs/` they swamp any
taxonomy.

Set `docs_root: docs/journal` in `.compound-engineering/config.yaml`. A configured root
becomes the sole location it reads and writes. This is the single setting that unifies those
artifacts with the taxonomy.

Also ship **in-repo templates** for `journal/solutions/README.md` and
`journal/decisions/README.md`. An ordinary session does not load the plugin and must still
be able to follow the format.

## Files in this skill

| Path | Use |
| --- | --- |
| `references/diagnose.md` | The measurement commands. Run these first, always. |
| `references/decisions.md` | The four questions to ask the owner, with trade-offs. |
| `references/pitfalls.md` | **Read before building the gate.** Mistakes with real cost. |
| `references/backlog.md` | Backlog options, and the branch-protection trap. |
| `references/templates/` | `docs-readme.md`, `conventions-documentation.md`, `solutions-readme.md`, `decisions-readme.md`, `agents-section.md` |
| `scripts/check_docs.py` | The gate. Copy in, edit the constants block. |
| `scripts/test_check_docs.py` | Its tests, both directions per rule. |
