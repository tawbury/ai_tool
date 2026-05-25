from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICIES = ROOT / "tests" / "fixtures" / "providers" / "sandbox_policies"
VALID = POLICIES / "valid"
INVALID = POLICIES / "invalid"
EDGE = POLICIES / "edge"
INDEX = POLICIES / "sandbox_policy_index.json"

SCHEMA_VERSION = "aios.sandbox_policy.v0"
INDEX_SCHEMA_VERSION = "aios.sandbox_policy_index.v0"
ALLOWED_SANDBOX_MODES = {"fixture-mock", "subprocess-temp-cwd"}
REQUIRED_FIELDS = {
    "schema_version",
    "sandbox_mode",
    "timeout_ms",
    "max_input_bytes",
    "max_output_bytes",
    "stdout_limit_bytes",
    "stderr_limit_bytes",
    "allowed_read_roots",
    "allowed_output_roots",
    "network_disabled",
    "deterministic_execution",
    "no_write_required",
    "env_policy",
    "filesystem_policy",
}
POSITIVE_INTEGER_FIELDS = {
    "timeout_ms",
    "max_input_bytes",
    "max_output_bytes",
    "stdout_limit_bytes",
    "stderr_limit_bytes",
}
VALID_FIXTURES = {
    "fixture_mock_default_policy.json",
    "subprocess_temp_cwd_policy.json",
    "no_read_roots_policy.json",
}
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
EDGE_FIXTURES = {
    "empty_allowed_read_roots.json",
    "max_limit_boundary.json",
    "overlapping_roots.json",
    "minimal_env_allowlist.json",
    "sandbox_tmp_output_root.json",
}
NON_EXECUTION_FLAGS = {
    "sandbox_execution": False,
    "provider_execution": False,
    "subprocess_execution": False,
    "dynamic_loading": False,
    "network_access": False,
    "generated_content_creation": False,
    "mutation_performed": False,
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_sandbox_policy_fixture_inventory_matches_contract() -> None:
    assert {path.name for path in VALID.glob("*.json")} == VALID_FIXTURES
    assert {path.name for path in INVALID.glob("*.json")} == set(INVALID_FIXTURES)
    assert {path.name for path in EDGE.glob("*.json")} == EDGE_FIXTURES

    index = load(INDEX)
    assert index["schema_version"] == INDEX_SCHEMA_VERSION
    for key, expected in NON_EXECUTION_FLAGS.items():
        assert index[key] is expected
    assert set(index["valid"]) == {f"valid/{name}" for name in VALID_FIXTURES}
    assert set(index["invalid"]) == {f"invalid/{name}" for name in INVALID_FIXTURES}
    assert set(index["edge"]) == {f"edge/{name}" for name in EDGE_FIXTURES}


def test_sandbox_policy_index_references_existing_fixtures() -> None:
    index = load(INDEX)

    for group in ("valid", "invalid", "edge"):
        for relative_path in index[group]:
            assert (POLICIES / relative_path).is_file(), relative_path


def test_every_sandbox_policy_fixture_parses() -> None:
    for path in sorted(POLICIES.glob("*/*.json")):
        data = load(path)

        assert isinstance(data, dict), path


def test_valid_sandbox_policy_fixtures_match_contract() -> None:
    for path in sorted(VALID.glob("*.json")):
        data = load(path)

        assert _validate_policy(data, allow_edge=True) == [], path
        _assert_policy_invariants(data, path=path)


def test_edge_sandbox_policy_fixtures_are_explicitly_classified() -> None:
    for path in sorted(EDGE.glob("*.json")):
        data = load(path)
        issues = _validate_policy(data, allow_edge=True)

        assert issues == [], (path, issues)
        assert isinstance(data.get("edge_classification"), str) and data["edge_classification"], path
        _assert_policy_invariants(data, path=path)


def test_invalid_sandbox_policy_fixtures_fail_expected_contract_assertion() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        data = load(INVALID / name)
        issues = _validate_policy(data, allow_edge=False)

        assert expected_code in issues, (name, issues)


def test_sandbox_policy_tests_are_fixture_only() -> None:
    index = load(INDEX)

    assert index["sandbox_execution"] is False
    assert index["provider_execution"] is False
    assert index["subprocess_execution"] is False
    assert index["dynamic_loading"] is False
    assert index["network_access"] is False
    assert index["generated_content_creation"] is False
    assert index["mutation_performed"] is False


def _assert_policy_invariants(data: dict[str, Any], *, path: Path) -> None:
    assert REQUIRED_FIELDS <= data.keys(), path
    assert data["schema_version"] == SCHEMA_VERSION, path
    assert data["sandbox_mode"] in ALLOWED_SANDBOX_MODES, path
    for field in POSITIVE_INTEGER_FIELDS:
        assert _positive_int(data[field]), (path, field)
    assert data["network_disabled"] is True, path
    assert data["deterministic_execution"] is True, path
    assert data["no_write_required"] is True, path
    assert _valid_env_policy(data["env_policy"]), path
    assert _valid_filesystem_policy(data["filesystem_policy"]), path
    assert _valid_read_roots(data["allowed_read_roots"], allow_edge=True), path
    assert _valid_output_roots(data["allowed_output_roots"]), path


def _validate_policy(data: dict[str, Any], *, allow_edge: bool) -> list[str]:
    issues: list[str] = []
    if not REQUIRED_FIELDS <= data.keys():
        issues.append("missing_required_field")
    if data.get("schema_version") != SCHEMA_VERSION:
        issues.append("unsupported_schema_version")
    if data.get("sandbox_mode") not in ALLOWED_SANDBOX_MODES:
        issues.append("unsupported_sandbox_mode")

    for field in POSITIVE_INTEGER_FIELDS:
        if not _positive_int(data.get(field)):
            issues.append("invalid_positive_integer")

    allowed_read_roots = data.get("allowed_read_roots")
    if not _valid_read_roots(allowed_read_roots, allow_edge=allow_edge):
        issues.append("invalid_allowed_read_roots")
    if isinstance(allowed_read_roots, list) and len(allowed_read_roots) != len(set(allowed_read_roots)):
        issues.append("duplicate_read_root")

    if not _valid_output_roots(data.get("allowed_output_roots")):
        issues.append("invalid_allowed_output_roots")
    if data.get("network_disabled") is not True:
        issues.append("network_not_disabled")
    if data.get("deterministic_execution") is not True:
        issues.append("deterministic_not_true")
    if data.get("no_write_required") is not True:
        issues.append("no_write_not_true")
    env_policy = data.get("env_policy")
    if not _valid_env_policy(env_policy):
        issues.append("invalid_env_policy")
    if isinstance(env_policy, dict) and "*" in env_policy.get("allowed", []):
        issues.append("wildcard_env_rule")
    if not _valid_filesystem_policy(data.get("filesystem_policy")):
        issues.append("invalid_filesystem_policy")

    return issues


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _valid_read_roots(value: Any, *, allow_edge: bool) -> bool:
    if not isinstance(value, list):
        return False
    if not value:
        return allow_edge
    for item in value:
        if not _safe_relative_path(item):
            return False
    return True


def _valid_output_roots(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, str):
            return False
        if ".." in Path(item).parts or "\\" in item:
            return False
        if not item.startswith("{sandbox_tmp}/"):
            return False
    return len(value) == len(set(value))


def _valid_env_policy(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("mode") != "allowlist":
        return False
    allowed = value.get("allowed")
    forbidden_prefixes = value.get("forbidden_prefixes")
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        return False
    if not isinstance(forbidden_prefixes, list) or not all(isinstance(item, str) for item in forbidden_prefixes):
        return False
    return "*" not in allowed


def _valid_filesystem_policy(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("cwd") != "{sandbox_tmp}":
        return False
    if value.get("temp_root_required") is not True:
        return False
    if value.get("symlink_policy") != "reject":
        return False
    if value.get("parent_traversal") != "reject":
        return False
    if value.get("absolute_paths") != "reject":
        return False
    protected_roots = value.get("protected_roots")
    return isinstance(protected_roots, list) and bool(protected_roots)


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value
