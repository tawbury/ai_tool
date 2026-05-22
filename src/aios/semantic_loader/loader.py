from __future__ import annotations

from pathlib import Path

from ..filesystem import read_text, rel_path
from .models import (
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

    return bundle


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
