# Sandbox Policy Runtime Rule Promotion Report

## 목적

이 보고서는 `aios validate <sandbox-policy.json>` static validation behavior를 runtime governance rules에 승격한 결과를 기록한다.

이번 작업은 문서와 규칙 승격만 수행했다. Runtime code, tests, fixtures는 변경하지 않았다.

## 변경 파일

Runtime rules:

- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`

Human context indexes:

- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

## Validation Rules Promotion

`.ai/rules/operations/validation.rules.md`에는 sandbox policy validation을 runtime JSON target으로 추가했다.

승격된 command:

- `python -m aios validate <sandbox-policy.json>`
- `python -m aios validate <sandbox-policy.json> --json`
- `python -m aios validate <sandbox-policy.json> --json --envelope-v2`

승격된 target/schema:

- target kind: `sandbox-policy`
- schema: `aios.sandbox_policy.v0`

승격된 boundary:

- static-only validation
- parsed JSON structure와 policy safety flags만 검증
- `sandbox_mode` available 시 보존

승격된 non-execution metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`

명시적으로 금지된 항목:

- sandbox launch
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- file write
- sync apply/mutation authorization

## Sync Rules Pointer

`.ai/rules/operations/sync.rules.md`에는 짧은 Sandbox Policy Validation pointer를 추가했다.

해당 pointer는 sandbox policy validation이 future sandbox/provider safety를 위한 static-only readiness context이며, sandbox launcher, subprocess execution, provider execution, replay execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, sync apply, mutation을 승인하지 않는다고 명시한다.

상세 command와 output behavior는 validation rules에 둔다.

## 제외한 내용

Runtime rules에는 다음을 포함하지 않았다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- invalid fixture lists
- edge fixture lists
- future sandbox execution result schema details
- launcher design details

## 병렬화 메모

Rule promotion, docs index update, promotion report는 이번 task에서 안전하게 묶었다. 모두 current runtime behavior를 governance에 반영하는 작업이며 sandbox execution을 추가하지 않는다.

Sandbox trace fixture contract와 sandbox execution result fixture contract는 별도 design-only parallel track으로 진행할 수 있다.

Sandbox launcher, subprocess execution, provider execution, replay execution, sync apply/mutation implementation은 계속 순차적으로 차단된다.

## 검증

최종 검증은 커밋 직전에 수행한다.
