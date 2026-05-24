from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "tests" / "fixtures" / "sync" / "real_previews" / "replay"
MANIFEST = REPLAY / "manifests" / "replay_manifest.json"


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "aios", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_json(path: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = cli("validate", str(path), "--json")
    return completed, json.loads(completed.stdout)


def copy_replay_tree(tmp_path: Path) -> Path:
    destination = tmp_path / "replay"
    shutil.copytree(REPLAY, destination)
    return destination / "manifests" / "replay_manifest.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def assert_fails_with(path: Path, code: str) -> dict[str, Any]:
    completed, data = validate_json(path)

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert data["target"]["kind"] == "replay-manifest"
    assert data["status"] == "fail"
    assert any(result["code"] == code for result in data["results"])
    return data


def test_valid_replay_manifest_target_passes() -> None:
    completed = cli("validate", str(MANIFEST))

    assert completed.returncode == 0
    assert "Status: pass" in completed.stdout
    assert "replay_manifest_checked" in completed.stdout


def test_valid_replay_manifest_json_shape() -> None:
    completed, data = validate_json(MANIFEST)

    assert completed.returncode == 0
    assert data["schema_version"] == "aios.validate.result.v0"
    assert data["target"]["kind"] == "replay-manifest"
    assert data["status"] == "pass"
    checked = next(result for result in data["results"] if result["code"] == "replay_manifest_checked")
    assert checked["details"]["schema_version"] == "aios.preview_replay_manifest.v0"
    assert checked["details"]["provider_id"] == "aios.preview.example"
    assert checked["details"]["provider_version"] == "0.1.0"
    assert checked["details"]["cases"] == 10


def test_invalid_schema_version_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["schema_version"] = "aios.preview_replay_manifest.v999"
    write_json(manifest, data)

    assert_fails_with(manifest, "unsupported_schema_version")


def test_missing_provider_snapshot_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    snapshot = manifest.parent.parent / "provider_snapshots" / "aios_preview_example_0_1_0.json"
    snapshot.unlink()

    assert_fails_with(manifest, "provider_snapshot_missing")


def test_provider_id_version_mismatch_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    snapshot = manifest.parent.parent / "provider_snapshots" / "aios_preview_example_0_1_0.json"
    data = read_json(snapshot)
    data["provider_version"] = "0.2.0"
    write_json(snapshot, data)

    assert_fails_with(manifest, "provider_identity_mismatch")


def test_duplicate_case_id_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["cases"][1]["case_id"] = data["cases"][0]["case_id"]
    write_json(manifest, data)

    assert_fails_with(manifest, "duplicate_case_id")


def test_unsafe_fixture_path_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["cases"][0]["input_fixture"] = "../inputs/whole_file_lf_input.json"
    write_json(manifest, data)

    assert_fails_with(manifest, "unsafe_fixture_path")


def test_missing_fixture_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    data = read_json(manifest)
    data["cases"][0]["expected_output_fixture"] = "outputs/missing_output.json"
    write_json(manifest, data)

    assert_fails_with(manifest, "replay_fixture_missing")


def test_placeholder_hash_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    output = manifest.parent.parent / "outputs" / "whole_file_lf_output.json"
    data = read_json(output)
    data["generated_bytes_hash"] = "sha256:<source>"
    write_json(output, data)

    assert_fails_with(manifest, "placeholder_hash")


def test_unavailable_output_with_generated_hash_fails(tmp_path: Path) -> None:
    manifest = copy_replay_tree(tmp_path)
    output = manifest.parent.parent / "outputs" / "unavailable_adapter_output.json"
    data = read_json(output)
    data["generated_bytes_hash"] = "sha256:1111111111111111111111111111111111111111111111111111111111111111"
    write_json(output, data)

    assert_fails_with(manifest, "unavailable_generated_hash_present")


def test_unrelated_json_is_not_misclassified() -> None:
    completed, data = validate_json(ROOT / "tests" / "fixtures" / "sync" / "manifests" / "non_manifest.json")

    assert completed.returncode == 0
    assert data["target"]["kind"] == "file"
    assert any(result["code"] == "unsupported_target_kind" for result in data["results"])
