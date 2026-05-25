# Provider Capability Validate Output Contract Report

> 이 문서는 human context용 테스트 안정화 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이번 작업은 provider capability validation 출력 계약 테스트를 보강했다.

## 목적

`aios validate <provider-capability.json>` 정적 검증이 native JSON과 envelope v2에서 안정적인 출력 계약을 유지하는지 고정했다. 이번 작업은 런타임 의미를 바꾸지 않고 contract tests를 강화했다.

## 보강된 테스트

수정 파일:

- `tests/test_provider_capability_validate_output_contract.py`

추가/강화된 커버리지:

- valid capability native JSON pass
- invalid capability native JSON fail
- provider-capability-shaped invalid schema detection
- provider-capability-shaped missing schema detection
- unrelated JSON non-misclassification
- envelope v2 pass/fail
- non-execution metadata preservation
- existing sync manifest target detection preservation
- existing replay manifest target detection preservation
- `--envelope-v2` without `--json` exit code `2`

## 고정된 Non-execution Metadata

Native JSON result details와 envelope v2 meta/messages에서 다음 값이 유지된다.

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

## 유지된 경계

이번 작업에서 추가하지 않은 것:

- provider execution
- sandbox execution
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply/mutation
- `.ai/rules` 변경

## 다음 권장 단계

1. Provider capability runtime rule promotion audit
2. Provider capability validation behavior runtime rule promotion
3. Deterministic mock provider boundary design

Provider execution과 sandbox execution은 계속 차단한다.
