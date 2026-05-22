from __future__ import annotations

from pathlib import Path

from .markdown_refs import (
    MarkdownReference,
    extract_markdown_file_links,
    extract_obsidian_file_links,
)


def extract_file_links(text: str) -> list[MarkdownReference]:
    return [*extract_markdown_file_links(text), *extract_obsidian_file_links(text)]


def is_external_or_anchor(reference: str) -> bool:
    return reference.startswith("#") or "://" in reference or reference.startswith("mailto:")


def is_obvious_relative_file_link(reference: str) -> bool:
    if is_external_or_anchor(reference):
        return False
    if any(token in reference for token in ("<", ">", "*", "[", "]", " ")):
        return False
    if not reference.endswith(".md"):
        return False
    return reference.startswith("../") or reference.startswith("./") or "/" in reference


def clean_file_reference(reference: str) -> str:
    return reference.split("#", 1)[0].split("|", 1)[0].strip()


def resolve_reference(root: Path, source: Path, reference: str) -> Path | None:
    clean = clean_file_reference(reference)
    if not clean:
        return None
    if clean.startswith(".ai/"):
        return root / clean
    return (source.parent / clean).resolve()


def resolve_ai_path(root: Path, reference: str) -> Path:
    return root / reference


def is_canonical_ai_markdown_path(reference: str) -> bool:
    return reference.startswith(".ai/") and reference.endswith(".md")

