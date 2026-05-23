from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .filesystem import read_text, rel_path
from .inventory import RepositoryInventory, build_inventory
from .semantic_loader.models import VALID_PROFILES
from .status import (
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
)


SCHEMA_VERSION_V0 = "aios.activation.v0"
SCHEMA_VERSION_V1 = "aios.activation.v1"
SUPPORTED_SCHEMA_VERSIONS = {SCHEMA_VERSION_V0, SCHEMA_VERSION_V1}

RUNTIME_MODES = {"validation", "context", "review", "planning"}

V0_ACTIVE_SET_KEYS = ("agents", "skills", "workflows", "validators")
V1_ACTIVE_SET_KEYS = (*V0_ACTIVE_SET_KEYS, "rules")
ACTIVE_SET_KEYS = V1_ACTIVE_SET_KEYS
ACTIVE_SET_TYPE_MAP = {
    "agents": "agent",
    "skills": "skill",
    "workflows": "workflow",
    "validators": "validator",
    "rules": "rule",
}


@dataclass(frozen=True)
class ActivationConfig:
    schema_version: str
    active_set: dict[str, list[str]]
    profiles: dict[str, Any]
    runtime_mode: str | None = None
    rule_sets: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "active_set": self.active_set,
            "profiles": self.profiles,
        }
        if self.runtime_mode is not None:
            data["runtime_mode"] = self.runtime_mode
        if self.rule_sets:
            data["rule_sets"] = self.rule_sets
        return data


@dataclass(frozen=True)
class ActivationIssue:
    code: str
    severity: str
    message: str
    field: str | None = None
    reference: str | None = None

    @property
    def status(self) -> str:
        if self.severity == SEVERITY_ERROR:
            return STATUS_FAIL
        if self.severity == SEVERITY_WARNING:
            return STATUS_WARN
        return STATUS_PASS

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
        }
        if self.field:
            data["field"] = self.field
        if self.reference:
            data["reference"] = self.reference
        return data


@dataclass(frozen=True)
class ActivationReference:
    type: str
    reference: str
    resolved: bool
    canonical_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": self.type,
            "reference": self.reference,
            "resolved": self.resolved,
        }
        if self.canonical_path:
            data["canonical_path"] = self.canonical_path
        return data


@dataclass
class ActivationResult:
    root: str
    path: str
    config: ActivationConfig
    issues: list[ActivationIssue] = field(default_factory=list)
    references: list[ActivationReference] = field(default_factory=list)
    inactive_counts: dict[str, int] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if any(issue.severity == SEVERITY_ERROR for issue in self.issues):
            return STATUS_FAIL
        if any(issue.severity == SEVERITY_WARNING for issue in self.issues):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SEVERITY_ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SEVERITY_WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SEVERITY_INFO)

    def to_dict(self, summary_only: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": "aios.activation.result.v0",
            "status": self.status,
            "root": self.root,
            "path": self.path,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
                "activation_schema_version": self.config.schema_version,
                "references": len(self.references),
                "resolved_references": sum(1 for ref in self.references if ref.resolved),
                "missing_references": sum(1 for ref in self.references if not ref.resolved),
                "inactive_counts": self.inactive_counts,
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }
        if not summary_only:
            data["activation"] = self.config.to_dict()
            data["references"] = [ref.to_dict() for ref in self.references]
        return data


def load_activation(path: Path) -> ActivationConfig:
    return activation_from_data(_parse_activation_yaml(read_text(path)))


def activation_from_data(data: dict[str, Any]) -> ActivationConfig:
    schema_version = str(data.get("schema_version", ""))
    active_set_raw = data.get("active_set")
    profiles_raw = data.get("profiles")
    active_set: dict[str, list[str]] = {}
    if isinstance(active_set_raw, dict):
        for key in _active_set_keys_for_schema(schema_version):
            if key in active_set_raw or key in V0_ACTIVE_SET_KEYS:
                active_set[key] = _as_string_list(active_set_raw.get(key))
    profiles: dict[str, Any] = {}
    if isinstance(profiles_raw, dict):
        if profiles_raw.get("default_loader") is not None:
            profiles["default_loader"] = str(profiles_raw.get("default_loader"))
        if schema_version == SCHEMA_VERSION_V1 or "agent_loader_overrides" in profiles_raw:
            profiles["agent_loader_overrides"] = _as_string_map(profiles_raw.get("agent_loader_overrides"))
        if schema_version == SCHEMA_VERSION_V1 or "workflow_loader_overrides" in profiles_raw:
            profiles["workflow_loader_overrides"] = _as_string_map(profiles_raw.get("workflow_loader_overrides"))
    return ActivationConfig(
        schema_version=schema_version,
        active_set=active_set,
        profiles=profiles,
        runtime_mode=str(data.get("runtime_mode", "")).strip() or None,
        rule_sets=_as_rule_sets(data.get("rule_sets")),
        raw=data,
    )


def validate_activation_schema(config: ActivationConfig) -> list[ActivationIssue]:
    issues: list[ActivationIssue] = []
    if not config.schema_version:
        issues.append(
            ActivationIssue(
                "missing_schema_version",
                SEVERITY_ERROR,
                "Activation file must define schema_version.",
                field="schema_version",
            )
        )
    elif config.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        issues.append(
            ActivationIssue(
                "unknown_schema_version",
                SEVERITY_WARNING,
                f"Activation schema_version is not a supported schema: {config.schema_version}",
                field="schema_version",
            )
        )

    if not isinstance(config.raw.get("active_set"), dict):
        issues.append(
            ActivationIssue(
                "missing_active_set",
                SEVERITY_ERROR,
                "Activation file must define active_set.",
                field="active_set",
            )
        )
    for key in V0_ACTIVE_SET_KEYS:
        if key not in config.active_set:
            issues.append(
                ActivationIssue(
                    "missing_active_set_key",
                    SEVERITY_WARNING,
                    f"active_set should define {key}.",
                    field=f"active_set.{key}",
            )
        )
    if config.schema_version == SCHEMA_VERSION_V1:
        if not config.runtime_mode:
            issues.append(
                ActivationIssue(
                    "missing_runtime_mode",
                    SEVERITY_WARNING,
                    "Activation v1 should define runtime_mode.",
                    field="runtime_mode",
                )
            )
        elif config.runtime_mode not in RUNTIME_MODES:
            issues.append(
                ActivationIssue(
                    "unknown_runtime_mode",
                    SEVERITY_ERROR,
                    f"runtime_mode does not match a known activation runtime mode: {config.runtime_mode}",
                    field="runtime_mode",
                    reference=config.runtime_mode,
                )
            )

    if not isinstance(config.raw.get("profiles"), dict):
        issues.append(
            ActivationIssue(
                "missing_profiles",
                SEVERITY_ERROR,
                "Activation file must define profiles.",
                field="profiles",
            )
        )
    default_loader = config.profiles.get("default_loader")
    if not default_loader:
        issues.append(
            ActivationIssue(
                "missing_default_loader",
                SEVERITY_ERROR,
                "profiles.default_loader is required.",
                field="profiles.default_loader",
            )
        )
    elif default_loader not in VALID_PROFILES:
        issues.append(
            ActivationIssue(
                "unknown_default_loader",
                SEVERITY_ERROR,
                f"profiles.default_loader does not match a known semantic loader profile: {default_loader}",
                field="profiles.default_loader",
                reference=default_loader,
            )
        )
    if config.schema_version == SCHEMA_VERSION_V1:
        issues.extend(_validate_loader_overrides(config))
        issues.extend(_validate_rule_sets(config))
    return issues


def validate_activation_references(
    config: ActivationConfig,
    inventory: RepositoryInventory,
) -> tuple[list[ActivationIssue], list[ActivationReference], dict[str, int]]:
    issues: list[ActivationIssue] = []
    references: list[ActivationReference] = []
    inventory_by_type = _inventory_lookup(inventory)
    active_canonical_by_type: dict[str, set[str]] = {item_type: set() for item_type in ACTIVE_SET_TYPE_MAP.values()}

    for key in _active_set_keys_for_schema(config.schema_version):
        item_type = ACTIVE_SET_TYPE_MAP[key]
        lookup = inventory_by_type[item_type]
        for raw_reference in config.active_set.get(key, []):
            normalized = raw_reference.strip()
            matched = lookup.get(normalized)
            if matched is None:
                issues.append(
                    ActivationIssue(
                        "unknown_activation_reference",
                        SEVERITY_ERROR,
                        f"Activation reference does not resolve against inventory: {normalized}",
                        field=f"active_set.{key}",
                        reference=normalized,
                    )
                )
                references.append(ActivationReference(item_type, normalized, False))
                continue
            active_canonical_by_type[item_type].add(matched.canonical_path)
            references.append(
                ActivationReference(
                    item_type,
                    normalized,
                    True,
                    canonical_path=matched.canonical_path,
                )
            )

    inactive_counts: dict[str, int] = {}
    active_item_types = {ACTIVE_SET_TYPE_MAP[key] for key in _active_set_keys_for_schema(config.schema_version)}
    for item_type in sorted(active_item_types):
        total = len([item for item in inventory.items if item.type == item_type])
        active = len(active_canonical_by_type[item_type])
        inactive_counts[item_type] = max(0, total - active)

    issues.extend(_validate_override_references(config, inventory_by_type))
    issues.extend(_validate_rule_set_references(config, inventory_by_type))

    return issues, references, inactive_counts


def validate_activation_sets(config: ActivationConfig) -> list[ActivationIssue]:
    issues: list[ActivationIssue] = []
    for key in active_set_keys_for_config(config):
        references = config.active_set.get(key, [])
        if not references:
            issues.append(
                ActivationIssue(
                    "empty_activation_list",
                    SEVERITY_INFO,
                    f"active_set.{key} is empty.",
                    field=f"active_set.{key}",
                )
            )
        for reference in _duplicate_references(references):
            issues.append(
                ActivationIssue(
                    "duplicate_activation_reference",
                    SEVERITY_WARNING,
                    f"active_set.{key} contains a duplicate activation reference: {reference}",
                    field=f"active_set.{key}",
                    reference=reference,
                )
            )
    return issues


def run_activation_check(root: Path, path: Path) -> ActivationResult:
    config = load_activation(path)
    inventory = build_inventory(root)
    schema_issues = validate_activation_schema(config)
    set_issues = validate_activation_sets(config)
    reference_issues, references, inactive_counts = validate_activation_references(config, inventory)
    return ActivationResult(
        root=str(root),
        path=rel_path(root, path) if _is_relative_to(path, root) else str(path),
        config=config,
        issues=[*schema_issues, *set_issues, *reference_issues],
        references=references,
        inactive_counts=inactive_counts,
    )


def _parse_activation_yaml(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, line.strip()))
    parsed, _ = _parse_map(lines, 0, 0)
    return parsed


def _inventory_lookup(inventory: RepositoryInventory):
    lookup: dict[str, dict[str, Any]] = {item_type: {} for item_type in ACTIVE_SET_TYPE_MAP.values()}
    for item in inventory.items:
        if item.type not in lookup:
            continue
        lookup[item.type][item.name] = item
        lookup[item.type][item.canonical_path] = item
        lookup[item.type][item.relative_path] = item
        metadata_name = item.metadata.get("name") if item.metadata else None
        if metadata_name:
            lookup[item.type][str(metadata_name)] = item
    return lookup


def _active_set_keys_for_schema(schema_version: str) -> tuple[str, ...]:
    if schema_version == SCHEMA_VERSION_V1:
        return V1_ACTIVE_SET_KEYS
    return V0_ACTIVE_SET_KEYS


def active_set_keys_for_config(config: ActivationConfig) -> tuple[str, ...]:
    return tuple(config.active_set)


def _duplicate_references(references: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for reference in references:
        normalized = reference.strip()
        if not normalized:
            continue
        if normalized in seen:
            duplicates.add(normalized)
        seen.add(normalized)
    return sorted(duplicates)


def _validate_loader_overrides(config: ActivationConfig) -> list[ActivationIssue]:
    issues: list[ActivationIssue] = []
    for field in ("agent_loader_overrides", "workflow_loader_overrides"):
        overrides = config.profiles.get(field, {})
        if not isinstance(overrides, dict):
            issues.append(
                ActivationIssue(
                    "invalid_loader_overrides",
                    SEVERITY_ERROR,
                    f"profiles.{field} must be a mapping.",
                    field=f"profiles.{field}",
                )
            )
            continue
        for reference, profile in overrides.items():
            if profile not in VALID_PROFILES:
                issues.append(
                    ActivationIssue(
                        "unknown_loader_override",
                        SEVERITY_ERROR,
                        f"profiles.{field}.{reference} does not match a known semantic loader profile: {profile}",
                        field=f"profiles.{field}.{reference}",
                        reference=profile,
                    )
                )
    return issues


def _validate_rule_sets(config: ActivationConfig) -> list[ActivationIssue]:
    issues: list[ActivationIssue] = []
    if not config.rule_sets:
        return issues
    for name, rule_set in config.rule_sets.items():
        for key in ("domain_rules", "operation_rules"):
            if key in rule_set and not isinstance(rule_set[key], list):
                issues.append(
                    ActivationIssue(
                        "invalid_rule_set",
                        SEVERITY_ERROR,
                        f"rule_sets.{name}.{key} must be a list.",
                        field=f"rule_sets.{name}.{key}",
                    )
                )
    return issues


def _validate_override_references(
    config: ActivationConfig,
    inventory_by_type: dict[str, dict[str, Any]],
) -> list[ActivationIssue]:
    if config.schema_version != SCHEMA_VERSION_V1:
        return []
    issues: list[ActivationIssue] = []
    override_fields = {
        "agent_loader_overrides": "agent",
        "workflow_loader_overrides": "workflow",
    }
    for field, item_type in override_fields.items():
        overrides = config.profiles.get(field, {})
        if not isinstance(overrides, dict):
            continue
        lookup = inventory_by_type[item_type]
        for reference in overrides:
            if reference not in lookup:
                issues.append(
                    ActivationIssue(
                        "unknown_loader_override_target",
                        SEVERITY_ERROR,
                        f"profiles.{field} target does not resolve against inventory: {reference}",
                        field=f"profiles.{field}",
                        reference=reference,
                    )
                )
    return issues


def _validate_rule_set_references(
    config: ActivationConfig,
    inventory_by_type: dict[str, dict[str, Any]],
) -> list[ActivationIssue]:
    if config.schema_version != SCHEMA_VERSION_V1:
        return []
    issues: list[ActivationIssue] = []
    lookup = inventory_by_type["rule"]
    for name, rule_set in config.rule_sets.items():
        for key in ("domain_rules", "operation_rules"):
            for reference in rule_set.get(key, []):
                if reference not in lookup:
                    issues.append(
                        ActivationIssue(
                            "unknown_rule_set_reference",
                            SEVERITY_ERROR,
                            f"rule_sets.{name}.{key} reference does not resolve against rule inventory: {reference}",
                            field=f"rule_sets.{name}.{key}",
                            reference=reference,
                        )
                    )
    return issues


def _parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    data: dict[str, Any] = {}
    while index < len(lines):
        line_indent, stripped = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent or stripped.startswith("- ") or ":" not in stripped:
            break
        key, value = _split_key_value(stripped)
        if value:
            data[key] = _parse_scalar_or_inline_list(value)
            index += 1
            continue
        next_index = index + 1
        if next_index >= len(lines) or lines[next_index][0] <= line_indent:
            data[key] = {}
            index = next_index
            continue
        next_indent, next_stripped = lines[next_index]
        if next_stripped.startswith("- "):
            data[key], index = _parse_list(lines, next_index, next_indent)
        else:
            data[key], index = _parse_map(lines, next_index, next_indent)
    return data, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    values: list[Any] = []
    while index < len(lines):
        line_indent, stripped = lines[index]
        if line_indent != indent or not stripped.startswith("- "):
            break
        values.append(_clean_scalar(stripped[2:]))
        index += 1
    return values, index


def _split_key_value(line: str) -> tuple[str, str]:
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar_or_inline_list(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        return [_clean_scalar(item) for item in value[1:-1].split(",") if item.strip()]
    return _clean_scalar(value)


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _as_string_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key).strip(): str(item).strip()
        for key, item in value.items()
        if str(key).strip() and str(item).strip()
    }


def _as_rule_sets(value: Any) -> dict[str, dict[str, list[str]]]:
    if not isinstance(value, dict):
        return {}
    rule_sets: dict[str, dict[str, list[str]]] = {}
    for name, raw_rule_set in value.items():
        if not isinstance(raw_rule_set, dict):
            continue
        rule_sets[str(name)] = {
            "domain_rules": _as_string_list(raw_rule_set.get("domain_rules")),
            "operation_rules": _as_string_list(raw_rule_set.get("operation_rules")),
        }
    return rule_sets


def _clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
