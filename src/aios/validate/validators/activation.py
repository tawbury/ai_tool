from __future__ import annotations

from pathlib import Path

from ...activation import (
    load_activation,
    validate_activation_references,
    validate_activation_schema,
    validate_activation_sets,
)
from ...filesystem import rel_path
from ...inventory import build_inventory
from ...status import SEVERITY_INFO
from ..result import ValidationRun
from ..targets import ValidationTarget


def validate_activation(root: Path, target: ValidationTarget, run: ValidationRun) -> None:
    path = target.path
    if path is None:
        return

    source = rel_path(root, path)
    config = load_activation(path)
    inventory = build_inventory(root)

    for issue in validate_activation_schema(config):
        run.add(
            "activation",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            reference=issue.reference,
        )

    reference_issues, references, inactive_counts = validate_activation_references(config, inventory)
    for issue in reference_issues:
        run.add(
            "activation",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            reference=issue.reference,
        )

    for issue in validate_activation_sets(config):
        run.add(
            "activation",
            issue.code,
            issue.severity,
            issue.message,
            path=source,
            field=issue.field,
            reference=issue.reference,
        )

    run.add(
        "activation",
        "activation_contract_checked",
        SEVERITY_INFO,
        "Activation contract was validated without semantic loading, workflow execution, or worker dispatch.",
        path=source,
        references=len(references),
        resolved_references=sum(1 for reference in references if reference.resolved),
        missing_references=sum(1 for reference in references if not reference.resolved),
        inactive_counts=inactive_counts,
    )
