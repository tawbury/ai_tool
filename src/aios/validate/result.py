from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..status import (
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
    VALIDATE_SEVERITY_STATUS,
)


SEVERITY_STATUS = VALIDATE_SEVERITY_STATUS


@dataclass
class ValidationMessage:
    validator: str
    code: str
    severity: str
    message: str
    path: str | None = None
    line: int | None = None
    recommendation: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        return SEVERITY_STATUS[self.severity]

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "validator": self.validator,
            "code": self.code,
            "severity": self.severity,
            "status": self.status,
            "message": self.message,
        }
        if self.path:
            data["path"] = self.path
        if self.line is not None:
            data["line"] = self.line
        if self.recommendation:
            data["recommendation"] = self.recommendation
        if self.details:
            data["details"] = self.details
        return data


@dataclass
class ValidationRun:
    target: dict[str, str]
    results: list[ValidationMessage] = field(default_factory=list)

    def add(
        self,
        validator: str,
        code: str,
        severity: str,
        message: str,
        path: str | None = None,
        line: int | None = None,
        recommendation: str | None = None,
        **details: Any,
    ) -> None:
        if severity not in SEVERITY_STATUS:
            raise ValueError(f"Unknown severity: {severity}")
        self.results.append(
            ValidationMessage(
                validator=validator,
                code=code,
                severity=severity,
                message=message,
                path=path,
                line=line,
                recommendation=recommendation,
                details=details,
            )
        )

    @property
    def status(self) -> str:
        if any(result.severity == SEVERITY_ERROR for result in self.results):
            return STATUS_FAIL
        if any(result.severity == SEVERITY_WARNING for result in self.results):
            return STATUS_WARN
        return STATUS_PASS

    @property
    def error_count(self) -> int:
        return sum(1 for result in self.results if result.severity == SEVERITY_ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for result in self.results if result.severity == SEVERITY_WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for result in self.results if result.severity == SEVERITY_INFO)

    @property
    def pass_count(self) -> int:
        return sum(1 for result in self.results if result.severity == SEVERITY_INFO)

    def to_dict(self, summary_only: bool = False, include_pass: bool = False) -> dict[str, Any]:
        results = [result.to_dict() for result in self.results]
        data: dict[str, Any] = {
            "schema_version": "aios.validate.result.v0",
            "status": self.status,
            "target": self.target,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
                "results": len(self.results),
            },
        }
        if summary_only:
            errors = [item for item in results if item["severity"] == SEVERITY_ERROR]
            warnings = [item for item in results if item["severity"] == SEVERITY_WARNING]
            info = [item for item in results if item["severity"] == SEVERITY_INFO]
            if errors:
                data["errors"] = errors
            if warnings:
                data["warnings"] = warnings
            if info:
                data["info"] = info
            return data

        # validate v0 does not record explicit pass items. Keep the parameter for
        # CLI/API symmetry without manufacturing pass results.
        _ = include_pass
        data["results"] = results
        return data
