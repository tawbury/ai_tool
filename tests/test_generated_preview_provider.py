from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from aios.sync.preview import (
    UNAVAILABLE_REASONS,
    FixturePreviewProvider,
    load_preview_output,
)


ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "tests" / "fixtures" / "sync" / "previews"
TARGET = ROOT / "tests" / "fixtures" / "sync" / "targets" / "clean_managed.md"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def provider() -> FixturePreviewProvider:
    return FixturePreviewProvider(PREVIEWS)


def test_whole_file_input_maps_to_whole_file_available_output() -> None:
    output = provider().preview("whole_file_clean_input.json")

    assert output.entry_id == "preview_whole_file_clean"
    assert output.preview_available is True
    assert output.generated_content_kind == "whole-file"
    assert output.generated_target_hash == output.generated_bytes_hash
    assert output.generated_managed_block_hash is None
    assert output.generated_metadata["deterministic"] is True
    assert output.generated_metadata["adapter_id"] == "codex-cli"


def test_managed_block_input_maps_to_managed_block_available_output() -> None:
    output = provider().preview("managed_block_clean_input.json")

    assert output.entry_id == "preview_managed_block_clean"
    assert output.preview_available is True
    assert output.generated_content_kind == "managed-block"
    assert output.generated_target_hash is None
    assert output.generated_managed_block_hash == output.generated_bytes_hash
    assert output.provenance["source_paths"] == [".ai/rules/operations/sync.rules.md"]


@pytest.mark.parametrize(
    ("input_fixture", "reason"),
    [
        ("adapter_unavailable_input.json", "adapter-unavailable"),
        ("source_missing_input.json", "source-missing"),
        ("marker_invalid_input.json", "marker-invalid"),
        ("activation_unresolved_input.json", "activation-unresolved"),
    ],
)
def test_unavailable_inputs_map_to_unavailable_outputs(input_fixture: str, reason: str) -> None:
    output = provider().preview(input_fixture)

    assert output.preview_available is False
    assert output.unavailable_reason == reason
    assert output.generated_bytes_hash is None
    assert output.generated_target_hash is None
    assert output.generated_managed_block_hash is None
    assert output.provenance["generated_by"] == "aios.generated_preview.v0"


def test_provider_rejects_unknown_fixture_mapping() -> None:
    with pytest.raises(ValueError, match="Unknown generated preview fixture mapping"):
        provider().preview("mixed_boundary_clean_input.json")


def test_provider_does_not_mutate_fixture_or_target_files() -> None:
    files = [
        PREVIEWS / "inputs" / "whole_file_clean_input.json",
        PREVIEWS / "outputs" / "whole_file_available_output.json",
        TARGET,
    ]
    before = {path: _digest(path) for path in files}

    output = provider().preview("whole_file_clean_input.json")

    assert output.preview_available is True
    assert {path: _digest(path) for path in files} == before


def test_output_hash_fields_validate_when_non_null() -> None:
    for output_path in sorted((PREVIEWS / "outputs").glob("*.json")):
        output = load_preview_output(output_path)

        for value in (
            output.generated_bytes_hash,
            output.generated_target_hash,
            output.generated_managed_block_hash,
        ):
            if value is not None:
                assert HASH_RE.match(value), (output_path, value)


def test_unavailable_reason_enum_is_enforced(tmp_path: Path) -> None:
    source = PREVIEWS / "outputs" / "adapter_unavailable_output.json"
    bad = tmp_path / "bad_output.json"
    bad.write_text(
        source.read_text(encoding="utf-8").replace("adapter-unavailable", "not-a-valid-reason"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown preview unavailable_reason"):
        load_preview_output(bad)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
