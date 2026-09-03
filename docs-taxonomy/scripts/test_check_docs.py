"""Tests for `check_docs.py`.

Two things are asserted, and the second is the one that matters:

1. A valid tree passes.
2. **Every rule rejects the shape it claims to reject.** A structural gate nobody
   has seen fail is indistinguishable from no gate, and a whole-tree test that
   only asserts "clean" stays green when you delete a rule.

Each test builds its own tree under `tmp_path` and repoints the script at it, so
the suite runs from any working directory and never needs the project's real
`docs/` to exist. The hostile tree at the end carries one instance of every
shape the gate should catch: delete a rule, and a test names the rule.

WHERE THIS FILE GOES: next to `check_docs.py`, or in the project's test tree
mirroring it. Both work - the import below tries the package path first, then
falls back to the sibling file.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

try:  # the project's layout, e.g. `scripts/check_docs.py` imported as a package
    from scripts import check_docs as cd
except ImportError:  # the file sitting next to this test
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_docs as cd

TOMORROW = dt.date.today() + dt.timedelta(days=365)


def frontmatter(folder: str, **overrides: object) -> str:
    """Return valid frontmatter for a maintained doc in `folder`."""
    fields: dict[str, object] = {
        "title": "A doc",
        "type": folder,
        "audience": "[agent]",
        "status": "stable",
        "stale_after": TOMORROW.isoformat(),
    }
    fields.update(overrides)
    lines = "\n".join(f"{key}: {value}" for key, value in fields.items())
    return f"---\n{lines}\n---\n"


@dataclass
class Tree:
    """A throwaway docs tree, with the gate pointed at it."""

    root: Path

    @property
    def docs(self) -> Path:
        """Return the tree's `docs/` folder."""
        return self.root / "docs"

    def write(self, relative: str, text: str) -> Path:
        """Write one file under `docs/`, creating its parents."""
        path = self.docs / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def index(self, *listed: str) -> None:
        """Write `docs/README.md` naming every maintained doc given."""
        rows = "".join(f"- [{name}]({name})\n" for name in listed)
        self.write("README.md", f"# Docs\n\n{rows}")

    def run(self) -> tuple[list[str], list[str]]:
        """Run every check, returning the failure and the warning messages."""
        problems = cd.check_docs()
        return (
            [p.message for p in problems if not p.warning],
            [p.message for p in problems if p.warning],
        )

    def failures(self) -> str:
        """Return the failure messages joined, for substring assertions."""
        return " | ".join(self.run()[0])


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Tree:
    """Return an empty tree with the gate repointed at it."""
    built = Tree(tmp_path)
    built.docs.mkdir()
    monkeypatch.setattr(cd, "REPO_ROOT", built.root)
    monkeypatch.setattr(cd, "DOCS", built.docs)
    return built


@pytest.fixture
def valid(tree: Tree) -> Tree:
    """Return a tree holding one valid doc in every folder."""
    tree.write("reference/a-contract.md", frontmatter("reference") + "\n# A contract\n")
    tree.write("how-to/do-a-thing.md", frontmatter("how-to") + "\n# Do a thing\n")
    tree.write(
        "explanation/why-it-is.md", frontmatter("explanation") + "\n# Why it is\n"
    )
    tree.write(
        "conventions/writing.md",
        frontmatter("conventions") + "\n# Writing\n\n**Scope: the prose in docs/.**\n",
    )
    tree.write(
        "journal/solutions/logic/a-lesson.md",
        "---\ncategory: docs/journal/solutions/logic\n---\n\n# A lesson\n",
    )
    tree.write("journal/decisions/0001-a-choice.md", "# A choice\n")
    tree.index(
        "reference/a-contract.md",
        "how-to/do-a-thing.md",
        "explanation/why-it-is.md",
        "conventions/writing.md",
    )
    return tree


# --------------------------------------------------------------------------
# The passing direction.


def test_a_valid_tree_passes(valid: Tree) -> None:
    """Everything the templates ship, as shipped, exits clean."""
    failures, _ = valid.run()
    assert failures == []


def test_a_missing_docs_folder_is_reported(tree: Tree) -> None:
    """Pointed at a tree with no `docs/`, the gate says so instead of crashing."""
    tree.docs.rmdir()
    assert "does not exist" in tree.failures()


# --------------------------------------------------------------------------
# Placement and naming.


def test_type_must_match_its_folder(valid: Tree) -> None:
    """The field that turns the routing rule into a gate."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference", type="explanation") + "\n"
    )
    assert "does not match its folder" in valid.failures()


def test_an_unknown_folder_fails(valid: Tree) -> None:
    """A folder outside the taxonomy is reported, not ignored."""
    valid.write("agent-design/x.md", frontmatter("reference") + "\n")
    assert "unknown folder" in valid.failures()


def test_a_loose_file_at_the_docs_root_fails(valid: Tree) -> None:
    """Only the index and the backlog mirror sit at the root."""
    valid.write("notes.md", "# Notes\n")
    assert "loose file at the root" in valid.failures()


def test_a_non_doc_extension_at_the_root_fails(valid: Tree) -> None:
    """A `.txt` cannot smuggle prose past the gate."""
    valid.write("notes.txt", "whatever\n")
    assert "loose file at the root" in valid.failures()


def test_a_non_doc_extension_in_a_folder_fails(valid: Tree) -> None:
    """Nor inside a quadrant."""
    valid.write("reference/notes.txt", "whatever\n")
    assert "unexpected `.txt`" in valid.failures()


def test_an_uppercase_markdown_file_is_still_checked(valid: Tree) -> None:
    """`.MD` is markdown, and a walker globbing `*.md` never sees it."""
    valid.write("how-to/Upper.MD", "# no frontmatter here\n")
    assert "kebab-case" in valid.failures()


def test_a_filename_must_be_kebab_case(valid: Tree) -> None:
    """Naming is part of the taxonomy, not decoration."""
    valid.write("reference/Not_Kebab.md", frontmatter("reference") + "\n")
    assert "kebab-case" in valid.failures()


def test_a_data_file_is_checked_for_its_name(valid: Tree) -> None:
    """A generated spec beside the docs still follows the naming rule."""
    valid.write("reference/openAPI_spec.yaml", "openapi: 3.1.0\n")
    assert "kebab-case" in valid.failures()


def test_a_well_named_data_file_passes(valid: Tree) -> None:
    """A kebab-case spec raises nothing, and needs no frontmatter."""
    valid.write("reference/openapi.yaml", "openapi: 3.1.0\n")
    assert valid.run()[0] == []


def test_a_symlinked_folder_is_reported(valid: Tree, tmp_path: Path) -> None:
    """A symlinked quadrant hides every file inside it from every rule."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "smuggled.md").write_text("# no frontmatter\n", encoding="utf-8")
    (valid.docs / "sneaky").symlink_to(outside, target_is_directory=True)
    assert "symlinked folder" in valid.failures()


def test_a_journal_entry_must_be_kebab_case(valid: Tree) -> None:
    """Append-only does not mean unnamed."""
    valid.write("journal/solutions/logic/Not_Kebab_CASE.md", "# A lesson\n")
    assert "kebab-case" in valid.failures()


def test_an_adr_must_be_numbered(valid: Tree) -> None:
    """A decision record carries its sequence in its filename."""
    valid.write("journal/decisions/why-postgres.md", "# Why Postgres\n")
    assert "NNNN-with-dashes" in valid.failures()


# --------------------------------------------------------------------------
# Frontmatter.


def test_frontmatter_is_required(valid: Tree) -> None:
    """A maintained doc with no frontmatter fails."""
    valid.write("reference/a-contract.md", "# A contract\n")
    assert "missing or unparseable YAML frontmatter" in valid.failures()


@pytest.mark.parametrize("key", cd.REQUIRED_KEYS)
def test_a_key_present_but_empty_counts_as_missing(valid: Tree, key: str) -> None:
    """`title:` with no value parses to `None` and must not satisfy the schema."""
    valid.write("reference/a-contract.md", frontmatter("reference", **{key: ""}) + "\n")
    assert f"missing `{key}`" in valid.failures()


def test_five_bare_keys_do_not_pass(valid: Tree) -> None:
    """The whole-file version of the rule above, which is how it shipped."""
    bare = "---\ntitle:\ntype:\naudience:\nstatus:\nstale_after:\n---\n\n# A doc\n"
    valid.write("reference/a-contract.md", bare)
    failures = valid.failures()
    assert failures.count("missing") == len(cd.REQUIRED_KEYS), failures


def test_an_invalid_status_fails(valid: Tree) -> None:
    """The status vocabulary is closed."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference", status="wip") + "\n"
    )
    assert "invalid status" in valid.failures()


def test_a_yaml_boolean_status_fails(valid: Tree) -> None:
    """`status: no` parses to False, which a truthiness test lets through."""
    valid.write("reference/a-contract.md", frontmatter("reference", status="no") + "\n")
    assert "invalid status" in valid.failures()


def test_an_invalid_audience_fails(valid: Tree) -> None:
    """So is the audience vocabulary."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference", audience="[robot]") + "\n"
    )
    assert "invalid audience" in valid.failures()


def test_a_passed_expiry_warns_rather_than_failing() -> None:
    """A review date must not redden a PR that did not touch the doc."""
    yesterday = dt.date.today() - dt.timedelta(days=1)
    problems = cd.check_expiry(Path("x.md"), yesterday)
    assert problems and all(problem.warning for problem in problems)
    assert "has passed" in problems[0].message


def test_an_unexpired_doc_raises_nothing() -> None:
    """A future expiry is silent."""
    assert cd.check_expiry(Path("x.md"), TOMORROW) == []


def test_a_yaml_timestamp_expiry_does_not_crash() -> None:
    """YAML parses `2027-03-02 00:00` as a datetime, which subclasses date."""
    stamp = dt.datetime.combine(TOMORROW, dt.time(0, 0))
    assert cd.check_expiry(Path("x.md"), stamp) == []


def test_a_non_date_expiry_is_reported() -> None:
    """A string that is not a date is a schema error, not a crash."""
    problems = cd.check_expiry(Path("x.md"), "soon")
    assert "not an ISO date" in problems[0].message


# --------------------------------------------------------------------------
# Prose rules.


def test_incident_narration_fails_in_reference(valid: Tree) -> None:
    """A reference states what is true, not what went wrong once."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nThe node used to be called first.\n",
    )
    assert "incident narration" in valid.failures()


def test_incident_narration_fails_in_a_how_to(valid: Tree) -> None:
    """A procedure is not the place for the story of a past failure."""
    valid.write(
        "how-to/do-a-thing.md",
        frontmatter("how-to") + "\nThe step used to be run before the deploy.\n",
    )
    assert "incident narration" in valid.failures()


def test_incident_narration_only_warns_in_explanation(valid: Tree) -> None:
    """Explanation is the one maintained folder allowed to narrate."""
    valid.write(
        "explanation/why-it-is.md",
        frontmatter("explanation") + "\nThe node used to be called first.\n",
    )
    failures, warnings = valid.run()
    assert failures == []
    assert any("incident narration" in message for message in warnings)


def test_incident_narration_is_allowed_in_the_journal(valid: Tree) -> None:
    """Recording what failed is the journal's whole purpose."""
    valid.write(
        "journal/solutions/logic/a-lesson.md",
        "# A lesson\n\nWe tried three attempts; the earlier version used to crash.\n",
    )
    assert valid.run()[0] == []


def test_used_to_meaning_used_for_passes(valid: Tree) -> None:
    """`used to build` is not narration."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nField names used to build citations.\n",
    )
    assert valid.run()[0] == []


def test_a_backlog_section_fails(valid: Tree) -> None:
    """Unbuilt work belongs in the tracker, where something prunes it."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\n## Future work\n\n- TODO: the rest\n",
    )
    assert "is a backlog" in valid.failures()


@pytest.mark.parametrize("heading", ["TODO", "Backlog", "Roadmap", "Open questions"])
def test_every_backlog_heading_shape_fails(valid: Tree, heading: str) -> None:
    """The synonyms are covered, not only the first one."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference") + f"\n### {heading}\n"
    )
    assert "is a backlog" in valid.failures()


def test_a_rule_about_backlogs_is_not_a_backlog(valid: Tree) -> None:
    """The conventions doc states this rule, and must pass its own gate."""
    valid.write(
        "conventions/writing.md",
        frontmatter("conventions")
        + "\n**Scope: docs prose.**\n\n### Never write a backlog\n\nOpen an issue.\n",
    )
    assert valid.run()[0] == []


def test_a_filler_opener_fails(valid: Tree) -> None:
    """Every sentence carries a fact, a rule, or a pointer."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nIt is worth mentioning that this is true.\n",
    )
    assert "filler phrase" in valid.failures()


def test_foreign_prose_fails(valid: Tree) -> None:
    """The language rule cannot erode one paragraph at a time."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nLe noeud est appele dans le graphe pour cela.\n",
    )
    assert "is French" in valid.failures()


def test_foreign_prose_fails_in_the_journal_too(valid: Tree) -> None:
    """The journal is exempt from narration, not from the language rule."""
    valid.write(
        "journal/solutions/logic/a-lesson.md",
        "# A lesson\n\nLe noeud est appele dans le graphe pour cela.\n",
    )
    assert "is French" in valid.failures()


def test_english_with_one_foreign_looking_word_passes(valid: Tree) -> None:
    """Scored, not matched singly: `la` and `des` occur in English prose."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nThe la Nina pattern is not French prose.\n",
    )
    assert valid.run()[0] == []


def test_quoted_foreign_text_inside_backticks_passes(valid: Tree) -> None:
    """Quoted prompt text and user-facing labels keep their language."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nThe prompt says `ne repete pas ce que dit le "
        "client dans la reponse`.\n",
    )
    assert valid.run()[0] == []


def test_quoted_foreign_text_inside_a_fence_passes(valid: Tree) -> None:
    """So does a fenced block, including one indented inside a list item."""
    valid.write(
        "how-to/do-a-thing.md",
        frontmatter("how-to") + "\n1. Send this:\n\n   ```text\n"
        "   Le noeud est appele dans le graphe pour cela.\n   ```\n",
    )
    assert valid.run()[0] == []


def test_a_tilde_fence_also_hides_its_content(valid: Tree) -> None:
    """`~~~` is a fence too, and treating it as prose is a false failure."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference")
        + "\n~~~text\nLe noeud est appele dans le graphe pour cela.\n~~~\n",
    )
    assert valid.run()[0] == []


def test_a_fence_containing_a_shorter_fence_still_closes(valid: Tree) -> None:
    """A four-backtick block holds a three-backtick one without leaking."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference")
        + "\n````markdown\n```\ncode\n```\n````\n\nThis line is prose.\n",
    )
    assert valid.run()[0] == []


def test_the_scope_line_is_required_in_conventions(valid: Tree) -> None:
    """A conventions file names the artifact it governs, or nobody can tell."""
    valid.write("conventions/writing.md", frontmatter("conventions") + "\n# Writing\n")
    assert "must open with a `Scope:` line" in valid.failures()


def test_a_plain_scope_line_passes(valid: Tree) -> None:
    """The templates write `Scope:` unbolded, so the gate must accept it."""
    valid.write(
        "conventions/writing.md",
        frontmatter("conventions") + "\n# Writing\n\nScope: the prose in docs/.\n",
    )
    assert valid.run()[0] == []


def test_size_is_a_warning_not_a_failure(valid: Tree) -> None:
    """Growth is reported; growth nobody looked at is what review catches."""
    long_body = "".join(f"Sentence {index} carries a fact.\n\n" for index in range(400))
    valid.write("reference/a-contract.md", frontmatter("reference") + long_body)
    failures, warnings = valid.run()
    assert failures == []
    assert any("prose lines" in message for message in warnings)


def test_prose_lines_ignores_code_tables_and_headings() -> None:
    """The count measures prose, so a big table is not a big document."""
    body = "# H\n\n| a | b |\n| --- | --- |\n\n```py\nx = 1\n```\n\nOne line.\n"
    assert cd.prose_lines(body) == 1


# --------------------------------------------------------------------------
# Links, anchors and the index.


def test_a_broken_link_fails(valid: Tree) -> None:
    """The rule that catches a renamed file."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nSee [gone](graph-routing.md).\n",
    )
    assert "broken link -> graph-routing.md" in valid.failures()


@pytest.mark.parametrize(
    "link",
    [
        "[a](../journal/ghost-dir/)",
        '[b](./nope.md "A title")',
        "[c](./GONE.MD)",
        "[d](./two%20words.md)",
        "[e](<./spaced out.md>)",
    ],
)
def test_every_broken_link_shape_fails(valid: Tree, link: str) -> None:
    """A folder link, a titled link, an uppercase name, an encoded space."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference") + f"\nSee {link}.\n"
    )
    assert "broken link" in valid.failures()


def test_a_link_to_an_existing_folder_passes(valid: Tree) -> None:
    """A folder link is legitimate - the templates ship one."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nSee [entries](../journal/solutions/logic/).\n",
    )
    assert valid.run()[0] == []


def test_a_broken_anchor_fails(valid: Tree) -> None:
    """Renaming a heading breaks the links into it, silently."""
    valid.write(
        "reference/a-contract.md", frontmatter("reference") + "\n## The real heading\n"
    )
    valid.write(
        "how-to/do-a-thing.md",
        frontmatter("how-to")
        + "\nSee [there](../reference/a-contract.md#the-old-heading).\n",
    )
    assert "broken anchor" in valid.failures()


def test_a_resolving_anchor_passes(valid: Tree) -> None:
    """Including a same-file fragment, and an identifier in the heading."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\n## `option_answer_node` — the fast path\n\n"
        "See [above](#option_answer_node--the-fast-path).\n",
    )
    assert valid.run()[0] == []


def test_an_explicit_anchor_target_passes(valid: Tree) -> None:
    """An `<a id>` is a valid target even with no heading of that name."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + '\n<a id="custom"></a>\n\nSee [it](#custom).\n',
    )
    assert valid.run()[0] == []


def test_anchor_matches_the_host_slugging() -> None:
    """Identifiers keep their underscores; punctuation and formatting go."""
    assert cd.anchor("0. `option_answer_node` — the fast path") == (
        "0-option_answer_node--the-fast-path"
    )
    assert cd.anchor("**Field entry keys**") == "field-entry-keys"


def test_a_heading_inside_a_fence_is_not_an_anchor(valid: Tree) -> None:
    """A `#` line in a shell example is a comment."""
    target = valid.write("reference/a-contract.md", "# Real\n\n```bash\n# Fake\n```\n")
    assert cd.anchors_of(target) == {"real"}


def test_an_unindexed_doc_fails(valid: Tree) -> None:
    """Every maintained doc is reachable from the index."""
    valid.write("reference/orphan.md", frontmatter("reference") + "\n# Orphan\n")
    assert "not listed in docs/README.md" in valid.failures()


def test_a_missing_index_fails(valid: Tree) -> None:
    """The index is the only entry point, so its absence is a failure."""
    (valid.docs / "README.md").unlink()
    assert "README.md is missing" in valid.failures()


# --------------------------------------------------------------------------
# The journal.


def test_a_journal_category_must_match_its_folder(valid: Tree) -> None:
    """A moved entry whose `category` still names the old path is reported."""
    valid.write(
        "journal/solutions/logic/a-lesson.md",
        "---\ncategory: docs/solutions/logic\n---\n\n# A lesson\n",
    )
    assert "is not its folder" in valid.failures()


def test_a_journal_entry_with_no_category_passes(valid: Tree) -> None:
    """Not every entry format carries the field."""
    valid.write("journal/solutions/logic/a-lesson.md", "# A lesson\n")
    assert valid.run()[0] == []


# --------------------------------------------------------------------------
# The backlog mirror.


def test_a_hand_edited_backlog_fails(valid: Tree) -> None:
    """A generated file with its header removed was edited by hand."""
    valid.write("BACKLOG.md", "# Backlog\n\n- something I typed\n")
    assert "missing the generated header" in valid.failures()


def test_a_generated_backlog_passes(valid: Tree) -> None:
    """The generated file carries its provenance."""
    valid.write("BACKLOG.md", cd.GENERATED_BACKLOG_HEADER + " -->\n\n# Backlog\n")
    assert valid.run()[0] == []


def test_no_backlog_file_is_not_a_problem(valid: Tree) -> None:
    """A project without a mirror is not failed for not having one."""
    assert valid.run()[0] == []


# --------------------------------------------------------------------------
# The documented adaptation path. Every "off" switch in the CONFIGURATION
# block is exercised here, because a docstring whose instructions crash the
# script is how an adopter's first five minutes get spent.


def test_the_language_rule_can_be_switched_off(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`SECOND_LANGUAGE_MARKERS = None` disables it without a NameError."""
    monkeypatch.setattr(cd, "SECOND_LANGUAGE_MARKERS", None)
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nLe noeud est appele dans le graphe pour cela.\n",
    )
    assert valid.run() == ([], [])


def test_switching_the_mirror_off_rejects_the_file_too(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One switch, both consequences: no header to check, no file tolerated.

    This asserted `== []` once, which made the half-configured state - the gate
    no longer checking a mirror it still allows at the root - the *documented*
    behaviour. A hand-written mirror would have passed forever.
    """
    monkeypatch.setattr(cd, "GENERATED_BACKLOG_HEADER", None)
    valid.write("BACKLOG.md", "# A hand-written backlog\n")
    assert "loose file at the root" in valid.failures()


def test_switching_the_mirror_off_raises_no_type_error(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`None.startswith` was the original crash; with no file there is nothing."""
    monkeypatch.setattr(cd, "GENERATED_BACKLOG_HEADER", None)
    assert valid.run() == ([], [])


def test_the_root_allowlist_cannot_be_set_to_disagree() -> None:
    """The derivation itself: one setting decides both, so no pair can conflict."""
    assert cd.BACKLOG_NAME in cd.root_allowed()
    import unittest.mock

    with unittest.mock.patch.object(cd, "GENERATED_BACKLOG_HEADER", None):
        assert cd.BACKLOG_NAME not in cd.root_allowed()
        assert cd.INDEX_NAME in cd.root_allowed()


def test_the_size_warning_can_be_switched_off(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PROSE_CAP_DEFAULT = None` drops the warning entirely."""
    monkeypatch.setattr(cd, "PROSE_CAP_DEFAULT", None)
    monkeypatch.setattr(cd, "PROSE_CAP", {})
    long_body = "".join(f"Sentence {index}.\n\n" for index in range(400))
    valid.write("explanation/why-it-is.md", frontmatter("explanation") + long_body)
    assert valid.run() == ([], [])


def test_the_narration_rule_can_be_switched_off(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`NARRATION_FAILS = ()` leaves narration to review."""
    monkeypatch.setattr(cd, "NARRATION_FAILS", ())
    monkeypatch.setattr(cd, "NARRATION_WARNS", ())
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\nThe node used to be called first.\n",
    )
    assert valid.run() == ([], [])


def test_the_scope_rule_can_be_switched_off(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`SCOPE_FOLDER = None` suits a project with one conventions file."""
    monkeypatch.setattr(cd, "SCOPE_FOLDER", None)
    valid.write("conventions/writing.md", frontmatter("conventions") + "\n# Writing\n")
    assert valid.run()[0] == []


def test_the_category_rule_can_be_switched_off(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`CATEGORY_KEY = None` suits an entry format without the field."""
    monkeypatch.setattr(cd, "CATEGORY_KEY", None)
    valid.write(
        "journal/solutions/logic/a-lesson.md",
        "---\ncategory: somewhere/else\n---\n\n# A lesson\n",
    )
    assert valid.run()[0] == []


def test_the_allowlist_downgrades_a_failure_to_a_warning(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The migration escape hatch: land the gate, then empty the allowlist."""
    valid.write("legacy/old.md", "# no frontmatter, unknown folder\n")
    assert valid.run()[0], "the fixture must fail before the allowlist is applied"

    monkeypatch.setattr(cd, "ALLOWLIST", ("docs/legacy/**",))
    failures, warnings = valid.run()
    assert failures == []
    assert any("unknown folder" in message for message in warnings)


def test_the_allowlist_does_not_cover_the_rest_of_the_tree(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An allowlisted folder must not silence the maintained tree."""
    monkeypatch.setattr(cd, "ALLOWLIST", ("docs/legacy/**",))
    valid.write("reference/a-contract.md", "# no frontmatter\n")
    assert "frontmatter" in valid.failures()


# --------------------------------------------------------------------------
# One hostile tree, carrying every shape at once. Delete a rule and the
# parametrised test below names the rule that stopped firing.


HOSTILE_EXPECTATIONS = {
    "loose file at the root": "a .txt at the docs root",
    "unknown folder": "a folder outside the taxonomy",
    "missing `title`": "an empty frontmatter value",
    "invalid status": "a YAML-boolean status",
    "does not match its folder": "a type/folder mismatch",
    "broken link": "a link that does not resolve",
    "broken anchor": "a fragment that does not resolve",
    "kebab-case": "a non-kebab filename",
    "NNNN-with-dashes": "an unnumbered ADR",
    "is a backlog": "a Future work section",
    "incident narration": "narration in a reference doc",
    "filler phrase": "a banned opener",
    "is French": "prose in the wrong language",
    "not listed in": "a doc missing from the index",
    "must open with a `Scope:` line": "a conventions file with no scope",
    "is not its folder": "a journal category naming the old path",
    "symlinked folder": "a symlinked quadrant",
    "unexpected `.txt`": "a non-doc file inside a quadrant",
    "missing the generated header": "a hand-edited backlog mirror",
}


@pytest.fixture
def hostile(tree: Tree, tmp_path: Path) -> Tree:
    """Return a tree carrying one instance of every rejectable shape."""
    tree.write("notes.txt", "a loose file\n")
    tree.write("agent-design/x.md", "# an unknown folder\n")
    tree.write("reference/notes.txt", "a non-doc file in a quadrant\n")
    tree.write(
        "reference/Not_Kebab.md",
        "---\ntitle:\ntype: explanation\naudience: [agent]\nstatus: no\n"
        f"stale_after: {TOMORROW}\n---\n\n"
        "It is worth mentioning that the node used to be called first.\n\n"
        "## Future work\n\n- TODO: the rest\n\n"
        "See [gone](nowhere.md) and [bad](../how-to/do-a-thing.md#no-such-heading).\n",
    )
    tree.write(
        "how-to/do-a-thing.md",
        frontmatter("how-to") + "\n# Do a thing\n\nLe noeud est appele dans le "
        "graphe pour cela.\n",
    )
    tree.write("conventions/writing.md", frontmatter("conventions") + "\n# Writing\n")
    tree.write(
        "journal/solutions/logic/a-lesson.md",
        "---\ncategory: docs/solutions/logic\n---\n\n# A lesson\n",
    )
    tree.write("journal/decisions/why-postgres.md", "# Why Postgres\n")
    tree.write("BACKLOG.md", "# Backlog\n\n- typed by hand\n")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "smuggled.md").write_text("# smuggled\n", encoding="utf-8")
    (tree.docs / "sneaky").symlink_to(outside, target_is_directory=True)
    tree.index()  # an empty index, so every maintained doc is unlisted
    return tree


def test_the_hostile_tree_fails(hostile: Tree) -> None:
    """It exited 0 once. That is the defect this test exists to prevent."""
    assert hostile.run()[0]


@pytest.mark.parametrize(
    ("fragment", "description"), sorted(HOSTILE_EXPECTATIONS.items())
)
def test_the_hostile_tree_names_every_rule(
    hostile: Tree, fragment: str, description: str
) -> None:
    """One case per rule, so a deleted rule fails a test that names it."""
    assert fragment in hostile.failures(), f"nothing caught {description}"


def test_the_gate_exits_non_zero_on_the_hostile_tree(hostile: Tree) -> None:
    """The exit code is the contract pre-commit and CI actually read."""
    assert cd.main() == 1


def test_the_gate_exits_zero_on_a_valid_tree(valid: Tree) -> None:
    """The other direction, which is what makes the first one mean anything."""
    assert cd.main() == 0


# --------------------------------------------------------------------------
# The templates must pass the gate they ship with. Nothing checked this, which
# is how three of them came to claim rules the code did not have.

TEMPLATES = Path(__file__).resolve().parent.parent / "references" / "templates"
TEMPLATE_DEST = {
    "docs-readme.md": "README.md",
    "conventions-documentation.md": "conventions/documentation.md",
    "solutions-readme.md": "journal/solutions/README.md",
    "decisions-readme.md": "journal/decisions/README.md",
}


def strip_placeholders(text: str) -> str:
    """Delete every `{{...}}` block, as an adopter with no such thing does.

    Deleting rather than unwrapping is the harder test: what remains is the
    unconditional template text, so any link a template ships outside a
    placeholder has to resolve on its own.
    """
    for _ in range(8):
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    return re.sub(r"stale_after:.*", f"stale_after: {TOMORROW}", text)


@pytest.mark.skipif(
    not TEMPLATES.is_dir(), reason="the templates ship with the skill, not the project"
)
def test_the_shipped_templates_pass_the_gate(tree: Tree) -> None:
    """Materialise every template at its documented destination, then run."""
    for quadrant in cd.MAINTAINED:
        (tree.docs / quadrant).mkdir(parents=True, exist_ok=True)
    for name, target in TEMPLATE_DEST.items():
        source = (TEMPLATES / name).read_text(encoding="utf-8")
        tree.write(target, strip_placeholders(source))
    written = tree.docs / "README.md"
    written.write_text(
        written.read_text(encoding="utf-8")
        + "\n- [conventions/documentation.md](conventions/documentation.md)\n",
        encoding="utf-8",
    )
    failures, _ = tree.run()
    assert failures == []


def test_the_tracker_only_configuration_rejects_a_mirror(
    valid: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The tracker-only configuration: a `BACKLOG.md` becomes a loose root file."""
    monkeypatch.setattr(cd, "GENERATED_BACKLOG_HEADER", None)
    valid.write("BACKLOG.md", "# a mirror nobody refreshes\n")
    assert "loose file at the root" in valid.failures()


def test_an_unresolved_template_placeholder_fails(valid: Tree) -> None:
    """A `{{PICK ONE ...}}` block left in a shipped doc is not content."""
    valid.write(
        "conventions/writing.md",
        frontmatter("conventions")
        + "\n**Scope: docs prose.**\n\n{{PICK ONE - with a mirror: ... without: ...}}\n",
    )
    assert "unresolved template placeholder" in valid.failures()


def test_an_unresolved_placeholder_in_the_journal_fails(valid: Tree) -> None:
    """Two of the templates land in `journal/`, so the rule reaches there too."""
    valid.write(
        "journal/solutions/logic/a-lesson.md", "# A lesson\n\n{{the category list}}\n"
    )
    assert "unresolved template placeholder" in valid.failures()


def test_a_placeholder_inside_a_code_fence_passes(valid: Tree) -> None:
    """Jinja, Handlebars and Helm templates are legitimate content in a fence."""
    valid.write(
        "reference/a-contract.md",
        frontmatter("reference") + "\n```yaml\nname: {{ .Release.Name }}\n```\n",
    )
    assert valid.run()[0] == []
