# Sandbox Execution Result Fixture Contract Plan

> 이 문서는 design-only 계획이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Sandbox execution result fixture는 future sandbox-like execution이 실제로 도입되기 전에 결과 evidence의 구조를 고정하기 위한 fixture-only 계약이다.

목적:

- future sandbox result evidence를 구조화한다.
- subprocess exit/output/resource/no-write evidence를 모델링한다.
- sandbox policy와 provider execution trace 사이의 연결 지점을 명확히 한다.
- sandbox success가 execution authorization, provider output approval, sync apply authorization이 아님을 고정한다.

비목적:

- sandbox launcher 구현
- subprocess execution 구현
- provider execution 구현
- provider output 승인
- generated content 생성
- snapshot update
- sync apply/mutation 승인

## Schema

Primary schema:

```json
{
  "schema_version": "aios.sandbox_execution_result.v0"
}
```

이 schema는 fixture-only artifact다. Runtime validation이나 execution runtime은 별도 계획과 구현 gate를 거쳐야 한다.

## Fixture Layout

권장 layout:

```text
tests/
  fixtures/
    providers/
      sandbox_results/
        valid/
          successful_subprocess_result.json
          successful_fixture_mock_result.json
          nonzero_exit_result.json
          timeout_result.json
          resource_limit_result.json
        invalid/
          missing_request_id.json
          mutation_performed_true.json
          no_write_false_pass.json
          network_disabled_false.json
          pass_with_failure_code.json
          fail_without_failure_code.json
          negative_stdout_bytes.json
          malformed_no_write_evidence.json
        edge/
          zero_duration_result.json
          truncated_stdout_result.json
          invalid_output_json_result.json
```

Fixture directory는 sandbox registry나 runtime discovery source가 아니다.

## Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must be `aios.sandbox_execution_result.v0`. |
| `sandbox_mode` | string | yes | Expected values align with sandbox policy modes. |
| `request_id` | string | yes | Stable identity for the sandbox request/result pair. |
| `exit_code` | integer/null | yes | Subprocess exit code or null when timeout prevented normal exit. |
| `status` | string | yes | `pass`, `fail`, `timeout`, or `resource-limit`. |
| `duration_ms` | integer | yes | Non-negative duration. |
| `stdout_bytes` | integer | yes | Non-negative byte count. |
| `stderr_bytes` | integer | yes | Non-negative byte count. |
| `stdout_truncated` | boolean | yes | Whether stdout exceeded display/storage cap. |
| `stderr_truncated` | boolean | yes | Whether stderr exceeded display/storage cap. |
| `output_json_valid` | boolean | yes | Whether expected sandbox output JSON parsed and matched minimal shape. |
| `failure_code` | string/null | yes | Required for non-pass status. Null for pass. |
| `failure_message` | string/null | yes | Human diagnostic summary for failures. |
| `resource_limit` | object/null | yes | Resource limit evidence when applicable. |
| `network_disabled` | boolean | yes | Must remain true in v0 fixtures. |
| `mutation_performed` | boolean | yes | Must be false. |
| `no_write_confirmed` | boolean | yes | Required true for pass. |
| `no_write_evidence` | object | yes | Protected root hash and cleanup evidence. |
| `trace_id` | string/null | yes | Link to future provider execution trace metadata when available. |

## Status Values

Allowed `status` values:

- `pass`
- `fail`
- `timeout`
- `resource-limit`

Semantics:

- `pass`: sandbox-like result completed under policy with no failure code.
- `fail`: sandbox-like result completed or stopped with a non-timeout failure.
- `timeout`: timeout policy stopped or would stop the run.
- `resource-limit`: output, input, memory, or other resource cap was exceeded.

Status does not authorize sync apply.

## Failure Codes

Allowed `failure_code` values:

- `sandbox-timeout`
- `sandbox-nonzero-exit`
- `sandbox-output-invalid`
- `sandbox-resource-limit`
- `sandbox-network-attempt`
- `sandbox-filesystem-violation`
- `sandbox-env-access-violation`
- `sandbox-nondeterministic-output`

Rules:

- `status: pass` requires `failure_code: null`.
- `status: fail` requires a non-null failure code.
- `status: timeout` requires `failure_code: sandbox-timeout`.
- `status: resource-limit` requires `failure_code: sandbox-resource-limit`.

## No-write Evidence Model

`no_write_evidence` is required for all result fixtures.

Canonical shape:

```json
{
  "protected_roots": ["source", "target", "manifest", "snapshots"],
  "pre_hashes": {
    "source": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "post_hashes": {
    "source": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "mutation_detected": false,
  "temp_root_cleaned": true,
  "unexpected_outputs": []
}
```

Validation expectations:

- `protected_roots` must be a non-empty ordered list.
- `pre_hashes` and `post_hashes` must be objects keyed by protected root identity.
- Hash strings must use `sha256:<lowercase-hex>` when present.
- `mutation_detected` must be false for pass.
- `temp_root_cleaned` must be true for pass.
- `unexpected_outputs` must be an array.
- Any unexpected output outside allowed roots is a failure candidate.

No-write evidence is proof data, not write authorization.

## Resource Limit Evidence

`resource_limit` may be null when no resource failure occurred.

Recommended shape when present:

```json
{
  "limit_kind": "stdout",
  "limit_bytes": 65536,
  "observed_bytes": 70000
}
```

Allowed `limit_kind` candidates:

- `input`
- `output`
- `stdout`
- `stderr`
- `memory`
- `duration`

`resource-limit` status requires a non-null `resource_limit`.

## Validation Expectations

Future fixture contract tests should enforce:

- required fields exist.
- `schema_version` is `aios.sandbox_execution_result.v0`.
- `status` belongs to the allowed enum.
- `failure_code` belongs to the allowed enum or null.
- `status: pass` requires `failure_code: null`.
- non-pass status requires a failure code.
- `mutation_performed` must be false.
- `network_disabled` must be true.
- `no_write_confirmed` must be true for pass.
- `duration_ms`, `stdout_bytes`, `stderr_bytes` must be non-negative integers.
- `stdout_truncated`, `stderr_truncated`, `output_json_valid` must be booleans.
- `no_write_evidence` is required and structurally valid.
- pass requires `output_json_valid: true`.
- `trace_id`, when present, is a string and does not imply full trace validation.

## Relationship to Provider Execution Trace

`trace_id` links a sandbox result fixture to future provider execution trace metadata.

Boundaries:

- sandbox result validation does not validate full trace content.
- provider execution trace validation remains static-only.
- sandbox result success does not authorize sync apply.
- sandbox result success does not approve generated provider output.
- a future integration may cross-check `trace_id`, but that is out of scope for fixture-only contracts.

## Relationship to Sandbox Policy

Sandbox policy describes constraints. Sandbox execution result describes observed result evidence under a declared policy.

Both are future readiness inputs only:

- valid sandbox policy does not authorize execution.
- valid sandbox result does not authorize sync apply.
- result fixtures must preserve non-execution assumptions until a future launcher is explicitly approved.

## Relationship to Envelope v2

Future envelope metadata may include:

- `sandbox_execution`
- `subprocess_execution`
- `provider_execution`
- `mutation_performed`
- `sandbox_mode`
- `trace_id`
- `failure_code`
- `request_id`

These fields must be evidence only. They must not imply write authorization or provider output approval.

## Explicit Non-goals

This plan does not implement or authorize:

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
- `.ai/rules` changes

## Parallelization Plan

Can proceed after this plan:

- sandbox execution result fixture-only bundle
- fixture contract tests
- fixture bundle report

Can proceed independently as design-only work:

- sandbox trace fixture contract
- sandbox trace fixture risk audit

Must remain sequential:

1. result fixture contract
2. result fixture-only bundle
3. result validator helper
4. validate output contract
5. validate integration
6. output contract stabilization
7. rule promotion audit

Sandbox launcher and subprocess execution remain blocked until a later readiness gate explicitly approves execution implementation.
