from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ...filesystem import read_text, rel_path
from ..result import ValidationRun
from ..targets import ValidationTarget


REQUIRED_FRONTMATTER_FIELDS = {
    "name",
    "type",
    "version",
    "updated",
    "role",
    "level",
    "tools",
    "domain_rules",
    "operation_rules",
    "validators",
}

REFERENCE_FIELDS = {"domain_rules", "operation_rules", "validators"}


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

    metadata = parse_simple_frontmatter(frontmatter)
    for field in sorted(REQUIRED_FRONTMATTER_FIELDS):
        if is_empty(metadata.get(field)):
            run.add(
                "agent",
                "missing_required_frontmatter_field",
                "error",
                f"Agent frontmatter is missing required field: {field}",
                path=source,
                details={"field": field},
            )

    for field in sorted(REFERENCE_FIELDS):
        for reference in as_list(metadata.get(field)):
            if not reference:
                continue
            if not _looks_like_ai_path(reference):
                run.add(
                    "agent",
                    "weak_reference_path",
                    "warning",
                    f"Agent reference is not a canonical .ai path: {reference}",
                    path=source,
                    details={"field": field, "reference": reference},
                )
                continue
            referenced_path = root / reference
            if not referenced_path.is_file():
                run.add(
                    "agent",
                    "missing_reference_path",
                    "error",
                    f"Agent {field} reference does not exist: {reference}",
                    path=source,
                    details={"field": field, "reference": reference},
                )


def extract_frontmatter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    return None


def parse_simple_frontmatter(frontmatter: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in frontmatter.splitlines():
        if not raw_line.strip():
            continue
        list_match = re.match(r"^\s*-\s+(?P<value>.+?)\s*$", raw_line)
        if list_match and current_key is not None:
            data.setdefault(current_key, []).append(_clean_scalar(list_match.group("value")))
            continue

        key_match = re.match(r"^(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)$", raw_line)
        if not key_match:
            current_key = None
            continue

        key = key_match.group("key")
        value = key_match.group("value").strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
            data[key] = [_clean_scalar(item) for item in items]
        else:
            data[key] = _clean_scalar(value)

    return data


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return len([item for item in value if str(item).strip()]) == 0
    return str(value).strip() == ""


def _clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")


def _looks_like_ai_path(reference: str) -> bool:
    return reference.startswith(".ai/") and reference.endswith(".md")
