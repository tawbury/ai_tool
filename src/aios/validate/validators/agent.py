from __future__ import annotations

from pathlib import Path

from ...contracts import AGENT_REFERENCE_FIELDS, AGENT_REQUIRED_FIELDS
from ...filesystem import read_text, rel_path
from ...frontmatter import as_list, extract_frontmatter, is_empty
from ...references import is_canonical_ai_markdown_path, resolve_ai_path
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_agent(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    text = read_text(path)
    frontmatter = extract_frontmatter(text)
    source = rel_path(root, path)

    if frontmatter is None:
        run.add(
            "agent",
            "missing_frontmatter",
            "error",
            "Agent file must include YAML-like frontmatter.",
            path=source,
        )
        return

    metadata = frontmatter.data
    for field in sorted(AGENT_REQUIRED_FIELDS):
        if is_empty(metadata.get(field)):
            run.add(
                "agent",
                "missing_required_frontmatter_field",
                "error",
                f"Agent frontmatter is missing required field: {field}",
                path=source,
                details={"field": field},
            )

    for field in sorted(AGENT_REFERENCE_FIELDS):
        for reference in as_list(metadata.get(field)):
            if not reference:
                continue
            if not is_canonical_ai_markdown_path(reference):
                run.add(
                    "agent",
                    "weak_reference_path",
                    "warning",
                    f"Agent reference is not a canonical .ai path: {reference}",
                    path=source,
                    details={"field": field, "reference": reference},
                )
                continue
            referenced_path = resolve_ai_path(root, reference)
            if not referenced_path.is_file():
                run.add(
                    "agent",
                    "missing_reference_path",
                    "error",
                    f"Agent {field} reference does not exist: {reference}",
                    path=source,
                    details={"field": field, "reference": reference},
                )
