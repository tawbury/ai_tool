# Sandbox Result Runtime Rule Promotion Report

## 목적

이 보고서는 `aios validate <sandbox-result.json>` 정적 검증 동작을 runtime governance rules에 승격한 결과를 기록한다. 이번 작업은 문서 규칙 승격만 수행했으며 runtime code, tests, fixtures는 변경하지 않았다.

## 변경 파일

- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

## Validation Rules Promotion

`validation.rules.md` Runtime JSON Targets section에 sandbox result validation을 추가했다.

승격된 내용:

- supported commands
  - `python -m aios validate <sandbox-result.json>`
  - `python -m aios validate <sandbox-result.json> --json`
  - `python -m aios validate <sandbox-result.json> --json --envelope-v2`
- target kind: `sandbox-result`
- schema: `aios.sandbox_execution_result.v0`
- static-only boundary
- JSON/envelope non-execution metadata
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `replay_execution: false`
  - `mutation_performed: false`
- evidence identifiers preserved when available
  - `sandbox_mode`
  - `request_id`
  - `failure_code`

명시적으로 계속 금지된 동작:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- file writes
- sync apply/mutation authorization

## Sync Rules Pointer

`sync.rules.md`에는 짧은 safety pointer를 추가했다. Sandbox result validation은 future sandbox/provider safety를 위한 static-only evidence이며 sync apply, mutation, execution readiness를 승인하지 않는다. 상세 command/output behavior는 validation rules에 남겼다.

## 제외한 내용

Runtime rules에는 다음을 넣지 않았다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- invalid fixture lists
- edge fixture lists
- future sandbox trace schema details
- launcher design details

## 문서 인덱스

`docs/index/document_status_registry.md`는 promotion audit를 historical/superseded로 전환하고 이 report를 completed implementation report로 추가했다. `docs/index/phase_6_8_summary.md`와 `docs/index/current_runtime_context.md`는 sandbox result rule promotion 완료와 다음 안전 방향을 반영했다.

## 병렬화 메모

Rule promotion, docs index update, report update는 같은 governance promotion 범위라 안전하게 묶어 진행했다. Sandbox trace fixture contract와 risk audit는 별도 design-only parallel track으로 유지된다. Sandbox launcher와 execution implementation은 계속 순차적으로 차단된다.

## 검증

실행 대상:

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios validate tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json --json`
- `python -m pytest tests/test_sandbox_result_validate_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
