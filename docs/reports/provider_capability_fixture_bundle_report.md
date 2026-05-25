# Provider Capability Fixture Bundle Report

> 이 문서는 human context용 구현 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이번 작업은 fixture와 테스트만 추가했다.

## 목적

Provider capability schema fixture contract를 바탕으로 concrete JSON fixture와 fixture-only contract tests를 추가했다. 이 작업은 provider 실행, sandbox 실행, runtime validator integration, provider discovery를 추가하지 않는다.

## 추가된 Fixture Layout

```text
tests/fixtures/providers/capabilities/
  valid/
  invalid/
  edge_cases/
```

## 추가된 Valid Fixtures

- `deterministic_fixture_provider.json`
- `whole_file_only_provider.json`
- `managed_block_provider.json`

Valid fixture는 모두 다음 조건을 만족한다.

- `schema_version: aios.provider_capability.v0`
- `deterministic_capable: true`
- `no_write_capable: true`
- `network_policy: disabled`
- `hash_policy: aios.hash_policy.v0`
- positive timeout/resource values
- safe relative `allowed_read_roots`
- `provenance_required: true`

## 추가된 Invalid Fixtures

- `unsupported_schema_version.json`
- `invalid_sync_mode.json`
- `missing_provider_version.json`
- `network_enabled.json`
- `no_write_false.json`
- `timeout_invalid.json`
- `duplicate_sync_mode.json`
- `malformed_resource_policy.json`

각 invalid fixture는 하나 이상의 contract assertion이 실패하도록 구성했다.

## 추가된 Edge Fixtures

- `empty_allowed_read_roots.json`
- `max_timeout_boundary.json`
- `minimal_output_affecting_config.json`

Edge fixture는 v0 contract에서 허용되는 경계 조건을 고정한다.

## 추가된 테스트

- `tests/test_provider_capability_fixtures.py`

테스트 범위:

- 모든 fixture JSON parse
- fixture inventory 고정
- required fields 확인
- schema version 확인
- sync mode enum과 uniqueness 확인
- hash policy 확인
- network disabled 확인
- no-write true 확인
- timeout/resource positive value 확인
- safe relative read roots 확인
- provenance required 확인
- invalid fixture별 expected issue 확인

## 유지된 경계

이번 작업에서 추가하지 않은 것:

- provider execution
- sandbox execution
- adapter execution
- generated content generation
- provider registry/discovery
- runtime validator integration
- `aios validate <provider-capability.json>`
- envelope v2 mapping
- snapshot update
- sync apply/mutation

## 다음 권장 단계

1. Provider capability validator helper 설계
2. Provider capability static validator 구현
3. `aios validate <provider-capability.json>` output contract 설계

Provider execution과 sandbox execution은 계속 차단 상태로 유지한다.
