# Sandbox Trace Fixture Bundle Report

## 목적

이 보고서는 `aios.sandbox_trace.v0` sandbox trace fixture-only bundle 구현 결과를 기록한다. 이번 작업은 fixture JSON, fixture index, contract tests, docs index update만 포함하며 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 추가된 fixture layout

추가된 경로:

```text
tests/fixtures/providers/sandbox_traces/
  sandbox_trace_index.json
  valid/
  invalid/
  edge/
```

추가된 valid fixtures:

- `successful_sandbox_trace.json`
- `fixture_mock_trace.json`
- `timeout_sandbox_trace.json`
- `resource_limit_sandbox_trace.json`

추가된 invalid fixtures:

- `missing_trace_id.json`
- `request_id_mismatch.json`
- `invalid_status.json`
- `pass_with_failure_code.json`
- `mutation_performed_true.json`
- `network_disabled_false.json`
- `unsafe_observed_output_path.json`
- `missing_provenance.json`

추가된 edge fixtures:

- `trace_without_provider_trace_ref.json`
- `zero_duration_trace.json`
- `partial_observed_outputs_trace.json`

## Fixture Index

`sandbox_trace_index.json`는 fixture inventory와 expected invalid issue mapping을 포함한다.

Index는 다음 non-execution flags를 보존한다.

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `generated_content_creation: false`
- `mutation_performed: false`

Index는 runtime registry, provider registry, sandbox discovery source가 아니다.

## Contract Tests

추가된 테스트:

- `tests/test_sandbox_trace_fixtures.py`

테스트가 확인하는 범위:

- fixture inventory consistency
- fixture index references existing files
- every fixture parses
- valid fixture structural contract
- invalid fixture expected issue code
- edge fixture `edge_classification`
- status enum validation
- status/failure-code mapping
- trace/request id presence
- non-negative duration
- timestamp string format
- non-execution flags
- safe relative refs
- observed input/output ref safety
- provenance presence and structure
- sandbox result relationship consistency for `trace_id` and `request_id`
- `provider_trace_ref` nullability only for explicit edge fixture

Provider trace body 전체 검증은 수행하지 않는다. Sandbox result relationship check도 referenced sandbox result의 `trace_id`와 `request_id` consistency만 확인한다.

## Boundary

이번 bundle은 다음을 수행하지 않는다.

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- `aios validate <sandbox-trace.json>`
- envelope v2 mapping
- sync apply
- mutation
- `.ai/rules` modification

## Docs Index Update

`docs/index/document_status_registry.md`에서 sandbox trace fixture contract plan은 fixture bundle로 superseded된 historical plan으로 갱신하고, 이 bundle report를 completed implementation report로 추가했다.

`docs/index/phase_6_8_summary.md`와 `docs/index/current_runtime_context.md`는 sandbox trace fixture-only bundle 완료 상태와 다음 sequential step인 sandbox trace validator helper를 반영했다.

## 병렬화 메모

이번 작업은 fixture JSON, contract tests, docs index update, bundle report를 안전하게 묶어 진행했다.

다음 순서:

1. Sandbox trace validator helper
2. Sandbox trace validate output contract
3. Sandbox trace validate integration
4. Output contract stabilization
5. Rule promotion audit if validation integration is implemented

Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation은 계속 차단된다.

## 검증

실행한 대표 검증:

- `python -m pytest tests/test_sandbox_trace_fixtures.py`

최종 검증 명령은 작업 완료 전에 별도로 실행한다.
