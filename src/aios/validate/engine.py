from __future__ import annotations

from pathlib import Path

from .result import ValidationRun
from .targets import ValidationTarget
from .validators.activation import validate_activation
from .validators.agent import validate_agent
from .validators.provider_capability import validate_provider_capability
from .validators.provider_execution_trace import validate_provider_execution_trace
from .validators.replay_manifest import validate_replay_manifest
from .validators.references import validate_validator_index
from .validators.sandbox_policy import validate_sandbox_policy
from .validators.sandbox_result import validate_sandbox_result
from .validators.skill import validate_skill
from .validators.sync_manifest import validate_sync_manifest
from .validators.workflow import validate_workflow


def run_validation(root: Path, targets: list[ValidationTarget], replay_compare: str | None = None) -> ValidationRun:
    run = ValidationRun(target=_target_summary(root, targets))
    for target in targets:
        if target.path is not None and not target.path.is_file():
            run.add(
                "target",
                "missing_target",
                "error",
                "Validation target does not exist.",
                path=_target_path(root, target),
            )
            continue
        if target.kind == "activation":
            validate_activation(root, target, run)
        elif target.kind == "agent":
            validate_agent(root, target, run)
        elif target.kind == "skill":
            validate_skill(root, target, run)
        elif target.kind == "replay-manifest":
            validate_replay_manifest(root, target, run, replay_compare=replay_compare)
        elif target.kind == "provider-capability":
            validate_provider_capability(root, target, run)
        elif target.kind == "provider-execution-trace":
            validate_provider_execution_trace(root, target, run)
        elif target.kind == "sandbox-policy":
            validate_sandbox_policy(root, target, run)
        elif target.kind == "sandbox-result":
            validate_sandbox_result(root, target, run)
        elif target.kind == "sync-manifest":
            validate_sync_manifest(root, target, run)
        elif target.kind == "workflow":
            validate_workflow(root, target, run)
        elif target.kind == "validator-index":
            validate_validator_index(root, target, run)
        else:
            run.add(
                "target",
                "unsupported_target_kind",
                "warning",
                f"No v0 validator registered for target kind: {target.kind}",
                path=_target_path(root, target),
            )
    run.add(
        "human-review-boundary",
        "human_review_checks_skipped",
        "info",
        "Human-review-only quality checks are intentionally skipped in validate v0.",
    )
    return run


def _target_summary(root: Path, targets: list[ValidationTarget]) -> dict[str, str]:
    if len(targets) == 1:
        return targets[0].to_dict(root)
    return {"kind": "repository", "label": "repository", "count": str(len(targets))}


def _target_path(root: Path, target: ValidationTarget) -> str | None:
    if target.path is None:
        return None
    return target.to_dict(root).get("path")
