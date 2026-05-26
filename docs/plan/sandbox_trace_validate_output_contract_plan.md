# Sandbox Trace Validate Output Contract Plan

## 목적

이 문서는 future `aios validate <sandbox-trace.json>` 정적 검증의 native JSON 및 envelope v2 출력 계약을 정의한다. 현재 sandbox trace validation은 helper-only 상태이며 `src/aios/providers/sandbox_trace.py`의 `validate_sandbox_trace_data(data)`는 parsed dict만 검증한다.

이 문서는 output contract만 설계한다. Runtime code, `aios validate` 통합, `.ai/rules` 변경, sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation은 포함하지 않는다.

## Target Detection

Sandbox trace target detection은 JSON object에만 적용한다.

명확한 detection 조건:

- JSON object이고 `schema_version: aios.sandbox_trace.v0`인 경우

Schema error validation을 위해 sandbox-trace-shaped JSON도 감지할 수 있다.

권장 shaped heuristic:

- JSON object이고 다음 sandbox trace fields 중 최소 7개 이상을 포함한다.
  - `trace_id`
  - `request_id`
  - `sandbox_mode`
  - `provider_mode`
  - `sandbox_policy_ref`
  - `sandbox_result_ref`
  - `provider_trace_ref`
  - `started_at`
  - `completed_at`
  - `duration_ms`
  - `status`
  - `failure_code`
  - `network_disabled`
  - `mutation_performed`
  - `no_write_confirmed`
  - `observed_inputs`
  - `observed_outputs`
  - `provenance`
- 그리고 `trace_id`, `request_id`, `sandbox_result_ref` 중 하나 이상이 존재한다.

Misclassification 방지:

- unrelated JSON은 sandbox-trace로 분류하지 않는다.
- 단순히 `trace_id` 하나만 있는 JSON은 sandbox trace가 아니다.
- sandbox result JSON은 sandbox result detection이 우선한다.
- sandbox policy, provider execution trace, provider capability, replay manifest, sync manifest detection이 기존 우선순위를 유지한다.

권장 priority order:

1. activation target detection
2. sync manifest detection
3. replay manifest detection
4. provider capability detection
5. provider execution trace detection
6. sandbox policy detection
7. sandbox result detection
8. sandbox trace detection
9. generic file or unsupported target fallback

## Target Kind

Future validate target kind:

```text
sandbox-trace
```

Native and envelope outputs must preserve:

```json
{
  "target": {
    "kind": "sandbox-trace"
  }
}
```

## Native JSON Contract

Native validate JSON must keep existing validate schema:

```json
{
  "schema_version": "aios.validate.result.v0",
  "command": "validate",
  "target": {
    "kind": "sandbox-trace"
  }
}
```

Success result:

- `code: sandbox_trace_checked`
- `severity: info`
- `status: pass`
- message must state static validation completed without sandbox or provider execution.

Success details:

- `trace_id`
- `request_id`
- `sandbox_mode`
- `provider_mode`
- `status`
- `failure_code`
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

`mutation_performed` in command output metadata must describe the validate command behavior and remain false even when an invalid trace document claims otherwise.

## Issue Mapping

Validator issues must preserve helper issue fields.

Mapping:

- `SandboxTraceIssue.code` -> result `code`
- `SandboxTraceIssue.severity` -> result `severity`
- `SandboxTraceIssue.status` -> result `status`
- `SandboxTraceIssue.message` -> result `message`
- `SandboxTraceIssue.field` -> result `field` when available

Failure result details:

- `trace_id` when available
- `request_id` when available
- `sandbox_mode` when available
- `provider_mode` when available
- `status` when available
- `failure_code` when available
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

Failure details must not imply sandbox execution or provider execution occurred.

## Envelope v2 Mapping

When `--json --envelope-v2` is used:

Top-level:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: sandbox-trace`
- canonical `status: pass|warn|fail`

Meta:

- `legacy_schema_version: aios.validate.result.v0`
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`
- `trace_id` when available
- `request_id` when available
- `failure_code` when available
- `sandbox_mode` when available
- `provider_mode` when available

Payload:

- `payload.results` preserves native validation results.

Messages:

- issue results map to messages with helper code/message/field/details preserved.
- success info may appear as an info message if consistent with existing validate envelope behavior.

Envelope metadata is evidence only. It must not authorize sandbox launch, subprocess execution, provider execution, replay execution, sync apply, or mutation.

## Exit Semantics

| Condition | Status | Exit code |
| --- | --- | --- |
| Valid sandbox trace | `pass` | 0 |
| Sandbox trace validation error | `fail` | 1 |
| Usage/config error | n/a | 2 |

Exit code `2` conditions include:

- existing `--envelope-v2` without `--json`
- unreadable target path
- malformed CLI usage

Unrelated JSON must not be force-classified as sandbox trace.

## Static-only Boundary

Future sandbox trace validate integration must validate parsed JSON structure only.

It must not:

- launch a sandbox
- run a subprocess
- execute a provider
- execute replay
- dynamically load providers
- discover or register providers
- execute adapters
- create generated content
- update snapshots
- write files
- validate full referenced sandbox result bodies as part of this target
- validate full referenced provider trace bodies as part of this target
- authorize sync apply or mutation

Validation success means the sandbox trace document is structurally acceptable. It does not approve future execution.

## Compatibility Requirements

Existing target detection must remain unchanged:

- sandbox result remains `sandbox-result`
- sandbox policy remains `sandbox-policy`
- provider execution trace remains `provider-execution-trace`
- provider capability remains `provider-capability`
- replay manifest remains `replay-manifest`
- sync manifest remains `sync-manifest`
- activation target detection remains unchanged
- unrelated JSON remains generic file or unsupported target, not `sandbox-trace`

Sandbox trace detection must be added after sandbox result detection so `aios.sandbox_execution_result.v0` is never misclassified.

Envelope v2 compatibility:

- `--envelope-v2` still requires `--json`.
- `meta.legacy_schema_version` remains `aios.validate.result.v0`.
- non-execution metadata naming should match sandbox policy/result validation.

## Required Future Tests

Future implementation should add tests for:

- valid sandbox trace native JSON pass.
- invalid sandbox trace native JSON fail.
- helper issue code/message/field preserved.
- sandbox-trace-shaped invalid schema detected and failed.
- sandbox-trace-shaped missing schema detected and failed.
- unrelated JSON not misclassified.
- valid sandbox trace envelope v2 pass.
- invalid sandbox trace envelope v2 fail.
- envelope v2 meta preserves execution flags false.
- envelope v2 meta preserves `trace_id`, `request_id`, `failure_code` when available.
- sandbox result target detection unchanged.
- sandbox policy target detection unchanged.
- provider execution trace target detection unchanged.
- provider capability target detection unchanged.
- replay manifest target detection unchanged.
- sync manifest target detection unchanged.
- `--envelope-v2` without `--json` remains exit code `2`.

Recommended files:

- `tests/test_validate_sandbox_trace.py`
- `tests/test_sandbox_trace_validate_output_contract.py`

## Explicit Non-goals

This contract does not implement or authorize:

- runtime code
- `aios validate <sandbox-trace.json>` integration
- envelope v2 implementation
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

## Next Implementation Slice

Recommended order:

1. Sandbox trace validate integration.
2. Sandbox trace validate output contract tests.
3. Sandbox trace output stabilization.
4. Sandbox trace runtime rule promotion audit, if integration is accepted.

Sandbox launcher, subprocess execution, provider execution, replay execution, generated content creation, snapshot update, sync apply, and mutation remain blocked.
