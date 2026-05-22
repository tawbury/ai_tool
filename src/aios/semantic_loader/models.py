from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DEFAULT_EXCLUDED_LAYERS = {"examples", "philosophy", "performance_metrics"}

PROFILE_INCLUDE_LAYERS = {
    "minimal-worker": {
        "executable_contract",
        "structural_rules",
        "runtime_policy",
        "input_output",
        "execution_logic",
        "constraints",
    },
    "reviewer": {
        "executable_contract",
        "structural_rules",
        "runtime_policy",
        "input_output",
        "execution_logic",
        "constraints",
        "human_review_guidance",
        "review_criteria",
    },
    "strategist": {
        "executable_contract",
        "structural_rules",
        "runtime_policy",
        "input_output",
        "execution_logic",
        "constraints",
        "human_review_guidance",
        "review_criteria",
        "philosophy",
    },
    "validation-runtime": {
        "executable_contract",
        "structural_rules",
        "runtime_policy",
    },
}

PROFILE_EXCLUDED_LAYERS = {
    "minimal-worker": DEFAULT_EXCLUDED_LAYERS | {"human_review_guidance", "review_criteria"},
    "reviewer": DEFAULT_EXCLUDED_LAYERS,
    "strategist": {"examples", "performance_metrics"},
    "validation-runtime": DEFAULT_EXCLUDED_LAYERS | {
        "human_review_guidance",
        "review_criteria",
        "input_output",
        "execution_logic",
        "constraints",
    },
}

VALID_PROFILES = set(PROFILE_INCLUDE_LAYERS)


@dataclass
class LoaderInput:
    path: str
    profile: str = "minimal-worker"
    include_layers: set[str] = field(default_factory=set)
    excluded_layers: set[str] = field(default_factory=set)


@dataclass
class ContextChunk:
    path: str
    semantic_layer: str
    content: str
    line_start: int
    line_end: int
    extraction_method: str
    confidence: str
    chars: int

    def to_dict(self, include_content: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "path": self.path,
            "semantic_layer": self.semantic_layer,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "extraction_method": self.extraction_method,
            "confidence": self.confidence,
            "chars": self.chars,
        }
        if include_content:
            data["content"] = self.content
        return data


@dataclass
class ExcludedLayer:
    path: str
    semantic_layer: str
    line_start: int
    line_end: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "semantic_layer": self.semantic_layer,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "reason": self.reason,
        }


@dataclass
class LoaderWarning:
    code: str
    message: str
    path: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass
class ContextBundle:
    root: str
    profile: str
    target: str
    chunks: list[ContextChunk] = field(default_factory=list)
    excluded: list[ExcludedLayer] = field(default_factory=list)
    warnings: list[LoaderWarning] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "warning" if self.warnings else "pass"

    def to_dict(self, include_content: bool = True, summary_only: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": "aios.semantic_loader.bundle.v0",
            "status": self.status,
            "root": self.root,
            "profile": self.profile,
            "target": self.target,
            "summary": {
                "chunks": len(self.chunks),
                "excluded": len(self.excluded),
                "warnings": len(self.warnings),
                "chars": sum(chunk.chars for chunk in self.chunks),
            },
            "warnings": [warning.to_dict() for warning in self.warnings],
        }
        if not summary_only:
            data["chunks"] = [chunk.to_dict(include_content=include_content) for chunk in self.chunks]
            data["excluded"] = [item.to_dict() for item in self.excluded]
        return data
