# Provider Execution Trace Validate Output Contract Report

> 이 문서는 구현 증거용 human context이다. 런타임 계약은 `.ai/rules/`가 기준이며, 이 작업은 `.ai/rules`를 수정하지 않았다.

## 목적

`aios validate <provider-trace.json>` 통합 이후 provider execution trace 검증 출력 계약을 안정화했다. 변경 범위는 테스트와 문서 증거 보강에 한정했으며 runtime semantics는 변경하지 않았다.

## 안정화한 계약

Native JSON 계약:

- `schema_version: aios.validate.result.v0`
- `target.kind: provider-execution-trace`
- valid trace는 `provider_execution_trace_checked` info result를 포함한다.
- invalid trace는 helper issue code를 보존하고 exit code 1을 반환한다.
- trace-shaped invalid schema는 provider execution trace target으로 감지되어 schema error로 실패한다.
- unrelated JSON은 provider execution trace로 오분류되지 않는다.

Envelope v2 계약:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: provider-execution-trace`
- `payload.results`와 `messages`가 provider trace validator details를 보존한다.
- meta는 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`, `provider_mode`를 보존한다.

## Metadata Invariants

다음 metadata invariant를 native JSON, envelope v2, payload, messages에서 확인했다.

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`
- `provider_mode`는 trace에 존재할 때 보존된다.
- `failure_code`와 `unavailable_reason`은 invalid trace failure details에서 보존된다.

## 보존된 Target Detection

다음 기존 target detection은 변경하지 않았다.

- provider capability: `target.kind: provider-capability`
- replay manifest: `target.kind: replay-manifest`
- sync manifest: `target.kind: sync-manifest`
- unrelated JSON: `target.kind: file`
- `--envelope-v2` without `--json`: exit code 2

## 차단 상태

이번 작업은 provider execution trace 출력 계약 안정화만 수행했다. 다음 기능은 계속 차단되어 있다.

- provider execution
- sandbox execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply/mutation

## 병렬화 평가

후속 작업은 일부 병렬화가 가능하지만 rule promotion은 audit 결과에 의존한다.

권장 bundled/parallel execution order:

1. 병렬 가능: rule promotion audit 초안 작성과 documentation index 영향 검토
2. 순차 필요: audit 결론 확정 후 `.ai/rules` promotion 작업
3. 병렬 가능: future sandbox architecture planning은 rule promotion과 직접 충돌하지 않지만, provider execution authorization으로 오해되지 않도록 별도 design-only bundle로 유지

현재 가장 안전한 다음 작업은 provider execution trace validation rule promotion audit이다.

## 검증

다음 검증 범위를 통과하도록 구성했다.

- provider trace output contract tests
- provider trace validate integration tests
- provider trace validator helper tests
- valid provider trace CLI JSON
- valid provider trace CLI envelope v2
- repository validate
- inspect
- compileall
- diff checks
