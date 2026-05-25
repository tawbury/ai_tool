# Sandbox Policy Validator Helper Report

## 목적

이 보고서는 `aios.sandbox_policy.v0` sandbox policy fixture를 대상으로 하는 순수 정적 검증 helper 구현 결과를 기록한다.

이번 작업은 sandbox launcher, subprocess execution, provider execution을 추가하지 않는다. Helper는 이미 파싱된 `dict`를 입력으로 받아 issue 목록을 반환하며, 파일 IO, CLI 통합, envelope v2 통합, `aios validate` 통합을 수행하지 않는다.

## 구현 범위

추가된 런타임 helper:

- `src/aios/providers/sandbox_policy.py`

추가된 테스트:

- `tests/test_sandbox_policy_validator.py`

Helper는 다음 상수를 정의한다.

- schema version: `aios.sandbox_policy.v0`
- sandbox modes:
  - `fixture-mock`
  - `subprocess-temp-cwd`
- env policy mode:
  - `allowlist`

Helper는 다음 issue/result 모델을 제공한다.

- `SandboxPolicyIssue`
- `SandboxPolicyValidationResult`
- `validate_sandbox_policy_data(data)`

## 검증 항목

Helper는 다음 항목을 정적으로 검증한다.

- 입력이 object인지 여부
- required fields 존재 여부
- `schema_version`
- `sandbox_mode` enum
- positive integer limits:
  - `timeout_ms`
  - `max_input_bytes`
  - `max_output_bytes`
  - `stdout_limit_bytes`
  - `stderr_limit_bytes`
- `allowed_read_roots` list
- `allowed_output_roots` list
- relative path safety
- parent traversal rejection
- absolute path rejection
- duplicate read/output roots
- output roots의 `{sandbox_tmp}/...` boundary
- `network_disabled: true`
- `deterministic_execution: true`
- `no_write_required: true`
- `env_policy.mode: allowlist`
- wildcard env rule rejection
- `forbidden_prefixes` list
- `filesystem_policy.cwd: {sandbox_tmp}`
- `temp_root_required: true`
- `symlink_policy: reject`
- `parent_traversal: reject`
- `absolute_paths: reject`
- non-empty `protected_roots`
- optional `edge_classification`

## 테스트 범위

추가된 unit tests는 다음을 고정한다.

- valid fixtures produce no errors
- edge fixtures produce no errors
- each invalid fixture returns the expected issue code
- unsupported schema
- unsupported sandbox mode
- zero timeout
- invalid integer limits
- absolute read root
- parent traversal output root
- duplicate read roots
- network enabled
- deterministic false
- no-write false
- wildcard env rule
- malformed/null env policy
- malformed filesystem policy
- output root repo target
- invalid edge classification
- non-object input error
- validator does not mutate input

## 명시적 비목표

이번 작업은 다음을 구현하지 않는다.

- `aios validate <sandbox-policy.json>`
- envelope v2 mapping
- CLI flag or command
- sandbox launcher
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

## 문서 인덱스 업데이트

문서 인덱스는 이번 helper completion을 summary-first context에 반영했다.

- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

이 인덱스들은 human context이며 runtime contract가 아니다. `.ai/rules/`가 계속 canonical runtime authority다.

## 병렬화 메모

이 helper는 sandbox policy fixture bundle 완료 뒤 순차적으로 진행되는 것이 맞다. Helper가 구현되었으므로 다음 `aios validate <sandbox-policy.json>` 통합은 별도 output contract design과 검증 계획을 먼저 거쳐야 한다.

Sandbox trace fixture contract와 sandbox execution result fixture contract는 이 helper와 독립적인 design-only track으로 진행할 수 있다. Sandbox launcher, subprocess execution, provider execution은 여전히 순차적으로 차단되어 있으며 별도 readiness gate와 rule promotion 없이 시작하면 안 된다.

## 검증 결과

최종 검증은 커밋 직전에 수행한다.
