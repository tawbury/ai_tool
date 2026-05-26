# Sandbox trace runtime rule promotion 보고서

> 이 보고서는 human context이다. 런타임 계약 변경은 `.ai/rules/operations/validation.rules.md`와 `.ai/rules/operations/sync.rules.md`에 반영되었다.

## 목적

`aios validate <sandbox-trace.json>` static validation behavior를 runtime governance rules에 승격했다. 이 승격은 정적 검증 boundary를 문서화하기 위한 것이며, sandbox launcher나 execution behavior를 승인하지 않는다.

## 변경 사항

### Validation rules

`.ai/rules/operations/validation.rules.md`에 sandbox trace validation section을 추가했다.

추가된 runtime-facing 내용:

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
- non-execution metadata:
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `replay_execution: false`
  - `mutation_performed: false`
- evidence identifiers:
  - `trace_id`
  - `request_id`
  - `sandbox_mode`
  - `provider_mode`
  - `status`
  - `failure_code`

### Sync rules

`.ai/rules/operations/sync.rules.md`에 짧은 Sandbox Trace Validation pointer를 추가했다.

추가된 의미:

- sandbox trace validation은 future sandbox/provider safety를 위한 static-only evidence validation이다.
- 상세 command/output behavior는 validation rules에 둔다.
- sync apply, mutation, sandbox launcher, subprocess execution, provider execution, replay execution을 승인하지 않는다.

## 명시적 비목표

이번 작업은 다음을 구현하거나 승인하지 않았다.

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
- sync apply/mutation
- runtime code changes
- fixture/test changes

## 병렬화 메모

이번 task에서는 rule promotion, promotion report, docs index update를 안전하게 묶었다. 다음 task인 static validation surface completion audit은 이 promotion 이후에만 진행한다. Execution readiness audit과 sandbox launcher/execution implementation은 계속 순차적으로 차단된다.

## 다음 단계

다음 순차 task는 static validation surface completion audit이다. 이 감사에서 sync/replay/provider/sandbox static validation surface가 governance promotion까지 완료되었는지 확인해야 한다.
