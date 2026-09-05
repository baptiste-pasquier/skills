# Versioning an install

This skill has no release number of its own. What it copies into a project — the gate
scripts, the seeded docs, the agent instructions section — has no version either, so a later
"what changed upstream since I installed this" has nothing to check against unless the
install itself records where it came from.

The skill repo is a git repo, so its commit SHA **is** the version. Write one file at the
project root, once, at install time:

```yaml
# .docs-taxonomy/manifest.yml
source: git@github.com:baptiste-pasquier/skills.git
path: docs-taxonomy
commit: {{sha}}
```

`commit` is the skill repo's `HEAD` at install time
(`git -C <path to the skill repo> rev-parse HEAD`). A leading dot keeps the file out of
`docs/` — it is metadata about the install, not a doc, and the gate already ignores hidden
paths.

## Using it later

Diff the whole skill directory at the recorded commit against its current `HEAD` — template
against template, in the skill repo itself, never the skill source against the project's
copy. A per-file diff against the project's copy would show the `CONFIGURATION` block edits
and every filled-in `{{PLACEHOLDER}}` as noise; this diff shows only what the skill itself
changed.

```bash
git -C <path to a checkout of the skill repo> diff <commit-from-manifest>..HEAD -- docs-taxonomy
```

Read the result as a changelog: which scripts changed outside their `CONFIGURATION` block,
which templates gained a rule or a table row, which reference files moved. Re-apply by hand
whatever is still relevant — re-copy a script, backport a rule into the project's already
customized doc — there is no project file to overwrite automatically.

Bump `commit` in the manifest to the `HEAD` you diffed against once done, so the next diff
starts from here.
