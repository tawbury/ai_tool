from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..filesystem import read_text, rel_path
from ..inventory import InventoryItem, build_inventory


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
        agent_path = _resolve_inventory_path(root, "agent", agent) or _resolve_agent(root, agent)
        return [ValidationTarget("agent", agent_path, agent)]

    if workflow:
        workflow_path = _resolve_inventory_path(root, "workflow", workflow) or _resolve_workflow(root, workflow)
        return [ValidationTarget("workflow", workflow_path, workflow)]

    if path_arg:
        path = (root / path_arg).resolve() if not Path(path_arg).is_absolute() else Path(path_arg).resolve()
        return [ValidationTarget(_kind_for_path(root, path), path, path_arg)]

    targets: list[ValidationTarget] = []
    inventory = build_inventory(root)
    targets.extend(_targets_from_inventory(inventory.items, "agent"))
    targets.extend(_targets_from_inventory(inventory.items, "skill"))
    targets.extend(_targets_from_inventory(inventory.items, "workflow"))
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


def _resolve_inventory_path(root: Path, item_type: str, reference: str) -> Path | None:
    normalized = reference.strip()
    suffix_stripped = _strip_reference_suffix(item_type, normalized)
    for item in build_inventory(root).items:
        if item.type != item_type:
            continue
        candidates = {
            item.name,
            item.canonical_path,
            item.relative_path,
            Path(item.path).name,
            Path(item.path).stem,
        }
        metadata_name = item.metadata.get("name") if item.metadata else None
        if metadata_name:
            candidates.add(str(metadata_name))
        if normalized in candidates or suffix_stripped in candidates:
            return Path(item.path)
    return None


def _strip_reference_suffix(item_type: str, reference: str) -> str:
    if item_type == "agent":
        normalized = reference.removesuffix(".agent.md")
        return normalized.removesuffix(".agent") if normalized.endswith(".agent") else normalized
    if item_type == "workflow":
        normalized = reference.removesuffix(".workflow.md")
        return normalized.removesuffix(".workflow") if normalized.endswith(".workflow") else normalized
    return reference


def _targets_from_inventory(items: list[InventoryItem], item_type: str) -> list[ValidationTarget]:
    return [
        ValidationTarget(item_type, Path(item.path), item.name)
        for item in items
        if item.type == item_type
    ]


def _kind_for_path(root: Path, path: Path) -> str:
    try:
        relative = rel_path(root, path)
    except ValueError:
        relative = ""
    if relative:
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
    if path.suffix.lower() == ".json":
        if _is_sync_manifest_file(path):
            return "sync-manifest"
        if _is_replay_manifest_file(path):
            return "replay-manifest"
        if _is_provider_capability_file(path):
            return "provider-capability"
        if _is_provider_execution_trace_file(path):
            return "provider-execution-trace"
        if _is_sandbox_policy_file(path):
            return "sandbox-policy"
        if _is_sandbox_result_file(path):
            return "sandbox-result"
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


def _is_sync_manifest_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    schema_version = data.get("schema_version")
    manifest_version = data.get("manifest_version")
    if schema_version == "aios.sync_manifest.v0" or manifest_version == "aios.sync_manifest.v0":
        return True
    # Allow schema-error validation for manifest-shaped JSON that forgot
    # schema_version, without hijacking arbitrary JSON files.
    manifest_shape = {"repository_id", "generated_at", "source_root", "target_root", "managed_entries"}
    return manifest_shape.issubset(data)


def _is_replay_manifest_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") == "aios.preview_replay_manifest.v0":
        return True
    # Allow schema-error validation for replay-manifest-shaped JSON that forgot
    # schema_version, without hijacking arbitrary JSON fixtures.
    replay_shape = {"provider", "hash_policy", "cases"}
    provider = data.get("provider")
    return replay_shape.issubset(data) and isinstance(provider, dict) and "provider_id" in provider


def _is_provider_capability_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") == "aios.provider_capability.v0":
        return True
    # Allow schema-error validation for capability-shaped JSON without
    # hijacking arbitrary provider-ish JSON files.
    capability_fields = {
        "provider_id",
        "provider_version",
        "deterministic_capable",
        "supported_sync_modes",
        "hash_policy",
        "output_affecting_config",
        "no_write_capable",
        "network_policy",
        "timeout_policy",
        "resource_policy",
        "allowed_read_roots",
        "provenance_required",
    }
    present = capability_fields.intersection(data)
    return len(present) >= 5 and ("provider_id" in data or "supported_sync_modes" in data)


def _is_provider_execution_trace_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") == "aios.provider_execution_trace.v0":
        return True
    # Allow schema-error validation for trace-shaped JSON without hijacking
    # arbitrary provider-ish JSON files.
    trace_fields = {
        "trace_id",
        "provider_id",
        "provider_version",
        "provider_mode",
        "input_hash",
        "output_hash",
        "generated_hashes",
        "duration_ms",
        "deterministic_execution",
        "no_write_confirmed",
        "network_disabled",
        "mutation_performed",
        "provenance",
    }
    present = trace_fields.intersection(data)
    return len(present) >= 6 and ("trace_id" in data or "provider_mode" in data)


def _is_sandbox_policy_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") == "aios.sandbox_policy.v0":
        return True
    # Allow schema-error validation for sandbox-policy-shaped JSON without
    # hijacking arbitrary JSON files. This runs after provider capability and
    # provider execution trace detection to preserve existing target priority.
    sandbox_policy_fields = {
        "sandbox_mode",
        "timeout_ms",
        "max_input_bytes",
        "max_output_bytes",
        "stdout_limit_bytes",
        "stderr_limit_bytes",
        "allowed_read_roots",
        "allowed_output_roots",
        "network_disabled",
        "deterministic_execution",
        "no_write_required",
        "env_policy",
        "filesystem_policy",
    }
    present = sandbox_policy_fields.intersection(data)
    return len(present) >= 5 and any(key in data for key in ("sandbox_mode", "env_policy", "filesystem_policy"))


def _is_sandbox_result_file(path: Path) -> bool:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    if data.get("schema_version") == "aios.sandbox_execution_result.v0":
        return True
    # Allow schema-error validation for sandbox-result-shaped JSON without
    # hijacking arbitrary sandbox-ish JSON files. This runs after sandbox
    # policy detection to preserve existing target priority.
    sandbox_result_fields = {
        "sandbox_mode",
        "request_id",
        "exit_code",
        "status",
        "duration_ms",
        "stdout_bytes",
        "stderr_bytes",
        "stdout_truncated",
        "stderr_truncated",
        "output_json_valid",
        "failure_code",
        "failure_message",
        "resource_limit",
        "network_disabled",
        "mutation_performed",
        "no_write_confirmed",
        "no_write_evidence",
        "trace_id",
    }
    present = sandbox_result_fields.intersection(data)
    return len(present) >= 6 and any(key in data for key in ("request_id", "status", "no_write_evidence"))
