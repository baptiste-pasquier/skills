"""Tests for `scripts/check_docs.py`.

The point of these tests is that the real `docs/` tree passes, and that each
individual rule actually rejects the shape it claims to reject. A structural
gate nobody has seen fail is indistinguishable from no gate.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from scripts.check_docs import (
    check_docs,
    check_expiry,
    check_frontmatter,
    check_prose,
    opens_with_scope,
    prose_lines,
    split_frontmatter,
)

GOOD_FRONTMATTER = {
    "title": "A doc",
    "type": "reference",
    "audience": ["agent"],
    "status": "stable",
    "stale_after": dt.date.today() + dt.timedelta(days=30),
}


def messages(problems: list) -> str:
    """Return every problem message joined, for substring assertions."""
    return " | ".join(problem.message for problem in problems)


def test_the_real_docs_tree_has_no_failures() -> None:
    """The committed `docs/` tree passes every gate."""
    failures = [problem for problem in check_docs() if not problem.warning]
    assert failures == [], messages(failures)


def test_type_must_match_its_folder() -> None:
    """A doc whose `type` disagrees with its folder is rejected."""
    meta = GOOD_FRONTMATTER | {"type": "explanation"}
    problems = check_frontmatter(Path("docs/reference/x.md"), meta, "reference")
    assert "does not match its folder" in messages(problems)


def test_frontmatter_is_required() -> None:
    """A doc with no frontmatter is rejected."""
    problems = check_frontmatter(Path("docs/reference/x.md"), None, "reference")
    assert "missing or unparseable" in messages(problems)


@pytest.mark.parametrize("key", ["title", "type", "audience", "status", "stale_after"])
def test_every_frontmatter_key_is_required(key: str) -> None:
    """Each required frontmatter key is reported when absent."""
    meta = {name: value for name, value in GOOD_FRONTMATTER.items() if name != key}
    problems = check_frontmatter(Path("docs/reference/x.md"), meta, "reference")
    assert f"missing `{key}`" in messages(problems)


def test_a_passed_expiry_fails() -> None:
    """`stale_after` in the past fails, so staleness announces itself."""
    meta = GOOD_FRONTMATTER | {"stale_after": dt.date.today() - dt.timedelta(days=1)}
    problems = check_frontmatter(Path("docs/reference/x.md"), meta, "reference")
    assert "has passed" in messages(problems)


def test_an_unexpired_doc_passes() -> None:
    """A doc whose expiry is still ahead raises nothing."""
    assert (
        check_frontmatter(Path("docs/reference/x.md"), GOOD_FRONTMATTER, "reference")
        == []
    )


def test_french_prose_fails() -> None:
    """Several French function words on one line is called French."""
    body = "Le modèle ne doit pas écrire cette liste dans la réponse du tour.\n"
    problems = check_prose(Path("docs/reference/x.md"), body, "reference")
    assert "is French" in messages(problems)


def test_english_prose_with_one_french_looking_word_passes() -> None:
    """One borrowed word does not make a line French - the check is scored."""
    body = "The rate is quoted with insurance included, plus the notary fees.\n"
    assert check_prose(Path("docs/reference/x.md"), body, "reference") == []


def test_quoted_french_inside_backticks_passes() -> None:
    """Quoted prompt text stays French, and is skipped inside backticks."""
    body = (
        "The prompt carries `ne répète pas ce que l'utilisateur vient de dire` here.\n"
    )
    assert check_prose(Path("docs/reference/x.md"), body, "reference") == []


def test_incident_narration_fails_in_a_maintained_doc() -> None:
    """A past-tense incident narrative is rejected from `reference/`."""
    body = "The node used to be called before the recap, and that broke ordering.\n"
    problems = check_prose(Path("docs/reference/x.md"), body, "reference")
    assert "incident narration" in messages(problems)


def test_used_to_meaning_used_for_passes() -> None:
    """`used to build` is not incident narration."""
    body = "Field names used to build citations are configured in `config.yaml`.\n"
    assert check_prose(Path("docs/reference/x.md"), body, "reference") == []


def test_incident_narration_is_allowed_in_explanation() -> None:
    """`explanation/` may narrate, so the same text raises no failure there."""
    body = "The node used to be called before the recap.\n"
    problems = check_prose(Path("docs/explanation/x.md"), body, "explanation")
    assert "incident narration" not in messages(problems)


def test_filler_phrases_fail() -> None:
    """A banned filler opener is rejected."""
    body = "It is worth mentioning that the recap is deterministic.\n"
    problems = check_prose(Path("docs/reference/x.md"), body, "reference")
    assert "filler phrase" in messages(problems)


def test_size_is_a_warning_not_a_failure() -> None:
    """Growth is reported, never fatal."""
    body = "".join(
        f"Sentence number {index} carries a fact.\n\n" for index in range(200)
    )
    problems = check_prose(Path("docs/explanation/x.md"), body, "explanation")
    size = [problem for problem in problems if "prose lines" in problem.message]
    assert size
    assert all(problem.warning for problem in size)


def test_prose_lines_ignores_code_tables_and_headings() -> None:
    """Only prose counts toward the size guideline."""
    body = (
        "# Title\n\n| a | b |\n| - | - |\n\n```python\nx = 1\ny = 2\n```\n\nOne line.\n"
    )
    assert prose_lines(body) == 1


def test_split_frontmatter_returns_metadata_and_body() -> None:
    """The frontmatter block is parsed and separated from the body."""
    meta, body = split_frontmatter(
        "---\ntitle: A\ntype: reference\n---\n\nBody here.\n"
    )
    assert meta == {"title": "A", "type": "reference"}
    assert body.strip() == "Body here."


def test_split_frontmatter_handles_a_doc_without_any() -> None:
    """A doc with no frontmatter returns `None` and the whole text."""
    meta, body = split_frontmatter("# Just a heading\n")
    assert meta is None
    assert body == "# Just a heading\n"


def test_a_yaml_timestamp_expiry_does_not_crash() -> None:
    """`stale_after: 2027-03-02 00:00` parses as a datetime, which subclasses date."""
    problems = check_expiry(Path("docs/reference/x.md"), dt.datetime(2020, 1, 1))
    assert "has passed" in messages(problems)


def test_expiry_is_a_warning_not_a_failure() -> None:
    """A passed expiry must not redden a PR that did not touch the doc."""
    problems = check_expiry(Path("docs/reference/x.md"), dt.date(2020, 1, 1))
    assert problems
    assert all(problem.warning for problem in problems)


def test_a_non_date_expiry_is_reported() -> None:
    """A `stale_after` that is not a date at all is still rejected."""
    problems = check_expiry(Path("docs/reference/x.md"), "soon")
    assert "not an ISO date" in messages(problems)


def test_an_indented_code_fence_is_skipped() -> None:
    """A fence nested in a list item is still a fence, so its French is quoted."""
    body = (
        "Steps:\n\n1. Run this:\n\n  ```\n"
        "  Le modèle ne doit pas écrire cette liste dans la réponse du tour.\n"
        "  ```\n"
    )
    assert check_prose(Path("docs/reference/x.md"), body, "reference") == []


def test_prose_lines_ignores_an_indented_fence() -> None:
    """An indented fence's contents do not count toward the size guideline."""
    body = "One line.\n\n  ```\n  x = 1\n  y = 2\n  ```\n"
    assert prose_lines(body) == 1


def test_scope_must_open_the_conventions_file() -> None:
    """A `Scope:` line buried far down the file does not satisfy the rule."""
    buried = "# Title\n\n" + "Filler paragraph.\n\n" * 5 + "**Scope: late.**\n"
    assert not opens_with_scope(buried)


def test_scope_at_the_top_of_a_conventions_file_passes() -> None:
    """A `Scope:` line in the opening paragraph satisfies the rule."""
    assert opens_with_scope("# Title\n\n**Scope: the prose in `docs/`.**\n")
