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

__all__ = [
    "HASH_POLICY_V0",
    "MANIFEST_SCHEMA_VERSION",
    "ManifestEntry",
    "ManifestIssue",
    "ManifestValidationResult",
    "SyncManifest",
    "format_sha256",
    "hash_bytes",
    "hash_file",
    "hash_managed_block_inner_bytes",
    "is_valid_hash_string",
    "load_manifest",
    "validate_manifest_data",
]
