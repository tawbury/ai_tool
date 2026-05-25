# Provider Capability Validate Integration Report

> 이 문서는 human context용 구현 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이번 작업은 provider capability 정적 검증을 `aios validate <provider-capability.json>`에 통합했다.

## 목적

Provider capability helper를 기존 `aios validate` target 체계에 연결해 capability declaration을 first-class static validation target으로 검증할 수 있게 했다.

## 구현 범위

추가/변경:

- `src/aios/validate/validators/provider_capability.py`
- `src/aios/validate/targets.py`
- `src/aios/validate/engine.py`
- `src/aios/cli.py`
- `tests/test_validate_provider_capability.py`
- `tests/test_provider_capability_validate_output_contract.py`

## Target Detection

Provider capability target은 다음 경우 감지된다.

- JSON `schema_version`이 `aios.provider_capability.v0`
- provider capability-shaped JSON이고, capability field가 5개 이상 있으며 `provider_id` 또는 `supported_sync_modes`가 있음

기존 replay manifest와 sync manifest detection은 provider capability detection보다 먼저 실행되어 우선순위를 유지한다.

## Validate Result Mapping

Helper issue는 validate result로 매핑된다.

- `ProviderCapabilityIssue.code` 보존
- severity/status/message 보존
- `field`는 details에 보존
- error details에는 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false` 포함

성공 result:

- `provider_capability_checked`

성공 details:

- `provider_id`
- `provider_version`
- `supported_sync_modes`
- `deterministic_capable`
- `no_write_capable`
- `network_policy`
- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

## Envelope V2

Provider capability validate envelope에는 다음 meta가 추가된다.

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

Payload results와 messages는 기존 validate envelope mapping을 사용한다.

## 유지된 경계

이번 작업에서 추가하지 않은 것:

- provider execution
- sandbox execution
- provider registry/discovery
- adapter execution
- generated content generation
- snapshot update
- replay execution
- sync apply/mutation
- `.ai/rules` 변경

## 검증 범위

추가 테스트는 다음을 확인한다.

- valid capability native JSON pass
- invalid capability native JSON fail
- provider-capability-shaped JSON with missing schema detection
- unrelated JSON non-misclassification
- envelope v2 pass/fail contract
- existing sync/replay manifest detection preservation
- `--envelope-v2` without `--json` exit code `2`

## 다음 권장 단계

1. Provider capability validate output contract stabilization
2. Provider capability runtime rule promotion audit
3. Provider capability validation behavior runtime rule promotion

Provider execution과 sandbox execution은 계속 차단한다.
