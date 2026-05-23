# Phase 7 Stabilization Output Contract Report

## 개요

이 문서는 Phase 7 read-only sync evaluation v0의 출력 계약 안정화 작업을 기록한다. 이번 작업은 기존 동작을 회귀 테스트로 고정하는 것이 목적이며, sync apply, 파일 mutation, manifest persistence, generated preview, repository-wide scan 같은 새 runtime capability는 추가하지 않았다.

## 변경 범위

추가한 테스트 파일은 다음과 같다.

- `tests/test_sync_output_contract.py`

이 테스트는 CLI를 실제로 실행해 native JSON, envelope v2, validate JSON, validate envelope v2, usage error exit code를 검증한다. 기존 runtime classification, dry-run evaluator, manifest validator 동작은 변경하지 않았다.

## 고정한 출력 계약

### Sync Dry-run Native JSON

`python -m aios sync --dry-run --manifest <manifest> --json` 출력에서 다음 계약을 고정했다.

- `schema_version`은 `aios.sync_dry_run.v0`
- `status`, `mode`, `manifest_path`, `summary`, `results`, `messages`, `meta`가 존재
- clean skip fixture는 `status: pass`, `summary.skip: 1`, `messages: []`
- `meta.dry_run`은 `true`
- `meta.mutation_performed`는 `false`
- clean managed block은 `action: skip`, `drift_state: clean`, `marker.integrity: valid`

### Drift-stop Native JSON

`e2e_drift_stop.json` fixture에 대해 다음 계약을 고정했다.

- CLI exit code는 `1`
- top-level `status`는 `fail`
- result action은 `drift-stop`
- `stop_reason`은 `target-modified`
- blocking message가 `target-modified` code로 보존됨

### Sync Dry-run Envelope v2

`e2e_orphan_marker.json` fixture의 envelope v2 출력에서 다음 계약을 고정했다.

- `schema_version`은 `aios.command_result.v2`
- `command`는 `sync`
- canonical `status`는 `warn`
- `target.kind`는 `sync-manifest`
- `meta.legacy_schema_version`은 `aios.sync_dry_run.v0`
- `meta.dry_run`은 `true`
- `meta.mutation_performed`는 `false`
- `payload.results`에 `skip`, `orphan-warning` 결과가 보존됨
- warning message에 `orphaned-managed-block` code가 보존됨

### Validate Sync Manifest JSON

`python -m aios validate <sync-manifest.json> --json` 출력에서 다음 계약을 고정했다.

- valid manifest는 `status: pass`
- target은 `kind: sync-manifest`로 인식됨
- `sync_manifest_checked` info result가 존재
- `details.schema_version`이 `aios.sync_manifest.v0`로 보존됨
- invalid hash fixture는 `status: fail`, `invalid_hash_format` error result를 반환
- error result는 `field`와 `entry_id` details를 보존

### Validate Sync Manifest Envelope v2

validate envelope v2 출력에서 다음 계약을 고정했다.

- `schema_version`은 `aios.command_result.v2`
- `command`는 `validate`
- target path가 보존됨
- `meta.legacy_schema_version`은 `aios.validate.result.v0`
- `payload.results`에 manifest validation result가 보존됨
- `messages`에 validator, field, entry_id details가 보존됨

### Usage Error

다음 usage error는 기존 exit code `2`를 유지하도록 고정했다.

- `python -m aios sync`
- `python -m aios sync --dry-run`
- `python -m aios sync --envelope-v2`

## 비범위

이번 안정화 작업은 다음을 구현하지 않는다.

- sync apply
- target file mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- adapter generation
- generated preview content
- default manifest discovery
- manifest preview generation
- repository-wide unmanaged scan
- force, decommission
- activation-driven sync selection
- orchestration, worker execution, workflow execution
- registry parser 또는 `.ai/registry/`
- auto-fix 또는 source mutation

## 결과

Phase 7 read-only sync evaluation v0의 핵심 출력 계약이 회귀 테스트로 고정되었다. 이후 안정화 작업은 human output snapshot, 더 넓은 envelope fixture, 문서/규칙 승격으로 이어질 수 있지만, 이번 작업만으로도 native JSON과 envelope v2의 주요 구조는 보호된다.
