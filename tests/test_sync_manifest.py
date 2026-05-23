from __future__ import annotations

import copy
import json
from pathlib import Path

from aios.status import SEVERITY_ERROR, STATUS_PASS
from aios.sync.manifest import load_manifest, validate_manifest_data


FIXTURES = Path(__file__).parent / "fixtures" / "sync" / "manifests"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def issue_codes(data: dict) -> list[str]:
    result = validate_manifest_data(data)
    return [issue.code for issue in result.issues if issue.severity == SEVERITY_ERROR]


def test_valid_whole_file_manifest() -> None:
    result = load_manifest(FIXTURES / "valid_whole_file.json")

    assert result.status == STATUS_PASS
    assert result.manifest is not None
    assert result.manifest.managed_entries[0].sync_mode == "whole-file"


def test_valid_managed_block_manifest() -> None:
    result = load_manifest(FIXTURES / "valid_managed_block.json")

    assert result.status == STATUS_PASS
    assert result.manifest is not None
    assert result.manifest.managed_entries[0].marker is not None


def test_valid_mixed_boundary_manifest() -> None:
    result = load_manifest(FIXTURES / "valid_mixed_boundary.json")

    assert result.status == STATUS_PASS
    assert result.manifest is not None
    assert result.manifest.managed_entries[0].sync_mode == "mixed-boundary"


def test_missing_schema_version_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    del data["schema_version"]

    assert "missing_required_field" in issue_codes(data)


def test_unsupported_schema_version_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["schema_version"] = "aios.sync_manifest.v999"

    assert "unsupported_schema_version" in issue_codes(data)


def test_missing_managed_entries_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    del data["managed_entries"]

    assert "missing_required_field" in issue_codes(data)


def test_invalid_ownership_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["ownership"] = "project-owned"

    assert "invalid_ownership" in issue_codes(data)


def test_invalid_sync_mode_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["sync_mode"] = "observe-only"

    assert "invalid_sync_mode" in issue_codes(data)


def test_invalid_hash_format_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["source_hash"] = "SHA256:ABC"

    assert "invalid_hash_format" in issue_codes(data)


def test_parent_traversal_path_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["source_path"] = ".ai/../AGENTS.md"

    assert "parent_traversal_path" in issue_codes(data)


def test_absolute_path_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["target_path"] = "C:/tmp/AGENTS.md"

    assert "absolute_path" in issue_codes(data)


def test_duplicate_entry_id_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"].append(copy.deepcopy(data["managed_entries"][0]))

    assert "duplicate_entry_id" in issue_codes(data)


def test_marker_entry_id_mismatch_is_error() -> None:
    data = load_fixture("valid_managed_block.json")
    data["managed_entries"][0]["marker"]["entry_id"] = "other_entry"

    assert "marker_entry_id_mismatch" in issue_codes(data)


def test_marker_required_for_managed_block() -> None:
    data = load_fixture("valid_managed_block.json")
    del data["managed_entries"][0]["marker"]

    assert "missing_marker_metadata" in issue_codes(data)


def test_marker_for_whole_file_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["marker"] = {
        "marker_version": "0",
        "marker_style": "markdown-html-comment",
        "entry_id": data["managed_entries"][0]["entry_id"],
    }

    assert "unexpected_marker_metadata" in issue_codes(data)


def test_target_hash_null_is_error() -> None:
    data = load_fixture("valid_whole_file.json")
    data["managed_entries"][0]["target_hash"] = None

    assert "target_hash_null" in issue_codes(data)


def test_manifest_version_alias_is_warning() -> None:
    data = load_fixture("valid_whole_file.json")
    data["manifest_version"] = data["schema_version"]

    result = validate_manifest_data(data)

    assert result.status == "warn"
    assert [issue.code for issue in result.warnings] == ["manifest_version_alias"]
