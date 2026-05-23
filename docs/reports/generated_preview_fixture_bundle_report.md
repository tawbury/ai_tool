# Generated Preview Fixture Bundle Report

## 개요

이 문서는 Phase 8 generated preview fixture-only bundle 구현 결과를 기록한다. 이번 작업은 provider 구현 전에 concrete JSON fixture와 schema/contract tests를 추가해 generated preview input/output/expected behavior를 고정하는 것이 목적이다.

런타임 provider, adapter execution, generated preview generation, sync apply, target mutation은 구현하지 않았다.

## 추가한 Fixture Layout

다음 fixture root를 추가했다.

```text
tests/fixtures/sync/previews/
  inputs/
  outputs/
  expected/
```

## Input Fixtures

추가한 input fixture는 다음과 같다.

- `tests/fixtures/sync/previews/inputs/whole_file_clean_input.json`
- `tests/fixtures/sync/previews/inputs/managed_block_clean_input.json`
- `tests/fixtures/sync/previews/inputs/mixed_boundary_clean_input.json`
- `tests/fixtures/sync/previews/inputs/source_missing_input.json`
- `tests/fixtures/sync/previews/inputs/marker_invalid_input.json`
- `tests/fixtures/sync/previews/inputs/adapter_unavailable_input.json`
- `tests/fixtures/sync/previews/inputs/activation_unresolved_input.json`

각 input fixture는 `aios.generated_preview.input.v0` schema, manifest entry, adapter identity, context reference, Phase 7 hash policy를 포함한다.

## Output Fixtures

추가한 output fixture는 다음과 같다.

- `tests/fixtures/sync/previews/outputs/whole_file_available_output.json`
- `tests/fixtures/sync/previews/outputs/managed_block_available_output.json`
- `tests/fixtures/sync/previews/outputs/adapter_unavailable_output.json`
- `tests/fixtures/sync/previews/outputs/source_missing_output.json`
- `tests/fixtures/sync/previews/outputs/marker_invalid_output.json`
- `tests/fixtures/sync/previews/outputs/activation_unresolved_output.json`

Available output은 deterministic metadata, adapter identity, generated hash, provenance source paths/hash를 포함한다. Unavailable output은 generated hash fields를 `null`로 유지하고 unavailable reason enum을 사용한다.

## Expected Classification Fixtures

추가한 expected fixture는 다음과 같다.

- `tests/fixtures/sync/previews/expected/whole_file_update_candidate_expected.json`
- `tests/fixtures/sync/previews/expected/whole_file_skip_expected.json`
- `tests/fixtures/sync/previews/expected/managed_block_update_candidate_expected.json`
- `tests/fixtures/sync/previews/expected/drift_stop_precedence_expected.json`
- `tests/fixtures/sync/previews/expected/marker_conflict_precedence_expected.json`
- `tests/fixtures/sync/previews/expected/preview_unavailable_no_update_expected.json`

이 fixture들은 future dry-run update candidate extension의 expected behavior를 고정한다.

핵심 정책:

- clean target + generated hash differs -> `update` candidate
- clean target + generated hash matches -> `skip`
- drifted target + generated hash exists -> `drift-stop`
- invalid marker + generated preview exists -> `conflict`
- preview unavailable -> no update candidate
- 모든 expected fixture는 `expected_no_mutation: true`

## 추가한 테스트

추가한 테스트 파일:

- `tests/test_generated_preview_fixtures.py`

검증 범위:

- 모든 JSON fixture parse
- fixture inventory가 계약에 맞는 최소 set인지 확인
- input fixture required fields 확인
- output fixture required fields 확인
- expected fixture required fields 확인
- hash field가 `sha256:<lowercase-hex>` 형식인지 확인
- available output은 deterministic metadata와 adapter identity를 포함하는지 확인
- unavailable output은 allowed unavailable reason enum을 사용하는지 확인
- provenance source paths/source hashes가 보존되는지 확인
- expected fixture가 `expected_no_mutation: true`를 포함하는지 확인

## Read-only Boundary

이번 작업은 다음을 추가하지 않았다.

- runtime provider
- dry-run update candidate logic
- adapter execution
- generated preview generation
- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- `.ai` rules 변경

## 검증

요청된 검증 대상은 다음과 같다.

- `python -m pytest tests/test_generated_preview_fixtures.py`
- `python -m pytest tests/test_sync_output_contract.py`
- `python -m pytest tests/test_sync_dry_run.py`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Generated preview fixture-only bundle은 provider 구현 전 단계로 필요한 concrete fixture와 schema tests를 추가했다. 다음 단계는 runtime provider 구현이 아니라 fixture-backed read-only provider design 또는 dry-run schema extension planning을 별도 bundle로 진행하는 것이 안전하다.
