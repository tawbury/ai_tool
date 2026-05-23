from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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


def sync_preview(manifest: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return cli(
        "sync",
        "--dry-run",
        "--manifest",
        f"{MANIFESTS}/{manifest}",
        "--json",
        "--preview-provider",
        "fixture",
        "--preview-fixtures",
        PREVIEWS,
        *extra,
    )


def test_clean_whole_file_generated_differs_is_update() -> None:
    completed = sync_preview("e2e_preview_whole_file_clean.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["status"] == "pass"
    assert data["summary"]["update"] == 1
    assert data["meta"]["preview_provider"] == "fixture"
    assert data["meta"]["preview_policy"] == "read-only-fixture"
    item = data["results"][0]
    assert item["action"] == "update"
    assert item["severity"] == "informational"
    assert item["hashes"]["generated_target_hash"] != item["hashes"]["actual_target_hash"]
    assert item["details"]["preview"]["preview_available"] is True
    assert item["details"]["preview_unavailable_reason"] is None


def test_clean_managed_block_generated_differs_is_update() -> None:
    completed = sync_preview("e2e_clean_skip.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    item = data["results"][0]
    assert item["action"] == "update"
    assert item["hashes"]["generated_managed_block_hash"] != item["hashes"]["actual_managed_block_hash"]
    assert item["details"]["preview"]["generated_content_kind"] == "managed-block"


def test_generated_match_remains_skip() -> None:
    completed = sync_preview("e2e_preview_whole_file_match.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["summary"]["skip"] == 1
    item = data["results"][0]
    assert item["action"] == "skip"
    assert item["hashes"]["generated_target_hash"] == item["hashes"]["actual_target_hash"]
    assert item["details"]["preview"]["preview_available"] is True


def test_drift_stop_still_fails_with_preview_configured() -> None:
    completed = sync_preview("e2e_drift_stop.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 1
    item = data["results"][0]
    assert item["action"] == "drift-stop"
    assert item["stop_reason"] == "target-modified"
    assert "preview" not in item["details"]


def test_marker_conflict_still_fails_with_preview_configured() -> None:
    completed = sync_preview("e2e_marker_corrupted.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 1
    item = data["results"][0]
    assert item["action"] == "conflict"
    assert item["stop_reason"] == "marker-corrupted"
    assert "preview" not in item["details"]


def test_preview_unavailable_preserves_skip_and_no_update() -> None:
    completed = sync_preview("e2e_preview_unavailable.json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["summary"]["update"] == 0
    assert data["summary"]["skip"] == 1
    item = data["results"][0]
    assert item["action"] == "skip"
    assert item["details"]["preview"]["preview_available"] is False
    assert item["details"]["preview_unavailable_reason"] == "adapter-unavailable"


def test_envelope_v2_preserves_preview_metadata() -> None:
    completed = sync_preview("e2e_orphan_marker.json", "--envelope-v2")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "sync"
    assert data["meta"]["preview_provider"] == "fixture"
    assert data["meta"]["preview_policy"] == "read-only-fixture"
    result = data["payload"]["results"][0]
    assert result["details"]["preview"]["preview_available"] is False
    assert result["details"]["preview_unavailable_reason"] == "adapter-unavailable"


def test_no_preview_flags_keep_existing_output_contract() -> None:
    completed = cli("sync", "--dry-run", "--manifest", f"{MANIFESTS}/e2e_clean_skip.json", "--json")
    data = json.loads(completed.stdout)

    assert completed.returncode == 0
    assert data["summary"]["skip"] == 1
    assert data["summary"]["update"] == 0
    assert "preview_provider" not in data["meta"]
    assert "preview" not in data["results"][0]["details"]


def test_preview_config_usage_errors_exit_code_2() -> None:
    cases = [
        (
            ("sync", "--dry-run", "--manifest", f"{MANIFESTS}/e2e_clean_skip.json", "--preview-fixtures", PREVIEWS),
            "--preview-fixtures requires --preview-provider fixture",
        ),
        (
            ("sync", "--dry-run", "--manifest", f"{MANIFESTS}/e2e_clean_skip.json", "--preview-provider", "fixture"),
            "--preview-provider fixture requires --preview-fixtures",
        ),
        (
            (
                "sync",
                "--dry-run",
                "--manifest",
                f"{MANIFESTS}/e2e_clean_skip.json",
                "--preview-provider",
                "real",
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
