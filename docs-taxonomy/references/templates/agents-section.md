<!-- Replaces the `## Documentation` section of AGENTS.md / CLAUDE.md.

     If the existing section contains bullets shaped "Use and update `docs/<file>`
     whenever X changes", those ARE the drift. Delete them; do not keep them
     alongside this. -->

## Documentation

`docs/` has one topology and one routing rule. **Read [`docs/README.md`](docs/README.md)
before creating or substantially extending anything under `docs/`.** Full rules:
[`docs/conventions/documentation.md`](docs/conventions/documentation.md).

### Where a paragraph goes

Two axes. **Lifecycle first**: the four folders below are *maintained* and are the sources
of truth; `docs/journal/` is *append-only*, dated, and **never cited as truth**. Then, for
maintained text, the [Diátaxis](https://diataxis.fr/compass/) compass — run it on **the
paragraph**, not on the file you have open.

| The content… | …serves the reader… | …belongs in |
| --- | --- | --- |
| informs **action** | **applying** a skill (working) | `docs/how-to/` |
| informs **action** | **acquiring** a skill (studying) | a tutorial — we have none, so `docs/how-to/` |
| informs **cognition** | **applying** a skill (working) | `docs/reference/` |
| informs **cognition** | **acquiring** a skill (studying) | `docs/explanation/` |

Four extensions, for text that is not about the product:

| The paragraph… | belongs in |
| --- | --- |
| tells a future writer or agent what to do | `docs/conventions/` |
| recounts what was tried, failed, or was measured | `docs/journal/solutions/` |
| records a choice between options | `docs/journal/decisions/` |
| names something not built yet | {{an issue labelled `backlog` / an issue, classified per [`docs/conventions/issues.md`](docs/conventions/issues.md)}} |

A maintained doc states the rule **once** and links the journal entry for the evidence. It
does not retell the story.

### Where a plugin's artifacts go

<!-- Delete this section if no artifact-writing plugin is installed, and delete any row
     whose plugin is not installed. -->

Every dated artifact a plugin writes is a journal entry. **The paths below override the ones
the plugins' own skills name** — an instruction in this file takes precedence over a skill's.

| Running | Do not write to | Write to |
| --- | --- | --- |
| `superpowers:brainstorming` | `docs/superpowers/specs/` | `docs/journal/specs/` |
| `superpowers:writing-plans` | `docs/superpowers/plans/` | `docs/journal/plans/` |
| a compound-engineering artifact skill | `docs/<artifact-name>/` | under `docs/journal/`, per `docs_root` in `.compound-engineering/config.yaml` |

**Only the directory changes.** Keep the plugin's own filename
(`YYYY-MM-DD-<topic>-design.md`) and its own frontmatter — a second schema means the plugin
keeps writing its own anyway. `docs/superpowers/` fails the gate as an unknown folder.

**In a plan or a spec, cite a repo file as a backticked path, not a markdown link**, unless
the path resolves from the artifact's own folder: the link check reads journal entries too,
and the plugin's examples link paths relative to the directory being worked on. A plan names
its spec as `../specs/<file>.md` — never as an absolute `docs/…` link.

A plan or a spec is a dated record of intent, so the no-backlog rule below does not reach
it — see that rule for what stays.

### Rules that are enforced

`scripts/check_docs.py` runs in pre-commit and CI. These fail:

- **Never narrate a past attempt, failure, or measured symptom in `docs/reference/`,
  `docs/conventions/` or `docs/how-to/`.** Write a `docs/journal/solutions/` entry
  (template: [`docs/journal/solutions/README.md`](docs/journal/solutions/README.md)) and
  leave the distilled rule with a link. This applies in **every** session, whether or not
  an artifact-writing plugin is running.
  `docs/explanation/` **may** narrate — that is what explanation is for — so the gate
  **warns** there rather than failing. A full write-up with symptoms and measurements still
  belongs in a journal entry, linked. `docs/journal/` is exempt: narrating what failed is
  its purpose.
- **Never add a backlog, TODO or "future work" section to a maintained doc.**
  Unbuilt work lives in the issue tracker and nowhere else — {{PICK ONE — `gh issue list
  --label backlog --limit 200` to read it, `gh issue create --label backlog` to add an item /
  opened and read per [`docs/conventions/issues.md`](docs/conventions/issues.md#commands)}}.
  **Link the issue** rather than describing the missing work. The gate fails on a section
  *headed* `TODO`, `Backlog`, `Future work`, `Roadmap` or `Open questions`; a single
  sentence asserting unbuilt work gets past it, so link instead of writing the sentence. A `TODO` comment in a source file is fine, and a doc
  may point at one; a *list* of unbuilt work in prose is not. `docs/journal/` is exempt, so a
  plan's own `Open Questions` section stays where the plugin wrote it.
- **Every maintained doc carries frontmatter** with `title`, `type` (equal to its folder
  name), `audience`, `status`, `stale_after`, and appears in `docs/README.md`. A key present
  but empty counts as missing. A passed `stale_after` **warns** rather than fails, so a
  review date cannot redden an unrelated PR.
- **Every `docs/conventions/` file opens with a `Scope:` line** naming the artifact it
  governs. The bolded form `**Scope:` passes too.
- **Every relative link and every `#fragment` resolves.** Renaming a heading breaks the
  links into it; the gate names them.
- **Filenames are kebab-case**, and a `docs/journal/decisions/` entry is
  `NNNN-with-dashes.md`.
- {{**{{Language}}**, everywhere in `docs/` including the journal. Quoted prompt text and
  user-facing labels stay {{other language}}, inside backticks or a code fence.}}

<!-- This list must match the code exactly. An overstated rule makes an agent move prose
     that belonged where it was. -->

### Rules that are reviewed, not gated

- **Before implementing a fix or a non-obvious behaviour change, check
  `docs/journal/solutions/`** for an entry in the relevant category.
- **Record a lasting architectural choice as an ADR** under `docs/journal/decisions/`. An
  accepted decision is never edited — a change adds a new entry marking the old superseded.
- **Documentation prose** — this governs the prose in `docs/`, not {{prompt text}}: lead
  with the conclusion; one claim per paragraph; no filler or hedging; prefer a table to
  enumerative prose. A single-claim paragraph is individually replaceable, which is what
  stops the next writer appending a third claim to it.
- **A PR that adds prose to a maintained doc says what it removed, or why nothing needed
  removing.** There is a checkbox in the PR template. The size check only warns, so this is
  what catches growth nobody looked at.

### What to update when

| You changed | Update |
| --- | --- |
| {{a tool / an endpoint / a schema}} | {{`docs/reference/<file>.md`}} |
| {{conversation flow / core behaviour}} | {{`docs/explanation/<file>.md`}} |
| {{deployment, CI/CD}} | {{`docs/how-to/<file>.md`}} |
| user-facing behaviour, setup, local workflow | `README.md` |
| {{an `area:*` label, or the issue types or priorities in use}} | {{`docs/conventions/issues.md`}} |
| what an agent must always know | this file |

<!-- Point at a DIRECTORY per trigger, never "append to this file". -->

### Three kinds of instruction, three homes

| Kind | Home |
| --- | --- |
| {{Prompt text sent to the model}} | {{`src/.../prompts/` — docs never quote more than one line}} |
| {{Conventions for writing a prompt}} | {{`docs/conventions/prompting.md`}} |
| Instructions to the coding agent | this file (always loaded) + `.claude/rules/` (path-scoped) |

### Outside this tree

- {{An external docs mirror: where it lives, and the citation rule.}}
- {{An autonomous sub-project: load its own instructions file first; the rules above do not
  apply there.}}
