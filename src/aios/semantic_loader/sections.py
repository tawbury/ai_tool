from __future__ import annotations

import re
from dataclasses import dataclass


START_RE = re.compile(r"<!--\s*ai-governance:start\s+([a-zA-Z0-9_-]+)\s+v\d+\s*-->")
END_RE = re.compile(r"<!--\s*ai-governance:end\s*-->")
INLINE_RE = re.compile(r"<!--\s*ai-governance:([a-zA-Z0-9_-]+)\s*-->")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")

STANDARD_HEADINGS = {
    "Executable Contract": "executable_contract",
    "Structural Rules": "structural_rules",
    "Runtime Policy": "runtime_policy",
    "Human Review Guidance": "human_review_guidance",
    "Review Criteria": "review_criteria",
    "Philosophy": "philosophy",
    "Examples": "examples",
}

LEGACY_HEADINGS = {
    "Validation Rules": "executable_contract",
    "Input/Output": "input_output",
    "Execution Logic": "execution_logic",
    "Constraints": "runtime_policy",
    "Quality Standards": "human_review_guidance",
    "Performance Metrics": "performance_metrics",
}

LAYER_ALIASES = {
    "contract": "executable_contract",
    "structural-rule": "structural_rules",
    "structural-rules": "structural_rules",
    "runtime-policy": "runtime_policy",
    "human-guidance": "human_review_guidance",
    "human-review-guidance": "human_review_guidance",
    "review-criteria": "review_criteria",
    "example-only": "examples",
    "examples": "examples",
    "philosophy": "philosophy",
    "performance-metrics": "performance_metrics",
    "performance_metrics": "performance_metrics",
}


@dataclass
class ExtractedSection:
    layer: str
    content: str
    line_start: int
    line_end: int
    method: str
    confidence: str


def normalize_layer(raw: str) -> str:
    cleaned = raw.strip().replace(" ", "-").lower()
    return LAYER_ALIASES.get(cleaned, cleaned.replace("-", "_"))


def extract_sections(text: str, is_rules_file: bool = False) -> tuple[list[ExtractedSection], list[str]]:
    sections = extract_annotation_sections(text)
    if sections:
        return sections, []

    sections = extract_inline_annotation_sections(text)
    if sections:
        return sections, []

    sections = extract_heading_sections(text, STANDARD_HEADINGS, "section-heading", "medium")
    if sections:
        return sections, ["standard_heading_fallback"]

    sections = extract_heading_sections(text, LEGACY_HEADINGS, "legacy-section-mapping", "low")
    if sections:
        return sections, ["legacy_section_fallback"]

    if is_rules_file and text.strip():
        line_count = max(1, len(text.splitlines()))
        return [
            ExtractedSection(
                layer="runtime_policy",
                content=text.strip(),
                line_start=1,
                line_end=line_count,
                method="rules-file-fallback",
                confidence="low",
            )
        ], ["rules_file_fallback"]

    return [], ["no_semantic_sections_found"]


def extract_annotation_sections(text: str) -> list[ExtractedSection]:
    lines = text.splitlines()
    sections: list[ExtractedSection] = []
    active_layer: str | None = None
    start_index: int | None = None
    buffer: list[str] = []

    for index, line in enumerate(lines, start=1):
        start_match = START_RE.search(line)
        if start_match and active_layer is None:
            active_layer = normalize_layer(start_match.group(1))
            start_index = index + 1
            buffer = []
            continue

        if END_RE.search(line) and active_layer is not None and start_index is not None:
            content = "\n".join(buffer).strip()
            sections.append(
                ExtractedSection(
                    layer=active_layer,
                    content=content,
                    line_start=start_index,
                    line_end=max(start_index, index - 1),
                    method="annotation-boundary",
                    confidence="high",
                )
            )
            active_layer = None
            start_index = None
            buffer = []
            continue

        if active_layer is not None:
            buffer.append(line)

    return sections


def extract_inline_annotation_sections(text: str) -> list[ExtractedSection]:
    lines = text.splitlines()
    sections: list[ExtractedSection] = []
    consumed_until = 0
    for index, line in enumerate(lines, start=1):
        if index <= consumed_until:
            continue
        match = INLINE_RE.search(line)
        if not match:
            continue
        layer = normalize_layer(match.group(1))
        block_start, block_end = _next_markdown_block(lines, index)
        if block_start is None or block_end is None:
            continue
        content = "\n".join(lines[block_start - 1 : block_end]).strip()
        if not content:
            continue
        sections.append(
            ExtractedSection(
                layer=layer,
                content=content,
                line_start=block_start,
                line_end=block_end,
                method="inline-annotation",
                confidence="high",
            )
        )
        consumed_until = block_end
    return sections


def _next_markdown_block(lines: list[str], annotation_line: int) -> tuple[int | None, int | None]:
    start = annotation_line + 1
    while start <= len(lines):
        stripped = lines[start - 1].strip()
        if stripped and not stripped.startswith("<!--"):
            break
        start += 1
    if start > len(lines):
        return None, None

    first = lines[start - 1]
    stripped_first = first.strip()

    if stripped_first.startswith("```"):
        end = start
        while end < len(lines):
            end += 1
            if lines[end - 1].strip().startswith("```"):
                break
        return start, end

    if stripped_first.startswith("|"):
        end = start
        while end + 1 <= len(lines) and lines[end].strip().startswith("|"):
            end += 1
        return start, end

    if _is_list_line(stripped_first):
        end = start
        while end + 1 <= len(lines):
            next_line = lines[end]
            stripped = next_line.strip()
            if not stripped:
                break
            if _is_list_line(stripped) or next_line.startswith((" ", "\t")):
                end += 1
                continue
            break
        return start, end

    end = start
    while end + 1 <= len(lines):
        stripped = lines[end].strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            break
        end += 1
    return start, end


def _is_list_line(stripped: str) -> bool:
    return bool(re.match(r"^([-*+]|\d+[.)])\s+", stripped))


def extract_heading_sections(
    text: str,
    heading_map: dict[str, str],
    method: str,
    confidence: str,
) -> list[ExtractedSection]:
    lines = text.splitlines()
    starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines, start=1):
        match = H2_RE.match(line)
        if not match:
            continue
        heading = match.group(1).strip()
        if heading in heading_map:
            starts.append((index, heading_map[heading]))

    sections: list[ExtractedSection] = []
    for offset, (start_line, layer) in enumerate(starts):
        next_start = starts[offset + 1][0] if offset + 1 < len(starts) else len(lines) + 1
        body_lines = lines[start_line - 1 : next_start - 1]
        content = "\n".join(body_lines).strip()
        sections.append(
            ExtractedSection(
                layer=layer,
                content=content,
                line_start=start_line,
                line_end=next_start - 1,
                method=method,
                confidence=confidence,
            )
        )
    return sections
