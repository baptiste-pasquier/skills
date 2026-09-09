# The four questions to ask the owner

These have no sensible default. Guessing wrong means redoing the content work, so ask
before moving anything — during the diagnosis, not after.

## 1. Language

Ask when the docs currently mix languages, or when the product domain is not in English.

| Option | Cost | Suits |
| --- | --- | --- |
| **One language, all docs** | Translating whatever is in the other one | Most repos. One rule, gateable. |
| **English docs, domain terms kept** | None. Needs the exception written down. | A non-English business domain: keep *dossier*, *apport*, *VEFA* in running text, because renaming them makes the docs disagree with the code. |
| **A stated per-folder boundary** | No translation, but the rule is "which folder am I in", which erodes | Genuinely split audiences (business docs vs infra docs) |
| **No rule** | This is the current state, and it is drift | Nothing |

If a language rule is chosen, **gate it** — and carve out quoted prompt text and
user-facing labels, which must stay verbatim. Require them inside backticks or a fence so
the checker skips them.

## 2. Scope

| Include | When |
| --- | --- |
| `docs/` + the agent instructions file + root `README.md` | Always. The minimum. |
| Co-located `README.md`s under `src/` | When one is a de facto reference doc other docs defer to. Move the content, leave a short pointer stub — do not orphan the directory. |
| Autonomous sub-projects with their own docs | Usually **exclude**, and say so explicitly in the instructions file. An unstated exclusion becomes a question every session. |
| An external docs mirror (Confluence, Notion) | Define only the **boundary**: what lives in the repo versus there. |

## 3. Existing plans, specs and brainstorms

These are often 40%+ of `docs/` and factually stale — enum values that changed, file paths
that were deleted.

| Option | Trade-off |
| --- | --- |
| **Move to `journal/plans/` with `status: shipped`** — an approved design to `journal/specs/`, an exploration to `journal/ideation/` | Recommended. Provenance stays navigable and explicitly marked as a record, so its stale content is harmless. Costs volume in the tree. |
| **Delete** | `docs/` shrinks immediately; git keeps the content. Loses browsable provenance and the `origin:` chain between documents. |
| **Archive outside the repo** | Cleanest tree, but a coding agent loses all provenance — and any artifact-writing plugin will just recreate the folders. |

**Do not "fix" the stale content in a record.** A record is a record. State that rule in
`conventions/documentation.md` instead, and repoint only dead metadata (an `origin:` path).

**Moving a plugin's artifact breaks its links.** These documents cite repo files with paths
relative to their old folder, and the gate resolves every link in a journal entry — so
budget for rewriting them in the move commit, or the restructure lands red on dozens of
broken links.

**Whatever the answer, repoint the writer in the same PR.** Move `docs/superpowers/specs/`
without redirecting `superpowers:brainstorming` and the next session recreates the folder —
where the gate now fails it, in a PR whose author did nothing wrong. The skill's
*Artifact-writing plugins* section has the redirect for each mechanism.

## 4. Backlog

The tracker is the source of truth either way. What you are asking is whether a mirror in
`docs/BACKLOG.md` earns its refresh mechanism, and **one fact decides it: can a workflow
push to the default branch?**

| Option | Cost | Suits |
| --- | --- | --- |
| **Mirror, refreshed by a GitHub Action** | A generator, a pre-commit hook, a workflow with `contents: write`, a header gate rule, a title-escaping contract | A repo whose default branch accepts a bot push. Preferred where possible: an agent sees unbuilt work with no tool call, and nobody has to remember anything. |
| **Tracker only, `gh issue list` in the agents file** | An agent with no `gh` credentials cannot read the backlog at all | **Everything else**, and the simpler answer anywhere. Zero machinery. |
| **Mirror refreshed by hand, or by a report-only job** | The full apparatus *and* a human who remembers | Nothing. See `backlog.md`. |
| **Gitignored mirror** | The full apparatus, none of the benefit | Nothing. Argued in `backlog.md`. |

Ask the owner, then **check the answer** — a protected branch is the common case and people
forget their own rulesets. `references/backlog.md` has the two `gh api` calls, the workflow
to ship when a push can land, and the reason report-only is not a fallback.

---

# Two decisions to make yourself

Do not put these to the owner — the answer is the same every time.

**Size warns, never fails.** And staleness too. See `pitfalls.md`. If asked for a hard cap,
explain what carries the load instead and offer the warning; if the owner insists, comply
and note the consequence — a legitimate reference-table addition will be blocked.

**No empty quadrants.** Create a folder when its first doc exists. `tutorials/` almost never
exists on day one.
