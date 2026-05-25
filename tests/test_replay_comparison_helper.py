from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from aios.sync.replay import compare_replay_outputs


def replay_output() -> dict[str, Any]:
    return {
        "schema_version": "aios.real_preview.output.v0",
        "entry_id": "whole_file_lf",
        "preview_available": True,
        "generated_content_kind": "whole-file",
        "generated_bytes_hash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "generated_target_hash": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "generated_managed_block_hash": None,
        "deterministic": True,
        "provider_metadata": {
            "provider_id": "aios.preview.example",
            "provider_version": "0.1.0",
            "hash_policy": "aios.hash_policy.v0",
            "supported_sync_mode": "whole-file",
            "output_affecting_config_ref": "provider_snapshots/aios_preview_example_0_1_0.json",
        },
        "provenance": {
            "source_paths": [".ai/rules/rules.md", ".ai/rules/operations/sync.rules.md"],
            "source_hashes": {
                ".ai/rules/rules.md": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
                ".ai/rules/operations/sync.rules.md": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
            },
            "activation_reference": None,
            "rule_context_reference": ".ai/rules/rules.md",
            "generated_by": "aios.real_preview_provider.v0",
        },
        "unavailable_reason": None,
    }


def single_issue_for(field: str, value: Any, expected_code: str) -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate[field] = value

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    issue = issues[0]
    assert issue.code == expected_code
    assert issue.severity == "error"
    assert issue.status == "fail"
    assert issue.case_id == "case-1"
    assert issue.comparison_field == field
    assert issue.message == f"Replay comparison field mismatch: {field}"


def test_exact_match_returns_no_issues() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)

    assert compare_replay_outputs(expected, candidate, case_id="case-1") == []


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("schema_version", "aios.real_preview.output.v999", "replay-schema-mismatch"),
        ("entry_id", "different-entry", "replay-entry-id-mismatch"),
        ("preview_available", False, "replay-preview-available-mismatch"),
        ("generated_content_kind", "managed-block", "replay-content-kind-mismatch"),
        ("generated_bytes_hash", "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "replay-hash-mismatch"),
        ("generated_target_hash", "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "replay-hash-mismatch"),
        ("generated_managed_block_hash", "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "replay-hash-mismatch"),
        ("deterministic", False, "replay-deterministic-flag-mismatch"),
        ("unavailable_reason", "provider-timeout", "replay-unavailable-reason-mismatch"),
    ],
)
def test_scalar_field_mismatches(field: str, value: Any, expected_code: str) -> None:
    single_issue_for(field, value, expected_code)


def test_provider_metadata_mismatch() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate["provider_metadata"]["provider_version"] = "0.2.0"

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    assert issues[0].code == "replay-provider-metadata-mismatch"
    assert issues[0].comparison_field == "provider_metadata"
    assert issues[0].expected_summary == (
        "object(keys=provider_id,provider_version,hash_policy,supported_sync_mode,output_affecting_config_ref)"
    )


def test_provenance_mismatch() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate["provenance"]["generated_by"] = "different-generator"

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    assert issues[0].code == "replay-provenance-mismatch"
    assert issues[0].comparison_field == "provenance"


def test_missing_field_is_mismatch_not_equal_to_null() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    del candidate["generated_managed_block_hash"]

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    assert issues[0].code == "replay-hash-mismatch"
    assert issues[0].comparison_field == "generated_managed_block_hash"
    assert issues[0].expected_value is None
    assert issues[0].actual_summary == "<missing>"


def test_list_order_mismatch_is_mismatch() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate["provenance"]["source_paths"] = list(reversed(candidate["provenance"]["source_paths"]))

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    assert issues[0].code == "replay-provenance-mismatch"


def test_string_true_differs_from_boolean_true() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate["preview_available"] = "true"

    issues = compare_replay_outputs(expected, candidate, case_id="case-1")

    assert len(issues) == 1
    assert issues[0].code == "replay-preview-available-mismatch"
    assert issues[0].expected_value is True
    assert issues[0].actual_value == "true"


def test_issue_to_dict_preserves_comparison_details() -> None:
    expected = replay_output()
    candidate = deepcopy(expected)
    candidate["entry_id"] = "different-entry"

    issue = compare_replay_outputs(expected, candidate, case_id="case-1")[0].to_dict()

    assert issue["code"] == "replay-entry-id-mismatch"
    assert issue["severity"] == "error"
    assert issue["status"] == "fail"
    assert issue["case_id"] == "case-1"
    assert issue["comparison_field"] == "entry_id"
    assert issue["expected_value"] == "whole_file_lf"
    assert issue["actual_value"] == "different-entry"
