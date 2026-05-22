from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FrontmatterBlock:
    raw: str
    data: dict[str, Any]
    start_line: int
    end_line: int


def extract_frontmatter(text: str) -> FrontmatterBlock | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            raw = "\n".join(lines[1:index])
            return FrontmatterBlock(
                raw=raw,
                data=parse_simple_frontmatter(raw),
                start_line=1,
                end_line=index + 1,
            )
    return None


def parse_simple_frontmatter(frontmatter: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in frontmatter.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        list_match = re.match(r"^\s*-\s+(?P<value>.+?)\s*$", raw_line)
        if list_match and current_key is not None:
            current = data.setdefault(current_key, [])
            if isinstance(current, list):
                current.append(_clean_scalar(list_match.group("value")))
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

