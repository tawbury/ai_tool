from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = "tests/fixtures/sync/manifests"


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "aios", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_json(path: str) -> dict:
    completed = cli("validate", f"{MANIFESTS}/{path}", "--json")
    return json.loads(completed.stdout)


def test_valid_sync_manifest_targets_pass() -> None:
    for name in ("valid_whole_file.json", "valid_managed_block.json", "valid_mixed_boundary.json"):
        completed = cli("validate", f"{MANIFESTS}/{name}")

        assert completed.returncode == 0
        assert "Status: pass" in completed.stdout
        assert "sync_manifest_checked" in completed.stdout


def test_invalid_sync_manifest_targets_fail_with_expected_codes() -> None:
    cases = {
        "missing_schema_version.json": "missing_required_field",
        "unsupported_schema_version.json": "unsupported_schema_version",
        "invalid_ownership.json": "invalid_ownership",
        "invalid_sync_mode.json": "invalid_sync_mode",
        "invalid_hash_format.json": "invalid_hash_format",
        "path_parent_traversal.json": "parent_traversal_path",
        "duplicate_entry_id.json": "duplicate_entry_id",
        "marker_entry_id_mismatch.json": "marker_entry_id_mismatch",
    }
    for name, code in cases.items():
        data = validate_json(name)

        assert data["status"] == "fail"
        assert any(result["code"] == code for result in data["results"])


def test_sync_manifest_details_include_field_and_entry_id() -> None:
    data = validate_json("marker_entry_id_mismatch.json")
    result = next(item for item in data["results"] if item["code"] == "marker_entry_id_mismatch")

    assert result["details"]["field"] == "managed_entries[0].marker.entry_id"
    assert result["details"]["entry_id"] == "entry_marker_mismatch"


def test_non_manifest_json_is_not_misclassified() -> None:
    completed = cli("validate", f"{MANIFESTS}/non_manifest.json", "--json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])
