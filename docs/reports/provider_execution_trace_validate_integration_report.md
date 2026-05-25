# Provider Execution Trace Validate Integration Report

> 이 문서는 구현 증거용 human context이다. 런타임 계약은 `.ai/rules/`가 기준이며, 이 작업은 `.ai/rules`를 수정하지 않았다.

## 목적

Provider execution trace fixture와 validator helper를 `aios validate <provider-trace.json>`에 정적 검증 대상으로 연결했다. 통합 범위는 JSON 구조와 안전 플래그 검증에 한정하며 provider 실행, sandbox 실행, replay 실행, generated content 생성, snapshot update, sync apply, mutation은 추가하지 않았다.

## 변경 사항

- `src/aios/validate/targets.py`
  - `schema_version: aios.provider_execution_trace.v0` JSON을 `provider-execution-trace` target으로 감지한다.
  - trace-shaped JSON은 schema 오류 검증을 받을 수 있도록 제한적 heuristic으로 감지한다.
  - JSON target detection 순서는 sync manifest, replay manifest, provider capability, provider execution trace 순서를 유지한다.
- `src/aios/validate/validators/provider_execution_trace.py`
  - `validate_provider_execution_trace_data(data)`를 validate result로 매핑한다.
  - helper issue의 code, severity, message, field를 보존한다.
  - 성공 시 `provider_execution_trace_checked` info result를 추가한다.
- `src/aios/validate/engine.py`
  - `provider-execution-trace` target을 provider execution trace validator로 dispatch한다.
- `src/aios/cli.py`
  - validate envelope v2 출력에서 provider trace target에 대해 non-execution metadata를 보존한다.
- Tests
  - `tests/test_validate_provider_execution_trace.py`
  - `tests/test_provider_execution_trace_validate_output_contract.py`

## 지원 동작

- `python -m aios validate <provider-trace.json>`
- `python -m aios validate <provider-trace.json> --json`
- `python -m aios validate <provider-trace.json> --json --envelope-v2`

Native JSON output은 `schema_version: aios.validate.result.v0`를 유지하고 `target.kind: provider-execution-trace`를 사용한다. 성공 결과는 `provider_execution_trace_checked`이며 다음 metadata를 포함한다.

- `provider_id`
- `provider_version`
- `provider_mode`
- `deterministic_execution`
- `no_write_confirmed`
- `network_disabled`
- `mutation_performed`
- `provider_execution: false`
- `sandbox_execution: false`

Envelope v2 output은 `command: validate`, `target.kind: provider-execution-trace`를 유지하고 meta에 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`, `provider_mode`를 포함한다.

## 보존된 경계

이번 통합은 static-only validation이다. 다음 기능은 계속 차단되어 있다.

- provider runtime execution
- sandbox runtime
- replay execution
- dynamic loading
- provider registry/discovery
- adapter execution
- generated content creation
- snapshot update
- sync apply/mutation

## 회귀 방지

다음 기존 동작은 유지되도록 테스트했다.

- replay manifest validation
- provider capability validation
- sync manifest validation target detection
- unrelated JSON non-misclassification
- `--envelope-v2` without `--json` usage error

## 다음 권장 작업

1. Provider execution trace validate output contract stabilization
2. Provider execution trace validation rule promotion audit
3. Deterministic mock provider helper boundary audit
