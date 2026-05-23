from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def json_cli(*args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = cli(*args)
    return completed, json.loads(completed.stdout)


def manifest(name: str) -> str:
    return f"{MANIFESTS}/{name}"


def test_sync_dry_run_native_clean_skip_contract() -> None:
    completed, data = json_cli(
        "sync",
        "--dry-run",
        "--manifest",
        manifest("e2e_clean_skip.json"),
        "--json",
    )

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.sync_dry_run.v0"
    assert data["status"] == "pass"
    assert data["mode"] == "dry-run"
    assert data["manifest_path"] == manifest("e2e_clean_skip.json")
    assert data["summary"]["total"] == 1
    assert data["summary"]["skip"] == 1
    assert data["messages"] == []
    assert data["meta"]["dry_run"] is True
    assert data["meta"]["mutation_performed"] is False
    assert data["meta"]["manifest_schema_version"] == "aios.sync_manifest.v0"

    item = data["results"][0]
    assert item["entry_id"] == "entry_clean_skip"
    assert item["action"] == "skip"
    assert item["severity"] == "informational"
    assert item["drift_state"] == "clean"
    assert item["marker"]["integrity"] == "valid"
    assert item["hashes"]["expected_target_hash"] == item["hashes"]["actual_target_hash"]


def test_sync_dry_run_native_drift_stop_contract() -> None:
    completed, data = json_cli(
        "sync",
        "--dry-run",
        "--manifest",
        manifest("e2e_drift_stop.json"),
        "--json",
    )

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.sync_dry_run.v0"
    assert data["status"] == "fail"
    assert data["summary"]["drift_stop"] == 1
    assert data["summary"]["blocking"] == 1

    item = data["results"][0]
    assert item["action"] == "drift-stop"
    assert item["severity"] == "blocking"
    assert item["stop_reason"] == "target-modified"
    assert item["drift_state"] == "drifted"
    assert item["recovery_hint"]

    assert data["messages"][0]["code"] == "target-modified"
    assert data["messages"][0]["status"] == "fail"


def test_sync_dry_run_envelope_v2_orphan_warning_contract() -> None:
    completed, data = json_cli(
        "sync",
        "--dry-run",
        "--manifest",
        manifest("e2e_orphan_marker.json"),
        "--json",
        "--envelope-v2",
    )

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "sync"
    assert data["status"] == "warn"
    assert data["target"]["kind"] == "sync-manifest"
    assert data["target"]["path"] == manifest("e2e_orphan_marker.json")
    assert data["meta"]["legacy_schema_version"] == "aios.sync_dry_run.v0"
    assert data["meta"]["legacy_status"] == "warn"
    assert data["meta"]["dry_run"] is True
    assert data["meta"]["mutation_performed"] is False

    results = data["payload"]["results"]
    assert [item["action"] for item in results] == ["skip", "orphan-warning"]
    assert any(message["code"] == "orphaned-managed-block" for message in data["messages"])
    assert any(message["status"] == "warn" for message in data["messages"])


def test_validate_sync_manifest_json_contract() -> None:
    completed, data = json_cli("validate", manifest("valid_whole_file.json"), "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sync-manifest"
    assert data["target"]["path"] == manifest("valid_whole_file.json")
    assert data["summary"]["errors"] == 0
    assert data["summary"]["info"] >= 1
    assert any(result["code"] == "sync_manifest_checked" for result in data["results"])

    checked = next(result for result in data["results"] if result["code"] == "sync_manifest_checked")
    assert checked["validator"] == "sync-manifest"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["details"]["schema_version"] == "aios.sync_manifest.v0"


def test_validate_sync_manifest_invalid_json_contract() -> None:
    completed, data = json_cli("validate", manifest("invalid_hash_format.json"), "--json")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sync-manifest"
    assert data["summary"]["errors"] == 1

    error = next(result for result in data["results"] if result["code"] == "invalid_hash_format")
    assert error["validator"] == "sync-manifest"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["path"] == manifest("invalid_hash_format.json")
    assert error["details"]["field"] == "managed_entries[0].source_hash"
    assert error["details"]["entry_id"] == "entry_invalid_hash"


def test_validate_sync_manifest_envelope_v2_contract() -> None:
    completed, data = json_cli(
        "validate",
        manifest("invalid_hash_format.json"),
        "--json",
        "--envelope-v2",
    )

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sync-manifest"
    assert data["target"]["path"] == manifest("invalid_hash_format.json")
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "fail"

    assert any(result["code"] == "invalid_hash_format" for result in data["payload"]["results"])
    message = next(message for message in data["messages"] if message["code"] == "invalid_hash_format")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["path"] == manifest("invalid_hash_format.json")
    assert message["details"]["validator"] == "sync-manifest"
    assert message["details"]["field"] == "managed_entries[0].source_hash"
    assert message["details"]["entry_id"] == "entry_invalid_hash"


def test_sync_usage_errors_remain_exit_code_2() -> None:
    cases = [
        ("--dry-run is required", ("sync",)),
        ("--manifest <path> is required", ("sync", "--dry-run")),
        ("--envelope-v2 requires --json", ("sync", "--envelope-v2")),
    ]

    for expected_stderr, args in cases:
        completed = cli(*args)

        assert completed.returncode == 2
        assert expected_stderr in completed.stderr
