# Sandbox Result Validation Rule Promotion Audit

## 목적

이 감사는 `aios validate <sandbox-result.json>` 정적 검증 동작을 `.ai OS` runtime governance rules에 승격할지 결정한다. 이번 작업은 감사와 권장안 작성만 수행하며 `.ai/rules`를 수정하지 않는다.

## 검토 대상

- `docs/reports/sandbox_result_validate_output_contract_report.md`
- `docs/plan/sandbox_result_validate_output_contract_plan.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/index/current_runtime_context.md`

## 현재 구현 성숙도

Sandbox result validation은 rule promotion에 충분히 성숙했다.

완료된 근거:

- `aios validate <sandbox-result.json>` static validation 구현
- target kind `sandbox-result`
- schema `aios.sandbox_execution_result.v0`
- native JSON output contract 안정화
- envelope v2 output contract 안정화
- helper issue code/message/field/details 보존
- shaped invalid schema와 missing schema detection 고정
- unrelated JSON non-misclassification 고정
- sandbox policy, provider execution trace, provider capability, replay manifest, sync manifest target detection regression 고정
- non-execution metadata 보존

보존되는 metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`
- `sandbox_mode` when available
- `request_id` when available
- `failure_code` when available

## Promotion Decision

권장 결정: 지금 승격한다.

권장 방식: split promotion.

- Primary: `.ai/rules/operations/validation.rules.md`
- Secondary pointer: `.ai/rules/operations/sync.rules.md`

새 provider/sandbox-specific rule file은 만들지 않는다. 현재 동작은 validation target behavior이며, sandbox execution architecture 전체를 다루는 별도 runtime rule을 만들 만큼 반복 유지보수 필요가 아직 없다.

## Promote To Validation Rules

`validation.rules.md`의 Runtime JSON Targets section에 다음 내용을 추가하는 것이 적절하다.

지원 명령:

- `python -m aios validate <sandbox-result.json>`
- `python -m aios validate <sandbox-result.json> --json`
- `python -m aios validate <sandbox-result.json> --json --envelope-v2`

Target/schema:

- target kind: `sandbox-result`
- schema: `aios.sandbox_execution_result.v0`

Boundary:

- parsed JSON structure와 sandbox result evidence만 정적으로 검증한다.
- sandbox result validation은 sandbox launcher, subprocess execution, provider execution, replay execution을 수행하지 않는다.

JSON/envelope metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`
- `sandbox_mode` preserved where available
- `request_id` preserved where available
- `failure_code` preserved where available

Explicit prohibitions:

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

## Promote To Sync Rules

`sync.rules.md`에는 짧은 pointer만 추가하는 것이 적절하다.

권장 내용:

- sandbox result validation is available through `aios validate <sandbox-result.json>`
- it is static-only evidence for future sandbox/provider safety
- it does not authorize sandbox launcher, subprocess execution, provider execution, replay execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, sync apply, or mutation
- detailed command/output behavior belongs in validation rules

Sync rules에는 fixture inventory, exact tests, helper internals, detection heuristic field counts를 넣지 않는다.

## Human-context Only

다음은 `.ai/rules`에 승격하지 않는다.

- fixture inventory details
- exact test filenames
- helper internals
- target detection heuristic field counts
- invalid fixture lists
- edge fixture lists
- future sandbox trace schema details
- future launcher design details

이 정보는 `docs/plan`, `docs/reports`, `tests/fixtures`의 human context로 충분하다.

## Defer Alternatives

### Defer until sandbox trace fixtures exist

비권장. Sandbox result validation은 이미 독립 static validation target으로 구현되고 output contract가 안정화되었다. Sandbox trace fixture contract는 별도 future artifact이며 현재 behavior promotion을 막을 필요가 없다.

### Validation rules only

부분 권장이나 충분하지 않다. Detailed behavior는 validation rules에 두는 것이 맞지만, sync/sandbox safety context에서는 sandbox result가 execution authorization이 아님을 짧게 연결해 두는 편이 안전하다.

## Parallelization Assessment

Rule promotion과 docs index/report update는 follow-up task에서 안전하게 묶을 수 있다.

독립 parallel design-only track:

- sandbox trace fixture contract
- sandbox trace fixture risk audit

순차로 유지해야 하는 작업:

1. rule promotion audit
2. rule promotion
3. rule promotion validation
4. future sandbox result rule promotion report

계속 차단:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- generated content
- snapshot update
- sync apply/mutation

## 결론

Sandbox result validation behavior는 runtime governance rule promotion에 충분히 안정화되었다. 다음 작업은 `.ai/rules/operations/validation.rules.md`에 primary rule을 추가하고 `.ai/rules/operations/sync.rules.md`에 짧은 safety pointer를 추가하는 promotion task가 적절하다.
