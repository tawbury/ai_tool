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


ACTIVE_SET_KEYS = ("agents", "skills", "workflows", "validators")
ACTIVE_SET_TYPE_MAP = {
    "agents": "agent",
    "skills": "skill",
    "workflows": "workflow",
    "validators": "validator",
}


@dataclass(frozen=True)
class ActivationConfig:
    schema_version: str
    active_set: dict[str, list[str]]
    profiles: dict[str, str]
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "active_set": self.active_set,
            "profiles": self.profiles,
        }


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
    active_set_raw = data.get("active_set")
    profiles_raw = data.get("profiles")
    active_set: dict[str, list[str]] = {}
    if isinstance(active_set_raw, dict):
        for key in ACTIVE_SET_KEYS:
            active_set[key] = _as_string_list(active_set_raw.get(key))
    profiles: dict[str, str] = {}
    if isinstance(profiles_raw, dict):
        profiles = {str(key): str(value) for key, value in profiles_raw.items() if value is not None}
    return ActivationConfig(
        schema_version=str(data.get("schema_version", "")),
        active_set=active_set,
        profiles=profiles,
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
    elif config.schema_version != "aios.activation.v0":
        issues.append(
            ActivationIssue(
                "unknown_schema_version",
                SEVERITY_WARNING,
                f"Activation schema_version is not the v0 schema: {config.schema_version}",
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
    for key in ACTIVE_SET_KEYS:
        if key not in config.active_set:
            issues.append(
                ActivationIssue(
                    "missing_active_set_key",
                    SEVERITY_WARNING,
                    f"active_set should define {key}.",
                    field=f"active_set.{key}",
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
    return issues


def validate_activation_references(
    config: ActivationConfig,
    inventory: RepositoryInventory,
) -> tuple[list[ActivationIssue], list[ActivationReference], dict[str, int]]:
    issues: list[ActivationIssue] = []
    references: list[ActivationReference] = []
    inventory_by_type = _inventory_lookup(inventory)
    active_canonical_by_type: dict[str, set[str]] = {item_type: set() for item_type in ACTIVE_SET_TYPE_MAP.values()}

    for key, item_type in ACTIVE_SET_TYPE_MAP.items():
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
    for item_type in ACTIVE_SET_TYPE_MAP.values():
        total = len([item for item in inventory.items if item.type == item_type])
        active = len(active_canonical_by_type[item_type])
        inactive_counts[item_type] = max(0, total - active)

    return issues, references, inactive_counts


def run_activation_check(root: Path, path: Path) -> ActivationResult:
    config = load_activation(path)
    inventory = build_inventory(root)
    schema_issues = validate_activation_schema(config)
    reference_issues, references, inactive_counts = validate_activation_references(config, inventory)
    return ActivationResult(
        root=str(root),
        path=rel_path(root, path) if _is_relative_to(path, root) else str(path),
        config=config,
        issues=[*schema_issues, *reference_issues],
        references=references,
        inactive_counts=inactive_counts,
    )


def _parse_activation_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_section: str | None = None
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and ":" in stripped:
            key, value = _split_key_value(stripped)
            if value == "":
                data[key] = {}
                current_section = key
            else:
                data[key] = _parse_scalar_or_inline_list(value)
                current_section = None
            current_list_key = None
            continue

        if indent == 2 and current_section and ":" in stripped:
            key, value = _split_key_value(stripped)
            section = data.setdefault(current_section, {})
            if not isinstance(section, dict):
                continue
            if value == "":
                section[key] = []
                current_list_key = key
            else:
                section[key] = _parse_scalar_or_inline_list(value)
                current_list_key = None
            continue

        if indent >= 4 and stripped.startswith("- ") and current_section and current_list_key:
            section = data.setdefault(current_section, {})
            if isinstance(section, dict):
                values = section.setdefault(current_list_key, [])
                if isinstance(values, list):
                    values.append(_clean_scalar(stripped[2:]))
            continue

    return data


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


def _clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
