# Sandbox Policy Fixture Bundle Report

> 이 문서는 fixture-only 구현 보고서이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

`aios.sandbox_policy.v0` sandbox policy 계약을 concrete JSON fixtures와 fixture-only contract tests로 고정했다. 이 작업은 future sandbox validator/helper 이전 단계이며 runtime validation integration이나 execution behavior를 추가하지 않았다.

## 추가한 Fixture Layout

```text
tests/fixtures/providers/sandbox_policies/
  sandbox_policy_index.json
  valid/
    fixture_mock_default_policy.json
    subprocess_temp_cwd_policy.json
    no_read_roots_policy.json
  invalid/
    unsupported_sandbox_mode.json
    zero_timeout.json
    absolute_read_root.json
    parent_traversal_output_root.json
    duplicate_read_root.json
    network_enabled.json
    wildcard_env_rule.json
    malformed_filesystem_policy.json
    null_env_policy.json
    output_root_repo_target.json
  edge/
    empty_allowed_read_roots.json
    max_limit_boundary.json
    overlapping_roots.json
    minimal_env_allowlist.json
    sandbox_tmp_output_root.json
```

## 고정한 Contract

- 모든 policy fixture는 `schema_version: aios.sandbox_policy.v0`를 사용한다.
- Fixture index는 non-execution flags를 명시한다.
- Required fields:
  - `sandbox_mode`
  - `timeout_ms`
  - `max_input_bytes`
  - `max_output_bytes`
  - `stdout_limit_bytes`
  - `stderr_limit_bytes`
  - `allowed_read_roots`
  - `allowed_output_roots`
  - `network_disabled`
  - `deterministic_execution`
  - `no_write_required`
  - `env_policy`
  - `filesystem_policy`
- Valid fixtures는 structural assertions를 통과한다.
- Invalid fixtures는 expected issue assertion을 고정한다.
- Edge fixtures는 explicit `edge_classification`을 가진다.

## 테스트

추가한 테스트:

- `tests/test_sandbox_policy_fixtures.py`

테스트 범위:

- fixture inventory consistency
- fixture index path references
- every JSON fixture parses
- valid fixtures structural assertions
- invalid fixtures expected assertions
- edge fixture explicit classification
- positive integer limit enforcement
- zero timeout invalid
- absolute path rejection
- parent traversal rejection
- duplicate roots invalid
- network disabled requirement
- deterministic execution requirement
- no-write requirement
- env allowlist requirement
- wildcard env rejection
- filesystem policy requirement
- sandbox temp output root requirement
- fixture-only non-execution flags

## Non-execution Boundary

이번 작업은 다음을 추가하지 않았다.

- sandbox validator helper
- `aios validate <sandbox-policy.json>`
- envelope v2 mapping
- sandbox launcher
- subprocess execution
- provider execution
- dynamic loading
- provider registry/discovery
- adapter execution
- generated content
- replay execution
- snapshot update
- sync apply/mutation
- `.ai/rules` changes

## 병렬화 메모

이번 task는 fixture JSON, contract tests, docs index update, bundle report를 안전하게 번들링했다.

다음 작업은 병렬 design-only track으로 분리할 수 있다.

- sandbox trace fixture contract
- sandbox execution result fixture contract

Sandbox policy validator helper는 fixture bundle이 완료된 뒤에 진행해야 한다. Sandbox execution은 계속 차단된다.

## 검증

다음 검증을 수행했다.

- `python -m pytest tests/test_sandbox_policy_fixtures.py`
- `python -m pytest tests/test_provider_execution_trace_validate_output_contract.py`
- `python -m pytest tests/test_provider_capability_validate_output_contract.py`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
