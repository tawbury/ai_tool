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


def test_no_flag_native_json_remains_unchanged() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "replay-manifest"
    assert not any(result["code"] == "replay_comparison_checked" for result in data["results"])
    assert not any(result.get("details", {}).get("comparison_mode") == "fixture" for result in data["results"])


def test_no_flag_envelope_v2_remains_unchanged() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "replay-manifest"
    assert "replay_compare" not in data["meta"]
    assert "comparison_mode" not in data["meta"]
    assert not any(result["code"] == "replay_comparison_checked" for result in data["payload"]["results"])


def test_replay_compare_fixture_native_json_success() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json", "--replay-compare", "fixture")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["target"]["kind"] == "replay-manifest"
    checked = next(result for result in data["results"] if result["code"] == "replay_comparison_checked")
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["details"]["comparison_mode"] == "fixture"
    assert checked["details"]["cases"] == 10


def test_replay_compare_fixture_envelope_v2_meta() -> None:
    completed, data = json_cli(
        "validate",
        MANIFEST,
        "--json",
        "--envelope-v2",
        "--replay-compare",
        "fixture",
    )

    assert completed.returncode == 0
    assert data["command"] == "validate"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["replay_compare"] == "fixture"
    assert data["meta"]["comparison_mode"] == "fixture"
    assert data["meta"]["provider_execution"] is False
    assert data["meta"]["mutation_performed"] is False
    assert any(result["code"] == "replay_comparison_checked" for result in data["payload"]["results"])


def test_comparison_mismatch_preserves_helper_code_and_details(monkeypatch) -> None:
    def fake_compare(expected: dict[str, Any], candidate: dict[str, Any], case_id: str | None = None):
        return [
            ReplayComparisonIssue(
                code="replay-hash-mismatch",
                severity=SEVERITY_ERROR,
                message="Replay comparison field mismatch: generated_target_hash",
                case_id=case_id,
                comparison_field="generated_target_hash",
                expected_value="sha256:" + "1" * 64,
                actual_value="sha256:" + "2" * 64,
            )
        ]

    import aios.validate.validators.replay_manifest as replay_validator

    monkeypatch.setattr(replay_validator, "compare_replay_outputs", fake_compare)
    targets = resolve_targets(ROOT, path_arg=MANIFEST)
    result = run_validation(ROOT, targets, replay_compare="fixture")
    data = result.to_dict()

    assert result.status == "fail"
    mismatch = next(item for item in data["results"] if item["code"] == "replay-hash-mismatch")
    assert mismatch["severity"] == "error"
    assert mismatch["status"] == "fail"
    assert mismatch["details"]["case_id"] == "whole_file_lf"
    assert mismatch["details"]["comparison_field"] == "generated_target_hash"
    assert mismatch["details"]["comparison_mode"] == "fixture"
    assert mismatch["details"]["expected_value"] == "sha256:" + "1" * 64
    assert mismatch["details"]["actual_value"] == "sha256:" + "2" * 64


def test_static_validation_failure_short_circuits_comparison(tmp_path: Path, monkeypatch) -> None:
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
    targets = resolve_targets(ROOT, path_arg=str(manifest))
    result = run_validation(ROOT, targets, replay_compare="fixture")
    result_data = result.to_dict()

    assert result.status == "fail"
    assert called is False
    assert any(item["code"] == "duplicate_case_id" for item in result_data["results"])
    assert not any(item["code"] == "replay_comparison_checked" for item in result_data["results"])


def test_unsupported_replay_compare_value_is_usage_error() -> None:
    completed = cli("validate", MANIFEST, "--replay-compare", "provider")

    assert completed.returncode == 2
    assert "unsupported replay compare mode" in completed.stderr


def test_replay_compare_on_non_replay_manifest_is_usage_error() -> None:
    completed = cli("validate", NON_MANIFEST, "--replay-compare", "fixture")

    assert completed.returncode == 2
    assert "only valid for replay manifest targets" in completed.stderr


def test_replay_compare_without_target_is_usage_error() -> None:
    completed = cli("validate", "--replay-compare", "fixture")

    assert completed.returncode == 2
    assert "requires a replay manifest target" in completed.stderr
