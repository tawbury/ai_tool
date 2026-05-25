# 제공자 실행 trace validate output contract 계획

> 이 문서는 human context 계획 문서이다. 런타임 계약의 정본은 `.ai/rules/`이며, 이 계획은 future `aios validate <provider-trace.json>` 정적 검증 출력 계약을 정의한다.

## 목적

`src/aios/providers/trace.py`의 `validate_provider_execution_trace_data(data)` helper는 parsed dict만 검증한다. 이를 `aios validate <provider-trace.json>`에 통합하기 전에 target detection, native JSON, envelope v2, non-execution metadata, exit semantics를 먼저 고정해야 한다.

이 계획은 출력 계약만 설계한다. Provider execution, sandbox launch, dynamic provider loading, registry/discovery, adapter execution, generated content, snapshot update, replay execution, sync apply/mutation은 포함하지 않는다.

## Target detection strategy

Provider execution trace target detection은 JSON 파일에만 적용한다.

명확한 detection 조건:

- JSON object이고 `schema_version: aios.provider_execution_trace.v0`인 경우

Schema error validation을 위해 trace-shaped JSON도 감지할 수 있다.

권장 heuristic:

- JSON object이고 다음 trace fields 중 최소 6개 이상을 포함한다.
  - `trace_id`
  - `provider_id`
  - `provider_version`
  - `provider_mode`
  - `input_hash`
  - `output_hash`
  - `generated_hashes`
  - `duration_ms`
  - `deterministic_execution`
  - `no_write_confirmed`
  - `network_disabled`
  - `mutation_performed`
  - `provenance`
- 그리고 `provider_mode` 또는 `trace_id` 중 하나가 존재한다.

Misclassification 방지:

- unrelated JSON은 provider-execution-trace로 분류하지 않는다.
- 단순히 `provider_id` 하나만 있는 JSON은 trace가 아니다.
- provider capability JSON은 provider capability detection이 우선한다.
- replay manifest JSON은 replay manifest detection이 우선한다.
- sync manifest JSON은 sync manifest detection이 우선한다.
- activation YAML/JSON target은 기존 activation detection이 우선한다.

권장 priority order:

1. activation target detection
2. sync manifest detection
3. replay manifest detection
4. provider capability detection
5. provider execution trace detection
6. existing generic repository/target validation fallback

## Target kind

Validate target kind:

```json
{
  "target": {
    "kind": "provider-execution-trace"
  }
}
```

Target path는 사용자가 지정한 JSON 파일 경로를 보존한다.

## Native JSON contract

Native JSON은 기존 validate schema를 유지한다.

```json
{
  "schema_version": "aios.validate.result.v0",
  "command": "validate",
  "status": "pass",
  "target": {
    "kind": "provider-execution-trace",
    "path": "tests/fixtures/providers/traces/valid/whole_file_trace.json"
  },
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 1,
    "results": 1
  },
  "results": [
    {
      "code": "provider_execution_trace_checked",
      "severity": "info",
      "status": "pass",
      "message": "Provider execution trace was statically validated without provider execution.",
      "path": "tests/fixtures/providers/traces/valid/whole_file_trace.json",
      "details": {
        "provider_id": "aios.mock.preview.fixture",
        "provider_version": "0.1.0",
        "provider_mode": "fixture-mock",
        "deterministic_execution": true,
        "no_write_confirmed": true,
        "network_disabled": true,
        "mutation_performed": false,
        "provider_execution": false,
        "sandbox_execution": false
      }
    }
  ]
}
```

## Success result semantics

Success code:

- `provider_execution_trace_checked`

Severity/status:

- `severity: info`
- `status: pass`

Required success details:

- `provider_id`
- `provider_version`
- `provider_mode`
- `deterministic_execution`
- `no_write_confirmed`
- `network_disabled`
- `mutation_performed`
- `provider_execution: false`
- `sandbox_execution: false`

Success means the trace structure is valid. It does not mean a provider may run.

## Issue mapping

Validator issues preserve `ProviderExecutionTraceIssue` fields.

Mapping:

- `ProviderExecutionTraceIssue.code` -> result `code`
- `ProviderExecutionTraceIssue.severity` -> result `severity`
- `ProviderExecutionTraceIssue.status` -> result `status`
- `ProviderExecutionTraceIssue.message` -> result `message`
- `ProviderExecutionTraceIssue.field` -> result `field`

Error details must include:

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

When available, error details should preserve:

- `provider_id`
- `provider_version`
- `provider_mode`
- `failure_code`
- `unavailable_reason`

## Failure metadata semantics

Failure metadata must not imply execution authorization.

Rules:

- `failure_code` is evidence from the trace, not a command failure reason by itself.
- `unavailable_reason` is preserved when present.
- Static validation failure exits with code `1`.
- Invalid trace shape never triggers provider execution, sandbox launch, replay execution, or generated content creation.
- `mutation_performed` in envelope/native metadata must remain false for the validate command itself, even if the invalid trace document claims otherwise.

## Envelope v2 mapping

When `--json --envelope-v2` is used:

Top-level:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: provider-execution-trace`
- canonical `status: pass|warn|fail`

Meta:

- `legacy_schema_version: aios.validate.result.v0`
- `legacy_status`
- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`
- `provider_mode`

Payload:

- `payload.results` preserves native validation results.

Messages:

- Issue results map to messages.
- Success info may be preserved as an info message if consistent with existing validate envelope behavior.

Envelope v2 must not imply trace replay or provider execution.

## Static-only boundary

`aios validate <provider-trace.json>` must only validate parsed JSON structure.

It must not perform:

- provider execution
- sandbox launch
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply
- file mutation

Validation success means the trace document is structurally acceptable. It does not approve future execution.

## Compatibility requirements

Replay validation compatibility:

- `aios validate <replay-manifest.json>` behavior must remain unchanged.
- `--replay-compare fixture` behavior must remain unchanged.

Provider capability compatibility:

- `aios validate <provider-capability.json>` detection must keep priority over trace-shaped heuristics.
- Provider capability envelope metadata remains unchanged.

Envelope v2 consistency:

- `--envelope-v2` still requires `--json`.
- `meta.legacy_schema_version` remains `aios.validate.result.v0`.
- Static-only metadata uses the same naming as provider capability validation where possible.

## Exit semantics

| Condition | Status | Exit code |
| --- | --- | --- |
| Valid provider execution trace | `pass` | 0 |
| Provider execution trace validation error | `fail` | 1 |
| Usage/config error | n/a | 2 |

Exit code `2` conditions:

- existing `--envelope-v2` without `--json`
- unreadable target path
- malformed CLI usage

Unrelated JSON should not be force-classified as provider-execution-trace.

## Required future tests

Future implementation should add tests for:

- valid provider trace native JSON pass
- invalid provider trace native JSON fail
- trace-shaped invalid schema detected and failed
- unrelated JSON not misclassified
- envelope v2 pass/fail
- non-execution metadata preserved
- replay manifest target detection unchanged
- provider capability target detection unchanged
- sync manifest target detection unchanged
- `--envelope-v2` without `--json` remains exit code `2`

Recommended files:

- `tests/test_validate_provider_execution_trace.py`
- `tests/test_provider_execution_trace_validate_output_contract.py`

## Explicit non-goals

This contract does not implement or authorize:

- provider runtime execution
- sandbox runtime
- trace replay execution
- generated content creation
- snapshot update
- provider registry/discovery
- dynamic provider loading
- adapter execution
- sync apply
- mutation
- `.ai/rules` changes

## Next implementation slice

Recommended order:

1. Provider execution trace validate integration
2. Provider execution trace validate output contract tests
3. Runtime rule promotion audit

Provider execution, sandbox execution, replay execution, adapter execution, generated content creation, snapshot update, sync apply, and mutation remain blocked after validate integration.
