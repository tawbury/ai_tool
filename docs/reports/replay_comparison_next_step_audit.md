# Replay comparison next step 감사

## 개요

Replay manifest/provider snapshot 정적 검증은 구현, 출력 계약 안정화, runtime governance rule promotion까지 완료되었다. 현재 남은 핵심 공백은 actual provider output replay comparison이다. 이 문서는 다음 단계로 replay comparison validation 설계를 진행할지, 아니면 추가 static stabilization을 먼저 해야 하는지 판단한다.

이번 작업은 감사 문서만 작성한다. Runtime code, `.ai` rules, fixture, test behavior는 변경하지 않았다.

## 현재 성숙도

| 영역 | 상태 | 판단 |
| --- | --- | --- |
| Replay fixture schema validation | 완료 | manifest, provider snapshot, input/output fixture schema가 정적으로 검증된다. |
| Provider snapshot validation | 완료 | provider id/version, hash policy, deterministic capability, supported sync modes, output-affecting config를 검증한다. |
| Fixture path safety | 완료 | relative path, parent traversal, missing fixture를 검증한다. |
| Hash validation | 완료 | `sha256:<lowercase-hex>` 형식과 placeholder hash rejection을 검증한다. |
| Provenance/provider metadata validation | 완료 | output fixture의 provenance와 provider metadata presence를 검증한다. |
| Unavailable output policy | 완료 | unavailable output의 generated hash null policy를 검증한다. |
| Validate JSON/envelope output contract | 완료 | native JSON과 envelope v2 contract tests가 있다. |
| Governance rule promotion | 완료 | sync rules와 validation rules에 static replay validation boundary가 반영되었다. |
| Actual output exact comparison | 미구현 | expected output fixture를 비교 대상으로 삼는 별도 comparison layer가 아직 없다. |
| Provider execution | 없음 | 의도적으로 차단되어 있다. |
| Adapter execution/generated content | 없음 | 의도적으로 차단되어 있다. |
| Mutation/apply | 차단 | sync rules에서 계속 금지한다. |

## Replay comparison validation의 의미

Replay comparison validation은 두 단계로 나눠서 정의해야 한다.

1. Fixture-backed replay comparison
   - Provider를 실행하지 않는다.
   - Adapter를 실행하지 않는다.
   - Generated content를 생성하지 않는다.
   - Replay manifest가 참조하는 expected output fixture를 load한다.
   - 비교 대상도 fixture 또는 fixture-derived object로 제한한다.
   - 목적은 comparison model, failure codes, result shape, envelope mapping을 검증하는 것이다.

2. Real provider replay comparison
   - Future real provider가 동일 input에서 output을 생성한다.
   - 생성된 actual output을 expected output fixture와 exact match로 비교한다.
   - 이 단계는 provider interface, execution policy, timeout policy, nondeterminism policy가 별도로 승인된 뒤에만 가능하다.

현재 다음 단계로 가능한 것은 1번 fixture-backed replay comparison design이다. 2번 real provider replay comparison은 아직 provider interface가 없으므로 설계 후보로만 남겨야 한다.

## 현재 공백

Static validation은 fixture가 유효한 모양인지 확인하지만, replay comparison의 핵심 의미를 아직 검증하지 않는다.

남은 공백:

- exact comparison field set의 runtime result 표현
- mismatch failure code mapping
- native validate JSON result shape
- envelope v2 message mapping
- comparison-only mode와 static validation mode의 경계
- provider execution 금지 상태에서의 fixture-backed comparison semantics
- replay comparison 실패가 provider nondeterminism인지 fixture drift인지 구분하는 정책

## 위험 평가

| 위험 | 설명 | 완화 방향 |
| --- | --- | --- |
| Provider를 실수로 실행 | replay comparison이라는 이름이 실제 provider execution으로 오해될 수 있다. | 다음 단계는 design-only 또는 fixture-backed-only로 제한한다. |
| Fixture comparison과 real replay 혼동 | expected output끼리 비교하는 단계가 real provider 검증처럼 보일 수 있다. | 용어를 fixture-backed replay comparison으로 고정한다. |
| Snapshot update 유혹 | mismatch가 나면 snapshot을 자동 갱신하고 싶어질 수 있다. | no snapshot auto-update를 rule과 design에 재확인한다. |
| Nondeterminism masking | retry나 fixture 교체로 nondeterminism을 숨길 수 있다. | retry 금지와 same provider version exact match 원칙을 유지한다. |
| Mutation/apply confusion | update candidate 또는 replay success가 write authorization으로 오해될 수 있다. | replay comparison은 validate-only이며 sync apply와 무관하다고 명시한다. |
| Provider interface 부재 | real provider execution 설계 없이 comparison 구현을 넓히면 추상화가 흔들릴 수 있다. | real provider execution은 후속 readiness gate로 분리한다. |

## 선택지 평가

| 선택지 | 장점 | 단점 | 판단 |
| --- | --- | --- | --- |
| Fixture-backed replay comparison 설계 next | provider 실행 없이 comparison model을 고정할 수 있다. failure codes와 output shape를 안전하게 설계할 수 있다. | 아직 구현 전 설계 문서가 하나 더 필요하다. | 권장 |
| Provider interface 전까지 comparison defer | provider execution boundary 혼동을 줄인다. | 이미 준비된 replay fixture와 validate contract의 다음 공백이 오래 남는다. | 비권장 |
| Static stabilization 추가 | 현재 동작의 안정성을 더 높인다. | 이미 schema/output/rule promotion이 완료되어 수익이 낮다. | 비권장 |

## 권고

권고: fixture-backed replay comparison validation design을 다음 단계로 진행한다.

단, 다음 단계는 design-only여야 한다.

정확한 scope:

- no provider execution
- no adapter execution
- no generated content generation
- no snapshot update
- no replay CLI
- no sync apply
- no mutation
- no target/source write
- compare expected output fixtures only as a model, or define fixture-backed comparison provider without executing real provider
- define exact mismatch failure codes before implementation
- define native validate JSON and envelope v2 mapping before implementation

## 다음 설계에서 정해야 할 항목

다음 design task는 다음을 정의해야 한다.

- comparison mode name
- comparison input model
- expected output loading rules
- actual output source boundary for fixture-backed mode
- exact fields to compare:
  - `schema_version`
  - `entry_id`
  - `preview_available`
  - `generated_content_kind`
  - generated hash fields
  - `deterministic`
  - `provider_metadata`
  - `provenance`
  - `unavailable_reason`
- mismatch codes:
  - `replay-hash-mismatch`
  - `replay-provenance-mismatch`
  - `replay-provider-metadata-mismatch`
  - `replay-unavailable-reason-mismatch`
  - `replay-deterministic-flag-mismatch`
  - `replay-schema-mismatch`
  - `replay-entry-id-mismatch`
- native validate result shape
- envelope v2 mapping
- static validation vs comparison validation ordering
- read-only proof checklist

## 명확히 defer할 항목

다음 단계에서도 defer해야 할 항목:

- real provider interface implementation
- provider execution
- adapter runtime
- generated content creation
- replay CLI
- snapshot update command
- sync apply
- mutation
- transaction/rollback
- repository-wide scan
- activation-driven provider selection

## 결론

현재 replay validation은 static layer로 충분히 안정화되었다. 다음 안전한 단계는 real provider를 실행하지 않는 fixture-backed replay comparison validation을 설계하는 것이다. 이 설계는 actual provider replay를 구현하지 않으며, future provider execution이 들어오기 전 exact comparison semantics와 failure reporting boundary를 고정하는 역할만 해야 한다.
