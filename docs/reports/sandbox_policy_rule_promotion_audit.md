# Sandbox Policy Validation Rule Promotion Audit

## 목적

이 감사는 `aios validate <sandbox-policy.json>` static validation behavior를 runtime governance rules에 승격할 만큼 안정되었는지 판단한다.

이번 작업은 감사 전용이다. `.ai/rules`를 수정하지 않으며 runtime code도 변경하지 않는다.

## 검토 자료

- `docs/reports/sandbox_policy_validate_output_contract_report.md`
- `docs/plan/sandbox_policy_validate_output_contract_plan.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/index/current_runtime_context.md`

## 현재 구현 상태

구현 및 안정화된 behavior:

- `aios validate <sandbox-policy.json>`
- `aios validate <sandbox-policy.json> --json`
- `aios validate <sandbox-policy.json> --json --envelope-v2`
- target kind: `sandbox-policy`
- schema: `aios.sandbox_policy.v0`
- native JSON output contract
- envelope v2 output contract
- shaped invalid/missing schema detection
- unrelated JSON non-misclassification
- existing target detection regression coverage

고정된 non-execution metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`
- `sandbox_mode` when available

계속 차단된 behavior:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- file writes
- sync apply
- mutation authorization

## Rule Promotion Maturity

Sandbox policy validation은 rule promotion이 가능할 만큼 안정되었다.

근거:

- static validator helper가 구현되어 있다.
- validate integration이 구현되어 있다.
- native JSON과 envelope v2 output contract tests가 안정화되어 있다.
- helper issue code, message, field가 보존된다.
- non-execution metadata가 native JSON, envelope payload, envelope messages, envelope meta에 보존된다.
- target detection regression tests가 provider capability, provider execution trace, replay manifest, sync manifest, unrelated JSON을 보호한다.
- sandbox execution이나 subprocess execution이 구현되지 않았다.

남은 위험:

- sandbox policy라는 이름이 execution approval처럼 오해될 수 있다.
- `sandbox_mode` preservation이 실제 sandbox 실행처럼 오해될 수 있다.
- future sandbox trace/result fixture design과 혼동될 수 있다.

완화:

- rule에는 static-only validation boundary를 명시해야 한다.
- rule에는 sandbox launcher와 subprocess execution 금지를 명시해야 한다.
- fixture inventory, helper internals, heuristic field counts는 rule에 넣지 않는다.

## Promotion Target Decision

결정: split promotion을 권장한다.

Primary target:

- `.ai/rules/operations/validation.rules.md`

Secondary pointer:

- `.ai/rules/operations/sync.rules.md`

새 provider/sandbox-specific operation rule은 아직 만들지 않는다. 현재 반복 유지보수 수요는 validation rules와 sync safety pointer로 충분하다. 별도 provider/sandbox rule은 real sandbox execution architecture나 launcher governance가 실제로 반복될 때 다시 검토한다.

## Promote Now vs Defer

결정: promote now.

Sandbox trace fixture contract와 sandbox execution result fixture contract가 아직 없더라도 sandbox policy validation behavior 자체는 이미 구현되고 안정화되었다. Rule promotion은 현재 runtime behavior를 정확히 반영하는 작업이며 execution authorization이 아니다.

Defer하지 않는 이유:

- 이미 `aios validate <sandbox-policy.json>`가 runtime command로 존재한다.
- output contracts가 안정화되었다.
- governance rules가 이를 모르면 future agents가 current runtime capability를 누락하거나 sandbox validation을 human-context-only로 오해할 수 있다.

## Promote할 내용

`.ai/rules/operations/validation.rules.md`에 추가할 최소 내용:

- supported commands:
  - `python -m aios validate <sandbox-policy.json>`
  - `python -m aios validate <sandbox-policy.json> --json`
  - `python -m aios validate <sandbox-policy.json> --json --envelope-v2`
- target kind:
  - `sandbox-policy`
- schema:
  - `aios.sandbox_policy.v0`
- static-only boundary:
  - parsed JSON structure와 policy safety flags만 검증
- JSON/envelope non-execution metadata:
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `mutation_performed: false`
- `sandbox_mode` preservation when available
- explicit prohibitions:
  - sandbox launcher
  - subprocess execution
  - provider execution
  - replay execution
  - dynamic provider loading
  - provider registry/discovery
  - adapter execution
  - generated content
  - snapshot update
  - file writes
  - sync apply/mutation authorization

`.ai/rules/operations/sync.rules.md`에 추가할 최소 pointer:

- sandbox policy validation is available through `aios validate <sandbox-policy.json>`
- it is static-only readiness context for future sandbox/provider safety
- it does not authorize sandbox launcher, subprocess execution, provider execution, replay execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, sync apply, or mutation
- detailed command/output behavior belongs in validation rules

## Human-context Only로 남길 내용

다음은 runtime rules에 포함하지 않는다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- future sandbox execution result schema details
- future launcher design details
- invalid fixture 목록
- edge fixture 목록

## 병렬화 및 후속 작업

안전하게 bundle 가능한 후속 작업:

- sandbox policy rule promotion
- docs index update
- promotion report

별도 design-only parallel track으로 가능한 작업:

- sandbox trace fixture contract design
- sandbox execution result fixture contract design

순차적으로 차단해야 하는 작업:

- sandbox launcher implementation
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation

Sandbox execution implementation은 sandbox trace/result fixtures, sandbox architecture gates, output contracts, rule promotion, readiness audit가 모두 완료되기 전까지 시작하면 안 된다.

## 결론

Sandbox policy validation behavior는 runtime governance rule promotion이 가능하다.

권장 다음 작업:

1. `.ai/rules/operations/validation.rules.md`에 sandbox policy validation section 추가
2. `.ai/rules/operations/sync.rules.md`에 짧은 sandbox policy validation safety pointer 추가
3. `docs/reports/sandbox_policy_runtime_rule_promotion_report.md` 작성

이 promotion task는 runtime code 변경이나 sandbox execution implementation과 결합하면 안 된다.
