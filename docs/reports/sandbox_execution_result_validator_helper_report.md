# Sandbox Execution Result Validator Helper Report

## 목적

이 보고서는 `aios.sandbox_execution_result.v0` sandbox execution result validation helper 구현 결과를 기록한다. Helper는 parsed dict만 정적으로 검증하며 file IO, sandbox launcher, subprocess execution, provider execution, replay execution을 수행하지 않는다.

## 구현 범위

추가된 모듈:

- `src/aios/providers/sandbox_result.py`

추가된 테스트:

- `tests/test_sandbox_execution_result_validator.py`

Helper는 다음 public API를 제공한다.

- `validate_sandbox_execution_result_data(data)`
- `SandboxExecutionResultIssue`
- `SandboxExecutionResultValidationResult`

## 검증 규칙

Helper는 다음을 정적으로 검증한다.

- required fields
- `schema_version: aios.sandbox_execution_result.v0`
- `sandbox_mode` enum
- `request_id` non-empty string
- `exit_code` integer 또는 null
- `status` enum
- `failure_code` enum 또는 null
- status/failure code mapping
- `duration_ms`, `stdout_bytes`, `stderr_bytes` non-negative integer
- boolean fields
- pass result의 `output_json_valid: true`
- `network_disabled: true`
- `mutation_performed: false`
- pass result의 `no_write_confirmed: true`
- `no_write_evidence` object와 protected root hash 구조
- lowercase `sha256:<hex>` hash format
- `mutation_detected: false`
- pass result의 `temp_root_cleaned: true`
- `unexpected_outputs` list
- `trace_id` null 또는 non-empty string
- resource-limit status의 `resource_limit` object
- optional `edge_classification`

## 테스트 범위

테스트는 valid/edge fixtures가 error 없이 통과하는지, invalid fixtures가 기대 issue code를 반환하는지, 그리고 mutation 기반 케이스가 개별 검증 규칙을 고정하는지 확인한다. 또한 issue dict shape와 입력 dict 불변성을 확인한다.

## 비목표

이번 작업은 다음을 구현하지 않았다.

- `aios validate <sandbox-result.json>`
- envelope v2 mapping
- CLI flag 또는 command
- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply 또는 mutation

## 문서 인덱스

`docs/index/document_status_registry.md`에 helper report를 completed implementation report로 추가했다. `docs/index/current_runtime_context.md`와 `docs/index/phase_6_8_summary.md`는 다음 안전 방향을 sandbox execution result validate output contract 설계로 갱신했다.

## 병렬화 메모

이 helper는 fixture bundle 완료 후 순차적으로 구현했다. Validate integration은 별도 output contract 설계가 완료된 뒤 진행해야 한다. Sandbox trace fixture contract는 design-only 작업으로 독립 진행할 수 있다. Sandbox launcher와 subprocess execution은 계속 차단된다.

## 검증

실행 대상:

- `python -m pytest tests/test_sandbox_execution_result_validator.py`
- `python -m pytest tests/test_sandbox_execution_result_fixtures.py`
- `python -m pytest tests/test_sandbox_policy_validate_output_contract.py`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
