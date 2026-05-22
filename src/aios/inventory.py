from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .filesystem import read_text, rel_path
from .frontmatter import as_list, extract_frontmatter


INVENTORY_TYPES = {"agent", "skill", "workflow", "validator", "rule", "command"}

_CACHE: dict[tuple[str, str], list["InventoryItem"]] = {}


@dataclass(frozen=True)
class InventoryItem:
    type: str
    name: str
    path: str
    canonical_path: str
    relative_path: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_metadata: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": self.type,
            "name": self.name,
            "path": self.path,
            "canonical_path": self.canonical_path,
            "relative_path": self.relative_path,
        }
        if self.tags:
            data["tags"] = self.tags
        if include_metadata and self.metadata:
            data["metadata"] = self.metadata
        return data


@dataclass(frozen=True)
class RepositoryInventory:
    root: str
    items: list[InventoryItem]

    @property
    def counts(self) -> dict[str, int]:
        counts = {item_type: 0 for item_type in sorted(INVENTORY_TYPES)}
        for item in self.items:
            counts[item.type] = counts.get(item.type, 0) + 1
        return counts

    def filter_type(self, item_type: str | None) -> "RepositoryInventory":
        if item_type is None:
            return self
        return RepositoryInventory(
            root=self.root,
            items=[item for item in self.items if item.type == item_type],
        )

    def to_dict(self, summary_only: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": "aios.inventory.v0",
            "status": "pass",
            "root": self.root,
            "summary": {
                "total": len(self.items),
                "counts": self.counts,
            },
        }
        if not summary_only:
            data["items"] = [item.to_dict() for item in self.items]
        return data


def discover_agents(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "agent", ".ai/agents", "*.agent.md", _strip_named_suffix(".agent"))


def discover_skills(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "skill", ".ai/skills", "**/*.skill.md", _strip_named_suffix(".skill"))


def discover_workflows(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "workflow", ".ai/workflows", "*.workflow.md", _strip_named_suffix(".workflow"))


def discover_validators(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "validator", ".ai/validators", "**/*.md", _strip_markdown_suffix)


def discover_rules(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "rule", ".ai/rules", "**/*.md", _strip_markdown_suffix)


def discover_commands(root: Path) -> list[InventoryItem]:
    return _discover_cached(root, "command", ".ai/commands", "**/*.command.md", _strip_named_suffix(".command"))


def build_inventory(root: Path) -> RepositoryInventory:
    items = [
        *discover_agents(root),
        *discover_skills(root),
        *discover_workflows(root),
        *discover_validators(root),
        *discover_rules(root),
        *discover_commands(root),
    ]
    items.sort(key=lambda item: (item.type, item.relative_path))
    return RepositoryInventory(root=str(root), items=items)


def _discover_cached(
    root: Path,
    item_type: str,
    base_relative: str,
    pattern: str,
    name_resolver,
) -> list[InventoryItem]:
    cache_key = (str(root.resolve()), item_type)
    if cache_key not in _CACHE:
        _CACHE[cache_key] = _discover(root, item_type, base_relative, pattern, name_resolver)
    return list(_CACHE[cache_key])


def _discover(
    root: Path,
    item_type: str,
    base_relative: str,
    pattern: str,
    name_resolver,
) -> list[InventoryItem]:
    base = root / base_relative
    if not base.is_dir():
        return []
    items = [
        _build_item(root, path, item_type, name_resolver(path))
        for path in sorted(base.glob(pattern))
        if path.is_file()
    ]
    return items


def _build_item(root: Path, path: Path, item_type: str, name: str) -> InventoryItem:
    relative = rel_path(root, path)
    metadata = _read_frontmatter_metadata(path)
    tags = as_list(metadata.get("tags")) if metadata else []
    return InventoryItem(
        type=item_type,
        name=name,
        path=str(path.resolve()),
        canonical_path=relative,
        relative_path=relative,
        tags=tags,
        metadata=metadata,
    )


def _read_frontmatter_metadata(path: Path) -> dict[str, Any]:
    try:
        block = extract_frontmatter(read_text(path))
    except OSError:
        return {}
    if block is None:
        return {}
    return block.data


def _strip_named_suffix(suffix: str):
    def resolve(path: Path) -> str:
        name = _strip_markdown_suffix(path)
        if name.endswith(suffix):
            return name[: -len(suffix)]
        return name

    return resolve


def _strip_markdown_suffix(path: Path) -> str:
    name = path.name
    if name.endswith(".md"):
        return name[:-3]
    return path.stem
