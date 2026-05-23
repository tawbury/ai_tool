from __future__ import annotations

import hashlib
from pathlib import Path

from aios.sync.hash import (
    hash_bytes,
    hash_file,
    hash_managed_block_inner_bytes,
    is_valid_hash_string,
)


FIXTURES = Path(__file__).parent / "fixtures" / "sync" / "hash"


def sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def test_hash_string_validation() -> None:
    assert is_valid_hash_string("sha256:" + "a" * 64)
    assert not is_valid_hash_string("sha256:" + "A" * 64)
    assert not is_valid_hash_string("md5:" + "a" * 64)
    assert not is_valid_hash_string("sha256:abc")


def test_lf_vs_crlf_hash_differs() -> None:
    lf_hash = hash_file(FIXTURES / "same_content_lf.txt")
    crlf_hash = hash_file(FIXTURES / "same_content_crlf.txt")

    assert lf_hash != crlf_hash


def test_trailing_newline_present_vs_absent_differs() -> None:
    present_hash = hash_file(FIXTURES / "trailing_newline_present.txt")
    absent_hash = hash_file(FIXTURES / "trailing_newline_absent.txt")

    assert present_hash != absent_hash


def test_utf8_korean_text_hashes_deterministically() -> None:
    path = FIXTURES / "utf8_korean_text.md"

    assert hash_file(path) == sha256("한글 텍스트\n".encode("utf-8"))


def test_utf8_bom_is_included_in_hash_bytes() -> None:
    without_bom = "utf8 text\n".encode("utf-8")
    with_bom = b"\xef\xbb\xbf" + without_bom

    assert hash_bytes(with_bom) == sha256(with_bom)
    assert hash_bytes(with_bom) != hash_bytes(without_bom)


def test_managed_block_inner_hash_accepts_inner_bytes_directly() -> None:
    inner = b"managed line 1\nmanaged line 2\n"

    assert hash_managed_block_inner_bytes(inner) == sha256(inner)
