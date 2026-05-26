# Sandbox Trace Validator Helper Report

## 목적

이 보고서는 `aios.sandbox_trace.v0` sandbox trace validator helper 구현 결과를 기록한다. 이번 작업은 parsed dict를 입력으로 받는 순수 정적 검증 helper와 unit tests만 추가했으며 `aios validate <sandbox-trace.json>` 통합, envelope v2 mapping, sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation은 구현하지 않았다.

## 추가된 모듈

추가 파일:

- `src/aios/providers/sandbox_trace.py`

제공 API:

- `validate_sandbox_trace_data(data)`
- `SandboxTraceIssue`
- `SandboxTraceValidationResult`

Helper 특성:

- parsed dict만 검증한다.
- file IO를 수행하지 않는다.
- sandbox result fixture나 provider trace fixture를 열지 않는다.
- sandbox launcher를 실행하지 않는다.
- subprocess/provider/replay execution을 수행하지 않는다.
- dynamic loading, registry/discovery, adapter execution을 수행하지 않는다.

## 검증 범위

검증 항목:

- `schema_version: aios.sandbox_trace.v0`
- required fields
- `trace_id`/`request_id` non-empty string
- sandbox/provider mode enums
- status/failure_code mapping
- non-negative `duration_ms`
- timestamp string format
- `network_disabled: true`
- `mutation_performed: false`
- `status: pass` requires `no_write_confirmed: true`
- safe relative refs
- observed input/output ref safety
- observed hash format
- provenance object shape
- `provider_trace_ref` nullability only with explicit `provider-trace-ref-unavailable` edge classification

## Relationship Boundary

`request_id_mismatch` 같은 cross-fixture relationship check는 sandbox result fixture 파일을 열어야 하므로 helper 범위에서 제외했다. 해당 관계 검증은 fixture contract tests의 범위로 남긴다.

Helper는 다음을 하지 않는다.

- referenced sandbox result body validation
- full provider trace body validation
- provider output approval
- sandbox execution evidence approval
- sync apply authorization

## Tests

추가 파일:

- `tests/test_sandbox_trace_validator.py`

테스트 범위:

- valid fixtures produce no errors
- edge fixtures produce no errors
- invalid fixtures produce expected helper-level issue codes
- relationship-only mismatch is out of helper scope
- unsupported schema
- invalid trace/request id
- invalid sandbox/provider modes
- status/failure-code mapping
- duration/timestamp validation
- network/mutation/no-write flags
- safe ref checks
- observed input/output validation
- provenance validation
- provider trace ref nullability policy
- issue dict shape
- non-object input error
- no input mutation

## Docs Index Update

`docs/index/document_status_registry.md`에 helper report를 completed implementation report로 추가했다.

`docs/index/phase_6_8_summary.md`와 `docs/index/current_runtime_context.md`는 sandbox trace validator helper 완료 상태와 다음 순서인 sandbox trace validate output contract design을 반영했다.

## 병렬화 메모

이번 작업은 helper 구현, unit tests, docs index update, report를 안전하게 묶었다.

다음 순서:

1. Sandbox trace validate output contract design.
2. Sandbox trace validate integration.
3. Sandbox trace output contract stabilization.
4. Runtime rule promotion audit if validation integration is implemented.

Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation은 계속 차단된다.

## 검증

실행한 대표 검증:

- `python -m pytest tests/test_sandbox_trace_validator.py`

최종 검증 명령은 작업 완료 전에 별도로 실행한다.
