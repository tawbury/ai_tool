# Provider Capability Runtime Rule Promotion Report

> 이 문서는 human context용 구현 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이번 작업은 provider capability static validation behavior를 runtime governance rules에 승격했다.

## 목적

`aios validate <provider-capability.json>` 정적 검증은 구현되었고 출력 계약도 안정화되었다. 이번 작업은 해당 동작과 non-execution boundary를 runtime-facing rule에 반영했다.

## 변경한 Runtime Rules

### `.ai/rules/operations/validation.rules.md`

`Runtime JSON Targets` 섹션을 갱신했다.

반영 내용:

- 지원 명령:
  - `python -m aios validate <provider-capability.json>`
  - `python -m aios validate <provider-capability.json> --json`
  - `python -m aios validate <provider-capability.json> --json --envelope-v2`
- target kind:
  - `provider-capability`
- schema:
  - `aios.provider_capability.v0`
- static-only boundary:
  - declaration shape and safety flags only
- JSON/envelope non-execution metadata:
  - `provider_execution: false`
  - `sandbox_execution: false`
  - `mutation_performed: false`
- explicit prohibitions:
  - provider execution
  - sandbox launch
  - provider registry/discovery
  - adapter execution
  - generated content
  - snapshot update
  - file writes
  - sync apply/mutation authorization

### `.ai/rules/operations/sync.rules.md`

Provider/replay safety context로 짧은 pointer를 추가했다.

반영 내용:

- provider capability validation은 future preview/replay provider safety를 위한 static-only readiness context다.
- detailed command/output behavior는 validation rules에 둔다.
- provider execution, sandbox execution, registry/discovery, adapter execution, generated content, snapshot update, sync apply, mutation은 계속 금지한다.

## 의도적으로 제외한 내용

Runtime rules에 넣지 않은 내용:

- fixture inventory details
- invalid fixture filename list
- exact test filenames
- future sandbox architecture details
- deterministic mock provider design
- provider registry/discovery design

## 유지된 경계

이번 작업은 runtime code를 변경하지 않았다.

계속 차단됨:

- provider execution
- sandbox execution
- provider registry/discovery
- adapter execution
- generated content generation
- snapshot update
- replay execution
- sync apply/mutation

## 검증

다음 검증을 수행했다.

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios validate tests/fixtures/providers/capabilities/valid/deterministic_fixture_provider.json --json`
- `python -m pytest tests/test_provider_capability_validate_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 다음 권장 단계

1. Deterministic mock provider boundary design
2. Subprocess sandbox architecture plan
3. Provider execution readiness audit after sandbox and mock boundaries are documented

Provider execution과 sandbox execution은 계속 차단한다.
