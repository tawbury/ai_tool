from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PREVIEW_INPUT_SCHEMA_VERSION = "aios.generated_preview.input.v0"
PREVIEW_OUTPUT_SCHEMA_VERSION = "aios.generated_preview.output.v0"

UNAVAILABLE_REASONS = {
    "adapter-unavailable",
    "source-missing",
    "unsupported-sync-mode",
    "marker-invalid",
    "generation-disabled",
    "activation-unresolved",
}

FIXTURE_OUTPUT_BY_INPUT = {
    "whole_file_clean_input.json": "whole_file_available_output.json",
    "managed_block_clean_input.json": "managed_block_available_output.json",
    "adapter_unavailable_input.json": "adapter_unavailable_output.json",
    "source_missing_input.json": "source_missing_output.json",
    "marker_invalid_input.json": "marker_invalid_output.json",
    "activation_unresolved_input.json": "activation_unresolved_output.json",
}

_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class PreviewInput:
    path: Path
    data: dict[str, Any]

    @property
    def entry_id(self) -> str:
        return str(self.data["entry_id"])


@dataclass(frozen=True)
class PreviewOutput:
    entry_id: str
    preview_available: bool
    generated_content_kind: str | None
    generated_bytes_hash: str | None
    generated_target_hash: str | None
    generated_managed_block_hash: str | None
    generated_metadata: dict[str, Any] = field(default_factory=dict)
    unavailable_reason: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)


class FixturePreviewProvider:
    """Read-only generated preview provider backed only by JSON fixtures."""

    def __init__(self, fixture_root: Path) -> None:
        self.fixture_root = fixture_root
        self.inputs_dir = fixture_root / "inputs"
        self.outputs_dir = fixture_root / "outputs"

    def preview(self, input_fixture: str | Path) -> PreviewOutput:
        input_path = self._input_path(input_fixture)
        preview_input = load_preview_input(input_path)
        output_name = FIXTURE_OUTPUT_BY_INPUT.get(input_path.name)
        if output_name is None:
            raise ValueError(f"Unknown generated preview fixture mapping: {input_path.name}")

        output_path = self.outputs_dir / output_name
        output = load_preview_output(output_path)
        if output.entry_id != preview_input.entry_id:
            raise ValueError(
                f"Preview fixture entry_id mismatch: {preview_input.entry_id} != {output.entry_id}"
            )
        return output

    def _input_path(self, input_fixture: str | Path) -> Path:
        path = Path(input_fixture)
        if not path.is_absolute():
            path = self.inputs_dir / path
        if not path.is_file():
            raise ValueError(f"Generated preview input fixture does not exist: {input_fixture}")
        return path


def load_preview_input(path: Path) -> PreviewInput:
    data = _load_json(path)
    _require(data, {"schema_version", "entry_id", "manifest_entry", "adapter", "context", "hash_policy"}, path)
    if data["schema_version"] != PREVIEW_INPUT_SCHEMA_VERSION:
        raise ValueError(f"Unsupported generated preview input schema_version in {path}")
    if not str(data["entry_id"]).strip():
        raise ValueError(f"Generated preview input entry_id is required in {path}")

    manifest_entry = data["manifest_entry"]
    _require(
        manifest_entry,
        {"source_path", "source_paths", "source_hash", "target_path", "sync_mode", "ownership", "marker"},
        path,
    )
    _assert_hash(manifest_entry["source_hash"], path, "manifest_entry.source_hash")
    if not data["adapter"].get("adapter_id"):
        raise ValueError(f"Generated preview input adapter.adapter_id is required in {path}")
    return PreviewInput(path=path, data=data)


def load_preview_output(path: Path) -> PreviewOutput:
    data = _load_json(path)
    _require(
        data,
        {
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
        },
        path,
    )
    if data["schema_version"] != PREVIEW_OUTPUT_SCHEMA_VERSION:
        raise ValueError(f"Unsupported generated preview output schema_version in {path}")
    _validate_output_hashes(data, path)
    _validate_provenance(data["provenance"], path)

    if data["preview_available"]:
        metadata = data["generated_metadata"]
        if metadata.get("deterministic") is not True:
            raise ValueError(f"Available preview output must be deterministic in {path}")
        if not metadata.get("adapter_id"):
            raise ValueError(f"Available preview output requires adapter identity in {path}")
        if data["unavailable_reason"] is not None:
            raise ValueError(f"Available preview output must not set unavailable_reason in {path}")
    else:
        if data["unavailable_reason"] not in UNAVAILABLE_REASONS:
            raise ValueError(f"Unknown preview unavailable_reason in {path}: {data['unavailable_reason']}")
        for field_name in ("generated_bytes_hash", "generated_target_hash", "generated_managed_block_hash"):
            if data[field_name] is not None:
                raise ValueError(f"Unavailable preview output must keep {field_name} null in {path}")

    return PreviewOutput(
        entry_id=str(data["entry_id"]),
        preview_available=bool(data["preview_available"]),
        generated_content_kind=data["generated_content_kind"],
        generated_bytes_hash=data["generated_bytes_hash"],
        generated_target_hash=data["generated_target_hash"],
        generated_managed_block_hash=data["generated_managed_block_hash"],
        generated_metadata=dict(data["generated_metadata"]),
        unavailable_reason=data["unavailable_reason"],
        provenance=dict(data["provenance"]),
        data=data,
    )


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Generated preview fixture must be a JSON object: {path}")
    return data


def _require(data: dict[str, Any], required: set[str], path: Path) -> None:
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Generated preview fixture missing required fields in {path}: {', '.join(missing)}")


def _validate_output_hashes(data: dict[str, Any], path: Path) -> None:
    for field_name in ("generated_bytes_hash", "generated_target_hash", "generated_managed_block_hash"):
        value = data[field_name]
        if value is not None:
            _assert_hash(value, path, field_name)


def _validate_provenance(provenance: dict[str, Any], path: Path) -> None:
    _require(provenance, {"source_paths", "source_hashes", "generated_by"}, path)
    if provenance["generated_by"] != "aios.generated_preview.v0":
        raise ValueError(f"Unexpected generated_by in preview provenance: {path}")
    for source_path in provenance["source_paths"]:
        if source_path not in provenance["source_hashes"]:
            raise ValueError(f"Preview provenance missing source hash for {source_path} in {path}")
    for digest in provenance["source_hashes"].values():
        _assert_hash(digest, path, "provenance.source_hashes")


def _assert_hash(value: Any, path: Path, field_name: str) -> None:
    if not isinstance(value, str) or not _HASH_RE.match(value):
        raise ValueError(f"Invalid generated preview hash for {field_name} in {path}: {value}")
