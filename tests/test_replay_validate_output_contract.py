from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def test_replay_manifest_validate_native_json_pass_contract() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["target"]["path"] == MANIFEST
    assert data["summary"]["errors"] == 0
    assert data["summary"]["info"] >= 1

    checked = next(result for result in data["results"] if result["code"] == "replay_manifest_checked")
    assert checked["validator"] == "replay-manifest"
    assert checked["severity"] == "info"
    assert checked["status"] == "pass"
    assert checked["path"] == MANIFEST
    assert checked["details"]["schema_version"] == "aios.preview_replay_manifest.v0"
    assert checked["details"]["provider_id"] == "aios.preview.example"
    assert checked["details"]["provider_version"] == "0.1.0"
    assert checked["details"]["cases"] == 10


def test_replay_manifest_validate_native_json_fail_contract(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["cases"][1]["case_id"] = data["cases"][0]["case_id"]
    write_json(manifest, data)

    completed, result = json_cli("validate", str(manifest), "--json")

    assert completed.returncode == 1
    assert result["schema_version"] == "aios.validate.result.v0"
    assert result["status"] == "fail"
    assert result["target"]["kind"] == "replay-manifest"
    assert result["summary"]["errors"] >= 1

    error = next(item for item in result["results"] if item["code"] == "duplicate_case_id")
    assert error["validator"] == "replay-manifest"
    assert error["severity"] == "error"
    assert error["status"] == "fail"
    assert error["details"]["field"] == "cases[1].case_id"
    assert error["details"]["case_id"] == "whole_file_lf"


def test_replay_manifest_validate_envelope_v2_pass_contract() -> None:
    completed, data = json_cli("validate", MANIFEST, "--json", "--envelope-v2")

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.command_result.v2"
    assert data["command"] == "validate"
    assert data["status"] == "pass"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["target"]["path"] == MANIFEST
    assert data["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert data["meta"]["legacy_status"] == "pass"

    assert any(result["code"] == "replay_manifest_checked" for result in data["payload"]["results"])
    message = next(message for message in data["messages"] if message["code"] == "replay_manifest_checked")
    assert message["severity"] == "info"
    assert message["status"] == "pass"
    assert message["path"] == MANIFEST
    assert message["details"]["validator"] == "replay-manifest"
    assert message["details"]["schema_version"] == "aios.preview_replay_manifest.v0"
    assert message["details"]["provider_id"] == "aios.preview.example"
    assert message["details"]["provider_version"] == "0.1.0"
    assert message["details"]["cases"] == 10


def test_replay_manifest_validate_envelope_v2_fail_contract(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    output = manifest.parent.parent / "outputs" / "unavailable_adapter_output.json"
    data = read_json(output)
    data["generated_bytes_hash"] = "sha256:1111111111111111111111111111111111111111111111111111111111111111"
    write_json(output, data)

    completed, result = json_cli("validate", str(manifest), "--json", "--envelope-v2")

    assert completed.returncode == 1
    assert result["schema_version"] == "aios.command_result.v2"
    assert result["command"] == "validate"
    assert result["status"] == "fail"
    assert result["target"]["kind"] == "replay-manifest"
    assert result["meta"]["legacy_schema_version"] == "aios.validate.result.v0"
    assert result["meta"]["legacy_status"] == "fail"

    assert any(item["code"] == "unavailable_generated_hash_present" for item in result["payload"]["results"])
    message = next(message for message in result["messages"] if message["code"] == "unavailable_generated_hash_present")
    assert message["severity"] == "error"
    assert message["status"] == "fail"
    assert message["details"]["validator"] == "replay-manifest"
    assert message["details"]["case_id"] == "unavailable_adapter"


def test_unrelated_json_is_not_replay_manifest_contract() -> None:
    completed, data = json_cli("validate", NON_MANIFEST, "--json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert not any(result["validator"] == "replay-manifest" for result in data["results"])
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])
