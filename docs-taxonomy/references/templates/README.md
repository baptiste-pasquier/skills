# Templates

Copy, then replace every `{{PLACEHOLDER}}`. Delete any section that does not apply — an
inherited section nobody meant is how the next drift starts.

| File | Goes to |
| --- | --- |
| `docs-readme.md` | `docs/README.md` |
| `conventions-documentation.md` | `docs/conventions/documentation.md` |
| `solutions-readme.md` | `docs/journal/solutions/README.md` |
| `decisions-readme.md` | `docs/journal/decisions/README.md` |
| `agents-section.md` | the `## Documentation` section of `AGENTS.md` / `CLAUDE.md` |
| `frontmatter.md` | the schema, for reference while writing the others |

`docs/README.md` and the agents section both carry the compass table. That duplication is
deliberate: the agent must not need a second file read to place a paragraph. Keep them in
sync — a diff between them is a bug.
