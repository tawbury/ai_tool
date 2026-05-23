# Phase 8 미리보기 dry-run 출력 계약 안정화 보고서

## 개요

Phase 8의 fixture 기반 generated preview 통합 경로에 대해 출력 계약 회귀 테스트를 추가했다. 이번 작업은 새 런타임 기능을 추가하지 않고, `aios sync --dry-run`의 preview 활성화 출력과 기존 no-preview 출력의 호환성을 테스트로 고정하는 데 한정했다.

## 변경 범위

- `tests/test_sync_preview_output_contract.py`를 추가했다.
- native `aios.sync_dry_run.v0` JSON 출력에서 preview update 후보, preview unavailable, drift-stop 우선순위, marker conflict 우선순위를 검증했다.
- envelope v2 출력에서 `command`, `target.kind`, `payload.results`, preview metadata, generated hash, mutation 불변식을 검증했다.
- preview 플래그가 없는 기존 clean skip 출력이 preview metadata 없이 유지되는지 검증했다.
- preview 설정 오류가 exit code 2로 유지되는지 검증했다.

## 고정한 출력 계약

preview 활성화 시 clean target과 generated hash가 다르면 결과는 read-only `update` 후보로 유지된다. whole-file은 `generated_target_hash`, managed-block은 `generated_managed_block_hash`를 통해 비교 결과를 노출한다.

preview unavailable 상태는 update 후보를 만들지 않는다. 기존 skip 결과를 유지하고 `details.preview_unavailable_reason`에 사유를 보존한다.

drift-stop과 marker conflict는 preview보다 우선한다. target drift 또는 marker integrity 문제가 있으면 preview metadata를 결과에 주입하지 않고 기존 blocking 결과를 유지한다.

envelope v2 출력은 native 결과를 `payload.results`에 보존하고, `meta.preview_provider: fixture`, `meta.preview_policy: read-only-fixture`, `meta.mutation_performed: false`를 유지한다.

## 읽기 전용 경계

이번 작업은 테스트와 보고서만 추가했다. sync apply, target mutation, manifest write, transaction log, rollback, marker insertion/repair/delete, real preview provider, adapter execution, generated content generation은 구현하지 않았다.

## 검증 항목

다음 검증을 수행 대상으로 삼았다.

- `python -m pytest tests/test_sync_preview_output_contract.py`
- `python -m pytest tests/test_sync_dry_run_preview.py`
- `python -m pytest tests/test_sync_output_contract.py`
- `python -m pytest tests/test_generated_preview_provider.py`
- `python -m pytest tests/test_generated_preview_fixtures.py`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_preview_whole_file_clean.json --json --preview-provider fixture --preview-fixtures tests/fixtures/sync/previews`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
