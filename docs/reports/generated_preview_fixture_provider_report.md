# Generated Preview Fixture Provider Report

## 개요

이 문서는 Phase 8 fixture-backed generated preview provider 구현 결과를 기록한다. 이번 작업은 실제 generation이나 adapter execution 없이 preview provider interface를 검증하기 위한 read-only fixture provider만 추가했다.

런타임 `aios sync --dry-run`에는 통합하지 않았다. Dry-run update candidate classification도 추가하지 않았다.

## 변경 범위

추가한 runtime module:

- `src/aios/sync/preview.py`

갱신한 export:

- `src/aios/sync/__init__.py`

추가한 테스트:

- `tests/test_generated_preview_provider.py`

## Provider Behavior

`FixturePreviewProvider`는 다음 동작만 수행한다.

- preview input fixture JSON을 읽는다.
- input fixture filename을 deterministic mapping으로 output fixture filename에 매핑한다.
- preview output fixture JSON을 읽는다.
- output을 `PreviewOutput` model로 반환한다.
- output schema, hash format, unavailable reason, deterministic metadata, provenance를 검증한다.

Provider는 다음을 하지 않는다.

- target file 읽기 또는 쓰기
- source file 읽기
- adapter execution
- generated content creation
- sync dry-run integration
- update candidate classification
- manifest write
- transaction log write
- marker insertion, repair, deletion

## Fixture Mapping

현재 provider mapping은 fixture contract의 minimum available/unavailable cases만 지원한다.

- `whole_file_clean_input.json` -> `whole_file_available_output.json`
- `managed_block_clean_input.json` -> `managed_block_available_output.json`
- `adapter_unavailable_input.json` -> `adapter_unavailable_output.json`
- `source_missing_input.json` -> `source_missing_output.json`
- `marker_invalid_input.json` -> `marker_invalid_output.json`
- `activation_unresolved_input.json` -> `activation_unresolved_output.json`

`mixed_boundary_clean_input.json`은 아직 output fixture가 없는 contract-only input이므로 unknown mapping으로 거부된다. 이는 provider가 암묵적으로 output을 생성하지 않는다는 점을 검증하기 위한 의도된 boundary다.

## Validation Rules

Provider는 다음을 검증한다.

- input schema version: `aios.generated_preview.input.v0`
- output schema version: `aios.generated_preview.output.v0`
- required input/output fields
- non-null hash format: `sha256:<lowercase-hex>`
- available output:
  - `preview_available: true`
  - `generated_metadata.deterministic: true`
  - adapter identity present
  - unavailable reason must be `null`
- unavailable output:
  - `preview_available: false`
  - generated hash fields must be `null`
  - unavailable reason must be one of the allowed enum values
- provenance:
  - `source_paths`
  - `source_hashes`
  - `generated_by: aios.generated_preview.v0`

## Test Coverage

`tests/test_generated_preview_provider.py` covers:

- whole-file input maps to available whole-file output
- managed-block input maps to available managed-block output
- adapter-unavailable input maps to unavailable output
- source-missing input maps to unavailable output
- marker-invalid input maps to unavailable output
- activation-unresolved input maps to unavailable output
- unknown fixture mapping is rejected
- provider does not mutate fixture files or target files
- non-null output hash fields match `sha256:<lowercase-hex>`
- unavailable reason enum is enforced

## Read-only Boundary

이번 작업은 read-only boundary를 유지한다.

특히 다음은 구현하지 않았다.

- real provider
- adapter execution
- generated preview content creation
- dry-run update candidate extension
- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback
- marker insertion, repair, deletion
- default manifest discovery
- repository-wide scan
- activation-driven sync selection
- `.ai/registry/`
- auto-fix
- source mutation

## 검증

요청된 검증 대상은 다음과 같다.

- `python -m pytest tests/test_generated_preview_fixtures.py`
- `python -m pytest tests/test_generated_preview_provider.py`
- `python -m pytest tests/test_sync_output_contract.py`
- `python -m pytest tests/test_sync_dry_run.py`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Fixture-backed generated preview provider는 provider interface와 fixture output validation을 검증하기 위한 격리된 read-only layer로 추가되었다. 다음 단계는 dry-run update candidate extension을 바로 구현하기보다, fixture-backed provider를 dry-run schema extension plan에 어떻게 연결할지 별도 설계하는 것이 안전하다.
