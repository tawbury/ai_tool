# Sandbox Execution Result Fixture Risk Audit

## 목적

이 감사는 `aios.sandbox_execution_result.v0` fixture-only 계약이 sandbox execution을 승인하는 것으로 오해될 위험을 점검한다.

현재 작업은 design-only이며 runtime code, `.ai/rules`, fixture files를 변경하지 않는다.

## 현재 상태

완료된 기반:

- subprocess sandbox architecture plan
- sandbox policy fixture contract
- sandbox policy fixtures and validator
- `aios validate <sandbox-policy.json>` static validation
- provider execution trace schema and static validation
- sandbox policy validation runtime rule promotion

아직 없는 것:

- sandbox execution result fixtures
- sandbox execution result validator helper
- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- sync apply/mutation

## 주요 위험

| 위험 | 설명 | 완화 |
| --- | --- | --- |
| execution authorization confusion | result fixture success를 sandbox execution 승인으로 오해할 수 있음 | fixture-only, evidence-only 문구를 반복하고 launcher를 명시적으로 금지 |
| provider output approval confusion | `output_json_valid` 또는 `trace_id`를 generated output approval로 오해할 수 있음 | result success does not approve provider output 규칙 명시 |
| mutation safety overclaim | no-write evidence가 sync apply safety 전체를 증명한다고 오해할 수 있음 | no-write evidence is proof data, not write authorization 명시 |
| false confidence from static fixtures | fixture가 실제 OS/network containment를 증명한다고 착각할 수 있음 | subprocess execution과 sandbox launcher가 아직 없음을 명시 |
| trace/result boundary confusion | `trace_id`가 full provider execution trace validation을 의미한다고 오해할 수 있음 | result validation does not validate full trace content 명시 |
| resource evidence ambiguity | resource-limit과 timeout evidence가 불명확하면 failure classification이 흔들릴 수 있음 | status/failure_code mapping을 엄격히 정의 |

## Schema Boundary Risk

`aios.sandbox_execution_result.v0`는 fixture-only schema다. 이 schema는 future result evidence의 shape를 정리하지만 실제 sandbox runtime output contract가 되려면 별도 validate helper, output contract tests, runtime rule promotion이 필요하다.

완화 규칙:

- schema 문서에는 launcher나 subprocess 실행을 승인하지 않는다고 명시한다.
- future validator helper는 parsed JSON만 검증해야 한다.
- future validate integration은 static-only여야 한다.

## No-write Evidence Risk

No-write evidence는 중요하지만 충분조건이 아니다.

한계:

- pre/post hash가 보호 root 전체를 완전히 대표하지 않을 수 있다.
- temp root cleanup 증거가 host mutation 전체를 증명하지 않는다.
- network isolation은 no-write evidence로 증명되지 않는다.
- no-write confirmation은 sync apply authorization이 아니다.

필요한 향후 보강:

- protected root 범위 명확화
- hash snapshot policy
- temp root cleanup verification
- unexpected output classification
- network attempt evidence

## Status and Failure Code Risk

Status와 failure code가 느슨하면 downstream behavior가 잘못 분기할 수 있다.

고정해야 할 규칙:

- `pass` requires `failure_code: null`.
- `fail`, `timeout`, `resource-limit` require non-null `failure_code`.
- `timeout` maps to `sandbox-timeout`.
- `resource-limit` maps to `sandbox-resource-limit`.
- `mutation_performed` must remain false.

## Relationship Risk

### Provider execution trace

`trace_id`는 link 역할만 한다. Sandbox result fixture validation은 full trace content를 검증하지 않는다.

### Sandbox policy

Sandbox policy는 intended constraints이고 sandbox result는 observed evidence다. 둘 다 execution authorization이 아니다.

### Sync apply

Sandbox result success는 sync apply readiness gate를 대체하지 않는다.

## Parallelization Assessment

병렬 진행 가능:

- sandbox execution result fixture-only bundle
- sandbox trace fixture contract design
- sandbox trace fixture risk audit

순차 진행 필요:

- result fixture bundle before result validator helper
- validator helper before validate integration
- output contract stabilization before rule promotion audit
- rule promotion before any execution readiness audit

계속 차단:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation

## 결론

Sandbox execution result fixture contract는 다음 fixture-only bundle을 진행할 만큼 충분히 정의될 수 있다. 다만 이 계약은 evidence shape만 정의하며 sandbox execution implementation을 승인하지 않는다.

다음 안전한 작업:

1. sandbox execution result fixture-only bundle
2. sandbox trace fixture contract design
3. sandbox execution result validator helper after fixture bundle
