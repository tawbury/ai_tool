"""Read-only sync planning primitives for future AIOS dry-run support."""

from .hash import (
    HASH_POLICY_V0,
    format_sha256,
    hash_bytes,
    hash_file,
    hash_managed_block_inner_bytes,
    is_valid_hash_string,
)
from .manifest import (
    MANIFEST_SCHEMA_VERSION,
    ManifestEntry,
    ManifestIssue,
    ManifestValidationResult,
    SyncManifest,
    load_manifest,
    validate_manifest_data,
)
from .markers import (
    AnchorRecord,
    MarkerBlock,
    MarkerEvent,
    MarkerParseResult,
    parse_marker_file,
    parse_marker_text,
)
from .preview import (
    PREVIEW_INPUT_SCHEMA_VERSION,
    PREVIEW_OUTPUT_SCHEMA_VERSION,
    FixturePreviewProvider,
    PreviewInput,
    PreviewOutput,
    load_preview_index,
    load_preview_input,
    load_preview_output,
)
from .dry_run import run_sync_dry_run
from .result import SYNC_DRY_RUN_SCHEMA_VERSION, SyncDryRunResult

__all__ = [
    "HASH_POLICY_V0",
    "MANIFEST_SCHEMA_VERSION",
    "PREVIEW_INPUT_SCHEMA_VERSION",
    "PREVIEW_OUTPUT_SCHEMA_VERSION",
    "FixturePreviewProvider",
    "ManifestEntry",
    "ManifestIssue",
    "AnchorRecord",
    "MarkerBlock",
    "MarkerEvent",
    "MarkerParseResult",
    "ManifestValidationResult",
    "PreviewInput",
    "PreviewOutput",
    "SyncManifest",
    "format_sha256",
    "hash_bytes",
    "hash_file",
    "hash_managed_block_inner_bytes",
    "is_valid_hash_string",
    "load_manifest",
    "load_preview_index",
    "load_preview_input",
    "load_preview_output",
    "parse_marker_file",
    "parse_marker_text",
    "run_sync_dry_run",
    "SYNC_DRY_RUN_SCHEMA_VERSION",
    "SyncDryRunResult",
    "validate_manifest_data",
]
