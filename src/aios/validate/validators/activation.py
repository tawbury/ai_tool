from __future__ import annotations

from pathlib import Path

from ...activation import (
    ACTIVE_SET_KEYS,
    ACTIVE_SET_TYPE_MAP,
    load_activation,
    validate_activation_references,
    validate_activation_schema,
)
from ...filesystem import rel_path
from ...inventory import build_inventory
from ...status import SEVERITY_INFO, SEVERITY_WARNING
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

    for key in ACTIVE_SET_KEYS:
        references_for_key = config.active_set.get(key, [])
        if not references_for_key:
            run.add(
                "activation",
                "empty_activation_list",
                SEVERITY_INFO,
                f"active_set.{key} is empty.",
                path=source,
                field=f"active_set.{key}",
            )
        _add_duplicate_reference_warnings(run, source, key, references_for_key)

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


def _add_duplicate_reference_warnings(
    run: ValidationRun,
    source: str,
    key: str,
    references: list[str],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for reference in references:
        normalized = reference.strip()
        if not normalized:
            continue
        if normalized in seen:
            duplicates.add(normalized)
        seen.add(normalized)

    for reference in sorted(duplicates):
        run.add(
            "activation",
            "duplicate_activation_reference",
            SEVERITY_WARNING,
            f"active_set.{key} contains a duplicate activation reference: {reference}",
            path=source,
            field=f"active_set.{key}",
            reference=reference,
            type=ACTIVE_SET_TYPE_MAP[key],
        )
