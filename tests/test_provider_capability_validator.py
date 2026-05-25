from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from aios.providers.capability import (
    ALLOWED_SYNC_MODES,
    PROVIDER_CAPABILITY_SCHEMA_VERSION,
    PROVIDER_HASH_POLICY,
    validate_provider_capability_data,
)


ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ROOT / "tests" / "fixtures" / "providers" / "capabilities"
VALID = CAPABILITIES / "valid"
INVALID = CAPABILITIES / "invalid"
EDGE_CASES = CAPABILITIES / "edge_cases"

INVALID_FIXTURES = {
    "unsupported_schema_version.json": "unsupported_schema_version",
    "invalid_sync_mode.json": "invalid_sync_mode",
    "missing_provider_version.json": "missing_required_field",
    "network_enabled.json": "network_policy_not_disabled",
    "no_write_false.json": "no_write_not_true",
    "timeout_invalid.json": "invalid_timeout_policy",
    "duplicate_sync_mode.json": "duplicate_sync_mode",
    "malformed_resource_policy.json": "invalid_resource_policy",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_codes(data: Any) -> set[str]:
    return {issue.code for issue in validate_provider_capability_data(data).issues}


def valid_capability() -> dict[str, Any]:
    return load(VALID / "deterministic_fixture_provider.json")


def test_provider_capability_constants_match_contract() -> None:
    assert PROVIDER_CAPABILITY_SCHEMA_VERSION == "aios.provider_capability.v0"
    assert PROVIDER_HASH_POLICY == "aios.hash_policy.v0"
    assert ALLOWED_SYNC_MODES == frozenset({"whole-file", "managed-block", "mixed-boundary"})


def test_valid_and_edge_provider_capability_fixtures_produce_no_errors() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(EDGE_CASES.glob("*.json")):
        result = validate_provider_capability_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_invalid_provider_capability_fixtures_return_expected_issue_codes() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        result = validate_provider_capability_data(load(INVALID / name))

        assert result.status == "fail", name
        assert expected_code in {issue.code for issue in result.errors}, (name, result.issues)


def test_provider_capability_must_be_object() -> None:
    assert "provider_capability_not_object" in issue_codes([])


def test_unsupported_schema_version() -> None:
    data = valid_capability()
    data["schema_version"] = "aios.provider_capability.v9"

    assert "unsupported_schema_version" in issue_codes(data)


def test_missing_required_field() -> None:
    data = valid_capability()
    del data["provider_id"]

    assert "missing_required_field" in issue_codes(data)


def test_invalid_provider_id_and_version() -> None:
    data = valid_capability()
    data["provider_id"] = ""
    data["provider_version"] = " "

    codes = issue_codes(data)
    assert "invalid_provider_id" in codes
    assert "invalid_provider_version" in codes


def test_deterministic_false() -> None:
    data = valid_capability()
    data["deterministic_capable"] = False

    assert "deterministic_not_true" in issue_codes(data)


def test_duplicate_sync_mode() -> None:
    data = valid_capability()
    data["supported_sync_modes"] = ["whole-file", "whole-file"]

    assert "duplicate_sync_mode" in issue_codes(data)


def test_invalid_sync_mode() -> None:
    data = valid_capability()
    data["supported_sync_modes"] = ["whole-file", "repository-wide"]

    assert "invalid_sync_mode" in issue_codes(data)


def test_invalid_hash_policy() -> None:
    data = valid_capability()
    data["hash_policy"] = "aios.hash_policy.normalized"

    assert "invalid_hash_policy" in issue_codes(data)


def test_network_enabled() -> None:
    data = valid_capability()
    data["network_policy"] = "enabled"

    assert "network_policy_not_disabled" in issue_codes(data)


def test_no_write_false() -> None:
    data = valid_capability()
    data["no_write_capable"] = False

    assert "no_write_not_true" in issue_codes(data)


def test_invalid_timeout() -> None:
    data = valid_capability()
    data["timeout_policy"] = {"timeout_ms": 0}

    assert "invalid_timeout_policy" in issue_codes(data)


def test_invalid_resource_policy() -> None:
    data = valid_capability()
    data["resource_policy"] = {"max_input_bytes": 1, "max_output_bytes": "many"}

    assert "invalid_resource_policy" in issue_codes(data)


def test_unsafe_allowed_read_roots() -> None:
    unsafe_values = [
        ["../outside"],
        ["/absolute"],
        ["C:/absolute"],
        ["nested\\windows"],
        ["nested//empty"],
    ]
    for roots in unsafe_values:
        data = valid_capability()
        data["allowed_read_roots"] = roots

        assert "invalid_allowed_read_roots" in issue_codes(data), roots


def test_provenance_false() -> None:
    data = valid_capability()
    data["provenance_required"] = False

    assert "provenance_not_true" in issue_codes(data)


def test_issue_dict_includes_code_severity_status_message_and_field() -> None:
    data = valid_capability()
    data["network_policy"] = "enabled"
    issue = validate_provider_capability_data(data).errors[0].to_dict()

    assert issue["code"] == "network_policy_not_disabled"
    assert issue["severity"] == "error"
    assert issue["status"] == "fail"
    assert issue["message"]
    assert issue["field"] == "network_policy"


def test_validator_does_not_mutate_input_data() -> None:
    data = valid_capability()
    before = copy.deepcopy(data)

    validate_provider_capability_data(data)

    assert data == before
