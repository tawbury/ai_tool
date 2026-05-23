# Dry-run Preview Integration Implementation Report

## 개요

이 문서는 Phase 8 fixture-backed dry-run preview integration 구현 결과를 기록한다. 이번 작업은 `aios sync --dry-run`에 opt-in fixture preview provider를 연결해 clean target에서 read-only `update` candidate를 분류할 수 있도록 했다.

기본 dry-run 동작은 변경하지 않았다. Preview flags가 없으면 기존 `aios.sync_dry_run.v0` output contract가 그대로 유지된다.

## 변경 범위

변경한 runtime code:

- `src/aios/cli.py`
- `src/aios/sync/dry_run.py`
- `src/aios/sync/preview.py`
- `src/aios/sync/__init__.py`

추가한 fixtures:

- `tests/fixtures/sync/previews/preview_index.json`
- `tests/fixtures/sync/previews/inputs/whole_file_match_input.json`
- `tests/fixtures/sync/previews/outputs/whole_file_match_output.json`
- `tests/fixtures/sync/manifests/e2e_preview_whole_file_clean.json`
- `tests/fixtures/sync/manifests/e2e_preview_whole_file_match.json`
- `tests/fixtures/sync/manifests/e2e_preview_unavailable.json`
- `tests/fixtures/sync/targets/whole_file_clean.txt`

추가한 tests:

- `tests/test_sync_dry_run_preview.py`

## CLI Behavior

새 opt-in options:

- `--preview-provider fixture`
- `--preview-fixtures <path>`

정책:

- no default preview provider
- preview flags가 없으면 기존 dry-run behavior 유지
- `--preview-provider fixture`와 `--preview-fixtures <path>`가 함께 있을 때만 fixture preview comparison 수행
- unsupported provider는 usage/config error
- `--preview-fixtures`만 있거나 `--preview-provider fixture`만 있으면 usage/config error
- usage/config error는 exit code `2`

## Preview Mapping

`tests/fixtures/sync/previews/preview_index.json`를 추가해 manifest `entry_id`를 preview input fixture filename에 명시적으로 매핑했다.

예:

```json
{
  "preview_inputs": {
    "entry_clean_skip": "managed_block_clean_input.json"
  }
}
```

Missing mapping은 update candidate를 만들지 않는다.

## Dry-run Evaluation Behavior

Preview comparison은 clean target에만 적용된다.

구현된 precedence:

- manifest schema error beats preview
- source-missing beats preview
- marker conflict beats preview
- drift-stop beats preview
- preview unavailable produces no update candidate

구현된 update rules:

- clean whole-file + `generated_target_hash` differs from `actual_target_hash` -> `action: update`
- clean whole-file + generated hash matches -> `action: skip`
- clean managed-block + `generated_managed_block_hash` differs from `actual_managed_block_hash` -> `action: update`
- preview unavailable -> existing Phase 7 result preserved

`update` candidate는 informational read-only result다. Write authorization이 아니며 `meta.mutation_performed`는 계속 `false`다.

## Result Schema Extension

Native result는 기존 shape를 호환적으로 확장한다.

추가/활성화되는 fields:

- `hashes.generated_target_hash`
- `hashes.generated_managed_block_hash`
- `details.preview`
- `details.preview_unavailable_reason`
- `meta.preview_provider: fixture`
- `meta.preview_policy: read-only-fixture`

Envelope v2는 기존 `payload.results`와 `meta` mapping을 통해 preview metadata를 보존한다.

## Test Coverage

`tests/test_sync_dry_run_preview.py`는 다음을 검증한다.

- clean whole-file + generated differs -> `update`
- clean managed-block + generated differs -> `update`
- generated matches -> `skip`
- drift-stop remains fail with preview configured
- marker conflict remains fail with preview configured
- preview unavailable -> no update
- envelope v2 preserves preview metadata
- no preview flags -> existing output contract unchanged
- preview config usage errors exit code `2`

Existing regression tests도 통과했다.

## Read-only Boundary

이번 작업은 다음을 구현하지 않았다.

- real preview provider
- adapter execution
- generated content creation
- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback
- marker insertion, repair, deletion
- default preview provider
- default manifest discovery
- repository-wide scan
- activation-driven preview selection
- `.ai/registry/`
- auto-fix
- source mutation

## 검증

수행한 검증:

- `python -m pytest tests/test_generated_preview_provider.py`
- `python -m pytest tests/test_generated_preview_fixtures.py`
- `python -m pytest tests/test_sync_output_contract.py`
- `python -m pytest tests/test_sync_dry_run.py`
- `python -m pytest tests/test_sync_dry_run_preview.py`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json --preview-provider fixture --preview-fixtures tests/fixtures/sync/previews`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_orphan_marker.json --json --envelope-v2 --preview-provider fixture --preview-fixtures tests/fixtures/sync/previews`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Fixture-backed generated preview output이 opt-in read-only path로 `aios sync --dry-run`에 통합되었다. Default behavior는 유지되며, preview가 명시적으로 구성된 경우에만 clean target에서 update candidate를 분류한다. Mutation/apply 경계는 그대로 차단되어 있다.
