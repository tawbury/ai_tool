from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICIES = "tests/fixtures/providers/sandbox_policies"
VALID = f"{POLICIES}/valid/subprocess_temp_cwd_policy.json"
INVALID = f"{POLICIES}/invalid/network_enabled.json"
UNRELATED_JSON = "tests/fixtures/sync/manifests/non_manifest.json"
PROVIDER_CAPABILITY = "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
PROVIDER_TRACE = "tests/fixtures/providers/traces/valid/whole_file_trace.json"
REPLAY_MANIFEST = "tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json"
SYNC_MANIFEST = "tests/fixtures/sync/manifests/valid_whole_file.json"


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


def test_sandbox_policy_native_json_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sandbox-policy"
    assert data["summary"] == {"errors": 0, "warnings": 0, "info": 2, "results": 2}
    assert [result["code"] for result in data["results"]] == [
        "sandbox_policy_checked",
        "human_review_checks_skipped",
    ]

    checked = data["results"][0]
    assert checked["path"] == VALID
    assert checked["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert checked["details"]["network_disabled"] is True
    assert checked["details"]["deterministic_execution"] is True
    assert checked["details"]["no_write_required"] is True
    assert checked["details"]["sandbox_execution"] is False
    assert checked["details"]["subprocess_execution"] is False
    assert checked["details"]["provider_execution"] is False
    assert checked["details"]["mutation_performed"] is False


def test_sandbox_policy_native_json_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sandbox-policy"
    assert data["summary"]["errors"] == 1

    error = next(result for result in data["results"] if result["code"] == "network_not_disabled")
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "network_disabled"
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_sandbox_policy_envelope_v2_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sandbox-policy"
    assert data["target"]["path"] == VALID
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["subprocess_execution"] is False
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["mutation_performed"] is False
    assert data["meta"]["sandbox_mode"] == "subprocess-temp-cwd"

    payload_result = next(result for result in data["payload"]["results"] if result["code"] == "sandbox_policy_checked")
    assert payload_result["details"]["sandbox_execution"] is False
    assert payload_result["details"]["subprocess_execution"] is False
    assert payload_result["details"]["provider_execution"] is False
    assert payload_result["details"]["mutation_performed"] is False

    message = next(message for message in data["messages"] if message["code"] == "sandbox_policy_checked")
    assert message["severity"] == "info"
    assert message["status"] == "pass"
    assert message["details"]["validator"] == "sandbox-policy"
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["subprocess_execution"] is False
    assert message["details"]["provider_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_sandbox_policy_envelope_v2_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json", "--envelope-v2")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sandbox-policy"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "fail"
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["subprocess_execution"] is False
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["mutation_performed"] is False
    assert data["meta"]["sandbox_mode"] == "fixture-mock"

    message = next(message for message in data["messages"] if message["code"] == "network_not_disabled")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["details"]["validator"] == "sandbox-policy"
    assert message["details"]["field"] == "network_disabled"
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["subprocess_execution"] is False
    assert message["details"]["provider_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_sandbox_policy_shaped_invalid_schema_contract(tmp_path: Path) -> None:
    path = tmp_path / "sandbox_policy_invalid_schema.json"
    data = json.loads((ROOT / VALID).read_text(encoding="utf-8"))
    data["schema_version"] = "aios.sandbox_policy.v9"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed, result = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert result["target"]["kind"] == "sandbox-policy"
    error = next(item for item in result["results"] if item["code"] == "unsupported_schema_version")
    assert error["details"]["field"] == "schema_version"
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_sandbox_policy_unrelated_json_not_misclassified_contract() -> None:
    completed, data = json_cli("validate", UNRELATED_JSON, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "sandbox-policy" for result in data["results"])


def test_existing_target_detection_contracts_remain_unchanged() -> None:
    capability_completed, capability_data = json_cli("validate", PROVIDER_CAPABILITY, "--json")
    trace_completed, trace_data = json_cli("validate", PROVIDER_TRACE, "--json")
    replay_completed, replay_data = json_cli("validate", REPLAY_MANIFEST, "--json", "--replay-compare", "fixture")
    sync_completed, sync_data = json_cli("validate", SYNC_MANIFEST, "--json")

    assert capability_completed.returncode == 0
    assert capability_data["target"]["kind"] == "provider-capability"
    assert trace_completed.returncode == 0
    assert trace_data["target"]["kind"] == "provider-execution-trace"
    assert replay_completed.returncode == 0
    assert replay_data["target"]["kind"] == "replay-manifest"
    assert sync_completed.returncode == 0
    assert sync_data["target"]["kind"] == "sync-manifest"


def test_envelope_v2_without_json_usage_contract() -> None:
    completed = cli("validate", VALID, "--envelope-v2")

    assert completed.returncode == 2
    assert "--envelope-v2 requires --json" in completed.stderr
