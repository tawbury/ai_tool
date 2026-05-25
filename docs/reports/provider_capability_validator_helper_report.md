# Provider Capability Validator Helper Report

> 이 문서는 human context용 구현 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이번 작업은 순수 provider capability 검증 helper만 추가했다.

## 목적

Provider capability fixture contract를 재사용 가능한 정적 검증 helper로 옮겼다. 이 helper는 parsed `dict`를 받아 capability declaration의 schema, required fields, enum, no-write, network, timeout/resource, safe path, provenance 조건을 검사한다.

## 추가된 모듈

- `src/aios/providers/__init__.py`
- `src/aios/providers/capability.py`

공개 helper:

- `validate_provider_capability_data(data)`

공개 모델:

- `ProviderCapabilityIssue`
- `ProviderCapabilityValidationResult`

공개 상수:

- `PROVIDER_CAPABILITY_SCHEMA_VERSION`
- `PROVIDER_HASH_POLICY`
- `ALLOWED_SYNC_MODES`
- `ALLOWED_NETWORK_POLICY`

## 검증 범위

Helper는 다음을 검증한다.

- required fields
- `schema_version: aios.provider_capability.v0`
- non-empty `provider_id`
- non-empty `provider_version`
- `deterministic_capable: true`
- non-empty, unique, allowed `supported_sync_modes`
- `hash_policy: aios.hash_policy.v0`
- object `output_affecting_config`
- `no_write_capable: true`
- `network_policy: disabled`
- positive `timeout_policy.timeout_ms`
- positive `resource_policy.max_input_bytes`
- positive `resource_policy.max_output_bytes`
- optional positive `resource_policy.max_memory_bytes`
- safe relative `allowed_read_roots`
- `provenance_required: true`

## 추가된 테스트

- `tests/test_provider_capability_validator.py`

테스트는 valid/invalid/edge fixture와 in-memory mutation cases를 모두 사용한다.

## 유지된 경계

이번 작업에서 추가하지 않은 것:

- `aios validate <provider-capability.json>`
- CLI flag
- envelope v2 mapping
- provider execution
- sandbox execution
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply/mutation

Helper는 파일 IO를 수행하지 않으며 provider를 실행하지 않는다.

## 다음 권장 단계

1. Provider capability validate integration output contract 설계
2. `aios validate <provider-capability.json>` static-only 통합
3. Provider capability validate output contract tests

Provider execution과 sandbox execution은 계속 차단한다.
