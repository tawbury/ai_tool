# Generated Preview Fixture Contract

## 개요

이 문서는 `.ai OS` Phase 8 generated preview의 fixture 계약을 정의한다. 목적은 provider 구현 전에 preview input/output fixture layout, 필수 fixture 이름, expected behavior, validation expectation을 고정하는 것이다.

이번 문서는 fixture 계약만 정의한다. 실제 runtime provider, adapter execution, generated content creation, sync apply, target mutation은 구현하지 않는다.

## Fixture Layout

미래 fixture root는 다음 구조를 사용한다.

```text
tests/fixtures/sync/previews/
  inputs/
    whole_file_clean_input.json
    managed_block_clean_input.json
    mixed_boundary_clean_input.json
    source_missing_input.json
    marker_invalid_input.json
    adapter_unavailable_input.json
    activation_unresolved_input.json

  outputs/
    whole_file_available_output.json
    managed_block_available_output.json
    adapter_unavailable_output.json
    source_missing_output.json
    marker_invalid_output.json
    activation_unresolved_output.json

  expected/
    whole_file_update_candidate_expected.json
    whole_file_skip_expected.json
    managed_block_update_candidate_expected.json
    drift_stop_precedence_expected.json
    marker_conflict_precedence_expected.json
    preview_unavailable_no_update_expected.json
```

`inputs/`는 preview provider에 들어갈 read-only input을 보관한다.

`outputs/`는 provider가 반환해야 할 preview output shape를 보관한다.

`expected/`는 dry-run evaluator가 preview output을 소비했을 때의 classification hint를 보관한다.

## Minimum Input Fixtures

### `whole_file_clean_input.json`

목적:

- `sync_mode: whole-file` entry의 clean target 상태에서 preview 비교를 수행할 수 있는 입력을 고정한다.

필수 특성:

- `schema_version: aios.generated_preview.input.v0`
- `entry_id: preview_whole_file_clean`
- `manifest_entry.sync_mode: whole-file`
- `manifest_entry.ownership: runtime-managed`
- `manifest_entry.marker: null`
- `source_hash`는 `sha256:<lowercase-hex>` 형식
- `adapter.adapter_id` 존재
- `hash_policy.version: aios.hash_policy.v0`

### `managed_block_clean_input.json`

목적:

- valid marker를 가진 managed block의 preview 비교 입력을 고정한다.

필수 특성:

- `entry_id: preview_managed_block_clean`
- `manifest_entry.sync_mode: managed-block`
- `manifest_entry.ownership: mixed-boundary`
- marker metadata 존재
- marker `entry_id`가 top-level `entry_id`와 일치

### `mixed_boundary_clean_input.json`

목적:

- mixed-boundary target에서 marker 내부 content만 preview comparison 대상으로 삼는 입력을 고정한다.

필수 특성:

- `entry_id: preview_mixed_boundary_clean`
- `manifest_entry.sync_mode: mixed-boundary`
- `manifest_entry.ownership: mixed-boundary`
- marker metadata 존재
- marker-external content가 user-owned임을 details 또는 metadata에 남길 수 있음

### `source_missing_input.json`

목적:

- source가 없으면 preview unavailable보다 기존 `source-missing` conflict가 우선해야 함을 고정한다.

필수 특성:

- `entry_id: preview_source_missing`
- `manifest_entry.source_path`가 missing source를 가리키는 fixture convention 사용
- source hash는 manifest expected value로 남김

### `marker_invalid_input.json`

목적:

- marker integrity가 invalid이면 generated hash가 있어도 marker conflict가 우선해야 함을 고정한다.

필수 특성:

- `entry_id: preview_marker_invalid`
- managed marker metadata 존재
- expected marker integrity hint는 invalid 또는 fixture expected에 기록

### `adapter_unavailable_input.json`

목적:

- adapter/provider가 준비되지 않은 경우 preview unavailable을 반환하고 update candidate를 만들지 않음을 고정한다.

필수 특성:

- `entry_id: preview_adapter_unavailable`
- `adapter.adapter_id`는 존재하지만 provider unavailable을 나타내는 expected state가 있음

### `activation_unresolved_input.json`

목적:

- activation 또는 rule context reference가 resolve되지 않으면 preview unavailable이 되며 update candidate를 만들지 않음을 고정한다.

필수 특성:

- `entry_id: preview_activation_unresolved`
- `context.activation_reference` 또는 `context.rule_context_reference`가 unresolved fixture convention을 사용

## Minimum Output Fixtures

### `whole_file_available_output.json`

목적:

- whole-file preview가 available일 때 generated target hash를 제공한다.

필수 필드:

- `schema_version: aios.generated_preview.output.v0`
- `entry_id`
- `preview_available: true`
- `generated_content_kind: whole-file`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash: null`
- `generated_metadata.deterministic: true`
- `unavailable_reason: null`
- `provenance.source_paths`
- `provenance.source_hashes`

### `managed_block_available_output.json`

목적:

- managed block preview가 available일 때 generated managed block hash를 제공한다.

필수 필드:

- `preview_available: true`
- `generated_content_kind: managed-block`
- `generated_bytes_hash`
- `generated_target_hash: null`
- `generated_managed_block_hash`
- `generated_metadata.hash_policy: aios.hash_policy.v0`
- marker boundary는 provenance 또는 metadata에서 추적 가능

### `adapter_unavailable_output.json`

목적:

- adapter unavailable 상태의 output shape를 고정한다.

필수 필드:

- `preview_available: false`
- generated hash fields는 모두 `null`
- `generated_metadata`는 empty object 또는 deterministic false를 명시
- `unavailable_reason: adapter-unavailable`

### `source_missing_output.json`

목적:

- source missing 상태의 preview unavailable output을 고정한다.

필수 필드:

- `preview_available: false`
- `unavailable_reason: source-missing`
- `provenance.source_paths`는 requested source를 보존할 수 있음
- generated hash fields는 모두 `null`

### `marker_invalid_output.json`

목적:

- invalid marker 상태에서 preview unavailable output을 고정한다.

필수 필드:

- `preview_available: false`
- `unavailable_reason: marker-invalid`
- generated hash fields는 모두 `null`
- marker problem details는 provenance 또는 generated_metadata가 아니라 expected classification에서 보존

### `activation_unresolved_output.json`

목적:

- activation/rule context unresolved 상태의 preview unavailable output을 고정한다.

필수 필드:

- `preview_available: false`
- `unavailable_reason: activation-unresolved`
- `provenance.activation_reference` 또는 `provenance.rule_context_reference` 보존
- generated hash fields는 모두 `null`

## Expected Dry-run Classification Hints

Expected fixtures는 provider output 자체가 아니라 dry-run이 preview output을 소비했을 때의 classification hint를 정의한다.

### `whole_file_update_candidate_expected.json`

조건:

- target is clean
- generated target hash differs from current target hash

기대:

- action: `update`
- severity: `informational`
- status: `pass`
- stop_reason: `null`
- mutation_performed: `false`

### `whole_file_skip_expected.json`

조건:

- target is clean
- generated target hash matches current target hash

기대:

- action: `skip`
- severity: `informational`
- status: `pass`

### `managed_block_update_candidate_expected.json`

조건:

- target managed block is clean
- generated managed block hash differs from current managed block hash

기대:

- action: `update`
- severity: `informational`
- drift_state: `clean`
- generated hash details preserved

### `drift_stop_precedence_expected.json`

조건:

- target hash differs from manifest `target_hash`
- generated hash exists

기대:

- action: `drift-stop`
- status: `fail`
- stop_reason: `target-modified`
- generated preview does not bypass drift-stop

### `marker_conflict_precedence_expected.json`

조건:

- marker integrity invalid
- generated hash exists or preview output fixture claims availability

기대:

- action: `conflict`
- status: `fail`
- stop_reason: `marker-corrupted` or specific marker code
- generated preview does not repair marker conflict

### `preview_unavailable_no_update_expected.json`

조건:

- target is clean
- preview output has `preview_available: false`

기대:

- no `update` candidate
- existing Phase 7 behavior is preserved
- unavailable reason is visible in result details, messages, or envelope metadata

## Required Fixture Fields

Preview input fixtures must include:

- `schema_version`
- `entry_id`
- `manifest_entry`
- `manifest_entry.source_path` or `manifest_entry.source_paths`
- `manifest_entry.source_hash`
- `manifest_entry.target_path`
- `manifest_entry.sync_mode`
- `manifest_entry.ownership`
- `manifest_entry.marker`
- `adapter`
- `context`
- `hash_policy`

Preview output fixtures must include:

- `schema_version`
- `entry_id`
- `preview_available`
- `generated_content_kind`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `generated_metadata`
- `unavailable_reason`
- `provenance`

Expected classification fixtures must include:

- `entry_id`
- `input_fixture`
- `output_fixture`
- `target_state`
- `expected_action`
- `expected_status`
- `expected_severity`
- `expected_stop_reason`
- `expected_no_mutation: true`
- `expected_hash_fields`
- `expected_message_codes`

## Validation Expectations

Future fixture validation should enforce the following.

Required fields:

- all required input/output fields must exist
- unavailable outputs must still include all generated hash fields as `null`

Hash format:

- all non-null hash values must use `sha256:<lowercase-hex>`
- only `sha256` is supported

Deterministic metadata:

- available preview outputs must include `generated_metadata.deterministic: true`
- available preview outputs must include adapter identity

Source hash provenance:

- `provenance.source_hashes` must include every source path used by preview generation
- source hash values must match hash format

Unavailable reason enum:

- allowed values:
  - `adapter-unavailable`
  - `source-missing`
  - `unsupported-sync-mode`
  - `marker-invalid`
  - `generation-disabled`
  - `activation-unresolved`
- unavailable output must use one of these values
- available output must use `unavailable_reason: null`

Read-only invariant:

- expected fixtures must always include `expected_no_mutation: true`
- no fixture may imply sync apply authorization

## Future Test Strategy

1. Fixture schema test
   - Load every preview input/output/expected JSON fixture.
   - Validate required fields, enum values, hash format, deterministic metadata, provenance.

2. Fixture-backed provider test
   - Implement a read-only fixture provider that maps input fixture names to output fixture names.
   - Assert provider never reads or writes target files.

3. Dry-run update candidate test
   - Feed clean target state plus preview output into evaluator.
   - Assert `update` candidate appears only when target is clean and generated hash differs.

4. Envelope v2 preview mapping test
   - Assert generated hashes, unavailable reason, provenance, and update candidate message details are preserved in envelope v2.

## Explicit Non-goals

This fixture contract does not implement:

- runtime provider
- adapter execution
- preview content generation
- sync apply
- file mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, or deletion
- repository-wide unmanaged scan
- activation-driven sync selection
- force
- decommission

## 결론

Generated preview fixture contract는 provider 구현 전에 input/output shape와 expected dry-run behavior를 고정하는 안전한 중간 단계다. 다음 단계는 실제 provider가 아니라 JSON fixture와 schema tests를 추가하는 fixture-only bundle이 적절하다.
