from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SEVERITY_ORDER = {"pass": 0, "info": 0, "warning": 1, "fail": 2}


@dataclass
class CheckResult:
    id: str
    status: str
    message: str
    source: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "status": self.status,
            "message": self.message,
        }
        if self.source is not None:
            data["source"] = self.source
        if self.details:
            data["details"] = self.details
        return data


@dataclass
class InspectResult:
    root: str
    checks: list[CheckResult] = field(default_factory=list)
    files_scanned: int = 0
    skills_found: int = 0
    workflows_found: int = 0

    def add(
        self,
        check_id: str,
        status: str,
        message: str,
        source: str | None = None,
        **details: Any,
    ) -> None:
        if status not in SEVERITY_ORDER:
            raise ValueError(f"Unknown status: {status}")
        self.checks.append(CheckResult(check_id, status, message, source, details))

    @property
    def status(self) -> str:
        if any(check.status == "fail" for check in self.checks):
            return "fail"
        if any(check.status == "warning" for check in self.checks):
            return "warning"
        return "pass"

    @property
    def error_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "fail")

    @property
    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "info")

    @property
    def pass_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "pass")

    def to_dict(self, summary_only: bool = False) -> dict[str, Any]:
        checks = self.checks
        if summary_only:
            checks = [check for check in checks if check.status != "pass"]
        return {
            "status": self.status,
            "root": self.root,
            "summary": {
                "files_scanned": self.files_scanned,
                "skills_found": self.skills_found,
                "workflows_found": self.workflows_found,
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
                "passes": self.pass_count,
            },
            "checks": [check.to_dict() for check in checks],
        }
