from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID = "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
INVALID = "tests/fixtures/providers/capabilities/invalid/network_enabled.json"


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
