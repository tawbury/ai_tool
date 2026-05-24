from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "tests" / "fixtures" / "sync" / "real_previews" / "replay"
INPUTS = REPLAY / "inputs"
OUTPUTS = REPLAY / "outputs"
MANIFESTS = REPLAY / "manifests"
SNAPSHOTS = REPLAY / "provider_snapshots"

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PLACEHOLDER_RE = re.compile(r"<|>|TODO|placeholder", re.IGNORECASE)
REQUIRED_CASE_IDS = {
    "whole_file_lf",
    "whole_file_crlf",
    "whole_file_trailing_newline",
    "whole_file_bom",
    "managed_block_lf",
    "managed_block_crlf",
    "mixed_boundary",
    "unavailable_adapter",
    "unavailable_nondeterministic",
    "unavailable_timeout",
}
UNAVAILABLE_REASONS = {
    "adapter-unavailable",
    "source-missing",
    "unsupported-sync-mode",
    "activation-unresolved",
    "nondeterministic-output",
    "provider-timeout",
    "generation-disabled",
    "marker-invalid",
}
EXPECTED_UNAVAILABLE_REASONS = {
    "adapter-unavailable",
    "nondeterministic-output",
    "provider-timeout",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_replay_manifest_and_provider_snapshot_match_contract() -> None:
    manifest = load(MANIFESTS / "replay_manifest.json")
    snapshot = load(SNAPSHOTS / "aios_preview_example_0_1_0.json")

    assert manifest["schema_version"] == "aios.preview_replay_manifest.v0"
    assert snapshot["schema_version"] == "aios.preview_provider_snapshot.v0"
    assert manifest["provider"]["provider_id"] == snapshot["provider_id"]
    assert manifest["provider"]["provider_version"] == snapshot["provider_version"]
    assert manifest["hash_policy"]["version"] == snapshot["hash_policy"]
    assert snapshot["deterministic_capable"] is True
    assert set(snapshot["supported_sync_modes"]) == {"whole-file", "managed-block", "mixed-boundary"}
    assert snapshot["output_affecting_config"]


def test_replay_manifest_cases_reference_safe_existing_fixtures() -> None:
    manifest = load(MANIFESTS / "replay_manifest.json")
    case_ids = [case["case_id"] for case in manifest["cases"]]

    assert set(case_ids) == REQUIRED_CASE_IDS
    assert len(case_ids) == len(set(case_ids))

    for case in manifest["cases"]:
        assert case["replay_dimensions"], case
        input_path = _safe_fixture_path(case["input_fixture"])
        output_path = _safe_fixture_path(case["expected_output_fixture"])

        assert input_path.is_file(), case
        assert output_path.is_file(), case
        assert input_path.parent == INPUTS
        assert output_path.parent == OUTPUTS


def test_replay_input_fixtures_match_contract() -> None:
    required_top = {
        "schema_version",
        "entry_id",
        "manifest_entry",
        "source_evidence",
        "context",
        "provider",
        "hash_policy",
    }
    required_entry = {
        "source_path",
        "source_paths",
        "source_hash",
        "target_path",
        "ownership",
        "sync_mode",
        "marker",
    }
    for path in sorted(INPUTS.glob("*.json")):
        data = load(path)

        assert required_top <= data.keys(), path
        assert data["schema_version"] == "aios.real_preview.input.v0"
        assert data["entry_id"], path
        assert required_entry <= data["manifest_entry"].keys(), path
        assert data["manifest_entry"]["sync_mode"] in {"whole-file", "managed-block", "mixed-boundary"}
        assert data["manifest_entry"]["ownership"] in {"runtime-managed", "user-owned", "mixed-boundary"}
        assert data["provider"]["provider_id"] == "aios.preview.example"
        assert data["provider"]["provider_version"] == "0.1.0"
        assert data["hash_policy"]["version"] == "aios.hash_policy.v0"
        assert data["hash_policy"]["line_endings"] == "preserve"
        assert data["hash_policy"]["trailing_newline"] == "preserve"
        assert data["hash_policy"]["managed_block_marker_lines"] == "exclude"
        _assert_source_order_is_explicit(data, path)
        _assert_marker_contract(data, path)
        _assert_hash_fields(data, path)


def test_replay_output_fixtures_match_contract() -> None:
    required = {
        "schema_version",
        "entry_id",
        "preview_available",
        "generated_content_kind",
        "generated_bytes_hash",
        "generated_target_hash",
        "generated_managed_block_hash",
        "deterministic",
        "provider_metadata",
        "provenance",
        "unavailable_reason",
    }
    unavailable_reasons = set()
    for path in sorted(OUTPUTS.glob("*.json")):
        data = load(path)

        assert required <= data.keys(), path
        assert data["schema_version"] == "aios.real_preview.output.v0"
        assert isinstance(data["preview_available"], bool), path
        assert data["provider_metadata"]["provider_id"] == "aios.preview.example", path
        assert data["provider_metadata"]["provider_version"] == "0.1.0", path
        assert data["provider_metadata"]["hash_policy"] == "aios.hash_policy.v0", path
        assert data["provider_metadata"]["output_affecting_config_ref"], path
        _assert_provenance(data["provenance"], path)
        _assert_hash_fields(data, path)

        if data["preview_available"]:
            assert data["deterministic"] is True, path
            assert data["generated_content_kind"] in {"whole-file", "managed-block", "mixed-boundary"}, path
            assert data["generated_bytes_hash"] is not None, path
            assert data["unavailable_reason"] is None, path
            if data["generated_content_kind"] == "whole-file":
                assert data["generated_target_hash"] is not None, path
                assert data["generated_managed_block_hash"] is None, path
            else:
                assert data["generated_target_hash"] is None, path
                assert data["generated_managed_block_hash"] is not None, path
        else:
            assert data["deterministic"] is False, path
            assert data["generated_content_kind"] is None, path
            assert data["generated_bytes_hash"] is None, path
            assert data["generated_target_hash"] is None, path
            assert data["generated_managed_block_hash"] is None, path
            assert data["unavailable_reason"] in UNAVAILABLE_REASONS, path
            unavailable_reasons.add(data["unavailable_reason"])

    assert EXPECTED_UNAVAILABLE_REASONS <= unavailable_reasons


def test_manifest_cases_match_input_and_output_entry_ids() -> None:
    manifest = load(MANIFESTS / "replay_manifest.json")
    for case in manifest["cases"]:
        input_data = load(_safe_fixture_path(case["input_fixture"]))
        output_data = load(_safe_fixture_path(case["expected_output_fixture"]))

        assert input_data["entry_id"] == case["case_id"]
        assert output_data["entry_id"] == case["case_id"]
        assert input_data["entry_id"] == output_data["entry_id"]
        assert output_data["provider_metadata"]["supported_sync_mode"] == input_data["manifest_entry"]["sync_mode"]


def _safe_fixture_path(relative: str) -> Path:
    candidate = Path(relative)
    assert not candidate.is_absolute(), relative
    assert ".." not in candidate.parts, relative
    return REPLAY / candidate


def _assert_hash_fields(value: Any, path: Path) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str):
                assert not PLACEHOLDER_RE.search(item), (path, key, item)
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


def _assert_source_order_is_explicit(data: dict[str, Any], path: Path) -> None:
    source_paths = data["source_evidence"]["source_paths"]
    source_hashes = data["source_evidence"]["source_hashes"]

    assert isinstance(source_paths, list), path
    assert source_paths, path
    assert len(source_paths) == len(set(source_paths)), path
    assert list(source_hashes.keys()) == source_paths, path


def _assert_marker_contract(data: dict[str, Any], path: Path) -> None:
    sync_mode = data["manifest_entry"]["sync_mode"]
    marker = data["manifest_entry"]["marker"]
    if sync_mode == "whole-file":
        assert marker is None, path
    else:
        assert marker["entry_id"] == data["entry_id"], path
        assert marker["marker_version"] == "0", path
        assert marker["marker_style"] in {
            "markdown-html-comment",
            "hash-line-comment",
            "yaml-line-comment",
        }, path


def _assert_provenance(provenance: dict[str, Any], path: Path) -> None:
    assert "source_paths" in provenance, path
    assert "source_hashes" in provenance, path
    assert "activation_reference" in provenance, path
    assert "rule_context_reference" in provenance, path
    assert provenance["generated_by"] == "aios.real_preview_provider.v0", path
    assert list(provenance["source_hashes"].keys()) == provenance["source_paths"], path
