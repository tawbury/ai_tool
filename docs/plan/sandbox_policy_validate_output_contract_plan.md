# Sandbox Policy Validate Output Contract Plan

> 이 문서는 설계 전용 계획서다. `aios validate <sandbox-policy.json>` 통합, sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Sandbox policy validator helper는 현재 `validate_sandbox_policy_data(data)` 형태로만 존재한다. 다음 구현 단계에서 `aios validate <sandbox-policy.json>`을 추가하려면 먼저 validate target detection, native JSON 출력, envelope v2 metadata, exit semantics를 고정해야 한다.

이 계약의 목적은 sandbox policy static validation을 기존 validation runtime에 추가하더라도 기존 activation, sync manifest, replay manifest, provider capability, provider execution trace validation을 흔들지 않는 것이다.

## 대상 스키마와 target kind

지원 대상 스키마:

- `aios.sandbox_policy.v0`

Validate target kind:

- `sandbox-policy`

성공 result code:

- `sandbox_policy_checked`

Helper issue code는 그대로 보존한다.

예상 issue code:

- `sandbox_policy_not_object`
- `missing_required_field`
- `unsupported_schema_version`
- `unsupported_sandbox_mode`
- `invalid_positive_integer`
- `invalid_allowed_read_roots`
- `duplicate_read_root`
- `invalid_allowed_output_roots`
- `duplicate_output_root`
- `network_not_disabled`
- `deterministic_not_true`
- `no_write_not_true`
- `invalid_env_policy`
- `wildcard_env_rule`
- `invalid_filesystem_policy`
- `invalid_edge_classification`

## Target Detection

### 명시적 schema detection

JSON object가 다음 값을 가지면 sandbox policy target으로 인식한다.

```json
{
  "schema_version": "aios.sandbox_policy.v0"
}
```

### shaped heuristic

schema가 누락되었거나 잘못되었더라도 sandbox policy로 보이는 JSON은 schema error validation을 받을 수 있어야 한다. 단, unrelated JSON을 잘못 분류하면 안 된다.

권장 heuristic:

- JSON object여야 한다.
- 아래 sandbox policy field 중 최소 5개 이상이 있어야 한다.
- 그리고 `sandbox_mode`, `env_policy`, `filesystem_policy` 중 하나 이상이 있어야 한다.

Sandbox policy shape fields:

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

이 heuristic은 schema 오류를 가진 sandbox policy 후보를 검증 대상으로 끌어들이기 위한 것이다. Provider capability, provider execution trace, replay manifest, sync manifest를 대체하거나 우선하지 않는다.

### Detection priority

기존 target detection 우선순위는 유지해야 한다. Sandbox policy는 provider execution trace 뒤에 위치한다.

권장 priority:

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy
7. generic file or repository validation

Unrelated JSON은 `sandbox-policy`로 분류되면 안 된다.

## Native JSON Contract

Native validate JSON은 기존 schema를 유지한다.

```json
{
  "schema_version": "aios.validate.result.v0",
  "target": {
    "kind": "sandbox-policy"
  },
  "results": []
}
```

### Success result

Sandbox policy가 유효하면 info result를 추가한다.

```json
{
  "code": "sandbox_policy_checked",
  "severity": "info",
  "status": "pass",
  "message": "Sandbox policy static validation completed without sandbox execution.",
  "details": {
    "sandbox_mode": "subprocess-temp-cwd",
    "network_disabled": true,
    "deterministic_execution": true,
    "no_write_required": true,
    "sandbox_execution": false,
    "subprocess_execution": false,
    "provider_execution": false,
    "mutation_performed": false
  }
}
```

Required success details:

- `sandbox_mode`
- `network_disabled`
- `deterministic_execution`
- `no_write_required`
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`

### Failure results

Helper issue는 validate result로 매핑하되 issue code, severity, status, message, field를 보존한다.

Failure result details는 non-execution metadata를 반드시 포함한다.

```json
{
  "code": "network_not_disabled",
  "severity": "error",
  "status": "fail",
  "message": "network_disabled must be true.",
  "field": "network_disabled",
  "details": {
    "sandbox_execution": false,
    "subprocess_execution": false,
    "provider_execution": false,
    "mutation_performed": false
  }
}
```

## Envelope v2 Mapping

Envelope v2는 기존 validate envelope contract와 일관되게 유지한다.

Required fields:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: sandbox-policy`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `payload.results`에 native validation results 보존
- `messages`에 error/info result 보존

Required envelope meta:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`
- `sandbox_mode` when available

Envelope v2는 sandbox approval이나 provider execution approval을 의미하지 않는다.

## Exit Semantics

Exit code policy:

- pass: `0`
- validation error: `1`
- usage/config error: `2`

`--envelope-v2` without `--json`은 기존 validate behavior처럼 exit code `2`를 유지해야 한다.

## Static-only Boundary

`aios validate <sandbox-policy.json>`은 parsed JSON structure와 policy safety flags만 검증한다.

금지:

- sandbox launch
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- file write
- sync apply
- mutation authorization

Sandbox policy validation은 future sandbox readiness evidence의 한 조각일 뿐 실행 허가가 아니다.

## Compatibility Requirements

다음 기존 target detection과 output contract는 유지되어야 한다.

- activation validation
- sync manifest validation
- replay manifest validation
- provider capability validation
- provider execution trace validation
- unrelated JSON generic file handling

Sandbox policy detection은 provider capability나 provider trace shaped JSON을 가로채면 안 된다.

## Required Future Tests

Validate integration 구현 시 필요한 테스트:

- valid sandbox policy native JSON pass
- invalid sandbox policy native JSON fail
- sandbox-policy-shaped invalid schema detected and failed
- unrelated JSON not misclassified
- envelope v2 pass/fail
- non-execution metadata preserved
- provider execution trace detection unchanged
- provider capability detection unchanged
- replay manifest detection unchanged
- sync manifest detection unchanged
- `--envelope-v2` without `--json` remains exit code `2`

## 병렬화 메모

Validate integration은 이 output contract가 완료된 뒤에만 진행해야 한다.

Sandbox trace fixture contract와 sandbox execution result fixture contract는 별도 design-only track으로 병렬 진행할 수 있다. 하지만 sandbox launcher, subprocess execution, provider execution은 계속 차단되어야 하며 validate integration과 묶으면 안 된다.

## 다음 권장 구현 Slice

다음 구현 slice는 `aios validate <sandbox-policy.json>` static integration이다. 해당 slice는 target detection, helper issue mapping, native JSON/envelope v2 output contract tests만 포함해야 하며 sandbox execution runtime은 포함하면 안 된다.
