# Fixture-backed replay comparison validation 계획

## 목적

Fixture-backed replay comparison validation은 real preview provider 실행 전에 replay comparison의 정확한 의미와 결과 계약을 고정하기 위한 read-only 설계다.

목적:

- expected output fixture comparison 규칙이 결정적임을 검증한다.
- future real provider output comparison의 failure code, result shape, envelope mapping을 미리 고정한다.
- provider execution 없이 exact comparison semantics를 검증 가능한 형태로 만든다.
- snapshot update, generated content creation, sync apply, mutation과 replay validation을 명확히 분리한다.

이 계획은 design-only다. Runtime code, provider execution, adapter execution, generated content generation, replay CLI, snapshot update, sync apply, mutation을 구현하지 않는다.

## 비교 대상 정의

현재 단계에서 real provider output은 존재하지 않는다. 따라서 fixture-backed replay comparison은 다음 중 하나의 read-only 모델로 제한한다.

권장 v0 모델:

- replay manifest case가 참조하는 expected output fixture를 load한다.
- 같은 fixture를 canonical expected snapshot object로 정규 로드한다.
- comparison helper는 expected object와 candidate object의 exact equality를 검증한다.
- candidate object는 provider output이 아니라 fixture-derived object다.

이 모델의 의미:

- comparison pipeline, field selection, mismatch reporting을 검증한다.
- real provider replay가 성공했다는 뜻이 아니다.
- generated content가 생성되었다는 뜻이 아니다.
- update candidate 또는 sync apply authorization을 만들지 않는다.

Alternative model:

- output fixture의 checksum baseline을 별도 manifest field로 두고 fixture bytes/hash를 비교한다.

Alternative는 fixture drift detection에는 유리하지만, field-level mismatch code를 설계하기 어렵다. 따라서 v0는 field-level exact comparison model을 우선한다.

## Comparison Units

하나의 comparison unit은 replay manifest의 한 case다.

구성 요소:

- `replay_case`
- `case_id`
- `input_fixture`
- `expected_output_fixture`
- `provider_snapshot`
- replay manifest provider metadata
- replay manifest hash policy
- replay dimensions

Comparison unit은 provider를 실행하지 않는다. Input fixture는 comparison context와 provenance 확인용이며 actual output 생성 입력으로 사용하지 않는다.

## 비교 필드

다음 필드는 exact value equality로 비교한다.

- `schema_version`
- `entry_id`
- `preview_available`
- `generated_content_kind`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `deterministic`
- `provider_metadata`
- `provenance`
- `unavailable_reason`

비교는 field-level로 보고되어야 한다. Nested object mismatch는 상위 field 단위로 시작하고, 필요할 때 `comparison_field`에 dotted path를 포함할 수 있다.

## Normalization Policy

Comparison v0는 숨은 normalization을 금지한다.

규칙:

- hash normalization 없음
- JSON semantic coercion 없음
- string/number/bool/null type coercion 없음
- object key order는 display 안정성을 위해 정렬할 수 있지만 비교 의미를 바꾸면 안 됨
- list order는 exact order 비교
- provenance source path order는 exact order 비교
- line ending normalization 없음
- trailing newline normalization 없음

비교 기준은 exact value equality다. 서로 같은 의미처럼 보이는 값도 JSON value가 다르면 mismatch다.

## Failure Codes

Comparison failure code:

- `replay-hash-mismatch`
- `replay-provenance-mismatch`
- `replay-provider-metadata-mismatch`
- `replay-unavailable-reason-mismatch`
- `replay-deterministic-flag-mismatch`
- `replay-schema-mismatch`
- `replay-entry-id-mismatch`
- `replay-preview-available-mismatch`
- `replay-content-kind-mismatch`

Field mapping:

| Field | Failure code |
| --- | --- |
| `schema_version` | `replay-schema-mismatch` |
| `entry_id` | `replay-entry-id-mismatch` |
| `preview_available` | `replay-preview-available-mismatch` |
| `generated_content_kind` | `replay-content-kind-mismatch` |
| `generated_bytes_hash` | `replay-hash-mismatch` |
| `generated_target_hash` | `replay-hash-mismatch` |
| `generated_managed_block_hash` | `replay-hash-mismatch` |
| `deterministic` | `replay-deterministic-flag-mismatch` |
| `provider_metadata` | `replay-provider-metadata-mismatch` |
| `provenance` | `replay-provenance-mismatch` |
| `unavailable_reason` | `replay-unavailable-reason-mismatch` |

모든 comparison mismatch는 severity `error`다.

## Native Validation Result Model

`aios validate <replay-manifest.json>` extension으로 구현될 경우, result item은 기존 validate result convention을 따른다.

Required details:

- `case_id`
- `comparison_field`
- `expected_value`
- `actual_value`

Recommended details:

- `expected_output_fixture`
- `input_fixture`
- `provider_id`
- `provider_version`
- `comparison_mode: fixture-backed`

Redaction policy:

- Hashes, schema versions, ids, enum values, fixture paths는 그대로 표시 가능하다.
- Large object mismatch는 full object를 표시하지 않고 field path와 short stable digest 또는 summary를 표시한다.
- Provenance object 전체가 클 경우 `expected_value`와 `actual_value`는 summary 또는 hash로 대체할 수 있다.
- Secret-bearing fields가 future schema에 추가되면 기본 redaction한다.

Valid comparison은 optional info result로 표현할 수 있다.

Suggested success code:

- `replay_comparison_checked`

Suggested success details:

- `cases`
- `comparison_mode: fixture-backed`
- `provider_id`
- `provider_version`

## Envelope v2 Mapping

Envelope v2는 validate command mapping을 사용한다.

Expected mapping:

- `command: validate`
- `target.kind: replay-manifest`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `payload.results`: comparison validation results
- `messages`: comparison errors and info results

Message details must preserve:

- `validator: replay-manifest`
- `case_id`
- `comparison_field`
- `comparison_mode`
- failure code

## Validation Ordering

Comparison validation must run after static validation.

Order:

1. Load replay manifest.
2. Run static validation.
3. If static validation has errors, stop comparison.
4. Load provider snapshot.
5. Load referenced input/output fixtures.
6. Build comparison units.
7. Compare expected output fixture against fixture-derived candidate object.
8. Emit comparison results.

Static validation errors must not be masked by comparison results.

## Future Implementation Slices

Recommended slices:

1. Fixture comparison helper
   - pure helper, no CLI
   - accepts expected/candidate dictionaries
   - returns comparison issues
2. Fixture comparison tests
   - one passing case
   - one mismatch per failure code group
   - no provider execution
3. Optional `aios validate <replay_manifest.json>` extension
   - opt-in or default extension decision required before implementation
   - preserve existing static validation output unless contract change is approved
4. Output contract tests
   - native JSON
   - envelope v2
5. Later provider-backed replay comparison
   - requires separate provider interface and execution policy approval

## Boundaries

Forbidden in this design and its immediate implementation:

- provider execution
- adapter execution
- generated content creation
- snapshot update
- replay CLI
- sync apply
- mutation
- target/source write
- manifest persistence
- transaction persistence
- rollback
- marker mutation
- repository-wide scan
- activation-driven provider selection

## Entry Criteria for Implementation

Implementation may begin only after:

- this plan is accepted
- output contract change strategy is chosen
- comparison helper boundary is confirmed
- fixture mutation policy remains no-write
- provider execution remains explicitly blocked

## Stop Criteria

Implementation should stop and require review if:

- provider execution becomes necessary
- adapter execution is proposed
- generated output creation is proposed
- snapshot update is proposed
- validate output shape requires breaking existing contract
- comparison results are interpreted as sync apply authorization

## 결론

Fixture-backed replay comparison validation은 real provider를 실행하지 않고 replay comparison semantics를 고정하는 안전한 중간 단계다. v0는 field-level exact comparison helper와 output contract design을 우선하고, provider-backed replay comparison은 별도 readiness gate 이후로 미룬다.
