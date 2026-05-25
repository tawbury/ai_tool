# Sandbox Policy Validate Integration Report

## 목적

이 보고서는 `aios validate <sandbox-policy.json>` static-only 통합 결과를 기록한다. 이번 작업은 sandbox policy helper를 validate runtime에 연결하지만 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하지 않는다.

## 구현 범위

추가된 런타임 통합:

- `src/aios/validate/validators/sandbox_policy.py`
- `src/aios/validate/targets.py`
- `src/aios/validate/engine.py`
- `src/aios/cli.py`

추가된 테스트:

- `tests/test_validate_sandbox_policy.py`
- `tests/test_sandbox_policy_validate_output_contract.py`

## Target Detection

Sandbox policy target kind는 다음으로 고정되었다.

- `sandbox-policy`

Detection은 다음 조건을 지원한다.

- `schema_version: aios.sandbox_policy.v0`
- sandbox-policy-shaped JSON with missing or invalid schema

Detection priority는 기존 target을 보존하도록 다음 순서 뒤에 위치한다.

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy

Unrelated JSON은 `sandbox-policy`로 분류되지 않도록 테스트로 고정했다.

## Native JSON Output

Native validate JSON은 기존 schema를 유지한다.

- `schema_version: aios.validate.result.v0`
- `target.kind: sandbox-policy`
- success code: `sandbox_policy_checked`

성공 result는 다음 non-execution metadata를 포함한다.

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`

추가로 가능한 경우 다음 policy fields를 보존한다.

- `sandbox_mode`
- `network_disabled`
- `deterministic_execution`
- `no_write_required`

실패 result는 helper issue code, severity, message, field를 보존하고 동일한 non-execution metadata를 포함한다.

## Envelope v2 Output

`--json --envelope-v2` 출력은 다음 metadata를 보존한다.

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`
- `sandbox_mode` when available

Envelope payload와 messages에는 native validation results가 보존된다.

## 유지된 경계

이번 작업은 다음을 구현하지 않았다.

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

Sandbox policy validation은 policy 구조와 safety flags를 정적으로 검증할 뿐 실행 허가가 아니다.

## 테스트 범위

추가 테스트는 다음을 고정한다.

- valid sandbox policy native JSON pass
- invalid sandbox policy native JSON fail
- sandbox-policy-shaped invalid schema detection
- unrelated JSON non-misclassification
- envelope v2 pass/fail metadata
- existing provider capability target detection
- existing provider execution trace target detection
- existing sync manifest target detection
- existing replay manifest target detection
- `--envelope-v2` without `--json` exit code `2`

## 병렬화 메모

Validate integration과 output contract tests는 이번 task에서 안전하게 묶었다. 둘 다 static validation과 serialization에만 영향을 주며 sandbox execution을 추가하지 않는다.

Sandbox trace fixture contract와 sandbox execution result fixture contract는 별도 design-only track으로 진행할 수 있다. Sandbox execution, subprocess launcher, provider execution은 계속 순차적으로 차단되어야 하며 별도 readiness gate와 runtime rule promotion 없이 시작하면 안 된다.

## 다음 권장 방향

다음 안전한 작업은 sandbox policy validate output contract stabilization 또는 sandbox trace/result fixture contract design이다. Runtime governance rule promotion은 output contract stabilization 뒤에 별도 audit를 거쳐야 한다.
