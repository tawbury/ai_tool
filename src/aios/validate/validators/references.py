from __future__ import annotations

from pathlib import Path

from ...filesystem import read_text, rel_path
from ...references import extract_file_links, is_external_or_anchor, resolve_reference
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_validator_index(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    text = read_text(path)
    links = extract_file_links(text)

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
        if is_external_or_anchor(link.raw):
            continue
        resolved = resolve_reference(root, path, link.raw)
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
