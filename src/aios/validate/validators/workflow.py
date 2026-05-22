from __future__ import annotations

import re
from pathlib import Path

from ...filesystem import read_text, rel_path
from ..result import ValidationRun
from ..targets import ValidationTarget


REQUIRED_WORKFLOW_SECTIONS = {
    "purpose": re.compile(r"^##\s+(Purpose|Workflow Overview|Overview|Objective)\b", re.IGNORECASE | re.MULTILINE),
    "workflow_stages": re.compile(r"^##\s+(Workflow Stages|Process Stages|Workflow|Process|Execution Flow)\b", re.IGNORECASE | re.MULTILINE),
}


def validate_workflow(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    text = read_text(path)

    if not path.name.endswith(".workflow.md"):
        run.add(
            "workflow",
            "invalid_workflow_filename",
            "error",
            "Workflow files must use the .workflow.md suffix.",
            path=source,
        )

    if not re.search(r"^#\s+\S", text, flags=re.MULTILINE):
        run.add(
            "workflow",
            "missing_title",
            "error",
            "Workflow file must include a top-level title.",
            path=source,
        )

    for section, pattern in REQUIRED_WORKFLOW_SECTIONS.items():
        if not pattern.search(text):
            run.add(
                "workflow",
                "missing_required_section",
                "error",
                f"Workflow file is missing required section: {section}",
                path=source,
                details={"section": section},
            )

    if re.search(r"^##\s+(Review Criteria|Quality Gates|Performance Metrics)\b", text, flags=re.IGNORECASE | re.MULTILINE):
        run.add(
            "workflow",
            "human_review_sections_skipped",
            "info",
            "Human-review-only workflow criteria are present and intentionally not scored.",
            path=source,
        )
