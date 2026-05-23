from __future__ import annotations

from pathlib import Path

from ..filesystem import read_text, rel_path
from .models import (
    BUDGET_LIMITS,
    ContextBundle,
    ContextChunk,
    ExcludedLayer,
    LoaderInput,
    LoaderWarning,
    PROFILE_EXCLUDED_LAYERS,
    PROFILE_INCLUDE_LAYERS,
    VALID_PROFILES,
)
from .sections import extract_sections, normalize_layer


LAYER_PRIORITY = {
    "executable_contract": 1,
    "structural_rules": 2,
    "runtime_policy": 3,
    "constraints": 4,
    "input_output": 5,
    "execution_logic": 6,
    "review_criteria": 7,
    "human_review_guidance": 8,
    "philosophy": 9,
    "examples": 10,
    "performance_metrics": 11,
}


def load_context(root: Path, loader_input: LoaderInput) -> ContextBundle:
    target = _resolve_target(root, loader_input.path)
    relative = rel_path(root, target) if _is_relative_to(target, root) else str(target)
    include_layers = _normalize_layers(PROFILE_INCLUDE_LAYERS.get(loader_input.profile, set()))
    include_layers.update(_normalize_layers(loader_input.include_layers))
    cli_includes = _normalize_layers(loader_input.include_layers)
    excluded_layers = _normalize_layers(PROFILE_EXCLUDED_LAYERS.get(loader_input.profile, set()))
    excluded_layers.update(_normalize_layers(loader_input.excluded_layers))
    excluded_layers.difference_update(cli_includes)

    bundle = ContextBundle(root=str(root), profile=loader_input.profile, target=relative)
    if loader_input.profile not in VALID_PROFILES:
        bundle.warnings.append(
            LoaderWarning(
                code="unknown_profile",
                message=f"Unknown loading profile: {loader_input.profile}",
                path=loader_input.path,
            )
        )
        return bundle

    if not target.is_file():
        bundle.warnings.append(
            LoaderWarning(
                code="target_missing",
                message="Target file does not exist.",
                path=loader_input.path,
            )
        )
        return bundle

    text = read_text(target)
    sections, fallback_warnings = extract_sections(text, is_rules_file=_is_rules_file(root, target))
    for warning_code in fallback_warnings:
        if warning_code == "standard_heading_fallback":
            continue
        bundle.warnings.append(
            LoaderWarning(
                code=warning_code,
                message=_warning_message(warning_code),
                path=relative,
            )
        )

    for section in sections:
        if include_layers and section.layer not in include_layers:
            bundle.excluded.append(
                ExcludedLayer(
                    path=relative,
                    semantic_layer=section.layer,
                    line_start=section.line_start,
                    line_end=section.line_end,
                    reason="not_included_by_profile",
                )
            )
            continue
        if section.layer in excluded_layers:
            bundle.excluded.append(
                ExcludedLayer(
                    path=relative,
                    semantic_layer=section.layer,
                    line_start=section.line_start,
                    line_end=section.line_end,
                    reason="excluded_by_profile",
                )
            )
            continue
        bundle.chunks.append(
            ContextChunk(
                path=relative,
                semantic_layer=section.layer,
                content=section.content,
                line_start=section.line_start,
                line_end=section.line_end,
                extraction_method=section.method,
                confidence=section.confidence,
                chars=len(section.content),
            )
        )

    _apply_budget(bundle, loader_input.max_chars)
    return bundle


def _apply_budget(bundle: ContextBundle, max_chars: int | None) -> None:
    limits = BUDGET_LIMITS.get(bundle.profile, BUDGET_LIMITS["minimal-worker"])
    soft_chars = limits["soft_chars"]
    hard_chars = max_chars if max_chars is not None else limits["hard_chars"]
    if hard_chars < 0:
        hard_chars = 0

    budget_excluded = 0
    excluded_chars = 0
    if _used_chars(bundle.chunks) > hard_chars:
        kept, excluded = _exclude_low_priority_chunks(bundle.chunks, hard_chars)
        bundle.chunks = kept
        budget_excluded = len(excluded)
        excluded_chars = sum(chunk.chars for chunk in excluded)
        for chunk in excluded:
            bundle.excluded.append(
                ExcludedLayer(
                    path=chunk.path,
                    semantic_layer=chunk.semantic_layer,
                    line_start=chunk.line_start,
                    line_end=chunk.line_end,
                    reason="budget_excluded_low_priority",
                    chars=chunk.chars,
                    extraction_method=chunk.extraction_method,
                    confidence=chunk.confidence,
                )
            )
        if excluded:
            bundle.warnings.append(
                LoaderWarning(
                    code="budget_hard_exceeded",
                    message=(
                        f"Context exceeded hard budget of {hard_chars} chars; "
                        f"excluded {len(excluded)} lower-priority chunks."
                    ),
                    path=bundle.target,
                )
            )
            bundle.warnings.append(
                LoaderWarning(
                    code="budget_excluded_low_priority",
                    message=f"Excluded {excluded_chars} chars due to hard budget filtering.",
                    path=bundle.target,
                )
            )

    used_chars = _used_chars(bundle.chunks)
    if used_chars > soft_chars:
        bundle.warnings.append(
            LoaderWarning(
                code="budget_soft_exceeded",
                message=f"Context uses {used_chars} chars, exceeding soft budget of {soft_chars} chars.",
                path=bundle.target,
            )
        )

    bundle.budget = {
        "profile": bundle.profile,
        "soft_chars": soft_chars,
        "hard_chars": hard_chars,
        "used_chars": used_chars,
        "excluded_chars": excluded_chars,
        "budget_excluded_chunks": budget_excluded,
        "truncated_chunks": 0,
    }


def _exclude_low_priority_chunks(
    chunks: list[ContextChunk],
    hard_chars: int,
) -> tuple[list[ContextChunk], list[ContextChunk]]:
    excluded_indices: set[int] = set()
    excluded: list[ContextChunk] = []
    removal_order = sorted(
        range(len(chunks)),
        key=lambda index: (_layer_priority(chunks[index].semantic_layer), index),
        reverse=True,
    )
    for index in removal_order:
        kept = [chunk for offset, chunk in enumerate(chunks) if offset not in excluded_indices]
        if _used_chars(kept) <= hard_chars:
            break
        chunk = chunks[index]
        excluded.append(chunk)
        excluded_indices.add(index)
    kept = [chunk for offset, chunk in enumerate(chunks) if offset not in excluded_indices]
    return kept, excluded


def _used_chars(chunks: list[ContextChunk]) -> int:
    return sum(chunk.chars for chunk in chunks)


def _layer_priority(layer: str) -> int:
    return LAYER_PRIORITY.get(layer, 100)


def _normalize_layers(layers: set[str]) -> set[str]:
    return {normalize_layer(layer) for layer in layers}


def _resolve_target(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (root / path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_rules_file(root: Path, path: Path) -> bool:
    try:
        relative = rel_path(root, path)
    except ValueError:
        return False
    return relative.startswith(".ai/rules/") and relative.endswith(".rules.md") or relative == ".ai/rules/rules.md"


def _warning_message(code: str) -> str:
    messages = {
        "legacy_section_fallback": "Used legacy section fallback because governance annotations and standard headings were not found.",
        "rules_file_fallback": "Used rules-file fallback because governance annotations and standard semantic headings were not found.",
        "no_semantic_sections_found": "No governance annotations or recognized semantic sections found.",
    }
    return messages.get(code, code)
