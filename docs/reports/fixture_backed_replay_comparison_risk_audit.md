# Fixture-backed replay comparison 위험 감사

## 개요

Fixture-backed replay comparison validation은 provider execution 없이 replay comparison semantics를 먼저 고정하기 위한 설계 단계다. 이 감사는 해당 접근이 만드는 혼동과 안전 리스크를 정리하고, immediate implementation 전에 유지해야 할 경계를 정의한다.

## 주요 위험

| 위험 | 설명 | 영향 | 완화 |
| --- | --- | --- | --- |
| Provider replay로 오해 | Fixture-derived object 비교가 실제 provider output 검증처럼 해석될 수 있다. | real provider readiness를 과대평가할 수 있다. | 용어를 `fixture-backed replay comparison`으로 고정하고 no provider execution을 반복 명시한다. |
| Snapshot update 유혹 | mismatch 발생 시 fixture를 자동 갱신하고 싶어질 수 있다. | 검증이 drift를 숨기는 도구가 될 수 있다. | snapshot auto-update를 금지하고 mismatch는 error로만 보고한다. |
| Hidden normalization | JSON coercion, key sorting, line ending normalization이 mismatch를 숨길 수 있다. | false pass가 발생할 수 있다. | exact value equality와 no normalization policy를 적용한다. |
| Fixture layout overfitting | 현재 fixture directory 구조에 comparison logic이 과도하게 묶일 수 있다. | future provider replay 확장이 어려워진다. | comparison helper는 loaded dict/object를 입력받고 path loading은 별도 layer로 둔다. |
| False confidence | fixture를 fixture와 비교하면 항상 안전하다고 착각할 수 있다. | real provider nondeterminism이 검증되지 않을 수 있다. | 이 단계는 comparison model validation일 뿐 provider validation이 아니라고 명시한다. |
| Output contract churn | static validation 결과에 comparison result를 추가하면 기존 output contract가 바뀔 수 있다. | downstream tests가 흔들릴 수 있다. | implementation 전에 opt-in/default extension 정책을 결정한다. |
| Mutation confusion | replay comparison success가 sync apply 준비로 오해될 수 있다. | mutation gate가 약해질 수 있다. | sync apply/mutation blocked 상태를 유지하고 result에 write authorization 의미를 부여하지 않는다. |

## Provider Execution Risk

가장 큰 위험은 comparison이라는 단어가 provider execution을 암시하는 것이다. 현재 시스템에는 real provider interface가 없고 adapter execution도 없다.

정책:

- Fixture-backed comparison must not call provider code.
- Fixture-backed comparison must not load adapters.
- Fixture-backed comparison must not generate content.
- Fixture-backed comparison must not make network/model calls.
- Fixture-backed comparison must not create files.

만약 비교를 위해 actual provider output이 필요하다는 결론이 나오면, 그 즉시 작업을 중단하고 provider execution boundary design으로 전환해야 한다.

## Snapshot Update Risk

Replay snapshot은 검증 기준이다. 자동 갱신되면 기준이 사라진다.

금지:

- mismatch 발생 시 expected output fixture 자동 갱신
- provider snapshot 자동 갱신
- replay manifest 자동 갱신
- migration note 자동 생성

허용 가능한 future path:

- 사람이 검토한 fixture 변경
- provider version bump
- explicit migration note
- 별도 리뷰/검증 command

## Normalization Risk

Replay comparison은 deterministic behavior를 검증하기 위한 것이므로 normalization을 숨기면 안 된다.

금지:

- hash string case normalization
- line ending normalization
- trailing newline normalization
- `null`과 missing field 동치 처리
- string `"true"`와 boolean `true` 동치 처리
- list order 무시
- provenance source path order 무시

허용:

- display용 object key sorting
- large object display redaction
- stable summary/hash for reporting only

## Static Validation과 Comparison Validation 경계

Static validation:

- schema shape
- fixture path safety
- provider snapshot presence
- hash format
- required metadata presence

Comparison validation:

- expected value와 candidate value의 exact equality
- mismatch failure code mapping
- comparison result reporting

경계 원칙:

- Static validation에 error가 있으면 comparison은 실행하지 않는다.
- Comparison은 static validation을 대체하지 않는다.
- Comparison success는 provider determinism proof가 아니다.
- Comparison success는 sync apply authorization이 아니다.

## Output Contract Risk

현재 replay validate output contract는 static validation 기준으로 안정화되어 있다. Comparison result를 기본 validate output에 추가하면 result count와 info/error 목록이 바뀔 수 있다.

Implementation 전에 결정해야 할 사항:

- comparison을 default로 실행할지 opt-in으로 둘지
- `replay_comparison_checked` info result를 추가할지
- static validation result와 comparison result를 같은 validator namespace에 둘지
- envelope v2 message count 변화가 허용되는지

권장:

- 첫 구현은 helper와 unit tests부터 시작한다.
- `aios validate` 통합은 output contract plan 이후에 진행한다.

## Risk Matrix

| 위험 | 가능성 | 영향 | 우선순위 |
| --- | --- | --- | --- |
| Provider execution 혼동 | 중간 | 높음 | P0 |
| Snapshot update 유혹 | 중간 | 높음 | P0 |
| Hidden normalization | 중간 | 중간 | P1 |
| Output contract churn | 높음 | 중간 | P1 |
| Fixture layout overfitting | 중간 | 중간 | P1 |
| False confidence | 중간 | 중간 | P1 |
| Mutation confusion | 낮음 | 높음 | P1 |

## 권고

다음 단계는 design-only에서 implementation-ready plan으로 충분히 좁혀졌지만, 즉시 `aios validate` 통합을 구현하기보다는 helper-first implementation이 더 안전하다.

권장 순서:

1. Pure fixture comparison helper 구현
2. Helper unit tests로 mismatch code 검증
3. Native/envelope output contract design 확정
4. 그 뒤 `aios validate <replay-manifest.json>` extension 여부 결정

## Non-goals

이 감사는 다음을 승인하지 않는다.

- provider execution
- adapter execution
- generated content generation
- replay CLI
- snapshot update
- sync apply
- mutation
- transaction persistence
- rollback execution
- marker mutation
- repository-wide scan
- activation-driven provider selection

## 결론

Fixture-backed replay comparison은 다음 단계로 타당하지만, 실제 provider replay로 오해되지 않도록 helper-first, no-execution, no-update, exact-comparison 원칙을 강하게 유지해야 한다. 가장 안전한 후속 작업은 runtime 통합이 아니라 pure comparison helper와 mismatch tests 구현이다.
