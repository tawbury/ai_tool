from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "tests" / "fixtures" / "sync" / "previews"
INPUTS = PREVIEWS / "inputs"
OUTPUTS = PREVIEWS / "outputs"
EXPECTED = PREVIEWS / "expected"

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
UNAVAILABLE_REASONS = {
    "adapter-unavailable",
    "source-missing",
    "unsupported-sync-mode",
    "marker-invalid",
    "generation-disabled",
    "activation-unresolved",
}
INPUT_FIXTURES = {
    "whole_file_clean_input.json",
    "whole_file_match_input.json",
    "managed_block_clean_input.json",
    "mixed_boundary_clean_input.json",
    "source_missing_input.json",
    "marker_invalid_input.json",
    "adapter_unavailable_input.json",
    "activation_unresolved_input.json",
}
OUTPUT_FIXTURES = {
    "whole_file_available_output.json",
    "whole_file_match_output.json",
    "managed_block_available_output.json",
    "adapter_unavailable_output.json",
    "source_missing_output.json",
    "marker_invalid_output.json",
    "activation_unresolved_output.json",
}
EXPECTED_FIXTURES = {
    "whole_file_update_candidate_expected.json",
    "whole_file_skip_expected.json",
    "managed_block_update_candidate_expected.json",
    "drift_stop_precedence_expected.json",
    "marker_conflict_precedence_expected.json",
    "preview_unavailable_no_update_expected.json",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_preview_fixture_inventory_is_minimal_contract_set() -> None:
    assert {path.name for path in INPUTS.glob("*.json")} == INPUT_FIXTURES
    assert {path.name for path in OUTPUTS.glob("*.json")} == OUTPUT_FIXTURES
    assert {path.name for path in EXPECTED.glob("*.json")} == EXPECTED_FIXTURES


def test_every_preview_json_fixture_parses() -> None:
    for path in sorted(PREVIEWS.glob("*/*.json")):
        data = load(path)

        assert isinstance(data, dict), path


def test_preview_input_fixtures_match_contract() -> None:
    required_top = {
        "schema_version",
        "entry_id",
        "manifest_entry",
        "adapter",
        "context",
        "hash_policy",
    }
    required_entry = {
        "source_path",
        "source_paths",
        "source_hash",
        "target_path",
        "sync_mode",
        "ownership",
        "marker",
    }
    for path in sorted(INPUTS.glob("*.json")):
        data = load(path)

        assert required_top <= data.keys(), path
        assert data["schema_version"] == "aios.generated_preview.input.v0"
        assert data["entry_id"]
        assert required_entry <= data["manifest_entry"].keys(), path
        assert data["manifest_entry"]["source_path"] or data["manifest_entry"]["source_paths"]
        assert data["manifest_entry"]["sync_mode"] in {"whole-file", "managed-block", "mixed-boundary"}
        assert data["manifest_entry"]["ownership"] in {"runtime-managed", "user-owned", "mixed-boundary"}
        assert data["adapter"].get("adapter_id"), path
        assert data["hash_policy"]["version"] == "aios.hash_policy.v0"
        assert data["hash_policy"]["algorithm"] == "sha256"
        assert data["hash_policy"]["line_endings"] == "preserve"
        assert data["hash_policy"]["managed_block_marker_lines"] == "exclude"
        _assert_hash_fields(data, path)

        marker = data["manifest_entry"]["marker"]
        if data["manifest_entry"]["sync_mode"] == "whole-file":
            assert marker is None, path
        else:
            assert marker["entry_id"] == data["entry_id"], path
            assert marker["marker_version"] == "0", path
            assert marker["marker_style"] in {
                "markdown-html-comment",
                "hash-line-comment",
                "yaml-line-comment",
            }


def test_preview_output_fixtures_match_contract() -> None:
    required = {
        "schema_version",
        "entry_id",
        "preview_available",
        "generated_content_kind",
        "generated_bytes_hash",
        "generated_target_hash",
        "generated_managed_block_hash",
        "generated_metadata",
        "unavailable_reason",
        "provenance",
    }
    for path in sorted(OUTPUTS.glob("*.json")):
        data = load(path)

        assert required <= data.keys(), path
        assert data["schema_version"] == "aios.generated_preview.output.v0"
        assert data["entry_id"], path
        assert isinstance(data["preview_available"], bool), path
        _assert_hash_fields(data, path)
        _assert_provenance(data["provenance"], path)

        if data["preview_available"]:
            assert data["generated_content_kind"] in {"whole-file", "managed-block", "mixed-boundary"}, path
            assert data["generated_bytes_hash"] is not None, path
            assert data["unavailable_reason"] is None, path
            assert data["generated_metadata"]["deterministic"] is True, path
            assert data["generated_metadata"]["adapter_id"], path
            assert data["generated_metadata"]["hash_policy"] == "aios.hash_policy.v0", path
        else:
            assert data["generated_content_kind"] is None, path
            assert data["generated_bytes_hash"] is None, path
            assert data["generated_target_hash"] is None, path
            assert data["generated_managed_block_hash"] is None, path
            assert data["unavailable_reason"] in UNAVAILABLE_REASONS, path


def test_expected_classification_fixtures_match_contract() -> None:
    required = {
        "entry_id",
        "input_fixture",
        "output_fixture",
        "target_state",
        "expected_action",
        "expected_status",
        "expected_severity",
        "expected_stop_reason",
        "expected_no_mutation",
        "expected_hash_fields",
        "expected_message_codes",
    }
    for path in sorted(EXPECTED.glob("*.json")):
        data = load(path)

        assert required <= data.keys(), path
        assert data["expected_no_mutation"] is True, path
        assert data["expected_action"] in {"update", "skip", "conflict", "drift-stop"}, path
        assert data["expected_status"] in {"pass", "warn", "fail"}, path
        assert data["expected_severity"] in {"informational", "warning", "blocking"}, path
        assert isinstance(data["expected_hash_fields"], list), path
        assert isinstance(data["expected_message_codes"], list), path
        assert (PREVIEWS / data["input_fixture"]).is_file(), path
        assert (PREVIEWS / data["output_fixture"]).is_file(), path


def _assert_hash_fields(value: Any, path: Path) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "source_hashes":
                assert isinstance(item, dict), path
                for digest in item.values():
                    assert HASH_RE.match(digest), (path, digest)
                continue
            if key.endswith("_hash") and item is not None:
                assert isinstance(item, str), (path, key)
                assert HASH_RE.match(item), (path, key, item)
            else:
                _assert_hash_fields(item, path)
    elif isinstance(value, list):
        for item in value:
            _assert_hash_fields(item, path)


def _assert_provenance(provenance: dict[str, Any], path: Path) -> None:
    assert "source_paths" in provenance, path
    assert "source_hashes" in provenance, path
    assert "generated_by" in provenance, path
    assert provenance["generated_by"] == "aios.generated_preview.v0", path
    for source_path in provenance["source_paths"]:
        assert source_path in provenance["source_hashes"], (path, source_path)
