from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from aios.providers.trace import (
    FAILURE_CODES,
    PROVIDER_EXECUTION_TRACE_SCHEMA_VERSION,
    PROVIDER_MODES,
    validate_provider_execution_trace_data,
)


ROOT = Path(__file__).resolve().parents[1]
TRACES = ROOT / "tests" / "fixtures" / "providers" / "traces"
VALID = TRACES / "valid"
INVALID = TRACES / "invalid"
EDGE_CASES = TRACES / "edge_cases"
INVALID_FIXTURES = {
    "missing_trace_id.json": "missing_trace_id",
    "invalid_provider_mode.json": "invalid_provider_mode",
    "mutation_performed_true.json": "mutation_performed_true",
    "network_disabled_false.json": "network_not_disabled",
    "missing_no_write_confirmed.json": "missing_no_write_confirmed",
    "invalid_failure_code.json": "invalid_failure_code",
    "invalid_hash_format.json": "invalid_hash_format",
    "missing_provenance.json": "missing_provenance",
    "nondeterministic_execution_false.json": "nondeterministic_execution_false",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def codes(data: Any) -> list[str]:
    return [issue.code for issue in validate_provider_execution_trace_data(data).issues]


def test_trace_validator_constants_match_contract() -> None:
    assert PROVIDER_EXECUTION_TRACE_SCHEMA_VERSION == "aios.provider_execution_trace.v0"
    assert PROVIDER_MODES == frozenset({"fixture-mock", "subprocess-sandbox"})
    assert {
        "provider-timeout",
        "nondeterministic-output",
        "provider-execution-disabled",
        "provider-isolation-violation",
        "provider-capability-missing",
        "provider-output-invalid",
        "provider-network-disabled",
        "provider-resource-limit",
    } <= FAILURE_CODES


def test_valid_and_edge_trace_fixtures_produce_no_errors() -> None:
    for path in sorted(VALID.glob("*.json")) + sorted(EDGE_CASES.glob("*.json")):
        result = validate_provider_execution_trace_data(load(path))

        assert result.errors == [], path
        assert result.status == "pass", path


def test_invalid_trace_fixtures_return_expected_issue_code() -> None:
    for name, expected_code in INVALID_FIXTURES.items():
        result = validate_provider_execution_trace_data(load(INVALID / name))

        assert expected_code in [issue.code for issue in result.errors], name
        assert result.status == "fail", name


def test_unsupported_schema_version_is_error() -> None:
    data = load(VALID / "whole_file_trace.json")
    data["schema_version"] = "aios.provider_execution_trace.v9"

    assert "unsupported_schema_version" in codes(data)


def test_missing_trace_id_is_error() -> None:
    data = load(VALID / "whole_file_trace.json")
    data.pop("trace_id")

    assert "missing_trace_id" in codes(data)


def test_invalid_provider_mode_is_error() -> None:
    data = load(VALID / "whole_file_trace.json")
    data["provider_mode"] = "real-provider"

    assert "invalid_provider_mode" in codes(data)


def test_invalid_failure_code_is_error() -> None:
    data = load(EDGE_CASES / "failure_without_generated_hashes.json")
    data["failure_code"] = "not-a-real-code"

    assert "invalid_failure_code" in codes(data)


def test_mutation_network_no_write_and_determinism_flags_are_enforced() -> None:
    data = load(VALID / "whole_file_trace.json")

    mutated = copy.deepcopy(data)
    mutated["mutation_performed"] = True
    assert "mutation_performed_true" in codes(mutated)

    networked = copy.deepcopy(data)
    networked["network_disabled"] = False
    assert "network_not_disabled" in codes(networked)

    no_write_missing = copy.deepcopy(data)
    no_write_missing.pop("no_write_confirmed")
    assert "missing_no_write_confirmed" in codes(no_write_missing)

    no_write_false = copy.deepcopy(data)
    no_write_false["no_write_confirmed"] = False
    assert "no_write_not_confirmed" in codes(no_write_false)

    nondeterministic = copy.deepcopy(data)
    nondeterministic["deterministic_execution"] = False
    assert "nondeterministic_execution_false" in codes(nondeterministic)


def test_hash_generated_hashes_and_provenance_validation() -> None:
    data = load(VALID / "whole_file_trace.json")

    invalid_hash = copy.deepcopy(data)
    invalid_hash["input_hash"] = "sha256:UPPERCASE"
    assert "invalid_hash_format" in codes(invalid_hash)

    invalid_generated = copy.deepcopy(data)
    invalid_generated["generated_hashes"] = {"generated_bytes_hash": "sha256:bad"}
    assert "invalid_generated_hashes" in codes(invalid_generated)
    assert "invalid_hash_format" in codes(invalid_generated)

    missing_provenance = copy.deepcopy(data)
    missing_provenance.pop("provenance")
    assert "missing_provenance" in codes(missing_provenance)

    bad_order = copy.deepcopy(data)
    bad_order["provenance"]["source_hashes"] = {
        ".ai/rules/other.md": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
    }
    assert "invalid_provenance" in codes(bad_order)


def test_unavailable_and_failure_semantics_are_enforced() -> None:
    data = load(VALID / "whole_file_trace.json")

    unavailable_with_hash = copy.deepcopy(data)
    unavailable_with_hash["unavailable_reason"] = "source-missing"
    assert "unavailable_generated_hash_present" in codes(unavailable_with_hash)

    failure_without_reason = copy.deepcopy(data)
    failure_without_reason["failure_code"] = "provider-output-invalid"
    failure_without_reason["generated_hashes"] = {
        "generated_bytes_hash": None,
        "generated_target_hash": None,
        "generated_managed_block_hash": None,
    }
    failure_without_reason["output_hash"] = None
    assert "missing_unavailable_reason" in codes(failure_without_reason)


def test_duration_and_hash_policy_are_validated() -> None:
    data = load(VALID / "whole_file_trace.json")

    invalid_duration = copy.deepcopy(data)
    invalid_duration["duration_ms"] = -1
    assert "invalid_duration" in codes(invalid_duration)

    invalid_policy = copy.deepcopy(data)
    invalid_policy["hash_policy"]["normalization"] = "lf"
    assert "invalid_hash_policy" in codes(invalid_policy)


def test_trace_validator_does_not_mutate_input() -> None:
    data = load(VALID / "whole_file_trace.json")
    before = copy.deepcopy(data)

    validate_provider_execution_trace_data(data)

    assert data == before


def test_non_object_trace_is_error() -> None:
    result = validate_provider_execution_trace_data(["not", "object"])

    assert result.status == "fail"
    assert result.errors[0].code == "provider_execution_trace_not_object"
