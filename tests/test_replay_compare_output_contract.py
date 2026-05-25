from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from aios.status import SEVERITY_ERROR
from aios.sync.replay import ReplayComparisonIssue
from aios.validate.engine import run_validation
from aios.validate.targets import resolve_targets


ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "tests" / "fixtures" / "sync" / "real_previews" / "replay"
MANIFEST = "tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json"
NON_MANIFEST = "tests/fixtures/sync/manifests/non_manifest.json"


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "aios", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def json_cli(*args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = cli(*args)
    return completed, json.loads(completed.stdout)


def copy_replay_tree(tmp_path: Path) -> Path:
    destination = tmp_path / "replay"
    shutil.copytree(REPLAY, destination)
    return destination / "manifests" / "replay_manifest.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_no_flag_native_json_contract_remains_static_only() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["summary"] == {"errors": 0, "warnings": 0, "info": 2, "results": 2}
    assert [result["code"] for result in data["results"]] == [
        "replay_manifest_checked",
        "human_review_checks_skipped",
    ]
    assert all(result.get("details", {}).get("comparison_mode") != "fixture" for result in data["results"])


def test_no_flag_envelope_v2_contract_remains_static_only() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"
    assert data["meta"]["summary_only"] is False
    assert "replay_compare" not in data["meta"]
    assert "comparison_mode" not in data["meta"]
    assert [result["code"] for result in data["payload"]["results"]] == [
        "replay_manifest_checked",
        "human_review_checks_skipped",
    ]


def test_opt_in_native_json_success_contract() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json", "--replay-compare", "fixture")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["summary"] == {"errors": 0, "warnings": 0, "info": 3, "results": 3}

    checked = next(result for result in data["results"] if result["code"] == "replay_comparison_checked")
    assert checked["validator"] == "replay-manifest"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["details"]["comparison_mode"] == "fixture"
    assert checked["details"]["cases"] == 10


def test_opt_in_envelope_v2_success_contract() -> None:
    completed, data = json_cli(
        "validate",
        MANIFEST,
        "--json",
        "--envelope-v2",
        "--replay-compare",
        "fixture",
    )

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"
    assert data["meta"]["replay_compare"] == "fixture"
    assert data["meta"]["comparison_mode"] == "fixture"
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["mutation_performed"] is False

    payload_checked = next(result for result in data["payload"]["results"] if result["code"] == "replay_comparison_checked")
    assert payload_checked["details"]["comparison_mode"] == "fixture"
    message = next(message for message in data["messages"] if message["code"] == "replay_comparison_checked")
    assert message["details"]["validator"] == "replay-manifest"
    assert message["details"]["comparison_mode"] == "fixture"
    assert message["details"]["cases"] == 10


def test_opt_in_mismatch_native_contract_preserves_helper_details(monkeypatch) -> None:
    def fake_compare(expected: dict[str, Any], candidate: dict[str, Any], case_id: str | None = None):
        return [
            ReplayComparisonIssue(
                code="replay-provenance-mismatch",
                severity=SEVERITY_ERROR,
                message="Replay comparison field mismatch: provenance",
                case_id=case_id,
                comparison_field="provenance",
                expected_summary="object(keys=source_paths,source_hashes)",
                actual_summary="object(keys=source_paths)",
            )
        ]

    import aios.validate.validators.replay_manifest as replay_validator

    monkeypatch.setattr(replay_validator, "compare_replay_outputs", fake_compare)
    result = run_validation(ROOT, resolve_targets(ROOT, path_arg=MANIFEST), replay_compare="fixture")
    data = result.to_dict()

    assert data["status"] == "fail"
    assert data["summary"]["errors"] == 10
    assert not any(item["code"] == "replay_comparison_checked" for item in data["results"])
    mismatch = next(item for item in data["results"] if item["code"] == "replay-provenance-mismatch")
    assert mismatch["severity"] == "error"
    assert mismatch["status"] == "fail"
    assert mismatch["details"]["case_id"] == "whole_file_lf"
    assert mismatch["details"]["comparison_field"] == "provenance"
    assert mismatch["details"]["comparison_mode"] == "fixture"
    assert mismatch["details"]["expected_summary"] == "object(keys=source_paths,source_hashes)"
    assert mismatch["details"]["actual_summary"] == "object(keys=source_paths)"


def test_opt_in_mismatch_envelope_contract_preserves_message_details(monkeypatch) -> None:
    def fake_compare(expected: dict[str, Any], candidate: dict[str, Any], case_id: str | None = None):
        return [
            ReplayComparisonIssue(
                code="replay-hash-mismatch",
                severity=SEVERITY_ERROR,
                message="Replay comparison field mismatch: generated_bytes_hash",
                case_id=case_id,
                comparison_field="generated_bytes_hash",
                expected_value="sha256:" + "a" * 64,
                actual_value="sha256:" + "b" * 64,
            )
        ]

    import aios.validate.validators.replay_manifest as replay_validator
    from aios.envelope import build_envelope

    monkeypatch.setattr(replay_validator, "compare_replay_outputs", fake_compare)
    result = run_validation(ROOT, resolve_targets(ROOT, path_arg=MANIFEST), replay_compare="fixture")
    legacy = result.to_dict()
    envelope = build_envelope("validate", legacy, root=str(ROOT), full=legacy)
    envelope["meta"].update(
        {
            "replay_compare": "fixture",
            "comparison_mode": "fixture",
            "provider_execution": False,
            "mutation_performed": False,
        }
    )

    assert envelope["schema_version"] == "aios.command_result.v2"
    assert envelope["command"] == "validate"
    assert envelope["status"] == "fail"
    assert envelope["target"]["kind"] == "replay-manifest"
    assert envelope["meta"]["replay_compare"] == "fixture"
    assert any(result["code"] == "replay-hash-mismatch" for result in envelope["payload"]["results"])
    message = next(message for message in envelope["messages"] if message["code"] == "replay-hash-mismatch")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["details"]["validator"] == "replay-manifest"
    assert message["details"]["case_id"] == "whole_file_lf"
    assert message["details"]["comparison_field"] == "generated_bytes_hash"
    assert message["details"]["comparison_mode"] == "fixture"
    assert message["details"]["expected_value"] == "sha256:" + "a" * 64
    assert message["details"]["actual_value"] == "sha256:" + "b" * 64


def test_static_validation_failure_short_circuits_output_contract(tmp_path: Path, monkeypatch) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["cases"][1]["case_id"] = data["cases"][0]["case_id"]
    write_json(manifest, data)
    called = False

    def fake_compare(expected: dict[str, Any], candidate: dict[str, Any], case_id: str | None = None):
        nonlocal called
        called = True
        return []

    import aios.validate.validators.replay_manifest as replay_validator

    monkeypatch.setattr(replay_validator, "compare_replay_outputs", fake_compare)
    result = run_validation(ROOT, resolve_targets(ROOT, path_arg=str(manifest)), replay_compare="fixture")
    data = result.to_dict()

    assert data["status"] == "fail"
    assert called is False
    assert any(item["code"] == "duplicate_case_id" for item in data["results"])
    assert not any(item["code"] == "replay_comparison_checked" for item in data["results"])


def test_usage_errors_contract() -> None:
    unsupported = cli("validate", MANIFEST, "--replay-compare", "provider")
    non_manifest = cli("validate", NON_MANIFEST, "--replay-compare", "fixture")
    no_target = cli("validate", "--replay-compare", "fixture")

    assert unsupported.returncode == 2
    assert "unsupported replay compare mode" in unsupported.stderr
    assert non_manifest.returncode == 2
    assert "only valid for replay manifest targets" in non_manifest.stderr
    assert no_target.returncode == 2
    assert "requires a replay manifest target" in no_target.stderr
