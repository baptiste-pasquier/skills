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
| **Move to `journal/plans/` with `status: shipped`** | Recommended. Provenance stays navigable and explicitly marked as a record, so its stale content is harmless. Costs volume in the tree. |
| **Delete** | `docs/` shrinks immediately; git keeps the content. Loses browsable provenance and the `origin:` chain between documents. |
| **Archive outside the repo** | Cleanest tree, but a coding agent loses all provenance — and any artifact-writing plugin will just recreate the folders. |

**Do not "fix" the stale content in a record.** A record is a record. State that rule in
`conventions/documentation.md` instead, and repoint only dead metadata (an `origin:` path).

## 4. Backlog

See `references/backlog.md`. The short version: the tracker is the source of truth, and the
only question is whether a mirror is worth its refresh mechanism.

---

# Two decisions to make yourself

Do not put these to the owner — the answer is the same every time.

**Size warns, never fails.** And staleness too. See `pitfalls.md`. If asked for a hard cap,
explain what carries the load instead and offer the warning; if the owner insists, comply
and note the consequence — a legitimate reference-table addition will be blocked.

**No empty quadrants.** Create a folder when its first doc exists. `tutorials/` almost never
exists on day one.
