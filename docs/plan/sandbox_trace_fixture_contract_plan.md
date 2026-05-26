# Sandbox Trace Fixture Contract Plan

> 이 문서는 design-only 계획이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Sandbox trace fixture는 sandbox result evidence와 provider execution trace metadata 사이의 연결 증거를 모델링하기 위한 fixture-only 계약이다. 이 계약은 future sandbox-like execution을 관찰했다는 형태의 정적 증거를 정의하지만, 실제 실행을 허용하거나 provider output을 승인하지 않는다.

목적:

- sandbox result의 `trace_id`를 provider execution trace metadata와 연결한다.
- sandbox-level execution observation을 정적 fixture로 표현한다.
- sandbox result, provider trace, sandbox policy 사이의 참조 경계를 명확히 한다.
- no-execution, no-authorization boundary를 보존한다.
- sync apply, mutation, provider output approval과 분리된 evidence contract를 정의한다.

Sandbox trace는 다음이 아니다.

- sandbox launcher authorization
- subprocess execution authorization
- provider execution authorization
- replay execution authorization
- generated content approval
- provider output approval
- sync apply or mutation authorization

## Schema

Primary schema:

```json
{
  "schema_version": "aios.sandbox_trace.v0"
}
```

이 schema는 fixture-only artifact에 대한 계약이다. Runtime validation, sandbox launcher, subprocess runtime, provider runtime은 별도 계획과 승인 gate 없이는 추가하지 않는다.

## Fixture Layout

권장 fixture layout:

```text
tests/
  fixtures/
    providers/
      sandbox_traces/
        sandbox_trace_index.json
        valid/
          successful_fixture_mock_trace.json
          successful_subprocess_trace.json
          failed_nonzero_trace.json
        invalid/
          missing_trace_id.json
          request_id_mismatch.json
          invalid_status.json
          pass_with_failure_code.json
          mutation_performed_true.json
          network_disabled_false.json
          unsafe_observed_output_path.json
          missing_provenance.json
        edge/
          timeout_trace.json
          resource_limit_trace.json
          no_provider_trace_ref.json
```

Fixture directory는 runtime discovery source가 아니며 provider registry도 아니다.

## Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must be `aios.sandbox_trace.v0`. |
| `trace_id` | string | yes | Stable sandbox trace identity. |
| `request_id` | string | yes | Stable sandbox request/result identity. |
| `sandbox_mode` | string | yes | Expected to align with sandbox policy/result modes. |
| `provider_mode` | string/null | yes | Provider-like mode such as `fixture-mock`; nullable when no provider trace exists. |
| `sandbox_policy_ref` | string/null | yes | Safe relative fixture reference to sandbox policy. |
| `sandbox_result_ref` | string | yes | Safe relative fixture reference to sandbox result. |
| `provider_trace_ref` | string/null | yes | Safe relative fixture reference to provider trace when available. |
| `started_at` | string | yes | RFC3339 UTC timestamp or deterministic placeholder. |
| `completed_at` | string | yes | RFC3339 UTC timestamp or deterministic placeholder. |
| `duration_ms` | integer | yes | Non-negative duration. |
| `status` | string | yes | `pass`, `fail`, `timeout`, or `resource-limit`. |
| `failure_code` | string/null | yes | Required for non-pass status. Null for pass. |
| `network_disabled` | boolean | yes | Must be true for v0 fixtures. |
| `mutation_performed` | boolean | yes | Must be false. |
| `no_write_confirmed` | boolean | yes | Required true for pass. |
| `observed_inputs` | array | yes | Ordered safe relative input observations. |
| `observed_outputs` | array | yes | Ordered safe relative output observations. |
| `provenance` | object | yes | Source refs, hashes, and relationship evidence. |

## Status Values

Allowed `status` values:

- `pass`
- `fail`
- `timeout`
- `resource-limit`

Semantics:

- `pass`: referenced sandbox result and trace evidence describe a successful read-only observation.
- `fail`: referenced evidence describes a non-timeout failure.
- `timeout`: referenced evidence describes timeout handling.
- `resource-limit`: referenced evidence describes resource limit handling.

Status never authorizes sync apply, file writes, provider execution, or sandbox execution.

## Failure Codes

Sandbox trace v0 reuses sandbox result failure code values:

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

## Reference Model

Reference fields are fixture references only.

- `sandbox_policy_ref` points to a sandbox policy fixture when policy evidence is included.
- `sandbox_result_ref` points to the sandbox result fixture that owns the observed `request_id` and `trace_id`.
- `provider_trace_ref` points to provider execution trace metadata when available.
- `provider_trace_ref` may be null for edge cases where sandbox observation exists but provider trace evidence is unavailable.

Reference safety requirements:

- repository-relative or fixture-root-relative paths only
- no absolute paths
- no parent traversal
- no empty path when the ref is non-null
- no runtime discovery or registry lookup

## Relationship Rules

Sandbox trace fixtures define cross-document relationship checks but do not validate full linked document bodies.

Rules:

- `trace_id` must match linked sandbox result `trace_id` when both are available.
- `request_id` must match linked sandbox result `request_id` when referenced.
- `sandbox_result_ref` is required because sandbox trace is anchored to sandbox result evidence.
- `provider_trace_ref` is optional and does not require full provider trace body validation in this fixture contract.
- Sandbox trace success does not authorize sync apply.
- Sandbox trace success does not approve generated provider output.
- Sandbox trace success does not bypass drift-stop, preview, replay, or mutation gates.

## Timestamp and Duration Policy

`started_at` and `completed_at` must be either parseable RFC3339 UTC timestamps or deterministic placeholders approved by fixture tests.

Recommended deterministic placeholder:

```text
1970-01-01T00:00:00Z
```

Validation expectations:

- both fields must be strings.
- parseable timestamps should use UTC `Z`.
- `duration_ms` must be a non-negative integer.
- if both timestamps are parseable and not placeholders, `completed_at` should not be earlier than `started_at`.

## Observed Inputs and Outputs

`observed_inputs` and `observed_outputs` are ordered arrays. Order is significant.

Recommended observation shape:

```json
{
  "kind": "sandbox-result",
  "ref": "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json",
  "hash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

Allowed `kind` candidates:

- `sandbox-policy`
- `sandbox-result`
- `provider-trace`
- `input-bundle`
- `output-json`
- `stdout`
- `stderr`

Validation expectations:

- refs must be safe relative paths or symbolic sandbox refs.
- hashes, when present, must use `sha256:<lowercase-hex>`.
- observed output refs must not point to repository target paths.
- observed output refs should use sandbox temporary/output refs such as `{sandbox_tmp}/outputs/result.json` or fixture-relative paths.
- observations are evidence only and must not create generated content.

## Provenance

`provenance` is required.

Recommended shape:

```json
{
  "source_refs": [
    "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json"
  ],
  "source_hashes": {
    "tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "relationship": "sandbox-result-to-provider-trace",
  "generated_by": "fixture-contract"
}
```

Rules:

- provenance must preserve referenced fixture identities.
- source ref order is significant.
- source hashes must use lowercase sha256 format.
- provenance does not prove provider output correctness.

## Invalid Cases

Required invalid fixture cases:

- `missing_trace_id`
- `request_id_mismatch`
- `invalid_status`
- `pass_with_failure_code`
- `mutation_performed_true`
- `network_disabled_false`
- `unsafe_observed_output_path`
- `missing_provenance`

Each invalid fixture should include an expected issue code in the fixture index or test case table.

## Edge Cases

Required edge fixture cases:

- `timeout_trace`
- `resource_limit_trace`
- `trace_without_provider_trace_ref`

Edge fixtures may pass structural validation when they preserve explicit status/failure-code semantics and non-execution metadata.

## Fixture Index Requirements

`sandbox_trace_index.json` should list fixture inventory and preserve non-execution flags:

```json
{
  "schema_version": "aios.sandbox_trace_index.v0",
  "sandbox_execution": false,
  "subprocess_execution": false,
  "provider_execution": false,
  "replay_execution": false,
  "generated_content_creation": false,
  "mutation_performed": false
}
```

The index is not a runtime registry, provider registry, or sandbox discovery mechanism.

## Validation Expectations

Future fixture tests should enforce:

- fixture inventory consistency.
- required fields exist.
- `schema_version` is `aios.sandbox_trace.v0`.
- status belongs to the allowed enum.
- failure code follows status mapping.
- timestamps are parseable or approved deterministic placeholders.
- `duration_ms` is non-negative.
- `network_disabled` is true.
- `mutation_performed` is false.
- `no_write_confirmed` is true for pass.
- observed input/output refs are safe relative refs.
- observed output refs do not target repository source/target paths.
- provenance exists and is structurally valid.
- relationship refs preserve `trace_id` and `request_id` where referenced.

## Relationship to Existing Artifacts

Sandbox trace fixtures bridge existing evidence layers:

- sandbox policy: declared constraints
- sandbox result: observed subprocess/sandbox-like result evidence
- provider execution trace: provider-like metadata evidence
- envelope v2: future output metadata carrier

The bridge is static. It does not execute or approve any linked artifact.

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

## Future Implementation Slices

Recommended order:

1. Sandbox trace fixture-only bundle.
2. Sandbox trace fixture contract tests.
3. Sandbox trace validator helper.
4. Sandbox trace validate output contract.
5. Sandbox trace validate integration.
6. Output contract stabilization.
7. Rule promotion audit, if runtime validation is implemented.

Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, and mutation remain blocked.

## Parallelization Note

This design can proceed independently from sandbox launcher design because it only defines static fixtures. The sandbox trace fixture bundle can follow this plan. The sandbox trace validator helper must wait until the fixture bundle exists. Sandbox launcher and execution implementation remain sequentially blocked behind future readiness gates.
