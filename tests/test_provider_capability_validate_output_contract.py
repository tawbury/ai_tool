from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID = "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
INVALID = "tests/fixtures/providers/capabilities/invalid/network_enabled.json"
SYNC_MANIFEST = "tests/fixtures/sync/manifests/valid_whole_file.json"
REPLAY_MANIFEST = "tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json"
UNRELATED_JSON = "tests/fixtures/sync/manifests/non_manifest.json"


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


def test_provider_capability_native_json_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "provider-capability"
    assert data["summary"] == {"errors": 0, "warnings": 0, "info": 2, "results": 2}
    assert [result["code"] for result in data["results"]] == [
        "provider_capability_checked",
        "human_review_checks_skipped",
    ]

    checked = data["results"][0]
    assert checked["details"]["provider_execution"] is False
    assert checked["details"]["sandbox_execution"] is False
    assert checked["details"]["mutation_performed"] is False


def test_provider_capability_native_json_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "provider-capability"
    assert data["summary"]["errors"] == 1

    error = next(result for result in data["results"] if result["code"] == "network_policy_not_disabled")
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "network_policy"
    assert error["details"]["provider_execution"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_provider_capability_envelope_v2_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "provider-capability"
    assert data["target"]["path"] == VALID
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["mutation_performed"] is False

    assert any(result["code"] == "provider_capability_checked" for result in data["payload"]["results"])
    message = next(message for message in data["messages"] if message["code"] == "provider_capability_checked")
    assert message["severity"] == "info"
    assert message["status"] == "pass"
    assert message["details"]["validator"] == "provider-capability"
    assert message["details"]["provider_execution"] is False
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_provider_capability_envelope_v2_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json", "--envelope-v2")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "provider-capability"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "fail"
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["mutation_performed"] is False

    message = next(message for message in data["messages"] if message["code"] == "network_policy_not_disabled")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["details"]["validator"] == "provider-capability"
    assert message["details"]["field"] == "network_policy"
    assert message["details"]["provider_execution"] is False
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_provider_capability_shaped_invalid_schema_contract(tmp_path: Path) -> None:
    path = tmp_path / "provider_capability_invalid_schema.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "aios.provider_capability.v9",
                "provider_id": "aios.preview.invalid_schema",
                "provider_version": "0.1.0",
                "deterministic_capable": True,
                "supported_sync_modes": ["whole-file"],
                "hash_policy": "aios.hash_policy.v0",
                "no_write_capable": True,
                "network_policy": "disabled",
                "timeout_policy": {"timeout_ms": 5000},
                "resource_policy": {
                    "max_input_bytes": 262144,
                    "max_output_bytes": 262144,
                },
                "allowed_read_roots": [],
                "provenance_required": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    completed, data = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "provider-capability"
    error = next(result for result in data["results"] if result["code"] == "unsupported_schema_version")
    assert error["details"]["field"] == "schema_version"
    assert error["details"]["provider_execution"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_provider_capability_shaped_missing_schema_contract(tmp_path: Path) -> None:
    path = tmp_path / "provider_capability_missing_schema.json"
    path.write_text(
        json.dumps(
            {
                "provider_id": "aios.preview.missing_schema",
                "provider_version": "0.1.0",
                "deterministic_capable": True,
                "supported_sync_modes": ["whole-file"],
                "hash_policy": "aios.hash_policy.v0",
                "no_write_capable": True,
                "network_policy": "disabled",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    completed, data = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert data["target"]["kind"] == "provider-capability"
    assert any(result["code"] == "missing_required_field" for result in data["results"])
    assert any(result["code"] == "unsupported_schema_version" for result in data["results"])
    assert not any(result["code"] == "provider_capability_checked" for result in data["results"])


def test_unrelated_json_not_misclassified_contract() -> None:
    completed, data = json_cli("validate", UNRELATED_JSON, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "provider-capability" for result in data["results"])
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])


def test_existing_sync_and_replay_target_detection_contract() -> None:
    sync_completed, sync_data = json_cli("validate", SYNC_MANIFEST, "--json")
    replay_completed, replay_data = json_cli("validate", REPLAY_MANIFEST, "--json", "--replay-compare", "fixture")

    assert sync_completed.returncode == 0
    assert sync_data["target"]["kind"] == "sync-manifest"
    assert any(result["code"] == "sync_manifest_checked" for result in sync_data["results"])

    assert replay_completed.returncode == 0
    assert replay_data["target"]["kind"] == "replay-manifest"
    assert any(result["code"] == "replay_comparison_checked" for result in replay_data["results"])


def test_envelope_v2_without_json_usage_contract() -> None:
    completed = cli("validate", VALID, "--envelope-v2")

    assert completed.returncode == 2
    assert "--envelope-v2 requires --json" in completed.stderr
