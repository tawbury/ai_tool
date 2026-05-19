from __future__ import annotations

from pathlib import Path

from .filesystem import (
    find_symlinks,
    find_utf8_bom_files,
    list_files,
    list_skill_files,
    list_workflow_files,
    read_text,
    rel_path,
)
from .markdown_refs import (
    extract_ai_path_refs,
    extract_markdown_file_links,
    extract_obsidian_file_links,
    extract_skill_refs,
    extract_workflow_refs,
    has_fenced_yaml,
    slice_between,
)
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
AGENT_REQUIRED_FIELDS = [
    "name",
    "type",
    "version",
    "updated",
    "role",
    "level",
    "tools",
    "domain_rules",
    "operation_rules",
    "validators",
]
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
    skill_files = list_skill_files(root)
    workflow_files = list_workflow_files(root)
    result.files_scanned = len(all_files)
    result.skills_found = len(skill_files)
    result.workflows_found = len(workflow_files)

    _check_required_structure(root, result)
    _check_root_adapters(root, result)
    _check_agent_frontmatter(root, result)
    _check_skill_references(root, result, skill_files)
    _check_workflow_references(root, result)
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


def _check_agent_frontmatter(root: Path, result: InspectResult) -> None:
    agents_root = root / ".ai" / "agents"
    agent_files = sorted(agents_root.glob("*.agent.md")) if agents_root.is_dir() else []
    if not agent_files:
        result.add("agent-frontmatter-inventory", "fail", "No agent files found.", ".ai/agents")
        return

    for path in agent_files:
        source = rel_path(root, path)
        text = read_text(path)
        frontmatter = _extract_frontmatter(text)
        if frontmatter is None:
            result.add("agent-frontmatter-present", "fail", "Agent frontmatter missing.", source)
            continue
        result.add("agent-frontmatter-present", "pass", "Agent frontmatter exists.", source)

        data = _parse_simple_frontmatter(frontmatter)
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

        for field in ("domain_rules", "operation_rules", "validators"):
            for ref in _as_list(data.get(field)):
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


def _extract_frontmatter(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    return None


def _parse_simple_frontmatter(frontmatter: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            current = data.setdefault(current_key, [])
            if isinstance(current, list):
                current.append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
        else:
            data[key] = value.strip('"').strip("'")
    return data


def _as_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    if isinstance(value, str) and value:
        return [value]
    return []


def _check_skill_references(root: Path, result: InspectResult, skill_files: list[Path]) -> None:
    inventory = {rel_path(root, path): path for path in skill_files}
    by_name: dict[str, list[str]] = {}
    for relative in inventory:
        by_name.setdefault(Path(relative).name, []).append(relative)

    if skill_files:
        result.add(
            "skill-inventory",
            "info",
            f"Found {len(skill_files)} skill files.",
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


def _check_workflow_references(root: Path, result: InspectResult) -> None:
    workflow_files = {
        rel_path(root, path): path for path in list_workflow_files(root)
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
        target = _resolve_relative_link(root, path, ref.raw)
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
        refs = [*extract_markdown_file_links(text), *extract_obsidian_file_links(text)]
        for ref in refs:
            raw = ref.raw.strip()
            if not _is_obvious_relative_file_link(raw):
                continue
            target = _resolve_relative_link(root, path, raw)
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


def _is_obvious_relative_file_link(raw: str) -> bool:
    if "://" in raw or raw.startswith("#"):
        return False
    if any(token in raw for token in ("<", ">", "*", "[", "]", " ")):
        return False
    if not raw.endswith(".md"):
        return False
    return raw.startswith("../") or raw.startswith("./") or "/" in raw


def _resolve_relative_link(root: Path, source: Path, raw: str) -> Path | None:
    clean = raw.split("#", 1)[0].split("|", 1)[0].strip()
    if not clean:
        return None
    if clean.startswith(".ai/"):
        return root / clean
    return (source.parent / clean).resolve()


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
