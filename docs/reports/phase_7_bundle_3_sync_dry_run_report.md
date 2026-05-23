# Phase 7 Bundle 3 Sync Dry-run 구현 보고서

## 개요

이 문서는 Phase 7 Bundle 3 `Sync Dry-run CLI Evaluation` 구현 결과를 기록한다. 이번 번들은 `python -m aios sync --dry-run`을 read-only evaluator로 추가했다.

이번 작업은 sync apply, target mutation, manifest write, transaction log persistence, rollback execution, marker insertion, marker repair, marker deletion, adapter generation, generated preview content, force, decommission, activation-driven sync selection, default manifest discovery, manifest preview generation, repository-wide unmanaged scan을 구현하지 않았다.

## 구현 범위

추가된 runtime 모듈:

- `src/aios/sync/result.py`
- `src/aios/sync/dry_run.py`

갱신된 모듈:

- `src/aios/sync/__init__.py`
- `src/aios/envelope.py`
- `src/aios/cli.py`

추가된 테스트:

- `tests/test_sync_dry_run.py`

추가된 fixture:

- `tests/fixtures/sync/sources/source_rules.md`
- `tests/fixtures/sync/targets/clean_managed.md`
- `tests/fixtures/sync/targets/drift_managed.md`
- `tests/fixtures/sync/targets/missing_marker.md`
- `tests/fixtures/sync/targets/corrupted_marker.md`
- `tests/fixtures/sync/targets/orphan_marker.md`
- `tests/fixtures/sync/manifests/e2e_clean_skip.json`
- `tests/fixtures/sync/manifests/e2e_create_whole_file.json`
- `tests/fixtures/sync/manifests/e2e_source_missing.json`
- `tests/fixtures/sync/manifests/e2e_marker_missing.json`
- `tests/fixtures/sync/manifests/e2e_marker_corrupted.json`
- `tests/fixtures/sync/manifests/e2e_drift_stop.json`
- `tests/fixtures/sync/manifests/e2e_orphan_marker.json`
- `tests/fixtures/sync/manifests/e2e_invalid_schema.json`

## CLI 동작

추가된 명령:

```bash
python -m aios sync --dry-run --manifest <path>
python -m aios sync --dry-run --manifest <path> --json
python -m aios sync --dry-run --manifest <path> --json --envelope-v2
```

강제 정책:

- `python -m aios sync`는 `--dry-run`이 없으므로 exit code 2로 실패한다.
- `python -m aios sync --dry-run`은 `--manifest <path>`가 없으므로 exit code 2로 실패한다.
- `--envelope-v2`는 기존 command들과 같이 `--json` 없이는 exit code 2로 실패한다.

## Dry-run Pipeline

구현된 read-only pipeline:

1. repository root 확인
2. explicit manifest path 확인
3. manifest JSON load
4. manifest schema validation
5. source existence check
6. target existence check
7. whole-file target hash check
8. managed marker parsing
9. managed block hash check
10. conflict/drift-stop/warning/pass result 구성
11. native `aios.sync_dry_run.v0` output 구성
12. optional envelope v2 output 구성

## Classification

구현된 classification:

- invalid manifest schema -> status `fail`, exit code 1
- missing source -> `conflict`, blocking, `source-missing`
- missing whole-file runtime-managed target -> `create`, informational
- missing managed-block/mixed-boundary target -> `conflict`, blocking, `marker-missing`
- valid marker + hash match -> `skip`
- valid marker + hash mismatch -> `drift-stop`, blocking, `target-modified`
- marker missing -> `conflict`, blocking, `marker-missing`
- marker duplicate -> `conflict`, blocking, `marker-duplicated`
- marker malformed/nested/mismatched/unsupported -> `conflict`, blocking, `marker-corrupted`
- safely detected orphan marker within manifest target scope -> `orphan-warning`, warning

의도적으로 제외한 classification:

- repository-wide unmanaged target scan
- default manifest discovery
- generated preview update candidate
- activation-driven sync selection

## Result Schema

Native schema:

```text
aios.sync_dry_run.v0
```

Top-level fields:

- `schema_version`
- `status`
- `root`
- `mode`
- `manifest_path`
- `summary`
- `results`
- `messages`
- `meta`

Result item fields:

- `entry_id`
- `action`
- `severity`
- `stop_reason`
- `recovery_hint`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `drift_state`
- `hashes`
- `marker`
- `details`

Envelope v2:

- `command: sync`
- `target.kind: sync-manifest`
- `payload.results`
- `meta.legacy_schema_version: aios.sync_dry_run.v0`
- `meta.dry_run: true`
- `messages` includes blocking/warning results

## Read-only Boundary

이번 번들은 다음을 수행하지 않았다.

- target file 생성/수정/삭제
- manifest 생성/수정/삭제
- transaction log 생성
- rollback 실행
- marker 삽입
- marker repair
- marker 삭제
- adapter generation
- generated preview content 생성
- force/decommission
- source mutation

테스트 fixture 파일은 `tests/fixtures/` 아래에만 추가되었다.

## 검증 결과

실행한 검증:

```bash
python -m pytest tests/test_sync_dry_run.py
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_drift_stop.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_orphan_marker.json --json --envelope-v2
python -m aios sync --envelope-v2
python -m aios sync
python -m aios inspect
python -m aios validate
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

최종 커밋 전 모든 검증이 통과해야 한다. Usage-error 검증 명령은 exit code 2가 기대 결과다.

## 다음 단계

Phase 7 dry-run의 기본 CLI evaluation은 구현되었다. 다음 단계는 별도 감사 또는 후속 번들에서 결정해야 한다.

가능한 후속 작업:

- `aios validate <manifest>` 통합
- dry-run human output 개선
- result fixture snapshot 강화
- repository-wide orphan/unmanaged scan 설계
- generated preview contract 설계

여전히 금지되는 작업:

- sync apply
- manifest persistence
- transaction logs
- rollback execution
- marker insertion/repair
- adapter generation
- force/decommission
