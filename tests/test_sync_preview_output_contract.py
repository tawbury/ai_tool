from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = "tests/fixtures/sync/manifests"
PREVIEWS = "tests/fixtures/sync/previews"


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


def sync_preview(manifest_name: str, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    return json_cli(
        "sync",
        "--dry-run",
        "--manifest",
        manifest(manifest_name),
        "--json",
        "--preview-provider",
        "fixture",
        "--preview-fixtures",
        PREVIEWS,
        *extra,
    )


def test_native_whole_file_preview_update_candidate_contract() -> None:
    completed, data = sync_preview("e2e_preview_whole_file_clean.json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.sync_dry_run.v0"
    assert data["status"] == "pass"
    assert data["summary"]["update"] == 1
    assert data["summary"]["skip"] == 0
    assert data["meta"]["preview_provider"] == "fixture"
    assert data["meta"]["preview_policy"] == "read-only-fixture"
    assert data["meta"]["mutation_performed"] is False

    item = data["results"][0]
    assert item["entry_id"] == "preview_whole_file_clean"
    assert item["action"] == "update"
    assert item["severity"] == "informational"
    assert item["sync_mode"] == "whole-file"
    assert item["drift_state"] == "clean"
    assert item["stop_reason"] is None
    assert item["recovery_hint"] is None
    assert item["hashes"]["generated_target_hash"] is not None
    assert item["hashes"]["generated_target_hash"] != item["hashes"]["actual_target_hash"]
    assert item["hashes"]["generated_managed_block_hash"] is None
    assert item["details"]["preview"]["provider"] == "fixture"
    assert item["details"]["preview"]["preview_available"] is True
    assert item["details"]["preview"]["generated_content_kind"] == "whole-file"
    assert item["details"]["preview"]["provenance"]["generated_by"] == "aios.generated_preview.v0"
    assert item["details"]["preview_unavailable_reason"] is None


def test_native_managed_block_preview_update_candidate_contract() -> None:
    completed, data = sync_preview("e2e_clean_skip.json")

    assert completed.returncode == 0
    assert data["summary"]["update"] == 1
    item = data["results"][0]
    assert item["entry_id"] == "entry_clean_skip"
    assert item["action"] == "update"
    assert item["sync_mode"] == "managed-block"
    assert item["marker"]["integrity"] == "valid"
    assert item["hashes"]["generated_managed_block_hash"] is not None
    assert item["hashes"]["generated_managed_block_hash"] != item["hashes"]["actual_managed_block_hash"]
    assert item["hashes"]["generated_target_hash"] is None
    assert item["details"]["preview"]["preview_available"] is True
    assert item["details"]["preview"]["generated_content_kind"] == "managed-block"
    assert item["details"]["preview_unavailable_reason"] is None


def test_native_generated_hash_match_remains_skip_contract() -> None:
    completed, data = sync_preview("e2e_preview_whole_file_match.json")

    assert completed.returncode == 0
    assert data["status"] == "pass"
    assert data["summary"]["update"] == 0
    assert data["summary"]["skip"] == 1
    item = data["results"][0]
    assert item["action"] == "skip"
    assert item["hashes"]["generated_target_hash"] == item["hashes"]["actual_target_hash"]
    assert item["hashes"]["generated_managed_block_hash"] is None
    assert item["details"]["preview"]["preview_available"] is True
    assert item["details"]["preview_unavailable_reason"] is None


def test_native_preview_unavailable_preserves_no_update_contract() -> None:
    completed, data = sync_preview("e2e_preview_unavailable.json")

    assert completed.returncode == 0
    assert data["status"] == "pass"
    assert data["summary"]["update"] == 0
    assert data["summary"]["skip"] == 1
    item = data["results"][0]
    assert item["action"] == "skip"
    assert item["hashes"]["generated_target_hash"] is None
    assert item["hashes"]["generated_managed_block_hash"] is None
    assert item["details"]["preview"]["preview_available"] is False
    assert item["details"]["preview"]["generated_content_kind"] is None
    assert item["details"]["preview_unavailable_reason"] == "adapter-unavailable"


def test_native_drift_stop_precedence_over_preview_contract() -> None:
    completed, data = sync_preview("e2e_drift_stop.json")

    assert completed.returncode == 1
    assert data["status"] == "fail"
    assert data["summary"]["drift_stop"] == 1
    assert data["summary"]["blocking"] == 1
    assert data["meta"]["preview_provider"] == "fixture"
    item = data["results"][0]
    assert item["action"] == "drift-stop"
    assert item["severity"] == "blocking"
    assert item["stop_reason"] == "target-modified"
    assert item["drift_state"] == "drifted"
    assert "preview" not in item["details"]
    assert "preview_unavailable_reason" not in item["details"]


def test_native_marker_conflict_precedence_over_preview_contract() -> None:
    completed, data = sync_preview("e2e_marker_corrupted.json")

    assert completed.returncode == 1
    assert data["status"] == "fail"
    assert data["summary"]["conflict"] == 1
    assert data["summary"]["blocking"] == 1
    item = data["results"][0]
    assert item["action"] == "conflict"
    assert item["severity"] == "blocking"
    assert item["stop_reason"] == "marker-corrupted"
    assert item["marker"]["integrity"] == "entry-id-mismatch"
    assert "preview" not in item["details"]
    assert "preview_unavailable_reason" not in item["details"]


def test_envelope_v2_preview_output_contract() -> None:
    completed, data = sync_preview("e2e_clean_skip.json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "sync"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sync-manifest"
    assert data["target"]["path"] == manifest("e2e_clean_skip.json")
    assert data["meta"]["legacy_schema_version"] == "aios.sync_dry_run.v0"
    assert data["meta"]["preview_provider"] == "fixture"
    assert data["meta"]["preview_policy"] == "read-only-fixture"
    assert data["meta"]["mutation_performed"] is False

    results = data["payload"]["results"]
    assert len(results) == 1
    item = results[0]
    assert item["action"] == "update"
    assert item["hashes"]["generated_managed_block_hash"] is not None
    assert item["hashes"]["generated_target_hash"] is None
    assert item["details"]["preview"]["provider"] == "fixture"
    assert item["details"]["preview"]["preview_available"] is True
    assert item["details"]["preview"]["generated_content_kind"] == "managed-block"
    assert item["details"]["preview_unavailable_reason"] is None


def test_no_preview_clean_skip_output_contract_remains_unchanged() -> None:
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
    assert data["summary"]["update"] == 0
    assert data["summary"]["skip"] == 1
    assert "preview_provider" not in data["meta"]
    assert "preview_policy" not in data["meta"]
    item = data["results"][0]
    assert item["action"] == "skip"
    assert item["hashes"]["generated_target_hash"] is None
    assert item["hashes"]["generated_managed_block_hash"] is None
    assert "preview" not in item["details"]
    assert "preview_unavailable_reason" not in item["details"]


def test_preview_configuration_usage_errors_contract() -> None:
    cases = [
        (
            (
                "sync",
                "--dry-run",
                "--manifest",
                manifest("e2e_clean_skip.json"),
                "--preview-provider",
                "fixture",
            ),
            "--preview-provider fixture requires --preview-fixtures",
        ),
        (
            (
                "sync",
                "--dry-run",
                "--manifest",
                manifest("e2e_clean_skip.json"),
                "--preview-fixtures",
                PREVIEWS,
            ),
            "--preview-fixtures requires --preview-provider fixture",
        ),
        (
            (
                "sync",
                "--dry-run",
                "--manifest",
                manifest("e2e_clean_skip.json"),
                "--preview-provider",
                "adapter",
                "--preview-fixtures",
                PREVIEWS,
            ),
            "unsupported preview provider",
        ),
    ]

    for args, expected in cases:
        completed = cli(*args)

        assert completed.returncode == 2
        assert expected in completed.stderr
