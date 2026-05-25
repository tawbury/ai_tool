# 제공자 실행 trace schema 계획

> 이 문서는 human context 계획 문서이다. 런타임 계약의 정본은 `.ai/rules/`이며, 이 계획은 provider-like execution을 실제로 구현하기 전에 필요한 trace schema 후보를 정의한다.

## 목적

Provider execution trace는 future mock provider helper, subprocess sandbox, real provider execution을 설계하기 전에 관측 가능성과 안전 증거를 고정하기 위한 구조다. Trace는 실행을 승인하지 않는다. Trace는 provider-like path가 어떤 input, provider identity, hash, no-write/network confirmation, failure reason을 남겨야 하는지 정의한다.

Trace의 목적:

- future provider-like execution의 observability 제공
- deterministic replay evidence 보존
- no-write/no-network confirmation 보존
- failure/unavailable explanation 표준화
- envelope v2와 future event model에 넣을 metadata 경계 정의

Trace는 다음이 아니다.

- provider execution authorization
- sandbox approval
- sync apply authorization
- generated content approval
- mutation safety 전체를 대체하는 증거

## Schema candidate

Schema version:

```json
{
  "schema_version": "aios.provider_execution_trace.v0"
}
```

Canonical shape 후보:

```json
{
  "schema_version": "aios.provider_execution_trace.v0",
  "trace_id": "trace-mock-example-0001",
  "provider_id": "aios.mock.preview.fixture",
  "provider_version": "0.1.0",
  "provider_mode": "fixture-mock",
  "case_id": "whole_file",
  "input_hash": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "output_hash": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "generated_hashes": {
    "generated_bytes_hash": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    "generated_target_hash": "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    "generated_managed_block_hash": null
  },
  "duration_ms": 1,
  "deterministic_execution": true,
  "no_write_confirmed": true,
  "network_disabled": true,
  "mutation_performed": false,
  "unavailable_reason": null,
  "failure_code": null,
  "provenance": {
    "source_paths": [".ai/rules/operations/validation.rules.md"],
    "source_hashes": {
      ".ai/rules/operations/validation.rules.md": "sha256:4444444444444444444444444444444444444444444444444444444444444444"
    },
    "generated_by": "aios.mock_provider.fixture.v0"
  }
}
```

## Required fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must be `aios.provider_execution_trace.v0`. |
| `trace_id` | string | yes | Stable trace identity for a provider-like run. |
| `provider_id` | string | yes | Provider identity from capability/snapshot. |
| `provider_version` | string | yes | Output-affecting version. |
| `provider_mode` | string | yes | Execution mode enum. |
| `case_id` | string/null | yes | Replay/mock case id when available. |
| `input_hash` | string | yes | Hash of normalized trace input object or fixture input reference. |
| `output_hash` | string/null | yes | Hash of output object or null when unavailable before output. |
| `generated_hashes` | object | yes | Generated hash fields, nullable by failure mode. |
| `duration_ms` | integer | yes | Non-negative duration measurement. |
| `deterministic_execution` | boolean | yes | Whether output is deterministic under declared mode. |
| `no_write_confirmed` | boolean | yes | Whether no-write check passed. |
| `network_disabled` | boolean | yes | Whether network was disabled by policy. |
| `mutation_performed` | boolean | yes | Must be false in current/future read-only phases. |
| `unavailable_reason` | string/null | yes | Explicit unavailable reason when preview/output is unavailable. |
| `failure_code` | string/null | yes | Explicit failure code when provider-like path failed. |
| `provenance` | object | yes | Source paths, hashes, and generation identity. |

## Enum values

`provider_mode` v0 values:

- `fixture-mock`
- future reserved: `subprocess-sandbox`

`failure_code` v0 values:

- `provider-timeout`
- `nondeterministic-output`
- `provider-execution-disabled`
- `provider-isolation-violation`
- `provider-capability-missing`
- `provider-output-invalid`
- `provider-network-disabled`
- `provider-resource-limit`

Future values require a plan, tests, and runtime rule promotion before use.

## Success semantics

Successful trace semantics:

- `mutation_performed: false`
- `no_write_confirmed: true`
- `network_disabled: true`
- `deterministic_execution: true`
- `failure_code: null`
- `unavailable_reason: null` when preview/output is available
- generated hashes are present according to sync mode

Success does not authorize writes. It only means the provider-like path produced a deterministic read-only comparison artifact under the declared mode.

## Failure and unavailable semantics

Failure and unavailable are separate but may appear together.

- `unavailable_reason` explains why preview/output is unavailable.
- `failure_code` explains why provider-like execution failed.
- Generated hashes may be null depending on failure mode.
- `mutation_performed` must remain false even on failure.
- `no_write_confirmed` may be false only if no-write verification itself failed or could not complete.
- `network_disabled` must remain true for all v0 allowed modes.

Failure is not update authorization. Unavailable output must not create an update candidate.

## Envelope v2 relationship

Future envelope v2 mappings may embed trace metadata in `payload.results[*].details.trace` or command-level `meta`.

Envelope metadata must preserve:

- `provider_execution`
- `sandbox_execution`
- `mutation_performed`
- `provider_mode`
- `provider_id`
- `provider_version`
- `trace_id`

For `fixture-mock`, `provider_execution` and `sandbox_execution` should remain false until a separately approved helper/runtime boundary exists.

## Mock provider fixture relationship

Current mock provider fixtures already contain compatible trace fields:

- `execution_trace_id`
- `provider_metadata.provider_id`
- `provider_metadata.provider_version`
- `deterministic_execution`
- `no_write_confirmed`
- `network_disabled`
- `input_hash`
- `output_hash`
- `duration_ms`
- `generated_*_hash`
- `unavailable_reason`
- `provenance`

No new execution behavior is required. A future trace fixture bundle can either wrap existing mock outputs into `aios.provider_execution_trace.v0` documents or add parallel trace fixtures under the mock provider fixture tree.

## Redaction and privacy policy

No secrets are expected in v0 fixture/mock traces.

Allowed to show:

- hashes
- provider id/version
- case id
- sync mode-related generated hash fields
- source-relative paths already present in provenance
- failure/unavailable codes

Must redact in future:

- environment variables
- credentials
- API keys
- host-specific absolute paths
- provider config values marked secret
- raw generated content when it may include sensitive context

Trace v0 should prefer hashes and summaries over large raw payloads.

## Explicit non-goals

This plan does not implement or authorize:

- provider execution
- sandbox launch
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply
- mutation
- `.ai/rules` changes

## Next implementation slice

Recommended order:

1. Provider execution trace fixture bundle
2. Trace validator helper
3. Mock provider helper design
4. Subprocess sandbox architecture plan

The next safest slice is trace fixtures, not execution code. Provider execution, sandbox execution, adapter execution, generated content creation, replay execution, snapshot update, sync apply, and mutation remain blocked.
