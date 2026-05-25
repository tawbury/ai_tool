# Provider Capability Fixture Contract

> 이 문서는 human context용 계획 문서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 future real preview/replay provider 실행 전 capability declaration fixture의 구조와 검증 경계를 정의한다.

## 목적

Provider capability fixture는 향후 provider 실행 가능성을 검토하기 위한 정적 선언이다. 이 fixture는 provider가 어떤 sync mode, hash policy, network policy, timeout, resource boundary, provenance policy를 지원한다고 주장하는지 기록한다.

Capability fixture는 다음이 아니다.

- 실행 승인
- provider 등록
- provider discovery runtime
- sandbox approval
- adapter execution approval
- generated content creation approval
- sync apply authorization

## Fixture Purpose

Capability fixture의 목적은 future provider execution 전에 다음을 정적으로 검증할 수 있게 하는 것이다.

- provider identity와 version이 명시되어 있는가
- provider가 deterministic replay에 적합하다고 선언하는가
- provider가 write 없이 실행 가능하다고 선언하는가
- provider가 어떤 sync mode를 지원하는가
- provider가 Phase 7 v0 hash policy와 호환되는가
- network access가 기본적으로 비활성화되어 있는가
- timeout/resource policy가 명시되어 있는가
- provenance가 필수로 보존되는가

이 검증은 provider 실행을 대체하지 않으며 sandbox 격리 검증을 대체하지 않는다.

## Fixture Layout Proposal

권장 fixture layout:

```text
tests/
  fixtures/
    providers/
      capabilities/
        valid/
          deterministic_fixture_provider.json
          whole_file_only_provider.json
          managed_block_provider.json
        invalid/
          unsupported_schema_version.json
          invalid_sync_mode.json
          missing_provider_version.json
          network_enabled.json
          no_write_false.json
          timeout_invalid.json
          duplicate_sync_mode.json
          malformed_resource_policy.json
        edge_cases/
          empty_allowed_read_roots.json
          max_timeout_boundary.json
          minimal_output_affecting_config.json
```

Fixture directory는 provider registry가 아니다. 테스트와 future validation 설계를 위한 정적 샘플 위치일 뿐이다.

## Canonical Schema

Canonical schema version:

```json
{
  "schema_version": "aios.provider_capability.v0"
}
```

전체 예시:

```json
{
  "schema_version": "aios.provider_capability.v0",
  "provider_id": "aios.preview.fixture",
  "provider_version": "0.1.0",
  "deterministic_capable": true,
  "supported_sync_modes": ["whole-file", "managed-block", "mixed-boundary"],
  "hash_policy": "aios.hash_policy.v0",
  "output_affecting_config": {
    "template_set": "fixture-v0",
    "normalization": "none"
  },
  "no_write_capable": true,
  "network_policy": "disabled",
  "timeout_policy": {
    "timeout_ms": 5000
  },
  "resource_policy": {
    "max_input_bytes": 262144,
    "max_output_bytes": 262144,
    "max_memory_bytes": 67108864
  },
  "allowed_read_roots": [],
  "provenance_required": true
}
```

## Required Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Must be `aios.provider_capability.v0`. |
| `provider_id` | string | yes | Stable provider identity. |
| `provider_version` | string | yes | Output-affecting changes require version change. |
| `deterministic_capable` | boolean | yes | Must be true for replay execution eligibility. |
| `supported_sync_modes` | array[string] | yes | Non-empty, unique sync modes. |
| `hash_policy` | string | yes | v0 requires `aios.hash_policy.v0`. |
| `output_affecting_config` | object | yes | May be empty, but must be explicit. |
| `no_write_capable` | boolean | yes | Must be true for any future execution eligibility. |
| `network_policy` | string | yes | v0 default and only approved value is `disabled`. |
| `timeout_policy` | object | yes | Must include positive `timeout_ms`. |
| `resource_policy` | object | yes | Must include positive byte limits. |
| `allowed_read_roots` | array[string] | yes | May be empty. Paths must be relative/safe unless future policy allows symbolic roots. |
| `provenance_required` | boolean | yes | Must be true for replay validation eligibility. |

## Enum Constraints

Supported sync modes:

- `whole-file`
- `managed-block`
- `mixed-boundary`

Supported hash policy:

- `aios.hash_policy.v0`

Supported network policy for v0:

- `disabled`

Future values require a new plan, validation update, output contract update, and runtime rule promotion before use.

## Validation Semantics

Static capability validation should apply these rules.

- Missing required field is an error.
- Unsupported `schema_version` is an error.
- `provider_id` and `provider_version` must be non-empty strings.
- `deterministic_capable` must be boolean and true for replay execution eligibility.
- `supported_sync_modes` must be a non-empty array.
- Duplicate sync modes are errors.
- Unknown sync mode is an error.
- `hash_policy` must match supported hash policy.
- `output_affecting_config` must be an object, not null.
- `no_write_capable` must be true.
- `network_policy` must be `disabled`.
- `timeout_policy.timeout_ms` must be a positive integer.
- `resource_policy.max_input_bytes` and `resource_policy.max_output_bytes` must be positive integers.
- If `resource_policy.max_memory_bytes` exists, it must be a positive integer.
- `allowed_read_roots` must be an array of safe relative paths or symbolic roots approved by future policy.
- `provenance_required` must be true.

Validation success means the declaration is structurally acceptable. It does not mean the provider can run.

## Invalid Fixture Cases

Required invalid fixtures:

| Fixture | Expected issue |
| --- | --- |
| `unsupported_schema_version.json` | unsupported schema version |
| `invalid_sync_mode.json` | unknown sync mode |
| `missing_provider_version.json` | missing required field |
| `network_enabled.json` | network policy not disabled |
| `no_write_false.json` | no-write capability not true |
| `timeout_invalid.json` | timeout missing, zero, negative, or wrong type |
| `duplicate_sync_mode.json` | repeated sync mode |
| `malformed_resource_policy.json` | missing or invalid resource limits |

Recommended edge fixtures:

- empty `allowed_read_roots`
- maximum accepted timeout boundary
- minimal empty `output_affecting_config`
- provider supporting only one sync mode

## Future Validate Integration Candidate

Future command candidate:

```bash
python -m aios validate <provider-capability.json>
python -m aios validate <provider-capability.json> --json
python -m aios validate <provider-capability.json> --json --envelope-v2
```

Boundary:

- static validation only
- no provider execution
- no provider discovery
- no provider registry update
- no sandbox launch
- no adapter execution
- no generated content
- no snapshot update
- no sync apply or mutation

Expected target kind:

- `provider-capability`

## Future Compatibility Boundaries

Capability declaration is only one gate. It must not be confused with later gates.

| Boundary | Meaning |
| --- | --- |
| Capability declaration | Provider claims deterministic/no-write/network/resource properties. |
| Capability validation | The declaration is structurally and semantically acceptable. |
| Sandbox approval | Future execution boundary is approved for a provider. |
| Replay validation | Provider output is checked for deterministic stability. |
| Runtime registration | Future optional discovery mechanism; not part of this fixture contract. |
| Execution authorization | Separate future explicit opt-in; not granted by this fixture. |

## Explicit Non-goals

- provider execution
- provider registry
- provider discovery
- provider loading
- sandbox runtime
- adapter execution
- generated content
- snapshot update
- replay CLI
- sync apply
- mutation
- `.ai/rules` update

## Recommended Implementation Slices

1. Capability fixtures only
2. Capability validator helper
3. `aios validate <provider-capability.json>` integration
4. Validate native JSON/envelope v2 output contract tests
5. Deterministic mock provider boundary design
6. Subprocess sandbox architecture design

Provider execution remains blocked until these slices and governance promotion are complete.
