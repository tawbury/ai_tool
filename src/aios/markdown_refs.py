from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SKILL_REF_RE = re.compile(r"(?P<ref>(?:\.ai/)?[A-Za-z0-9_./-]+\.skill\.md)")
WORKFLOW_REF_RE = re.compile(
    r"(?P<ref>[A-Za-z0-9_./-]+(?:\.workflow\.md|_workflow\.md|workflow_index\.md)(?:\.backup_[0-9]+)?)"
)
AI_PATH_RE = re.compile(r"(?P<ref>\.ai/[A-Za-z0-9_./-]+)")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((?P<ref>[^)]+\.md)\)")
OBSIDIAN_LINK_RE = re.compile(r"\[\[(?P<ref>[^\]|#]+\.md)(?:[|#][^\]]*)?\]\]")


@dataclass(frozen=True)
class MarkdownReference:
    raw: str
    line: int
    column: int


def extract_references(text: str, pattern: re.Pattern[str]) -> list[MarkdownReference]:
    refs: list[MarkdownReference] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in pattern.finditer(line):
            refs.append(
                MarkdownReference(
                    raw=match.group("ref"),
                    line=line_number,
                    column=match.start("ref") + 1,
                )
            )
    return refs


def extract_skill_refs(text: str) -> list[MarkdownReference]:
    return extract_references(text, SKILL_REF_RE)


def extract_workflow_refs(text: str) -> list[MarkdownReference]:
    return extract_references(text, WORKFLOW_REF_RE)


def extract_ai_path_refs(text: str) -> list[MarkdownReference]:
    return extract_references(text, AI_PATH_RE)


def extract_markdown_file_links(text: str) -> list[MarkdownReference]:
    return extract_references(text, MARKDOWN_LINK_RE)


def extract_obsidian_file_links(text: str) -> list[MarkdownReference]:
    return extract_references(text, OBSIDIAN_LINK_RE)


def has_fenced_yaml(text: str) -> bool:
    return bool(re.search(r"```ya?ml\s+.*?```", text, flags=re.IGNORECASE | re.DOTALL))


def slice_between(text: str, start_marker: str, end_marker: str) -> str | None:
    start = text.find(start_marker)
    if start == -1:
        return None
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        return None
    return text[start : end + len(end_marker)]


def reference_source(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
