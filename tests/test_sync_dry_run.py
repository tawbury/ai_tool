from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from aios.status import STATUS_FAIL, STATUS_PASS, STATUS_WARN
from aios.sync.dry_run import run_sync_dry_run


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "tests" / "fixtures" / "sync" / "manifests"


def run_manifest(name: str):
    return run_sync_dry_run(ROOT, MANIFESTS / name)


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "aios", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_clean_skip_managed_block() -> None:
    result = run_manifest("e2e_clean_skip.json")
    data = result.to_dict()

    assert result.status == STATUS_PASS
    assert data["schema_version"] == "aios.sync_dry_run.v0"
    assert data["results"][0]["action"] == "skip"
    assert data["results"][0]["marker"]["integrity"] == "valid"


def test_whole_file_create_candidate() -> None:
    result = run_manifest("e2e_create_whole_file.json")

    assert result.status == STATUS_PASS
    assert result.results[0].action == "create"
    assert result.results[0].drift_state == "missing"


def test_source_missing_conflict() -> None:
    result = run_manifest("e2e_source_missing.json")

    assert result.status == STATUS_FAIL
    assert result.results[0].action == "conflict"
    assert result.results[0].stop_reason == "source-missing"


def test_marker_missing_conflict() -> None:
    result = run_manifest("e2e_marker_missing.json")

    assert result.status == STATUS_FAIL
    assert result.results[0].stop_reason == "marker-missing"


def test_marker_corrupted_conflict() -> None:
    result = run_manifest("e2e_marker_corrupted.json")

    assert result.status == STATUS_FAIL
    assert result.results[0].action == "conflict"
    assert result.results[0].stop_reason == "marker-corrupted"


def test_drift_stop() -> None:
    result = run_manifest("e2e_drift_stop.json")

    assert result.status == STATUS_FAIL
    assert result.results[0].action == "drift-stop"
    assert result.results[0].stop_reason == "target-modified"


def test_orphan_marker_warning() -> None:
    result = run_manifest("e2e_orphan_marker.json")

    assert result.status == STATUS_WARN
    assert [item.action for item in result.results] == ["skip", "orphan-warning"]
    assert result.results[1].stop_reason == "orphaned-managed-block"


def test_invalid_manifest_schema_fail() -> None:
    result = run_manifest("e2e_invalid_schema.json")

    assert result.status == STATUS_FAIL
    assert result.results == []
    assert result.messages[0].code == "missing_required_field"


def test_cli_json_output_shape() -> None:
    completed = cli("sync", "--dry-run", "--manifest", "tests/fixtures/sync/manifests/e2e_clean_skip.json", "--json")

    assert completed.returncode == 0
    data = json.loads(completed.stdout)
    assert data["schema_version"] == "aios.sync_dry_run.v0"
    assert data["status"] == "pass"
    assert data["summary"]["skip"] == 1


def test_cli_envelope_v2_output_shape() -> None:
    completed = cli(
        "sync",
        "--dry-run",
        "--manifest",
        "tests/fixtures/sync/manifests/e2e_orphan_marker.json",
        "--json",
        "--envelope-v2",
    )

    assert completed.returncode == 0
    data = json.loads(completed.stdout)
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "sync"
    assert data["status"] == "warn"
    assert data["meta"]["legacy_schema_version"] == "aios.sync_dry_run.v0"
    assert data["meta"]["dry_run"] is True
    assert data["payload"]["results"][1]["action"] == "orphan-warning"


def test_cli_without_dry_run_is_usage_error() -> None:
    completed = cli("sync")

    assert completed.returncode == 2
    assert "--dry-run is required" in completed.stderr


def test_cli_dry_run_without_manifest_is_usage_error() -> None:
    completed = cli("sync", "--dry-run")

    assert completed.returncode == 2
    assert "--manifest <path> is required" in completed.stderr


def test_cli_envelope_v2_without_json_is_usage_error() -> None:
    completed = cli("sync", "--envelope-v2")

    assert completed.returncode == 2
    assert "--envelope-v2 requires --json" in completed.stderr
