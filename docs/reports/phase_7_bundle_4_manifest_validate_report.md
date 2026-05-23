# Phase 7 Bundle 4 Manifest Validate 구현 보고서

## 개요

이 문서는 Phase 7 Bundle 4 `Manifest Validation Integration` 구현 결과를 기록한다. 이번 번들은 sync dry-run 내부에서 사용하던 `aios.sync_manifest.v0` schema validation을 `aios validate <manifest.json>`의 first-class target으로 연결했다.

현재 시스템은 계속 read-only 상태다. 이번 작업은 sync apply, target mutation, manifest write, transaction log persistence, rollback execution, marker insertion/repair/delete, adapter generation, force, decommission, default manifest discovery, manifest preview generation, activation-driven sync selection을 구현하지 않았다.

## 구현 범위

추가된 validator:

- `src/aios/validate/validators/sync_manifest.py`

갱신된 validate integration:

- `src/aios/validate/targets.py`
- `src/aios/validate/registry.py`
- `src/aios/validate/engine.py`

추가된 테스트:

- `tests/test_validate_sync_manifest.py`

추가된 fixture:

- `tests/fixtures/sync/manifests/missing_schema_version.json`
- `tests/fixtures/sync/manifests/unsupported_schema_version.json`
- `tests/fixtures/sync/manifests/missing_managed_entries.json`
- `tests/fixtures/sync/manifests/invalid_ownership.json`
- `tests/fixtures/sync/manifests/invalid_sync_mode.json`
- `tests/fixtures/sync/manifests/invalid_hash_format.json`
- `tests/fixtures/sync/manifests/path_parent_traversal.json`
- `tests/fixtures/sync/manifests/duplicate_entry_id.json`
- `tests/fixtures/sync/manifests/marker_entry_id_mismatch.json`
- `tests/fixtures/sync/manifests/non_manifest.json`

## Target Detection

`aios validate <path>`는 JSON 파일을 다음 조건에서 `sync-manifest` target으로 분류한다.

- `schema_version`이 `aios.sync_manifest.v0`
- 또는 `manifest_version`이 `aios.sync_manifest.v0`
- 또는 `schema_version`이 누락되었지만 manifest-shaped top-level fields를 모두 가진 JSON

manifest-shaped detection fields:

- `repository_id`
- `generated_at`
- `source_root`
- `target_root`
- `managed_entries`

일반 JSON은 가로채지 않는다. `non_manifest.json` fixture는 기존 `file` target으로 남고, 기존 validate convention에 따라 unsupported target warning을 반환한다.

## Validation Scope

`aios validate <manifest>`에서 수행하는 항목:

- schema version
- required top-level fields
- required managed entry fields
- generated metadata required fields
- ownership enum
- sync mode enum
- marker style enum
- repository-relative path safety
- parent traversal prohibition
- hash format
- duplicate `entry_id`
- marker metadata consistency
- `marker.entry_id`와 entry `entry_id` 일치
- `target_hash: null` 금지
- `manifest_version` alias warning

의도적으로 제외한 항목:

- source existence runtime evaluation
- target existence runtime evaluation
- marker parsing in target files
- hash comparison
- drift-stop classification
- dry-run action classification
- sync apply

## Result Mapping

`src/aios/sync/manifest.py`의 `ManifestIssue`를 기존 `ValidationRun` result로 변환한다.

매핑:

- `code` -> validate result code
- `severity` -> validate severity/status
- `message` -> validate message
- target path -> validate path
- `field` -> result details
- `entry_id` -> result details

유효한 manifest는 `sync_manifest_checked` info result를 추가한다. 이 info result는 schema/static validation만 수행했으며 runtime dry-run evaluation을 수행하지 않았음을 명시한다.

## 테스트 범위

테스트한 항목:

- valid whole-file manifest passes
- valid managed-block manifest passes
- valid mixed-boundary manifest passes
- missing schema_version fails
- unsupported schema_version fails
- invalid ownership fails
- invalid sync_mode fails
- invalid hash format fails
- parent traversal path fails
- duplicate entry_id fails
- marker.entry_id mismatch fails
- field and entry_id details are preserved
- non-manifest JSON is not misclassified

## Read-only Boundary

이번 번들은 다음을 수행하지 않았다.

- runtime target file 생성/수정/삭제
- manifest 생성/수정/삭제
- transaction log 생성
- marker 삽입
- marker repair
- marker 삭제
- sync apply
- rollback 실행
- adapter generation
- source mutation

테스트 fixture 파일은 `tests/fixtures/` 아래에만 추가되었다.

## 검증 결과

실행한 검증:

```bash
python -m pytest tests/test_sync_manifest.py
python -m pytest tests/test_sync_hash.py
python -m pytest tests/test_sync_markers.py
python -m pytest tests/test_sync_dry_run.py
python -m pytest tests/test_validate_sync_manifest.py
python -m aios validate tests/fixtures/sync/manifests/valid_whole_file.json
python -m aios validate tests/fixtures/sync/manifests/valid_managed_block.json
python -m aios validate tests/fixtures/sync/manifests/invalid_hash_format.json
python -m aios validate tests/fixtures/sync/manifests/path_parent_traversal.json
python -m aios validate --json --summary-only
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json
python -m aios inspect
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

invalid manifest validation commands are expected to fail clearly with validate status `fail`.

## 다음 단계

Phase 7 dry-run은 이제 CLI evaluation과 manifest validate target integration을 모두 갖는다. 다음 후속 작업은 별도 범위로 결정해야 한다.

가능한 후속 작업:

- sync runtime rules update
- dry-run result snapshot 강화
- manifest validation envelope v2 fixture 강화
- repository-wide orphan/unmanaged scan 설계
- generated preview contract 설계
