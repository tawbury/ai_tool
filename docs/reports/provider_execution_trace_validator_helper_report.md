# 제공자 실행 trace validator helper 보고서

> 이 문서는 human context 구현 보고서이다. 런타임 계약의 정본은 `.ai/rules/`이며, 이번 작업은 provider execution trace의 순수 정적 검증 helper를 추가했을 뿐 provider execution이나 runtime integration을 구현하지 않았다.

## 목적

Provider execution trace fixture bundle 이후, `aios.provider_execution_trace.v0` 문서를 parsed dict 상태에서 검증하는 helper를 추가했다. Helper는 fixture와 future trace data의 구조적 안전성을 검증하기 위한 준비 단계이며, provider-like execution을 수행하지 않는다.

## 추가한 모듈

추가 파일:

- `src/aios/providers/trace.py`

주요 API:

- `validate_provider_execution_trace_data(data)`
- `ProviderExecutionTraceIssue`
- `ProviderExecutionTraceValidationResult`

상수:

- `PROVIDER_EXECUTION_TRACE_SCHEMA_VERSION`
- `PROVIDER_MODES`
- `FAILURE_CODES`

## 검증 범위

Helper는 다음을 정적으로 검증한다.

- required fields
- schema version
- non-empty trace id
- non-empty provider id/version
- provider mode enum
- input/output/generated hash format and nullability
- duration non-negative integer
- deterministic execution true
- no_write_confirmed true
- network_disabled true
- mutation_performed false
- unavailable/failure semantics
- failure code enum
- provenance object and source path/hash order
- optional hash policy preservation fields

## 테스트

추가 테스트:

- `tests/test_provider_execution_trace_validator.py`

테스트 범위:

- valid/edge fixtures produce no errors
- invalid fixtures return expected issue codes
- unsupported schema
- missing trace id
- invalid provider mode
- invalid failure code
- mutation/network/no-write/determinism flag enforcement
- invalid hash format
- invalid generated_hashes
- missing provenance
- unavailable generated hash present
- failure without unavailable reason
- invalid duration
- invalid hash policy
- validator input immutability
- non-object data error

## 유지한 경계

이번 작업은 다음을 구현하지 않았다.

- `aios validate` 통합
- envelope v2 mapping
- CLI
- provider execution
- sandbox execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply
- mutation
- `.ai/rules` 변경

Helper는 file IO를 수행하지 않으며 parsed dict만 검증한다.

## 검증

수행한 단독 검증:

- `python -m pytest tests/test_provider_execution_trace_validator.py`

최종 validation 단계에서 관련 회귀 테스트와 CLI 검증을 함께 수행한다.

## 다음 권장 작업

다음 안전한 작업은 provider execution trace validate output contract design이다. `aios validate <provider-trace.json>` 통합을 구현하기 전에 target detection, native JSON, envelope v2, non-execution metadata를 먼저 설계해야 한다.
