from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACES = "tests/fixtures/providers/sandbox_traces"
VALID = f"{TRACES}/valid/successful_sandbox_trace.json"
INVALID = f"{TRACES}/invalid/network_disabled_false.json"
SANDBOX_RESULT = "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json"
SANDBOX_POLICY = "tests/fixtures/providers/sandbox_policies/valid/subprocess_temp_cwd_policy.json"
PROVIDER_CAPABILITY = "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
PROVIDER_TRACE = "tests/fixtures/providers/traces/valid/whole_file_trace.json"
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


def test_valid_sandbox_trace_native_json_pass() -> None:
    completed, data = json_cli("validate", VALID, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "sandbox-trace"
    assert data["target"]["path"] == VALID
    assert data["summary"]["errors"] == 0

    checked = next(result for result in data["results"] if result["code"] == "sandbox_trace_checked")
    assert checked["validator"] == "sandbox-trace"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["details"]["trace_id"] == "trace-sandbox-subprocess-0001"
    assert checked["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert checked["details"]["sandbox_mode"] == "subprocess-temp-cwd"
    assert checked["details"]["provider_mode"] == "subprocess-sandbox"
    assert checked["details"]["status"] == "pass"
    assert checked["details"]["failure_code"] is None
    assert checked["details"]["network_disabled"] is True
    assert checked["details"]["mutation_performed"] is False
    assert checked["details"]["no_write_confirmed"] is True
    assert checked["details"]["sandbox_execution"] is False
    assert checked["details"]["subprocess_execution"] is False
    assert checked["details"]["provider_execution"] is False
    assert checked["details"]["replay_execution"] is False


def test_invalid_sandbox_trace_native_json_fail() -> None:
    completed, data = json_cli("validate", INVALID, "--json")

    assert completed.returncode == 1
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "sandbox-trace"

    error = next(result for result in data["results"] if result["code"] == "network_not_disabled")
    assert error["validator"] == "sandbox-trace"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "network_disabled"
    assert error["details"]["trace_id"] == "trace-sandbox-subprocess-0001"
    assert error["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert error["details"]["network_disabled"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["replay_execution"] is False
    assert error["details"]["mutation_performed"] is False
    assert not any(result["code"] == "sandbox_trace_checked" for result in data["results"])


def test_sandbox_trace_shaped_json_with_invalid_schema_is_detected_and_fails(tmp_path: Path) -> None:
    path = tmp_path / "sandbox_trace_invalid_schema.json"
    data = json.loads((ROOT / VALID).read_text(encoding="utf-8"))
    data["schema_version"] = "aios.sandbox_trace.v9"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed, result = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert result["target"]["kind"] == "sandbox-trace"
    error = next(item for item in result["results"] if item["code"] == "unsupported_schema_version")
    assert error["details"]["field"] == "schema_version"
    assert error["details"]["trace_id"] == "trace-sandbox-subprocess-0001"
    assert error["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["replay_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_sandbox_trace_shaped_json_with_missing_schema_is_detected_and_fails(tmp_path: Path) -> None:
    path = tmp_path / "sandbox_trace_missing_schema.json"
    data = json.loads((ROOT / VALID).read_text(encoding="utf-8"))
    data.pop("schema_version")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed, result = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert result["target"]["kind"] == "sandbox-trace"
    assert any(item["code"] == "missing_required_field" for item in result["results"])
    error = next(item for item in result["results"] if item["code"] == "unsupported_schema_version")
    assert error["details"]["field"] == "schema_version"
    assert error["details"]["trace_id"] == "trace-sandbox-subprocess-0001"
    assert error["details"]["request_id"] == "sandbox-request-success-subprocess-0001"
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["subprocess_execution"] is False
    assert error["details"]["provider_execution"] is False
    assert error["details"]["replay_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_unrelated_json_is_not_sandbox_trace() -> None:
    completed, data = json_cli("validate", UNRELATED_JSON, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "sandbox-trace" for result in data["results"])
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])


def test_existing_target_detection_priority_is_preserved() -> None:
    result_completed, result_data = json_cli("validate", SANDBOX_RESULT, "--json")
    policy_completed, policy_data = json_cli("validate", SANDBOX_POLICY, "--json")
    capability_completed, capability_data = json_cli("validate", PROVIDER_CAPABILITY, "--json")
    trace_completed, trace_data = json_cli("validate", PROVIDER_TRACE, "--json")
    sync_completed, sync_data = json_cli("validate", SYNC_MANIFEST, "--json")
    replay_completed, replay_data = json_cli("validate", REPLAY_MANIFEST, "--json", "--replay-compare", "fixture")

    assert result_completed.returncode == 0
    assert result_data["target"]["kind"] == "sandbox-result"
    assert any(result["code"] == "sandbox_result_checked" for result in result_data["results"])

    assert policy_completed.returncode == 0
    assert policy_data["target"]["kind"] == "sandbox-policy"
    assert any(result["code"] == "sandbox_policy_checked" for result in policy_data["results"])

    assert capability_completed.returncode == 0
    assert capability_data["target"]["kind"] == "provider-capability"
    assert any(result["code"] == "provider_capability_checked" for result in capability_data["results"])

    assert trace_completed.returncode == 0
    assert trace_data["target"]["kind"] == "provider-execution-trace"
    assert any(result["code"] == "provider_execution_trace_checked" for result in trace_data["results"])

    assert sync_completed.returncode == 0
    assert sync_data["target"]["kind"] == "sync-manifest"
    assert any(result["code"] == "sync_manifest_checked" for result in sync_data["results"])

    assert replay_completed.returncode == 0
    assert replay_data["target"]["kind"] == "replay-manifest"
    assert any(result["code"] == "replay_comparison_checked" for result in replay_data["results"])


def test_envelope_v2_without_json_still_exits_2() -> None:
    completed = cli("validate", VALID, "--envelope-v2")

    assert completed.returncode == 2
    assert "--envelope-v2 requires --json" in completed.stderr
