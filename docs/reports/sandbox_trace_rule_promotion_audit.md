# Sandbox trace validation rule promotion 감사

> 이 보고서는 human context이다. 본 작업은 감사만 수행하며 `.ai/rules`를 수정하지 않는다.

## 목적

`aios validate <sandbox-trace.json>` static validation behavior를 runtime governance rules로 승격할 만큼 안정적인지 판단하고, 승격이 필요하다면 최소 변경 대상을 정의한다.

## 검토한 근거

- `docs/reports/sandbox_trace_validate_integration_report.md`
- `docs/reports/sandbox_trace_validate_output_contract_report.md`
- `docs/plan/sandbox_trace_validate_output_contract_plan.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/index/current_runtime_context.md`

## 현재 구현 성숙도

Sandbox trace validation은 다음 조건을 충족한다.

- `aios validate <sandbox-trace.json>`가 구현되어 있다.
- target kind는 `sandbox-trace`로 고정되어 있다.
- schema는 `aios.sandbox_trace.v0`이다.
- native JSON schema는 `aios.validate.result.v0`이다.
- envelope v2는 `aios.command_result.v2`를 사용한다.
- success code는 `sandbox_trace_checked`이다.
- helper issue code, severity, status, message, field가 보존된다.
- shaped invalid/missing schema detection이 검증되어 있다.
- unrelated JSON non-misclassification이 검증되어 있다.
- sandbox result, sandbox policy, provider execution trace, provider capability, replay manifest, sync manifest target detection regression이 검증되어 있다.
- non-execution metadata가 native JSON과 envelope v2에서 보존된다.

보존되는 non-execution metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

보존되는 evidence identifiers:

- `trace_id`
- `request_id`
- `sandbox_mode`
- `provider_mode`
- `status`
- `failure_code`

## 승격 판단

권장 결정: **지금 승격한다.**

이유:

- 구현, integration tests, output contract tests가 모두 존재한다.
- 기존 sandbox policy/result/provider trace validation과 동일한 static-only 패턴을 따른다.
- target detection 회귀가 고정되어 있다.
- non-execution boundary가 출력 계약에 포함되어 있다.
- sandbox trace는 sandbox result와 provider execution trace evidence를 연결하는 정적 증거 계층이므로 runtime governance rules에 명시해 혼동을 줄일 필요가 있다.

## 권장 promotion target

권장 방식: **split promotion**

Primary target:

- `.ai/rules/operations/validation.rules.md`

Secondary pointer:

- `.ai/rules/operations/sync.rules.md`

별도 provider/sandbox-specific rule은 지금 만들지 않는다. 현재는 validation rules에 command/output boundary를 두고, sync rules에는 future sandbox/provider safety context pointer만 추가하는 것이 가장 작은 변경이다.

## 승격할 내용

`validation.rules.md`에 추가할 내용:

- 지원 명령:
  - `python -m aios validate <sandbox-trace.json>`
  - `python -m aios validate <sandbox-trace.json> --json`
  - `python -m aios validate <sandbox-trace.json> --json --envelope-v2`
- target kind:
  - `sandbox-trace`
- schema:
  - `aios.sandbox_trace.v0`
- static-only boundary:
  - parsed JSON structure와 sandbox trace evidence만 검증한다.
- JSON/envelope non-execution metadata:
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `replay_execution: false`
  - `mutation_performed: false`
- evidence identifiers preservation:
  - `trace_id`
  - `request_id`
  - `sandbox_mode`
  - `provider_mode`
  - `status`
  - `failure_code`
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

`sync.rules.md`에 추가할 내용:

- sandbox trace validation은 `aios validate <sandbox-trace.json>`로 사용할 수 있는 static-only evidence validation이다.
- future sandbox/provider safety context로만 사용된다.
- sandbox launcher, subprocess execution, provider execution, replay execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, sync apply, mutation을 승인하지 않는다.
- 상세 command/output behavior는 validation rules에 둔다.

## human-context-only로 남길 내용

다음 내용은 runtime rules에 넣지 않는다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- invalid fixture lists
- edge fixture lists
- future sandbox launcher design details
- future execution prototype planning details

## 병렬화 및 후속 순서

안전하게 묶을 수 있는 다음 작업:

- sandbox trace rule promotion
- promotion report 작성
- docs index update

분리해야 하는 작업:

- static validation surface completion audit은 rule promotion 후에 진행한다.
- execution readiness audit은 static validation surface completion audit 후에 진행한다.
- sandbox launcher/execution implementation은 계속 차단된다.

## 결론

Sandbox trace validation은 runtime governance rules로 승격할 만큼 안정화되었다. 다음 task에서 `.ai/rules/operations/validation.rules.md`를 primary target으로 갱신하고, `.ai/rules/operations/sync.rules.md`에는 짧은 safety pointer를 추가하는 것을 권장한다.
