# Provider Capability Validate Output Contract Plan

> 이 문서는 human context용 계획 문서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 future `aios validate <provider-capability.json>` 정적 검증 출력 계약을 정의한다.

## 목적

`src/aios/providers/capability.py`의 `validate_provider_capability_data(data)` helper는 parsed `dict`만 검증한다. 다음 단계에서 이를 `aios validate <provider-capability.json>`에 통합하려면 native validate JSON과 envelope v2 출력 형태를 먼저 고정해야 한다.

이 계획은 출력 계약만 설계한다. provider 실행, sandbox 실행, registry/discovery, adapter 실행, generated content, snapshot update, sync apply/mutation은 포함하지 않는다.

## Target Detection

Provider capability target detection은 JSON 파일에만 적용한다.

명확한 detection 조건:

- JSON object이고 `schema_version: aios.provider_capability.v0`인 경우
- JSON object이고 provider capability required field 중 충분한 shape를 가진 경우

Schema error validation을 위해 다음도 provider-capability로 감지할 수 있다.

- `schema_version`이 없거나 지원되지 않지만 다음 필드 중 다수를 포함하는 JSON:
  - `provider_id`
  - `provider_version`
  - `deterministic_capable`
  - `supported_sync_modes`
  - `hash_policy`
  - `no_write_capable`
  - `network_policy`
  - `timeout_policy`
  - `resource_policy`
  - `provenance_required`

오분류 방지:

- unrelated JSON은 provider-capability로 분류하지 않는다.
- 단순히 `provider_id` 하나만 있는 JSON은 충분하지 않다.
- sync manifest, replay manifest, activation JSON/YAML 등 기존 target detection을 가로채지 않는다.
- JSON parse error는 provider-capability validation이 아니라 일반 target/usage error 정책을 따른다.

권장 detection heuristic:

- `schema_version == "aios.provider_capability.v0"`이면 provider-capability다.
- 또는 capability required field 중 최소 5개 이상이 있고, 그중 `provider_id` 또는 `supported_sync_modes`가 포함되면 provider-capability-shaped로 본다.

이 heuristic은 implementation 전에 테스트로 고정해야 한다.

## Target Kind

Validate target kind:

```json
{
  "target": {
    "kind": "provider-capability"
  }
}
```

Target path는 사용자가 지정한 JSON 파일 경로를 보존한다.

## Native Validate JSON Contract

Native JSON은 기존 validate schema를 유지한다.

```json
{
  "schema_version": "aios.validate.result.v0",
  "command": "validate",
  "status": "pass",
  "target": {
    "kind": "provider-capability",
    "path": "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json"
  },
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 1,
    "results": 1
  },
  "results": [
    {
      "code": "provider_capability_checked",
      "severity": "info",
      "status": "pass",
      "message": "Provider capability declaration was statically validated without provider execution.",
      "path": "tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json",
      "details": {
        "provider_id": "aios.preview.fixture",
        "provider_version": "0.1.0",
        "supported_sync_modes": ["whole-file", "managed-block", "mixed-boundary"],
        "deterministic_capable": true,
        "no_write_capable": true,
        "network_policy": "disabled",
        "provider_execution": false,
        "sandbox_execution": false,
        "mutation_performed": false
      }
    }
  ]
}
```

### Success Result

Success code:

- `provider_capability_checked`

Severity:

- `info`

Status:

- `pass`

Required details:

- `provider_id`
- `provider_version`
- `supported_sync_modes`
- `deterministic_capable`
- `no_write_capable`
- `network_policy`
- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

### Error Results

Provider capability errors preserve `ProviderCapabilityIssue.code`.

Example:

```json
{
  "code": "network_policy_not_disabled",
  "severity": "error",
  "status": "fail",
  "message": "network_policy must be disabled.",
  "path": "tests/fixtures/providers/capabilities/invalid/network_enabled.json",
  "field": "network_policy",
  "details": {
    "provider_execution": false,
    "sandbox_execution": false,
    "mutation_performed": false
  }
}
```

Mismatch or invalid capability increments native validate error counters and exits with code `1`.

## Envelope V2 Contract

When `--json --envelope-v2` is used, output uses `aios.command_result.v2`.

Envelope fields:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `status: pass|warn|fail`
- `target.kind: provider-capability`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `meta.provider_execution: false`
- `meta.sandbox_execution: false`
- `meta.mutation_performed: false`
- `payload.results` preserves native validation results
- `messages` preserves info/error details

Example meta:

```json
{
  "legacy_schema_version": "aios.validate.result.v0",
  "legacy_status": "pass",
  "provider_execution": false,
  "sandbox_execution": false,
  "mutation_performed": false
}
```

Envelope v2 must not imply provider execution capability. It only wraps static validation output.

## Exit Code Behavior

| Condition | Status | Exit code |
| --- | --- | --- |
| Valid provider capability | `pass` | 0 |
| Provider capability validation error | `fail` | 1 |
| Usage/config error | n/a | 2 |

Usage/config errors include unsupported CLI flag combinations already governed by validate conventions, such as `--envelope-v2` without `--json`.

## Static-only Boundary

`aios validate <provider-capability.json>` must not perform:

- provider execution
- sandbox launch
- provider registry update
- provider discovery
- provider loading
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply
- file mutation

Validation success means the declaration is structurally acceptable. It does not mean the provider may run.

## Required Implementation Tests

Future implementation should add tests for:

- valid provider capability native JSON pass
- invalid provider capability native JSON fail
- envelope v2 pass
- envelope v2 fail
- unrelated JSON not misclassified
- provider-capability-shaped JSON with missing schema detected and failed
- existing sync/replay manifest target detection still works
- `--envelope-v2` without `--json` remains exit code `2`

Recommended test file:

- `tests/test_validate_provider_capability.py`
- `tests/test_provider_capability_validate_output_contract.py`

## Non-goals

- runtime provider execution
- sandbox execution
- provider registry/discovery
- adapter execution
- generated content generation
- snapshot update
- deterministic replay execution
- sync apply/mutation
- `.ai/rules` update

## Next Implementation Slice

Recommended next slice:

1. Add provider capability validator target under `src/aios/validate/validators/`.
2. Add JSON target detection for provider capability and provider-capability-shaped JSON.
3. Preserve existing validate behavior for unrelated JSON.
4. Add native JSON and envelope v2 output contract tests.

Provider execution remains blocked after this integration.
