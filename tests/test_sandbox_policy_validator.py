from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from aios.providers.sandbox_policy import (
    ALLOWED_ENV_POLICY_MODE,
    ALLOWED_SANDBOX_MODES,
    SANDBOX_POLICY_SCHEMA_VERSION,
    validate_sandbox_policy_data,
)


ROOT = Path(__file__).resolve().parents[1]
POLICIES = ROOT / "tests" / "fixtures" / "providers" / "sandbox_policies"
VALID = POLICIES / "valid"
INVALID = POLICIES / "invalid"
EDGE = POLICIES / "edge"

INVALID_FIXTURES = {
    "unsupported_sandbox_mode.json": "unsupported_sandbox_mode",
    "zero_timeout.json": "invalid_positive_integer",
    "absolute_read_root.json": "invalid_allowed_read_roots",
    "parent_traversal_output_root.json": "invalid_allowed_output_roots",
    "duplicate_read_root.json": "duplicate_read_root",
    "network_enabled.json": "network_not_disabled",
    "wildcard_env_rule.json": "wildcard_env_rule",
    "malformed_filesystem_policy.json": "invalid_filesystem_policy",
    "null_env_policy.json": "invalid_env_policy",
    "output_root_repo_target.json": "invalid_allowed_output_roots",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_policy() -> dict[str, Any]:
    return load(VALID / "subprocess_temp_cwd_policy.json")


def issue_codes(data: Any) -> set[str]:
    return {issue.code for issue in validate_sandbox_policy_data(data).issues}


def test_sandbox_policy_constants_match_contract() -> None:
    assert SANDBOX_POLICY_SCHEMA_VERSION == "aios.sandbox_policy.v0"
    assert ALLOWED_SANDBOX_MODES == frozenset({"fixture-mock", "subprocess-temp-cwd"})
    assert ALLOWED_ENV_POLICY_MODE == "allowlist"


def test_valid_sandbox_policy_fixtures_produce_no_errors() -> None:
    for path in sorted(VALID.glob("*.json")):
        result = validate_sandbox_policy_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_edge_sandbox_policy_fixtures_produce_no_errors() -> None:
    for path in sorted(EDGE.glob("*.json")):
        result = validate_sandbox_policy_data(load(path))

        assert result.status == "pass", path
        assert result.errors == [], path
        assert result.warnings == [], path


def test_invalid_sandbox_policy_fixtures_return_expected_issue_codes() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        result = validate_sandbox_policy_data(load(INVALID / name))

        assert result.status == "fail", name
        assert expected_code in {issue.code for issue in result.errors}, (name, result.issues)


def test_sandbox_policy_must_be_object() -> None:
    assert "sandbox_policy_not_object" in issue_codes([])


def test_unsupported_schema_version() -> None:
    data = valid_policy()
    data["schema_version"] = "aios.sandbox_policy.v9"

    assert "unsupported_schema_version" in issue_codes(data)


def test_unsupported_sandbox_mode() -> None:
    data = valid_policy()
    data["sandbox_mode"] = "direct-host"

    assert "unsupported_sandbox_mode" in issue_codes(data)


def test_zero_timeout() -> None:
    data = valid_policy()
    data["timeout_ms"] = 0

    assert "invalid_positive_integer" in issue_codes(data)


def test_invalid_integer_limits() -> None:
    for field in ("max_input_bytes", "max_output_bytes", "stdout_limit_bytes", "stderr_limit_bytes"):
        data = valid_policy()
        data[field] = "many"

        assert "invalid_positive_integer" in issue_codes(data), field


def test_absolute_read_root() -> None:
    data = valid_policy()
    data["allowed_read_roots"] = ["C:/tmp/source"]

    assert "invalid_allowed_read_roots" in issue_codes(data)


def test_parent_traversal_output_root() -> None:
    data = valid_policy()
    data["allowed_output_roots"] = ["{sandbox_tmp}/../outputs"]

    assert "invalid_allowed_output_roots" in issue_codes(data)


def test_duplicate_read_roots() -> None:
    data = valid_policy()
    data["allowed_read_roots"] = [".ai", ".ai"]

    assert "duplicate_read_root" in issue_codes(data)


def test_network_enabled() -> None:
    data = valid_policy()
    data["network_disabled"] = False

    assert "network_not_disabled" in issue_codes(data)


def test_deterministic_false() -> None:
    data = valid_policy()
    data["deterministic_execution"] = False

    assert "deterministic_not_true" in issue_codes(data)


def test_no_write_false() -> None:
    data = valid_policy()
    data["no_write_required"] = False

    assert "no_write_not_true" in issue_codes(data)


def test_wildcard_env_rule() -> None:
    data = valid_policy()
    data["env_policy"]["allowed"] = ["*"]

    assert "wildcard_env_rule" in issue_codes(data)


def test_malformed_or_null_env_policy() -> None:
    data = valid_policy()
    data["env_policy"] = None

    assert "invalid_env_policy" in issue_codes(data)

    data = valid_policy()
    data["env_policy"] = {"mode": "inherit", "allowed": [], "forbidden_prefixes": []}

    assert "invalid_env_policy" in issue_codes(data)


def test_malformed_filesystem_policy() -> None:
    data = valid_policy()
    data["filesystem_policy"]["symlink_policy"] = "allow"

    assert "invalid_filesystem_policy" in issue_codes(data)


def test_output_root_repo_target() -> None:
    data = valid_policy()
    data["allowed_output_roots"] = ["src/aios"]

    assert "invalid_allowed_output_roots" in issue_codes(data)


def test_invalid_edge_classification() -> None:
    data = valid_policy()
    data["edge_classification"] = "approved-for-execution"

    assert "invalid_edge_classification" in issue_codes(data)


def test_issue_dict_includes_code_severity_status_message_and_field() -> None:
    data = valid_policy()
    data["network_disabled"] = False
    issue = validate_sandbox_policy_data(data).errors[0].to_dict()

    assert issue["code"] == "network_not_disabled"
    assert issue["severity"] == "error"
    assert issue["status"] == "fail"
    assert issue["message"]
    assert issue["field"] == "network_disabled"


def test_validator_does_not_mutate_input_data() -> None:
    data = valid_policy()
    before = copy.deepcopy(data)

    validate_sandbox_policy_data(data)

    assert data == before
