from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRACES = "tests/fixtures/providers/traces"
VALID = f"{TRACES}/valid/whole_file_trace.json"
INVALID = f"{TRACES}/invalid/invalid_provider_mode.json"
INVALID_FAILURE = f"{TRACES}/invalid/invalid_failure_code.json"
PROVIDER_CAPABILITY = "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
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


def test_valid_provider_execution_trace_native_json_pass() -> None:
    completed, data = json_cli("validate", VALID, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "provider-execution-trace"
    assert data["target"]["path"] == VALID
    assert data["summary"]["errors"] == 0

    checked = next(result for result in data["results"] if result["code"] == "provider_execution_trace_checked")
    assert checked["validator"] == "provider-execution-trace"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["details"]["provider_id"] == "aios.mock.preview.fixture"
    assert checked["details"]["provider_version"] == "0.1.0"
    assert checked["details"]["provider_mode"] == "fixture-mock"
    assert checked["details"]["deterministic_execution"] is True
    assert checked["details"]["no_write_confirmed"] is True
    assert checked["details"]["network_disabled"] is True
    assert checked["details"]["mutation_performed"] is False
    assert checked["details"]["provider_execution"] is False
    assert checked["details"]["sandbox_execution"] is False


def test_invalid_provider_execution_trace_native_json_fail() -> None:
    completed, data = json_cli("validate", INVALID, "--json")

    assert completed.returncode == 1
    assert data["status"] == "fail"
    assert data["target"]["kind"] == "provider-execution-trace"
    assert data["summary"]["errors"] >= 1

    error = next(result for result in data["results"] if result["code"] == "invalid_provider_mode")
    assert error["validator"] == "provider-execution-trace"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "provider_mode"
    assert error["details"]["provider_mode"] == "real-provider"
    assert error["details"]["provider_execution"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["mutation_performed"] is False
    assert not any(result["code"] == "provider_execution_trace_checked" for result in data["results"])


def test_invalid_trace_preserves_failure_and_unavailable_metadata() -> None:
    completed, data = json_cli("validate", INVALID_FAILURE, "--json")

    assert completed.returncode == 1
    error = next(result for result in data["results"] if result["code"] == "invalid_failure_code")
    assert error["details"]["failure_code"] == "provider-random-failure"
    assert error["details"]["unavailable_reason"] == "provider-output-invalid"
    assert error["details"]["provider_execution"] is False
    assert error["details"]["sandbox_execution"] is False
    assert error["details"]["mutation_performed"] is False


def test_trace_shaped_invalid_schema_is_detected_and_fails(tmp_path: Path) -> None:
    path = tmp_path / "trace_invalid_schema.json"
    data = json.loads((ROOT / VALID).read_text(encoding="utf-8"))
    data["schema_version"] = "aios.provider_execution_trace.v9"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    completed, result = json_cli("validate", str(path), "--json")

    assert completed.returncode == 1
    assert result["target"]["kind"] == "provider-execution-trace"
    assert any(item["code"] == "unsupported_schema_version" for item in result["results"])


def test_unrelated_json_is_not_provider_execution_trace() -> None:
    completed, data = json_cli("validate", UNRELATED_JSON, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "provider-execution-trace" for result in data["results"])
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])


def test_existing_target_detection_priority_is_preserved() -> None:
    provider_completed, provider_data = json_cli("validate", PROVIDER_CAPABILITY, "--json")
    sync_completed, sync_data = json_cli("validate", SYNC_MANIFEST, "--json")
    replay_completed, replay_data = json_cli("validate", REPLAY_MANIFEST, "--json", "--replay-compare", "fixture")

    assert provider_completed.returncode == 0
    assert provider_data["target"]["kind"] == "provider-capability"
    assert any(result["code"] == "provider_capability_checked" for result in provider_data["results"])

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
