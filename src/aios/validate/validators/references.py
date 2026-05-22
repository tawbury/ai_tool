from __future__ import annotations

from pathlib import Path

from ...filesystem import read_text, rel_path
from ...markdown_refs import extract_markdown_file_links, extract_obsidian_file_links
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_validator_index(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    text = read_text(path)
    links = [*extract_markdown_file_links(text), *extract_obsidian_file_links(text)]

    if not links:
        run.add(
            "references",
            "validator_index_no_links",
            "warning",
            "Validator index contains no obvious Markdown or Obsidian file links.",
            path=source,
        )
        return

    for link in links:
        if _is_external_or_anchor(link.raw):
            continue
        resolved = _resolve_link(root, path, link.raw)
        if resolved is None or not resolved.is_file():
            run.add(
                "references",
                "missing_validator_index_reference",
                "error",
                f"Validator index reference does not exist: {link.raw}",
                path=source,
                line=link.line,
                details={"reference": link.raw},
            )


def _is_external_or_anchor(reference: str) -> bool:
    return (
        reference.startswith("#")
        or "://" in reference
        or reference.startswith("mailto:")
    )


def _resolve_link(root: Path, source: Path, reference: str) -> Path | None:
    cleaned = reference.split("#", 1)[0].strip()
    if not cleaned:
        return None
    if cleaned.startswith(".ai/"):
        return root / cleaned
    return (source.parent / cleaned).resolve()
