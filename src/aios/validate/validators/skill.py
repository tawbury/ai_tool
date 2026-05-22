from __future__ import annotations

import re
from pathlib import Path

from ...filesystem import read_text, rel_path
from ...frontmatter import extract_frontmatter
from ..result import ValidationRun
from ..targets import ValidationTarget


STANDARD_SECTION_PATTERNS = {
    "purpose": re.compile(
        r"^##\s+(Purpose|Overview|Core Purpose|Objective|Description)\b",
        re.IGNORECASE | re.MULTILINE,
    ),
    "input_output": re.compile(
        r"^##\s+(Input/Output|Input / Output|Inputs?|Outputs?|Usage)\b",
        re.IGNORECASE | re.MULTILINE,
    ),
    "execution": re.compile(
        r"^##\s+(Execution Logic|Workflow|Process|Core Logic|Core Concept|Key Capabilities|Responsibilities)\b",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def validate_skill(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    text = read_text(path)

    if not path.name.endswith(".skill.md"):
        run.add(
            "skill",
            "invalid_skill_filename",
            "error",
            "Skill files must use the .skill.md suffix.",
            path=source,
        )

    frontmatter = extract_frontmatter(text)
    if frontmatter is None:
        run.add(
            "skill",
            "missing_frontmatter",
            "error",
            "Skill file must include YAML-like frontmatter.",
            path=source,
        )
    else:
        metadata = frontmatter.data
        if not str(metadata.get("name", "")).strip():
            run.add(
                "skill",
                "missing_skill_name",
                "error",
                "Skill frontmatter is missing required field: name",
                path=source,
            )

    if not re.search(r"^#\s+\S", text, flags=re.MULTILINE):
        run.add(
            "skill",
            "missing_title",
            "error",
            "Skill file must include a top-level title.",
            path=source,
        )

    found_sections = [
        name
        for name, pattern in STANDARD_SECTION_PATTERNS.items()
        if pattern.search(text)
    ]
    if not found_sections:
        run.add(
            "skill",
            "weak_skill_structure",
            "warning",
            "Skill file does not expose a recognizable v0 purpose, usage, or execution section.",
            path=source,
        )
