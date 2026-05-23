from __future__ import annotations

from pathlib import Path

from ..filesystem import rel_path
from ..status import SEVERITY_ERROR, STATUS_FAIL
from .hash import HASH_POLICY_V0, hash_file, hash_managed_block_inner_bytes
from .manifest import ManifestEntry, load_manifest
from .markers import (
    INTEGRITY_BEGIN_DUPLICATED,
    INTEGRITY_END_DUPLICATED,
    INTEGRITY_VALID,
    MarkerBlock,
    parse_marker_file,
)
from .preview import FixturePreviewProvider
from .result import (
    ACTION_CONFLICT,
    ACTION_CREATE,
    ACTION_DRIFT_STOP,
    ACTION_ORPHAN_WARNING,
    ACTION_SKIP,
    ACTION_UPDATE,
    SEVERITY_BLOCKING,
    SEVERITY_INFORMATIONAL,
    SEVERITY_WARNING,
    SyncDryRunItem,
    SyncDryRunMessage,
    SyncDryRunResult,
    message_for_item,
)


def run_sync_dry_run(
    root: Path,
    manifest_path: Path,
    *,
    preview_provider: FixturePreviewProvider | None = None,
    preview_inputs: dict[str, str] | None = None,
) -> SyncDryRunResult:
    manifest_rel = _display_path(root, manifest_path)
    validation = load_manifest(manifest_path)
    if validation.manifest is None:
        messages = [
            SyncDryRunMessage(
                code=issue.code,
                severity=SEVERITY_ERROR,
                status=STATUS_FAIL,
                message=issue.message,
                path=manifest_rel,
                details={"field": issue.field, "entry_id": issue.entry_id},
            )
            for issue in validation.issues
        ]
        return SyncDryRunResult(
            root=str(root),
            manifest_path=manifest_rel,
            messages=messages,
            meta={"manifest_valid": False},
        )

    results: list[SyncDryRunItem] = []
    messages: list[SyncDryRunMessage] = []
    for entry in validation.manifest.managed_entries:
        entry_results = _evaluate_entry(
            root,
            entry,
            preview_provider=preview_provider,
            preview_inputs=preview_inputs or {},
        )
        results.extend(entry_results)
        for item in entry_results:
            if item.severity == SEVERITY_BLOCKING:
                messages.append(message_for_item(item, _message_text(item), line=_marker_line(item)))
            elif item.severity == SEVERITY_WARNING:
                messages.append(message_for_item(item, _message_text(item), line=_marker_line(item)))

    return SyncDryRunResult(
        root=str(root),
        manifest_path=manifest_rel,
        results=results,
        messages=messages,
        meta={
            "manifest_valid": True,
            "manifest_schema_version": validation.manifest.schema_version,
            "hash_policy": HASH_POLICY_V0,
            **(
                {
                    "preview_provider": "fixture",
                    "preview_policy": "read-only-fixture",
                }
                if preview_provider is not None
                else {}
            ),
        },
    )


def _evaluate_entry(
    root: Path,
    entry: ManifestEntry,
    *,
    preview_provider: FixturePreviewProvider | None = None,
    preview_inputs: dict[str, str],
) -> list[SyncDryRunItem]:
    source = (root / entry.source_path).resolve()
    target = (root / entry.target_path).resolve()
    hashes: dict[str, str | None] = {
        "expected_source_hash": entry.source_hash,
        "actual_source_hash": hash_file(source) if source.is_file() else None,
        "expected_target_hash": entry.target_hash,
        "actual_target_hash": None,
        "generated_target_hash": None,
        "generated_managed_block_hash": None,
    }
    if not source.is_file():
        return [
            _item(
                entry,
                ACTION_CONFLICT,
                SEVERITY_BLOCKING,
                "source-missing",
                "Restore the source file or remove the manifest entry through an explicit decommission path.",
                "missing",
                hashes,
                details={"message": "Source path does not exist."},
            )
        ]

    if not target.exists():
        if entry.sync_mode == "whole-file" and entry.ownership == "runtime-managed":
            return [
                _item(
                    entry,
                    ACTION_CREATE,
                    SEVERITY_INFORMATIONAL,
                    None,
                    None,
                    "missing",
                    hashes,
                    marker={"expected": False, "present": False, "count": 0, "integrity": "not-expected"},
                    details={"message": "Target file is missing and whole-file runtime-managed create is safe to plan."},
                )
            ]
        return [
            _item(
                entry,
                ACTION_CONFLICT,
                SEVERITY_BLOCKING,
                "marker-missing",
                "Confirm first-create ownership before planning a managed block.",
                "missing",
                hashes,
                details={"message": "Target file is missing for a managed-block or mixed-boundary entry."},
            )
        ]

    if entry.sync_mode == "whole-file":
        hashes["actual_target_hash"] = hash_file(target)
        if hashes["actual_target_hash"] != entry.target_hash:
            return [
                _item(
                    entry,
                    ACTION_DRIFT_STOP,
                    SEVERITY_BLOCKING,
                    "target-modified",
                    "Review target changes and refresh the manifest only after confirming intent.",
                    "drifted",
                    hashes,
                    marker={"expected": False, "present": False, "count": 0, "integrity": "not-expected"},
                    details={"message": "Whole target hash differs from manifest target_hash."},
                )
            ]
        clean_item = _item(
            entry,
            ACTION_SKIP,
            SEVERITY_INFORMATIONAL,
            None,
            None,
            "clean",
            hashes,
            marker={"expected": False, "present": False, "count": 0, "integrity": "not-expected"},
            details={"message": "Target hash matches manifest target_hash; generated preview is unavailable."},
        )
        return [
            _apply_preview_to_clean_item(
                clean_item,
                entry,
                preview_provider,
                preview_inputs,
                "generated_target_hash",
            )
        ]

    parse_result = parse_marker_file(target, expected_entry_ids={entry.entry_id})
    entry_blocks = [block for block in parse_result.blocks if block.entry_id == entry.entry_id]
    orphan_items = [
        _orphan_item(entry, block, hashes)
        for block in parse_result.blocks
        if block.orphan and block.valid
    ]
    if not entry_blocks:
        return [
            _item(
                entry,
                ACTION_CONFLICT,
                SEVERITY_BLOCKING,
                "marker-missing",
                "Confirm whether this is first creation or accidental marker removal.",
                "conflicted",
                hashes,
                marker={"expected": True, "present": False, "count": 0, "integrity": "missing"},
                details={"message": "Expected managed marker is missing."},
            ),
            *orphan_items,
        ]
    marker_problem = _marker_problem(entry_blocks)
    if marker_problem is not None:
        return [
            _item(
                entry,
                ACTION_CONFLICT,
                SEVERITY_BLOCKING,
                marker_problem[0],
                marker_problem[1],
                "conflicted",
                hashes,
                marker=_marker_dict(entry_blocks[0], len(entry_blocks)),
                details={"message": "Managed marker is not safe to evaluate."},
            ),
            *orphan_items,
        ]

    block = entry_blocks[0]
    actual_block_hash = _hash_block_inner_bytes(target, block)
    hashes["actual_target_hash"] = actual_block_hash
    hashes["actual_managed_block_hash"] = actual_block_hash
    hashes["expected_managed_block_hash"] = entry.target_hash
    if actual_block_hash != entry.target_hash:
        return [
            _item(
                entry,
                ACTION_DRIFT_STOP,
                SEVERITY_BLOCKING,
                "target-modified",
                "Review target managed block changes and refresh the manifest only after confirming intent.",
                "drifted",
                hashes,
                marker=_marker_dict(block, len(entry_blocks)),
                details={"message": "Managed block hash differs from manifest target_hash."},
            ),
            *orphan_items,
        ]
    clean_item = _item(
        entry,
        ACTION_SKIP,
        SEVERITY_INFORMATIONAL,
        None,
        None,
        "clean",
        hashes,
        marker=_marker_dict(block, len(entry_blocks)),
        details={"message": "Managed block hash matches manifest target_hash; generated preview is unavailable."},
    )
    return [
        _apply_preview_to_clean_item(
            clean_item,
            entry,
            preview_provider,
            preview_inputs,
            "generated_managed_block_hash",
        ),
        *orphan_items,
    ]


def _item(
    entry: ManifestEntry,
    action: str,
    severity: str,
    stop_reason: str | None,
    recovery_hint: str | None,
    drift_state: str,
    hashes: dict[str, str | None],
    *,
    marker: dict | None = None,
    details: dict | None = None,
) -> SyncDryRunItem:
    return SyncDryRunItem(
        entry_id=entry.entry_id,
        action=action,
        severity=severity,
        stop_reason=stop_reason,
        recovery_hint=recovery_hint,
        source_path=entry.source_path,
        target_path=entry.target_path,
        ownership=entry.ownership,
        sync_mode=entry.sync_mode,
        drift_state=drift_state,
        hashes=hashes,
        marker=marker,
        details=details or {},
    )


def _orphan_item(entry: ManifestEntry, block: MarkerBlock, hashes: dict[str, str | None]) -> SyncDryRunItem:
    return SyncDryRunItem(
        entry_id=f"orphan_{block.entry_id}",
        action=ACTION_ORPHAN_WARNING,
        severity=SEVERITY_WARNING,
        stop_reason="orphaned-managed-block",
        recovery_hint="Review the marker manually; do not remove it automatically without decommission policy.",
        source_path=None,
        target_path=entry.target_path,
        ownership="mixed-boundary",
        sync_mode=entry.sync_mode,
        drift_state="orphaned",
        hashes={key: None for key in hashes},
        marker=_marker_dict(block, 1),
        details={"message": "AIOS managed marker exists without a matching manifest entry."},
    )


def _apply_preview_to_clean_item(
    item: SyncDryRunItem,
    entry: ManifestEntry,
    provider: FixturePreviewProvider | None,
    preview_inputs: dict[str, str],
    generated_hash_field: str,
) -> SyncDryRunItem:
    if provider is None:
        return item

    input_fixture = preview_inputs.get(entry.entry_id)
    if not input_fixture:
        return _copy_item_with_preview(
            item,
            hashes=dict(item.hashes),
            details={
                **item.details,
                "preview_unavailable_reason": "preview-mapping-missing",
            },
        )

    preview = provider.preview(input_fixture)
    hashes = dict(item.hashes)
    if preview.generated_target_hash is not None:
        hashes["generated_target_hash"] = preview.generated_target_hash
    if preview.generated_managed_block_hash is not None:
        hashes["generated_managed_block_hash"] = preview.generated_managed_block_hash

    details = {
        **item.details,
        "preview": {
            "provider": "fixture",
            "preview_available": preview.preview_available,
            "generated_content_kind": preview.generated_content_kind,
            "provenance": preview.provenance,
        },
        "preview_unavailable_reason": preview.unavailable_reason,
    }

    generated_hash = hashes.get(generated_hash_field)
    actual_hash = hashes.get("actual_target_hash")
    if preview.preview_available and generated_hash and actual_hash and generated_hash != actual_hash:
        details["message"] = "Generated preview differs from clean target; update candidate is read-only."
        return _copy_item_with_preview(
            item,
            action=ACTION_UPDATE,
            hashes=hashes,
            details=details,
        )

    if preview.preview_available and generated_hash and actual_hash and generated_hash == actual_hash:
        details["message"] = "Generated preview matches clean target; no update candidate is needed."
    elif not preview.preview_available:
        details["message"] = "Generated preview is unavailable; preserving existing dry-run result."
    return _copy_item_with_preview(item, hashes=hashes, details=details)


def _copy_item_with_preview(
    item: SyncDryRunItem,
    *,
    action: str | None = None,
    hashes: dict,
    details: dict,
) -> SyncDryRunItem:
    return SyncDryRunItem(
        entry_id=item.entry_id,
        action=action or item.action,
        severity=item.severity,
        stop_reason=item.stop_reason,
        recovery_hint=item.recovery_hint,
        source_path=item.source_path,
        target_path=item.target_path,
        ownership=item.ownership,
        sync_mode=item.sync_mode,
        drift_state=item.drift_state,
        hashes=hashes,
        marker=item.marker,
        details=details,
    )


def _marker_problem(blocks: list[MarkerBlock]) -> tuple[str, str] | None:
    if len(blocks) > 1:
        return "marker-duplicated", "Remove duplicate markers before sync can be planned."
    block = blocks[0]
    if block.valid:
        return None
    if INTEGRITY_BEGIN_DUPLICATED in block.problems or INTEGRITY_END_DUPLICATED in block.problems:
        return "marker-duplicated", "Remove duplicate markers before sync can be planned."
    return "marker-corrupted", "Repair marker boundaries manually after review."


def _marker_dict(block: MarkerBlock, count: int) -> dict:
    return {
        "expected": True,
        "present": block.begin_line is not None or block.end_line is not None,
        "count": count,
        "entry_id": block.entry_id,
        "marker_version": block.marker_version,
        "marker_style": block.marker_style,
        "begin_line": block.begin_line,
        "end_line": block.end_line,
        "integrity": block.integrity,
        "problems": block.problems,
        "orphan": block.orphan,
        "nested": block.nested,
        "duplicate": block.duplicate,
    }


def _hash_block_inner_bytes(path: Path, block: MarkerBlock) -> str:
    lines = path.read_bytes().splitlines(keepends=True)
    start = block.begin_line or 0
    end = (block.end_line or 1) - 1
    return hash_managed_block_inner_bytes(b"".join(lines[start:end]))


def _message_text(item: SyncDryRunItem) -> str:
    detail = item.details.get("message") if item.details else None
    return str(detail or item.stop_reason or item.action)


def _marker_line(item: SyncDryRunItem) -> int | None:
    marker = item.marker or {}
    return marker.get("begin_line") or marker.get("end_line")


def _display_path(root: Path, path: Path) -> str:
    try:
        return rel_path(root, path)
    except ValueError:
        return str(path)
