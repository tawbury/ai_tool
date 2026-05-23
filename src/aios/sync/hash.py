from __future__ import annotations

import hashlib
import re
from pathlib import Path


HASH_ALGORITHM = "sha256"
HASH_POLICY_V0 = {
    "version": "aios.hash_policy.v0",
    "algorithm": HASH_ALGORITHM,
    "encoding": "observed-utf8-bytes",
    "line_endings": "preserve",
    "trailing_newline": "preserve",
    "managed_block_marker_lines": "exclude",
}

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def is_valid_hash_string(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))


def format_sha256(digest: bytes) -> str:
    return f"{HASH_ALGORITHM}:{digest.hex()}"


def hash_bytes(data: bytes) -> str:
    return format_sha256(hashlib.sha256(data).digest())


def hash_file(path: Path) -> str:
    """Hash observed file bytes without newline, BOM, or text normalization."""
    return hash_bytes(path.read_bytes())


def hash_text_as_observed_utf8(text: str) -> str:
    return hash_bytes(text.encode("utf-8"))


def hash_managed_block_inner_bytes(inner_content: bytes) -> str:
    """Hash marker inner bytes only.

    The marker parser is intentionally not part of Bundle 1. Callers must pass
    only the bytes between begin/end marker lines, excluding the marker lines.
    """
    return hash_bytes(inner_content)
