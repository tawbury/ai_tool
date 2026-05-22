from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..filesystem import list_skill_files, read_text, rel_path


@dataclass
class ValidationTarget:
    kind: str
    path: Path | None
    label: str

    def to_dict(self, root: Path) -> dict[str, str]:
        data = {"kind": self.kind, "label": self.label}
        if self.path is not None:
            try:
                data["path"] = rel_path(root, self.path)
            except ValueError:
                data["path"] = str(self.path)
        return data


def resolve_targets(
    root: Path,
    path_arg: str | None = None,
    agent: str | None = None,
    workflow: str | None = None,
) -> list[ValidationTarget]:
    if sum(bool(value) for value in (path_arg, agent, workflow)) > 1:
        raise ValueError("Use only one of <path>, --agent, or --workflow.")

    if agent:
        agent_path = _resolve_agent(root, agent)
        return [ValidationTarget("agent", agent_path, agent)]

    if workflow:
        workflow_path = _resolve_workflow(root, workflow)
        return [ValidationTarget("workflow", workflow_path, workflow)]

    if path_arg:
        path = (root / path_arg).resolve() if not Path(path_arg).is_absolute() else Path(path_arg).resolve()
        return [ValidationTarget(_kind_for_path(root, path), path, path_arg)]

    targets: list[ValidationTarget] = []
    agents_root = root / ".ai" / "agents"
    if agents_root.is_dir():
        targets.extend(ValidationTarget("agent", path, path.stem) for path in sorted(agents_root.glob("*.agent.md")))
    targets.extend(ValidationTarget("skill", path, path.stem) for path in list_skill_files(root))
    workflows_root = root / ".ai" / "workflows"
    if workflows_root.is_dir():
        targets.extend(
            ValidationTarget("workflow", path, path.stem)
            for path in sorted(workflows_root.glob("*.workflow.md"))
        )
    targets.extend(
        ValidationTarget("activation", path, path.stem)
        for path in _list_activation_files(root)
    )
    targets.append(ValidationTarget("validator-index", root / ".ai" / "validators" / "validator_index.md", "validator-index"))
    return targets


def _resolve_agent(root: Path, agent: str) -> Path:
    normalized = agent.removesuffix(".agent.md")
    if normalized.endswith(".agent"):
        normalized = normalized.removesuffix(".agent")
    return root / ".ai" / "agents" / f"{normalized}.agent.md"


def _resolve_workflow(root: Path, workflow: str) -> Path:
    normalized = workflow.removesuffix(".workflow.md")
    if normalized.endswith(".workflow"):
        normalized = normalized.removesuffix(".workflow")
    return root / ".ai" / "workflows" / f"{normalized}.workflow.md"


def _kind_for_path(root: Path, path: Path) -> str:
    try:
        relative = rel_path(root, path)
    except ValueError:
        return "file"
    if relative.startswith(".ai/agents/") and relative.endswith(".agent.md"):
        return "agent"
    if relative.endswith(".skill.md"):
        return "skill"
    if relative.startswith(".ai/workflows/") and relative.endswith(".workflow.md"):
        return "workflow"
    if relative == ".ai/validators/validator_index.md":
        return "validator-index"
    if path.suffix.lower() in {".yaml", ".yml"} and _is_activation_file(path):
        return "activation"
    return "file"


def _list_activation_files(root: Path) -> list[Path]:
    ai_root = root / ".ai"
    if not ai_root.is_dir():
        return []
    paths = [*ai_root.glob("**/*.yaml"), *ai_root.glob("**/*.yml")]
    return sorted(path for path in paths if path.is_file() and _is_activation_file(path))


def _is_activation_file(path: Path) -> bool:
    try:
        text = read_text(path)
    except OSError:
        return False
    return (
        "schema_version:" in text
        and "active_set:" in text
        and "profiles:" in text
    )
