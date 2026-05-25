# Provider Capability Fixture Risk Audit

> 이 문서는 human context용 위험 감사 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 provider capability fixture가 future provider execution으로 오해되지 않도록 위험과 경계를 정리한다.

## 목적

Provider capability fixture contract는 실제 provider 실행 전에 정적 선언을 표준화하기 위한 준비 단계다. 이 감사는 capability fixture가 도입할 수 있는 혼동, 과신, 확장 위험을 점검하고, fixture validation의 안전 경계를 정의한다.

## 현재 상태

| 항목 | 상태 |
| --- | --- |
| Fixture-backed replay comparison | 구현됨 |
| Replay manifest static validation | 구현됨 |
| Opt-in replay comparison | 구현됨 |
| Provider isolation requirements | 감사 및 계획 완료 |
| Provider capability fixture | 이번 단계에서 설계 |
| Provider execution | 미구현, 금지 |
| Sandbox execution | 미구현, 금지 |
| Adapter execution | 미구현, 금지 |
| Sync apply/mutation | 차단 |

## 핵심 위험

### Capability가 실행 승인으로 오해될 위험

`no_write_capable: true` 또는 `deterministic_capable: true` 같은 선언은 provider의 주장일 뿐이다. 검증기는 선언의 구조와 허용 값을 확인할 수 있지만, provider가 실제로 write하지 않는지는 실행 격리와 no-mutation verification 없이는 증명할 수 없다.

완화:

- 문서와 future validation output에서 capability validation은 execution authorization이 아니라고 명시한다.
- `aios validate <provider-capability.json>`가 추가되더라도 실행하지 않는다.
- sandbox approval을 별도 future gate로 유지한다.

### Provider registry로 오해될 위험

`tests/fixtures/providers/capabilities/` layout은 테스트 fixture 위치다. 이 경로가 provider discovery 또는 runtime registration으로 오해되면 임의 fixture가 provider로 로드되는 위험이 생긴다.

완화:

- fixture layout은 tests 전용으로 정의한다.
- runtime provider discovery는 explicit non-goal로 둔다.
- future registry가 필요하면 별도 registry design과 rule promotion을 요구한다.

### Network policy 확장 위험

외부 model/API provider는 network와 nondeterminism 위험을 동시에 도입한다. `network_policy`를 너무 일찍 확장하면 fixture validation이 외부 호출 허가처럼 보일 수 있다.

완화:

- v0는 `disabled`만 허용한다.
- `network_policy` 확장은 별도 plan, validation, sandbox, observability rule이 있을 때만 가능하다.
- network enabled fixture는 invalid case로 둔다.

### Determinism 과신 위험

`deterministic_capable: true`는 capability 선언이지 replay 증명 결과가 아니다. 동일 input에서 실제 output이 같은지는 deterministic replay test가 필요하다.

완화:

- deterministic replay는 별도 gate로 유지한다.
- capability validation success는 replay success와 다르다고 명시한다.
- output-affecting config snapshot을 필수로 둔다.

### Hash policy drift 위험

Provider가 line ending, trailing newline, BOM, whitespace를 조용히 정규화하면 Phase 7 v0 hash policy와 충돌한다.

완화:

- v0 `hash_policy`는 `aios.hash_policy.v0`만 허용한다.
- `output_affecting_config.normalization`이 있다면 `none` 또는 명시 정책이어야 한다.
- future validator는 hash policy mismatch를 error로 처리해야 한다.

### Resource policy 형식만 있고 실제 제한이 없는 위험

`timeout_policy`와 `resource_policy`가 fixture에 있어도 runtime sandbox가 없으면 실제 제한은 적용되지 않는다.

완화:

- capability validation은 policy declaration만 검증한다.
- sandbox runtime 없이는 provider execution을 금지한다.
- future sandbox plan에서 timeout/resource enforcement를 별도 검증한다.

### Allowed read roots 오용 위험

`allowed_read_roots`가 넓거나 절대 경로를 허용하면 provider가 source boundary 밖을 읽을 수 있다.

완화:

- v0 fixture는 상대/safe path만 허용한다.
- parent traversal과 absolute path는 future validation에서 error로 둔다.
- empty array는 "추가 read root 없음"으로 해석한다.

## Invalid Fixture Risk Coverage

필수 invalid fixtures는 다음 위험을 잠근다.

| Invalid case | 잠그는 위험 |
| --- | --- |
| unsupported schema version | 암묵적 schema 확장 |
| invalid sync mode | 지원하지 않는 sync mode 실행 |
| missing provider version | output drift 추적 실패 |
| network enabled | 외부 호출 허가 오해 |
| no_write false | mutation-capable provider 허용 |
| invalid timeout | 무제한 실행 위험 |
| duplicate sync mode | 모호한 capability 선언 |
| malformed resource policy | resource limit 부재 |

## Future Validate Integration Risk

`aios validate <provider-capability.json>`가 추가되면 사용자에게 "이 provider는 안전하게 실행 가능하다"는 인상을 줄 수 있다.

완화 정책:

- target kind는 `provider-capability`로 하되, result message에 static-only boundary를 포함한다.
- validation success code는 `provider_capability_checked`처럼 구조 검증임을 드러낸다.
- output meta에는 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`를 포함하는 방향을 권장한다.
- envelope v2 mapping도 동일한 boundary를 유지한다.

## Fixture Contract Sufficiency

이 설계는 다음에는 충분하다.

- capability fixture bundle 작성
- schema/contract tests 작성
- static validator helper 설계
- validate output contract 설계

이 설계만으로는 다음에 충분하지 않다.

- real provider execution
- sandbox approval
- adapter-backed provider
- external model/API provider
- generated preview content creation
- sync apply readiness

## 권장 다음 단계

권장 순서:

1. Provider capability fixture-only bundle 구현
2. Provider capability validator helper 설계 및 구현
3. `aios validate <provider-capability.json>` output contract 설계
4. Deterministic mock provider boundary 설계

Provider execution, adapter execution, generated content, snapshot update, sync apply, mutation은 계속 차단한다.

## 결론

Provider capability fixture는 real provider execution을 향한 안전한 전제 조건이지만 실행 권한은 아니다. v0에서는 `network_policy: disabled`, `no_write_capable: true`, `deterministic_capable: true`, `hash_policy: aios.hash_policy.v0`를 강하게 요구해야 한다.

Capability validation이 추가되더라도 provider 실행, sandbox 실행, adapter 실행, snapshot update, generated content creation, sync apply/mutation은 별도 승인 전까지 금지 상태로 유지해야 한다.
