from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SEVERITY_STATUS = {
    "info": "pass",
    "warning": "warn",
    "error": "fail",
}


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
        if any(result.severity == "error" for result in self.results):
            return "fail"
        if any(result.severity == "warning" for result in self.results):
            return "warn"
        return "pass"

    @property
    def error_count(self) -> int:
        return sum(1 for result in self.results if result.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for result in self.results if result.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for result in self.results if result.severity == "info")

    @property
    def pass_count(self) -> int:
        return sum(1 for result in self.results if result.severity == "info")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "aios.validate.result.v0",
            "status": self.status,
            "target": self.target,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
                "results": len(self.results),
            },
            "results": [result.to_dict() for result in self.results],
        }
