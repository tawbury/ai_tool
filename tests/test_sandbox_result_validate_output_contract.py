from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = "tests/fixtures/providers/sandbox_results"
VALID = f"{RESULTS}/valid/successful_subprocess_result.json"
INVALID = f"{RESULTS}/invalid/network_disabled_false.json"
UNRELATED_JSON = "tests/fixtures/sync/manifests/non_manifest.json"
SANDBOX_POLICY = "tests/fixtures/providers/sandbox_policies/valid/subprocess_temp_cwd_policy.json"
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


def test_sandbox_result_native_json_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sandbox-result"
    assert data["summary"] == {"errors": 0, "warnings": 0, "info": 2, "results": 2}
    assert [result["code"] for result in data["results"]] == [
        "sandbox_result_checked",
        "human_review_checks_skipped",
    ]

    checked = data["results"][0]
    assert checked["validator"] == "sandbox-result"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["path"] == VALID
    assert checked["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert checked["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert checked["details"]["status"] == "pass"
    assert checked["details"]["failure_code"] is None
    assert checked["details"]["trace_id"] == "trace-sandbox-subprocess-0001"
    assert checked["details"]["network_disabled"] is True
    assert checked["details"]["mutation_performed"] is False
    assert checked["details"]["no_write_confirmed"] is True
    assert checked["details"]["sandbox_execution"] is False
    assert checked["details"]["subprocess_execution"] is False
    assert checked["details"]["provider_execution"] is False
    assert checked["details"]["replay_execution"] is False


def test_sandbox_result_native_json_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sandbox-result"
    assert data["summary"]["errors"] == 1

    error = next(result for result in data["results"] if result["code"] == "network_not_disabled")
    assert error["validator"] == "sandbox-result"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["message"] == "network_disabled must be true."
    assert error["path"] == INVALID
    assert error["details"]["field"] == "network_disabled"
    assert error["details"]["sandbox_mode"] == "fixture-mock"
    assert error["details"]["request_id"] == "sandbox-invalid-network-0001"
    assert error["details"]["status"] == "pass"
    assert error["details"]["failure_code"] is None
    assert error["details"]["network_disabled"] is False
    assert error["details"]["mutation_performed"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["replay_execution"] is False
    assert not any(result["code"] == "sandbox_result_checked" for result in data["results"])


def test_sandbox_result_envelope_v2_pass_contract() -> None:
    completed, data = json_cli("validate", VALID, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sandbox-result"
    assert data["target"]["path"] == VALID
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["subprocess_execution"] is False
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["replay_execution"] is False
    assert data["meta"]["mutation_performed"] is False
    assert data["meta"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert data["meta"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert data["meta"]["failure_code"] is None

    payload_result = next(result for result in data["payload"]["results"] if result["code"] == "sandbox_result_checked")
    assert payload_result["validator"] == "sandbox-result"
    assert payload_result["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert payload_result["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert payload_result["details"]["sandbox_execution"] is False
    assert payload_result["details"]["subprocess_execution"] is False
    assert payload_result["details"]["provider_execution"] is False
    assert payload_result["details"]["replay_execution"] is False
    assert payload_result["details"]["mutation_performed"] is False

    message = next(message for message in data["messages"] if message["code"] == "sandbox_result_checked")
    assert message["severity"] == "info"
    assert message["status"] == "pass"
    assert message["path"] == VALID
    assert message["details"]["validator"] == "sandbox-result"
    assert message["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert message["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["subprocess_execution"] is False
    assert message["details"]["provider_execution"] is False
    assert message["details"]["replay_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_sandbox_result_envelope_v2_fail_contract() -> None:
    completed, data = json_cli("validate", INVALID, "--json", "--envelope-v2")

    assert completed.returncode == 1
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sandbox-result"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "fail"
    assert data["meta"]["sandbox_execution"] is False
    assert data["meta"]["subprocess_execution"] is False
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["replay_execution"] is False
    assert data["meta"]["mutation_performed"] is False
    assert data["meta"]["sandbox_mode"] == "fixture-mock"
    assert data["meta"]["request_id"] == "sandbox-invalid-network-0001"
    assert data["meta"]["failure_code"] is None

    payload_result = next(result for result in data["payload"]["results"] if result["code"] == "network_not_disabled")
    assert payload_result["validator"] == "sandbox-result"
    assert payload_result["details"]["field"] == "network_disabled"
    assert payload_result["details"]["sandbox_mode"] == "fixture-mock"
    assert payload_result["details"]["request_id"] == "sandbox-invalid-network-0001"
    assert payload_result["details"]["network_disabled"] is False
    assert payload_result["details"]["sandbox_execution"] is False
    assert payload_result["details"]["subprocess_execution"] is False
    assert payload_result["details"]["provider_execution"] is False
    assert payload_result["details"]["replay_execution"] is False
    assert payload_result["details"]["mutation_performed"] is False

    message = next(message for message in data["messages"] if message["code"] == "network_not_disabled")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["details"]["validator"] == "sandbox-result"
    assert message["details"]["field"] == "network_disabled"
    assert message["details"]["sandbox_mode"] == "fixture-mock"
    assert message["details"]["request_id"] == "sandbox-invalid-network-0001"
    assert message["details"]["sandbox_execution"] is False
    assert message["details"]["subprocess_execution"] is False
    assert message["details"]["provider_execution"] is False
    assert message["details"]["replay_execution"] is False
    assert message["details"]["mutation_performed"] is False


def test_sandbox_result_shaped_invalid_schema_contract(tmp_path: Path) -> None:
    path = tmp_path / "sandbox_result_invalid_schema.json"
    data = json.loads((ROOT / VALID).read_text(encoding="utf-8"))
    data["schema_version"] = "aios.sandbox_execution_result.v9"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed, result = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert result["target"]["kind"] == "sandbox-result"
    error = next(item for item in result["results"] if item["code"] == "unsupported_schema_version")
    assert error["validator"] == "sandbox-result"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "schema_version"
    assert error["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert error["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["replay_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_sandbox_result_unrelated_json_not_misclassified_contract() -> None:
    completed, data = json_cli("validate", UNRELATED_JSON, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "sandbox-result" for result in data["results"])
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])


def test_existing_target_detection_contracts_remain_unchanged() -> None:
    policy_completed, policy_data = json_cli("validate", SANDBOX_POLICY, "--json")
    capability_completed, capability_data = json_cli("validate", PROVIDER_CAPABILITY, "--json")
    trace_completed, trace_data = json_cli("validate", PROVIDER_TRACE, "--json")
    replay_completed, replay_data = json_cli("validate", REPLAY_MANIFEST, "--json", "--replay-compare", "fixture")
    sync_completed, sync_data = json_cli("validate", SYNC_MANIFEST, "--json")

    assert policy_completed.returncode == 0
    assert policy_data["target"]["kind"] == "sandbox-policy"
    assert any(result["code"] == "sandbox_policy_checked" for result in policy_data["results"])
    assert capability_completed.returncode == 0
    assert capability_data["target"]["kind"] == "provider-capability"
    assert any(result["code"] == "provider_capability_checked" for result in capability_data["results"])
    assert trace_completed.returncode == 0
    assert trace_data["target"]["kind"] == "provider-execution-trace"
    assert any(result["code"] == "provider_execution_trace_checked" for result in trace_data["results"])
    assert replay_completed.returncode == 0
    assert replay_data["target"]["kind"] == "replay-manifest"
    assert any(result["code"] == "replay_comparison_checked" for result in replay_data["results"])
    assert sync_completed.returncode == 0
    assert sync_data["target"]["kind"] == "sync-manifest"
    assert any(result["code"] == "sync_manifest_checked" for result in sync_data["results"])


def test_envelope_v2_without_json_usage_contract() -> None:
    completed = cli("validate", VALID, "--envelope-v2")

    assert completed.returncode == 2
    assert "--envelope-v2 requires --json" in completed.stderr
