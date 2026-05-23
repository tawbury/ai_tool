from __future__ import annotations

from pathlib import Path

from aios.sync.markers import (
    INTEGRITY_ANCHOR_DUPLICATED,
    INTEGRITY_ANCHOR_IN_CODE_FENCE,
    INTEGRITY_ANCHOR_MISSING,
    INTEGRITY_BEGIN_DUPLICATED,
    INTEGRITY_BEGIN_MISSING,
    INTEGRITY_END_DUPLICATED,
    INTEGRITY_END_MISSING,
    INTEGRITY_ENTRY_ID_MISMATCH,
    INTEGRITY_MALFORMED,
    INTEGRITY_NESTED,
    INTEGRITY_VALID,
    INTEGRITY_VERSION_UNSUPPORTED,
    STYLE_HASH,
    STYLE_MARKDOWN,
    STYLE_YAML,
    parse_marker_file,
)


FIXTURES = Path(__file__).parent / "fixtures" / "sync" / "markers"


def parse(relative: str, expected: set[str] | None = None, expected_anchors: set[str] | None = None):
    return parse_marker_file(FIXTURES / relative, expected_entry_ids=expected, expected_anchor_entry_ids=expected_anchors)


def test_valid_markdown_pair_preserves_line_numbers() -> None:
    result = parse("valid/valid_markdown_pair.md")

    assert len(result.blocks) == 1
    block = result.blocks[0]
    assert block.integrity == INTEGRITY_VALID
    assert block.marker_style == STYLE_MARKDOWN
    assert block.entry_id == "entry_markdown"
    assert block.begin_line == 2
    assert block.end_line == 4
    assert block.content_line_start == 3
    assert block.content_line_end == 3


def test_valid_hash_line_pair() -> None:
    result = parse("valid/valid_hash_line_pair.txt")

    assert result.blocks[0].integrity == INTEGRITY_VALID
    assert result.blocks[0].marker_style == STYLE_HASH
    assert result.blocks[0].entry_id == "entry_hash"


def test_valid_yaml_line_pair_classifies_yaml_style_from_file_suffix() -> None:
    result = parse("valid/valid_yaml_line_pair.yaml")

    assert result.blocks[0].integrity == INTEGRITY_VALID
    assert result.blocks[0].marker_style == STYLE_YAML
    assert result.blocks[0].entry_id == "entry_yaml"


def test_multiple_independent_blocks_are_deterministically_ordered() -> None:
    result = parse("valid/multiple_independent_blocks.md")

    assert [block.entry_id for block in result.blocks] == ["entry_a", "entry_b"]
    assert [block.begin_line for block in result.blocks] == [1, 5]


def test_missing_end_marker_classifies_end_missing() -> None:
    result = parse("invalid/missing_end_marker.md")

    assert result.blocks[0].integrity == INTEGRITY_END_MISSING
    assert INTEGRITY_END_MISSING in result.blocks[0].problems


def test_duplicate_begin_marker_classifies_duplicate_and_nested() -> None:
    result = parse("invalid/duplicate_begin_marker.md")

    assert any(block.integrity == INTEGRITY_NESTED for block in result.blocks)
    assert any(INTEGRITY_BEGIN_DUPLICATED in block.problems for block in result.blocks)


def test_duplicate_end_marker_classifies_duplicate() -> None:
    result = parse("invalid/duplicate_end_marker.md")

    assert any(INTEGRITY_END_DUPLICATED in block.problems for block in result.blocks)
    assert any(block.integrity == INTEGRITY_BEGIN_MISSING for block in result.blocks)


def test_nested_marker_classifies_nested_state() -> None:
    result = parse("invalid/nested_marker.md")

    assert any(block.nested for block in result.blocks)
    assert any(block.integrity == INTEGRITY_NESTED for block in result.blocks)


def test_malformed_marker_classifies_malformed() -> None:
    result = parse("invalid/malformed_marker.md")

    assert any(block.integrity == INTEGRITY_MALFORMED for block in result.blocks)


def test_mismatched_entry_id_classifies_mismatch() -> None:
    result = parse("invalid/mismatched_entry_id.md")

    assert result.blocks[0].integrity == INTEGRITY_ENTRY_ID_MISMATCH
    assert INTEGRITY_ENTRY_ID_MISMATCH in result.blocks[0].problems


def test_unsupported_marker_version_classifies_unsupported() -> None:
    result = parse("invalid/unsupported_marker_version.md")

    assert all(block.integrity == INTEGRITY_VERSION_UNSUPPORTED for block in result.blocks)


def test_code_fence_marker_looking_text_is_ignored() -> None:
    result = parse("ignored/fenced_code_marker_ignored.md")

    assert result.blocks == []
    assert result.ignored_code_fence_markers == 2


def test_unmanaged_file_does_not_create_markers() -> None:
    result = parse("ignored/unmanaged_file.md")

    assert result.blocks == []
    assert result.anchors == []


def test_orphan_state_uses_expected_entry_ids() -> None:
    result = parse("valid/valid_markdown_pair.md", expected={"other_entry"})

    assert result.blocks[0].orphan


def test_valid_anchor_is_detected() -> None:
    result = parse("anchors/valid_anchor.md", expected_anchors={"entry_anchor"})

    assert len(result.anchors) == 1
    assert result.anchors[0].integrity == INTEGRITY_VALID
    assert result.anchors[0].line == 2


def test_missing_anchor_is_reported_for_expected_anchor() -> None:
    result = parse("anchors/missing_anchor.md", expected_anchors={"entry_anchor"})

    assert result.anchors[0].integrity == INTEGRITY_ANCHOR_MISSING


def test_duplicate_anchor_is_reported() -> None:
    result = parse("anchors/duplicate_anchor.md", expected_anchors={"entry_anchor"})

    assert len(result.anchors) == 2
    assert all(anchor.integrity == INTEGRITY_ANCHOR_DUPLICATED for anchor in result.anchors)


def test_anchor_inside_code_fence_is_invalid() -> None:
    result = parse("anchors/anchor_inside_code_fence.md", expected_anchors={"entry_anchor"})

    assert result.anchors[0].integrity == INTEGRITY_ANCHOR_IN_CODE_FENCE
    assert result.anchors[0].in_code_fence
