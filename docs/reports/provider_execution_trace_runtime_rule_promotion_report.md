# Provider Execution Trace Runtime Rule Promotion Report

> 이 문서는 rule promotion 증거용 human context이다. Runtime governance의 실제 권한은 `.ai/rules/`에 있다.

## 목적

`aios validate <provider-trace.json>` static validation behavior를 runtime governance rules에 승격했다. 이번 작업은 규칙 문서와 인덱스/보고서만 갱신했으며 runtime code, tests, fixtures는 변경하지 않았다.

## 변경 사항

### Validation rules

`.ai/rules/operations/validation.rules.md`의 Runtime JSON Targets section에 provider execution trace validation을 추가했다.

승격한 내용:

- Supported commands:
  - `python -m aios validate <provider-trace.json>`
  - `python -m aios validate <provider-trace.json> --json`
  - `python -m aios validate <provider-trace.json> --json --envelope-v2`
- Target kind:
  - `provider-execution-trace`
- Schema:
  - `aios.provider_execution_trace.v0`
- Static-only boundary:
  - parsed JSON structure and safety evidence only
- Non-execution metadata:
  - `provider_execution: false`
  - `sandbox_execution: false`
  - `mutation_performed: false`
- `provider_mode` preservation where available

명시적으로 계속 금지한 항목:

- provider execution
- sandbox launch
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- file writes
- sync apply/mutation authorization

### Sync rules

`.ai/rules/operations/sync.rules.md`에는 짧은 safety pointer를 추가했다.

- Provider execution trace validation is available through `aios validate <provider-trace.json>`.
- It is static-only evidence for future provider/replay safety.
- It does not authorize provider execution, sandbox execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, replay execution, sync apply, or mutation.
- Detailed command/output behavior belongs in validation rules.

## 제외한 내용

Runtime rules에는 다음 세부사항을 넣지 않았다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- future sandbox architecture details

## 병렬화 메모

이번 task에서는 rule promotion, docs index update, promotion report 작성을 안전하게 번들링했다.

Sandbox architecture planning은 별도 design-only parallel track으로 진행할 수 있지만, provider execution이나 sandbox execution 구현과 결합하면 안 된다. Provider/sandbox execution implementation은 sandbox policy, capability gate, deterministic replay boundary가 별도로 승인될 때까지 순차적으로 차단되어야 한다.

## 검증 범위

다음 검증을 수행했다.

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios validate tests/fixtures/providers/traces/valid/whole_file_trace.json --json`
- `python -m pytest tests/test_provider_execution_trace_validate_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
