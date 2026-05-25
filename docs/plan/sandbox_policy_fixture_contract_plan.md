# Sandbox Policy Fixture Contract Plan

> 이 문서는 design-only 계획서이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Sandbox policy fixture는 future subprocess sandbox를 구현하기 전에 실행 제약, deterministic evidence, no-write evidence, network prohibition, resource limit, environment isolation policy를 정적 JSON fixture로 고정하기 위한 계약이다.

이 fixture는 sandbox approval이 아니며 provider execution authorization도 아니다. 목적은 future validator/helper와 output contract가 어떤 구조를 검증해야 하는지 먼저 명확히 하는 것이다.

## Fixture Goals

- explicit execution constraints를 문서화한다.
- deterministic execution evidence 요구사항을 고정한다.
- no-write evidence 요구사항을 고정한다.
- network prohibition evidence를 고정한다.
- timeout/resource limit policy를 고정한다.
- environment isolation policy를 고정한다.
- filesystem root policy를 검증 가능한 형태로 만든다.
- future provider execution trace와 envelope v2 metadata에 연결 가능한 필드를 정의한다.

## Fixture Layout

권장 fixture layout:

```text
tests/
  fixtures/
    providers/
      sandbox_policies/
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
        edge/
          empty_allowed_read_roots.json
          max_limit_boundary.json
          overlapping_roots.json
          minimal_env_allowlist.json
```

Fixture directory는 provider registry가 아니다. Runtime discovery나 sandbox execution에 사용하면 안 된다.

## Schema Candidates

Primary schema:

```json
{
  "schema_version": "aios.sandbox_policy.v0"
}
```

Optional future schemas:

- `aios.sandbox_execution_request.v0`
- `aios.sandbox_execution_result.v0`

v0에서는 policy fixture를 우선 정의한다. Execution request/result는 sandbox launcher 설계가 승인된 뒤 별도 fixture contract로 확장한다.

## Sandbox Policy Schema

Canonical shape 후보:

```json
{
  "schema_version": "aios.sandbox_policy.v0",
  "sandbox_mode": "subprocess-temp-cwd",
  "timeout_ms": 5000,
  "max_input_bytes": 262144,
  "max_output_bytes": 262144,
  "stdout_limit_bytes": 65536,
  "stderr_limit_bytes": 65536,
  "allowed_read_roots": [".ai", "tests/fixtures/providers"],
  "allowed_output_roots": ["{sandbox_tmp}/outputs"],
  "network_disabled": true,
  "deterministic_execution": true,
  "no_write_required": true,
  "env_policy": {
    "mode": "allowlist",
    "allowed": ["PYTHONUTF8", "AIOS_SANDBOX_MODE"],
    "forbidden_prefixes": ["AWS_", "AZURE_", "GCP_", "OPENAI_", "ANTHROPIC_"]
  },
  "filesystem_policy": {
    "cwd": "{sandbox_tmp}",
    "temp_root_required": true,
    "symlink_policy": "reject",
    "parent_traversal": "reject",
    "absolute_paths": "reject",
    "protected_roots": ["source", "target", "manifest", "snapshots"]
  }
}
```

## Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must be `aios.sandbox_policy.v0`. |
| `sandbox_mode` | string | yes | v0 allowed mode should be explicit. |
| `timeout_ms` | integer | yes | Positive integer. |
| `max_input_bytes` | integer | yes | Positive integer. |
| `max_output_bytes` | integer | yes | Positive integer. |
| `stdout_limit_bytes` | integer | yes | Positive integer. |
| `stderr_limit_bytes` | integer | yes | Positive integer. |
| `allowed_read_roots` | array[string] | yes | May be empty only for no-read fixture. |
| `allowed_output_roots` | array[string] | yes | Must be restricted to sandbox temp output roots. |
| `network_disabled` | boolean | yes | Must be true for v0. |
| `deterministic_execution` | boolean | yes | Must be true for replay eligibility. |
| `no_write_required` | boolean | yes | Must be true. |
| `env_policy` | object | yes | Must describe allowlist behavior. |
| `filesystem_policy` | object | yes | Must describe cwd/temp/symlink/path rules. |

## Enum Candidates

Sandbox mode:

- `subprocess-temp-cwd`
- `fixture-mock`

Reserved future mode:

- `os-container`

Environment policy mode:

- `allowlist`

Filesystem policies:

- `symlink_policy: reject`
- `parent_traversal: reject`
- `absolute_paths: reject`

## Validation Expectations

Static fixture validation should enforce:

- integer limit fields must be positive.
- zero timeout is invalid.
- oversized limits may be allowed only at documented edge boundaries.
- paths must be relative unless symbolic sandbox token such as `{sandbox_tmp}` is explicitly allowed.
- parent traversal is invalid.
- duplicate roots are invalid.
- overlapping roots must be classified as edge or warning candidate, not silently accepted as normal.
- empty `allowed_read_roots` is valid only when the fixture explicitly models no-read behavior.
- `allowed_output_roots` must not point to source, target, manifest, snapshot, or repository root.
- wildcard env allow rules such as `*` are invalid.
- unsupported `sandbox_mode` is invalid.
- `network_disabled` must be true.
- `deterministic_execution` must be true.
- `no_write_required` must be true.
- null policy objects are invalid.

## Edge Cases

Required edge coverage:

- zero timeout: invalid
- oversized limits: boundary-specific edge fixture
- overlapping read roots: warning or explicit edge case
- wildcard env rules: invalid
- null/empty env policy: invalid unless a minimal explicit allowlist is present
- empty read roots: valid only for explicit no-read policy
- output root using `{sandbox_tmp}`: valid
- output root using repository-relative target path: invalid

## No-Write Verification Evidence Model

Future sandbox execution result may include no-write evidence. Policy fixtures should define the expected evidence shape before execution exists.

Candidate evidence fields:

```json
{
  "no_write_evidence": {
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
}
```

Rules:

- pre/post hashes must be comparable by protected root identity.
- `mutation_detected: true` is a blocking failure.
- temp root cleanup evidence is required when a sandbox temp root is used.
- unexpected output outside allowlist is a filesystem violation.

## Failure Evidence Fields

Sandbox failure evidence should support these codes:

- `sandbox-timeout`
- `sandbox-output-invalid`
- `sandbox-resource-limit`
- `sandbox-network-attempt`
- `sandbox-filesystem-violation`
- `sandbox-env-access-violation`
- `sandbox-nondeterministic-output`

Future execution result fixtures should preserve:

- `failure_code`
- `failure_message`
- `sandbox_mode`
- `duration_ms`
- `stdout_truncated`
- `stderr_truncated`
- `resource_limit`
- `network_disabled`
- `mutation_performed`
- `no_write_confirmed`

## Relationship Boundaries

### Provider capability validation

Provider capability validates provider-declared ability. Sandbox policy validates execution environment constraints. Both are necessary future gates, but neither authorizes execution alone.

### Provider execution trace validation

Provider execution trace validates evidence after a provider-like path. Sandbox policy validates the constraints that would govern such a path. Trace success is not sandbox approval.

### Replay comparison

Replay comparison remains fixture-backed. Sandbox policy must not cause provider replay execution or snapshot update.

### Envelope v2

Future envelope metadata may include sandbox fields:

- `sandbox_mode`
- `sandbox_execution`
- `provider_execution`
- `mutation_performed`
- `failure_code`
- `trace_id`

These fields are evidence, not write authorization.

## Explicit Non-goals

This plan does not implement or authorize:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- adapter execution
- dynamic provider loading
- provider registry/discovery
- generated content
- snapshot update
- sync apply/mutation
- `.ai/rules` changes

## Parallelization Plan

Can proceed independently:

- sandbox policy fixture files
- sandbox trace fixture contract
- sandbox execution result fixture contract
- static sandbox policy validator helper design
- envelope metadata design

Can be bundled:

- fixture layout creation
- valid/invalid/edge fixture JSON
- fixture contract tests
- fixture bundle report

Must remain sequential:

1. policy fixture contract
2. fixture-only bundle
3. validator helper
4. validate integration/output contract
5. rule promotion audit
6. launcher architecture review
7. execution readiness audit

Runtime execution work remains blocked until all static and governance gates are complete.

## Next Recommended Slice

다음 안전한 작업은 sandbox policy fixture-only bundle이다. 이 작업은 JSON fixtures와 schema/contract tests만 포함해야 하며 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, sync apply, mutation은 계속 금지해야 한다.
