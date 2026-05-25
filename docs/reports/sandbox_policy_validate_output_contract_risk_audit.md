# Sandbox Policy Validate Output Contract Risk Audit

## 목적

이 감사는 future `aios validate <sandbox-policy.json>` 통합 전에 native JSON과 envelope v2 출력 계약의 위험을 점검한다. 현재 상태는 helper-only이며 sandbox policy validation은 CLI에 연결되어 있지 않다.

## 현재 상태

완료된 항목:

- sandbox policy fixture contract
- sandbox policy fixture-only bundle
- `validate_sandbox_policy_data(data)` helper
- sandbox policy validator unit tests

아직 구현되지 않은 항목:

- `aios validate <sandbox-policy.json>`
- sandbox policy validate JSON output
- sandbox policy envelope v2 output
- runtime rule promotion
- sandbox launcher
- subprocess execution
- provider execution

## 주요 위험

| 위험 | 설명 | 완화 |
| --- | --- | --- |
| target misclassification | provider capability, provider trace, replay manifest, sync manifest를 sandbox policy로 잘못 분류할 수 있음 | detection priority를 activation, sync, replay, capability, trace 뒤에 둠 |
| schema error invisibility | schema가 틀린 sandbox policy 후보를 generic JSON으로 넘기면 명확한 validation error를 제공하지 못함 | shaped heuristic으로 sandbox-policy-shaped JSON을 감지 |
| execution authorization confusion | sandbox policy validation pass를 sandbox execution 승인으로 오해할 수 있음 | output details와 envelope meta에 `sandbox_execution: false`, `subprocess_execution: false`, `provider_execution: false`를 포함 |
| envelope metadata drift | native result와 envelope meta의 non-execution 값이 달라질 수 있음 | output contract tests로 metadata invariants 고정 |
| existing validate regression | 기존 replay/provider/sync validation target detection이 깨질 수 있음 | 기존 target detection regression tests를 필수화 |
| mutation boundary confusion | policy가 output roots를 포함하므로 write authorization처럼 보일 수 있음 | validation은 policy shape만 검증하며 file write와 mutation은 금지한다고 명시 |

## Detection Risk

Sandbox policy shaped heuristic은 schema가 없는 오류 fixture를 검증하기 위해 필요하다. 하지만 heuristic이 넓으면 unrelated JSON이 `sandbox-policy`로 분류될 수 있다.

권장 완화:

- object가 아니면 sandbox policy로 분류하지 않는다.
- sandbox policy field가 최소 5개 이상 있어야 한다.
- `sandbox_mode`, `env_policy`, `filesystem_policy` 중 하나 이상이 있어야 한다.
- provider capability와 provider execution trace detection 뒤에만 평가한다.

## Output Risk

Native JSON과 envelope v2 모두 validation result일 뿐 execution trace가 아니다. 특히 다음 값은 반드시 false로 유지해야 한다.

- `sandbox_execution`
- `subprocess_execution`
- `provider_execution`
- `mutation_performed`

`sandbox_mode`는 가능한 경우 보존하되, sandbox가 실행되었다는 의미로 해석하면 안 된다.

## Static-only Boundary

Future validate integration은 다음만 수행해야 한다.

- JSON parse
- target detection
- helper validation
- result serialization

금지:

- sandbox launch
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply
- mutation

## Compatibility Audit

Validate integration 구현 전후로 다음 대상은 동일하게 인식되어야 한다.

- activation target
- sync manifest
- replay manifest
- provider capability
- provider execution trace
- unrelated JSON

Sandbox policy validation은 이들보다 낮은 우선순위를 가져야 하며, 기존 output contract tests를 유지해야 한다.

## 병렬화 메모

Validate integration은 이 output contract가 완료된 뒤에 순차적으로 진행해야 한다.

Sandbox trace fixture contract와 sandbox execution result fixture contract는 sandbox execution을 승인하지 않는 design-only 작업이므로 별도 병렬 track으로 진행할 수 있다. Rule promotion audit은 validate integration과 output contract stabilization 뒤에 진행해야 한다.

Sandbox execution implementation은 계속 차단되어 있으며, fixture/helper/validate 문서 작업과 병합하면 안 된다.

## 결론

Sandbox policy validate output contract는 구현 준비가 가능하다. 다만 첫 구현은 static-only `aios validate <sandbox-policy.json>` 통합과 output contract tests로 제한해야 한다.

Sandbox launcher, subprocess execution, provider execution은 이 계약으로도 여전히 승인되지 않는다.
