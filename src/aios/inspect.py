from __future__ import annotations

from pathlib import Path

from .contracts import AGENT_REFERENCE_FIELDS, AGENT_REQUIRED_FIELDS
from .filesystem import (
    find_symlinks,
    find_utf8_bom_files,
    list_files,
    read_text,
    rel_path,
)
from .inventory import InventoryItem, build_inventory
from .markdown_refs import (
    extract_ai_path_refs,
    extract_markdown_file_links,
    extract_skill_refs,
    extract_workflow_refs,
    has_fenced_yaml,
    slice_between,
)
from .frontmatter import as_list
from .references import extract_file_links, is_obvious_relative_file_link, resolve_reference
from .result import InspectResult


REQUIRED_DIRS = [
    ".ai",
    ".ai/rules",
    ".ai/rules/domains",
    ".ai/rules/operations",
    ".ai/agents",
    ".ai/skills",
    ".ai/workflows",
    ".ai/validators",
    ".ai/commands",
    ".ai/templates",
]

ROOT_ADAPTERS = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
SKILL_REFERENCE_FILES = [
    ".ai/skills/_shared/skill_index.md",
    ".ai/agents/developer.agent.md",
    ".ai/agents/pm.agent.md",
]
WORKFLOW_REFERENCE_FILE = ".ai/workflows/README.md"
AGENT_RULES_FILE = ".ai/rules/operations/agent.rules.md"
VALIDATOR_INDEX_FILE = ".ai/validators/validator_index.md"
AGENT_ROUTING_START = "<!-- ai-config:start agent-routing v1 -->"
AGENT_ROUTING_END = "<!-- ai-config:end -->"

SKILL_RECOMMENDATIONS = {
    "dev_frontend.skill.md": ".ai/skills/developer/dev_frontend_stack_unified.skill.md",
    "pm_planning.skill.md": ".ai/skills/pm/pm_strategy_unified.skill.md or .ai/skills/_shared/execution_planning.skill.md",
    "product_analytics.skill.md": ".ai/skills/pm/pm_analytics_unified.skill.md",
    "market_research.skill.md": ".ai/skills/_shared/research_framework.skill.md",
    "pm_roadmap_management.skill.md": ".ai/skills/_shared/operational_roadmap_management.skill.md",
    "product_growth.skill.md": ".ai/skills/pm/product_retention.skill.md or .ai/skills/pm/pm_strategy_unified.skill.md",
    "product_launch.skill.md": ".ai/skills/pm/product_lifecycle_management.skill.md",
    "global_product_strategy.skill.md": ".ai/skills/pm/pm_strategy_unified.skill.md",
    "data_driven_decision_making.skill.md": ".ai/skills/_shared/decision_analysis.skill.md",
    "user_research.skill.md": ".ai/skills/_shared/research_framework.skill.md",
}

WORKFLOW_RECOMMENDATIONS = {
    "l2_review_workflow.md": ".ai/workflows/l2_review.workflow.md",
    "software_development.workflow.md.backup_20260120": "Remove stale archive reference or create an archive directory intentionally.",
}


def run_inspection(root: Path) -> InspectResult:
    result = InspectResult(root=str(root))
    all_files = list_files(root)
    inventory = build_inventory(root)
    agent_items = _inventory_items(inventory.items, "agent")
    skill_items = _inventory_items(inventory.items, "skill")
    workflow_items = _inventory_items(inventory.items, "workflow")
    result.files_scanned = len(all_files)
    result.skills_found = len(skill_items)
    result.workflows_found = len(workflow_items)

    _check_required_structure(root, result)
    _check_root_adapters(root, result)
    _check_agent_frontmatter(root, result, agent_items)
    _check_skill_references(root, result, skill_items)
    _check_workflow_references(root, result, workflow_items)
    _check_stale_cursorrules(root, result)
    _check_validator_index(root, result)
    _check_obvious_relative_links(root, result)
    _check_symlinks(root, result)
    _check_utf8_bom(root, result)
    _check_agent_routing(root, result)
    return result


def _check_required_structure(root: Path, result: InspectResult) -> None:
    for directory in REQUIRED_DIRS:
        path = root / directory
        if path.is_dir():
            result.add("required-directory", "pass", f"Required directory exists: {directory}", directory)
        else:
            result.add("required-directory", "fail", f"Required directory missing: {directory}", directory)

    rules_file = root / ".ai" / "rules" / "rules.md"
    if rules_file.is_file():
        result.add("rules-entrypoint", "pass", "Rules entrypoint exists.", ".ai/rules/rules.md")
    else:
        result.add("rules-entrypoint", "fail", "Rules entrypoint is missing.", ".ai/rules/rules.md")

    src_dir = root / "src"
    if src_dir.is_dir():
        result.add("src-directory", "info", "src directory exists.", "src")
    else:
        result.add("src-directory", "info", "src directory does not exist yet.", "src")


def _check_root_adapters(root: Path, result: InspectResult) -> None:
    for adapter in ROOT_ADAPTERS:
        if (root / adapter).is_file():
            result.add("root-adapter", "pass", f"Root adapter exists: {adapter}", adapter)
        else:
            result.add("root-adapter", "warning", f"Root adapter missing: {adapter}", adapter)


def _check_agent_frontmatter(root: Path, result: InspectResult, agent_items: list[InventoryItem]) -> None:
    if not agent_items:
        result.add("agent-frontmatter-inventory", "fail", "No agent files found.", ".ai/agents")
        return

    for item in agent_items:
        source = item.relative_path
        data = item.metadata
        if not data:
            result.add("agent-frontmatter-present", "fail", "Agent frontmatter missing.", source)
            continue
        result.add("agent-frontmatter-present", "pass", "Agent frontmatter exists.", source)

        for field in AGENT_REQUIRED_FIELDS:
            value = data.get(field)
            if value:
                result.add(
                    "agent-frontmatter-required-field",
                    "pass",
                    f"Required agent field exists: {field}",
                    source,
                    field=field,
                )
            else:
                result.add(
                    "agent-frontmatter-required-field",
                    "fail",
                    f"Required agent field missing or empty: {field}",
                    source,
                    field=field,
                )

        for field in AGENT_REFERENCE_FIELDS:
            for ref in as_list(data.get(field)):
                if (root / ref).is_file():
                    result.add(
                        "agent-frontmatter-reference",
                        "pass",
                        f"Agent frontmatter reference exists: {ref}",
                        source,
                        field=field,
                        resolved=ref,
                    )
                else:
                    result.add(
                        "agent-frontmatter-reference",
                        "fail",
                        f"Agent frontmatter reference missing: {ref}",
                        source,
                        field=field,
                    )


def _check_skill_references(root: Path, result: InspectResult, skill_items: list[InventoryItem]) -> None:
    inventory = {item.relative_path: Path(item.path) for item in skill_items}
    by_name: dict[str, list[str]] = {}
    for relative in inventory:
        by_name.setdefault(Path(relative).name, []).append(relative)

    if skill_items:
        result.add(
            "skill-inventory",
            "info",
            f"Found {len(skill_items)} skill files.",
            ".ai/skills",
        )
    else:
        result.add("skill-inventory", "fail", "No skill files found.", ".ai/skills")

    for source in SKILL_REFERENCE_FILES:
        path = root / source
        if not path.is_file():
            result.add("skill-reference-source", "fail", f"Skill reference source missing: {source}", source)
            continue
        text = read_text(path)
        refs = extract_skill_refs(text)
        if not refs:
            result.add("skill-reference-source", "warning", "No skill references found.", source)
            continue
        for ref in refs:
            raw = ref.raw.replace("\\", "/")
            candidates = _resolve_skill_ref(root, raw, inventory, by_name)
            if len(candidates) == 1:
                result.add(
                    "skill-reference-exists",
                    "pass",
                    f"Skill reference resolves: {raw}",
                    source,
                    line=ref.line,
                    resolved=candidates[0],
                )
            elif len(candidates) > 1:
                result.add(
                    "skill-reference-ambiguous",
                    "warning",
                    f"Skill reference is ambiguous: {raw}",
                    source,
                    line=ref.line,
                    candidates=candidates,
                )
            else:
                result.add(
                    "skill-reference-missing",
                    "fail",
                    f"Skill reference target missing: {raw}",
                    source,
                    line=ref.line,
                    recommendation=SKILL_RECOMMENDATIONS.get(Path(raw).name),
                )


def _resolve_skill_ref(
    root: Path,
    raw: str,
    inventory: dict[str, Path],
    by_name: dict[str, list[str]],
) -> list[str]:
    normalized = raw.removeprefix("./")
    if normalized.startswith(".ai/"):
        return [normalized] if normalized in inventory else []

    direct_shared = f".ai/skills/_shared/{normalized}"
    if direct_shared in inventory:
        return [direct_shared]

    direct_skills = f".ai/skills/{normalized}"
    if direct_skills in inventory:
        return [direct_skills]

    return sorted(by_name.get(Path(normalized).name, []))


def _check_workflow_references(root: Path, result: InspectResult, workflow_items: list[InventoryItem]) -> None:
    workflow_files = {
        item.relative_path: Path(item.path) for item in workflow_items
    }
    workflow_names = {Path(path).name: path for path in workflow_files}
    source = WORKFLOW_REFERENCE_FILE
    path = root / source
    if not path.is_file():
        result.add("workflow-reference-source", "fail", f"Workflow reference source missing: {source}", source)
        return
    text = read_text(path)
    refs = extract_workflow_refs(text)
    for ref in refs:
        raw = ref.raw.replace("\\", "/")
        if raw.startswith(".ai/"):
            candidate = raw
        elif "/" in raw:
            candidate = f".ai/workflows/{raw}"
        else:
            candidate = workflow_names.get(raw, f".ai/workflows/{raw}")

        if candidate in workflow_files:
            result.add(
                "workflow-reference-exists",
                "pass",
                f"Workflow reference resolves: {raw}",
                source,
                line=ref.line,
                resolved=candidate,
            )
        else:
            result.add(
                "workflow-reference-missing",
                "fail",
                f"Workflow reference target missing: {raw}",
                source,
                line=ref.line,
                recommendation=WORKFLOW_RECOMMENDATIONS.get(Path(raw).name),
            )


def _check_stale_cursorrules(root: Path, result: InspectResult) -> None:
    ai_root = root / ".ai"
    targets = sorted(ai_root.rglob("*.md")) if ai_root.is_dir() else []
    stale_hits: list[dict[str, object]] = []
    for path in targets:
        if not path.is_file():
            continue
        for line_number, line in enumerate(read_text(path).splitlines(), start=1):
            if ".ai/.cursorrules" in line or "../.cursorrules" in line:
                stale_hits.append({"file": rel_path(root, path), "line": line_number, "text": line.strip()})

    if stale_hits:
        result.add(
            "stale-cursorrules-reference",
            "warning",
            "Stale .ai/.cursorrules references found.",
            ".ai",
            hits=stale_hits,
            recommendation=".ai/rules/rules.md",
        )
    else:
        result.add("stale-cursorrules-reference", "pass", "No stale .ai/.cursorrules references found.", ".ai")


def _check_validator_index(root: Path, result: InspectResult) -> None:
    source = VALIDATOR_INDEX_FILE
    path = root / source
    if not path.is_file():
        result.add("validator-index-source", "fail", "validator_index.md is missing.", source)
        return

    text = read_text(path)
    refs = extract_markdown_file_links(text)
    if not refs:
        result.add("validator-index-reference", "warning", "No validator index markdown links found.", source)
        return

    for ref in refs:
        target = resolve_reference(root, path, ref.raw)
        if target and target.is_file():
            result.add(
                "validator-index-reference",
                "pass",
                f"validator_index reference exists: {ref.raw}",
                source,
                line=ref.line,
                resolved=rel_path(root, target),
            )
        else:
            result.add(
                "validator-index-reference",
                "fail",
                f"validator_index reference missing: {ref.raw}",
                source,
                line=ref.line,
            )


def _check_obvious_relative_links(root: Path, result: InspectResult) -> None:
    ai_root = root / ".ai"
    if not ai_root.is_dir():
        return

    checked = 0
    missing: list[dict[str, object]] = []
    for path in sorted(ai_root.rglob("*.md")):
        text = read_text(path)
        refs = extract_file_links(text)
        for ref in refs:
            raw = ref.raw.strip()
            if not is_obvious_relative_file_link(raw):
                continue
            target = resolve_reference(root, path, raw)
            checked += 1
            if not target or not target.is_file():
                missing.append({"file": rel_path(root, path), "line": ref.line, "target": raw})

    if missing:
        result.add(
            "obvious-relative-link",
            "warning",
            "Some obvious relative Markdown/Obsidian file links are missing.",
            ".ai",
            checked=checked,
            missing=missing[:50],
            omitted=max(0, len(missing) - 50),
        )
    else:
        result.add(
            "obvious-relative-link",
            "pass",
            f"All {checked} obvious relative Markdown/Obsidian file links resolve.",
            ".ai",
            checked=checked,
        )

def _check_symlinks(root: Path, result: InspectResult) -> None:
    paths = [root / ".ai" / "rules", root / ".ai" / "agents", root / ".ai" / "commands"]
    symlinks = find_symlinks(paths)
    if symlinks:
        result.add(
            "symlink-detection",
            "fail",
            "Symlinks found under managed rule/agent/command directories.",
            ".ai",
            paths=[rel_path(root, path) for path in symlinks],
        )
    else:
        result.add("symlink-detection", "pass", "No symlinks found under rules, agents, or commands.", ".ai")


def _check_utf8_bom(root: Path, result: InspectResult) -> None:
    bom_files = find_utf8_bom_files(root)
    if bom_files:
        result.add(
            "utf8-bom-detection",
            "fail",
            "UTF-8 BOM found in text files.",
            str(root),
            paths=[rel_path(root, path) for path in bom_files],
        )
    else:
        result.add("utf8-bom-detection", "pass", "No UTF-8 BOM found in markdown/json/yaml/toml files.", str(root))


def _check_agent_routing(root: Path, result: InspectResult) -> None:
    source = AGENT_RULES_FILE
    path = root / source
    if not path.is_file():
        result.add("agent-routing-source", "fail", f"Agent rules file missing: {source}", source)
        return

    text = read_text(path)
    has_start = AGENT_ROUTING_START in text
    has_end = AGENT_ROUTING_END in text
    if has_start and has_end:
        result.add("agent-routing-anchors", "pass", "agent-routing anchors exist.", source)
    else:
        result.add(
            "agent-routing-anchors",
            "fail",
            "agent-routing start/end anchors are missing or incomplete.",
            source,
            has_start=has_start,
            has_end=has_end,
        )
        return

    block = slice_between(text, AGENT_ROUTING_START, AGENT_ROUTING_END)
    if block is None:
        result.add("agent-routing-block", "fail", "agent-routing block could not be sliced.", source)
        return

    if has_fenced_yaml(block):
        result.add("agent-routing-yaml-fence", "pass", "agent-routing block contains a fenced YAML block.", source)
    else:
        result.add("agent-routing-yaml-fence", "fail", "agent-routing block does not contain a fenced YAML block.", source)

    for ref in extract_ai_path_refs(block):
        raw = ref.raw.rstrip(".,)")
        if (root / raw).exists():
            result.add(
                "agent-routing-path-reference",
                "pass",
                f"agent-routing path exists: {raw}",
                source,
                line=ref.line,
                resolved=raw,
            )
        else:
            result.add(
                "agent-routing-path-reference",
                "fail",
                f"agent-routing path missing: {raw}",
                source,
                line=ref.line,
            )


def _inventory_items(items: list[InventoryItem], item_type: str) -> list[InventoryItem]:
    return [item for item in items if item.type == item_type]
