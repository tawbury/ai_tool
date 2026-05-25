# Provider Execution Trace Rule Promotion Audit

> 이 문서는 감사 보고서이며 runtime contract가 아니다. 실제 runtime governance는 `.ai/rules/`에 승격된 뒤에만 효력을 가진다. 이번 작업은 `.ai/rules`를 수정하지 않았다.

## 목적

`aios validate <provider-trace.json>` static validation이 runtime governance rules로 승격될 만큼 안정적인지 판단하고, 승격 대상과 후속 병렬/번들 작업 순서를 정한다.

## 검토 대상

- `docs/reports/provider_execution_trace_validate_output_contract_report.md`
- `docs/plan/provider_execution_trace_validate_output_contract_plan.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/index/current_runtime_context.md`

## 성숙도 감사

Provider execution trace validation은 rule promotion에 충분히 안정적이다.

근거:

- `aios validate <provider-trace.json>` static validation이 구현되어 있다.
- Native JSON은 `target.kind: provider-execution-trace`와 `schema_version: aios.validate.result.v0`를 유지한다.
- Envelope v2는 `command: validate`, `target.kind: provider-execution-trace`를 유지한다.
- Native JSON, envelope v2, payload, messages에서 non-execution metadata가 고정되어 있다.
- `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`가 보존된다.
- `provider_mode`는 trace에 존재할 때 보존된다.
- `failure_code`와 `unavailable_reason`은 failure details에서 보존된다.
- Target detection regression이 테스트로 고정되어 provider capability, replay manifest, sync manifest, unrelated JSON의 기존 분류를 깨지 않는다.

남은 위험은 구현 안정성보다 rule 표현의 범위 문제다. Trace validation은 validation command behavior이므로 primary rule target은 validation rules가 맞고, sync rules에는 provider/replay safety context pointer만 두는 편이 적절하다.

## 승격 여부

결론: 지금 승격한다.

권장 방식: split promotion

- Primary: `.ai/rules/operations/validation.rules.md`
- Secondary pointer: `.ai/rules/operations/sync.rules.md`
- Provider-specific operation rule은 아직 만들지 않는다.

Provider-specific rule은 provider execution, sandbox, registry/discovery, provider lifecycle이 반복적으로 등장하고 단일 파일로 관리할 필요가 생길 때 검토한다. 현재는 static validation과 sync/replay safety boundary의 일부이므로 별도 rule file은 과하다.

## 승격할 내용

`validation.rules.md`에 승격할 내용:

- Supported commands:
  - `python -m aios validate <provider-trace.json>`
  - `python -m aios validate <provider-trace.json> --json`
  - `python -m aios validate <provider-trace.json> --json --envelope-v2`
- Target kind:
  - `provider-execution-trace`
- Schema:
  - `aios.provider_execution_trace.v0`
- Static-only validation boundary:
  - parsed JSON structure and safety evidence only
- Non-execution metadata:
  - `provider_execution: false`
  - `sandbox_execution: false`
  - `mutation_performed: false`
- Provider mode preservation:
  - `provider_mode` is preserved when available.
- Explicit prohibitions:
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

`sync.rules.md`에 둘 내용:

- Provider execution trace validation is available through `aios validate <provider-trace.json>`.
- It is static-only evidence for future provider/replay safety.
- It does not authorize provider execution, sandbox execution, dynamic loading, registry/discovery, adapter execution, generated content, snapshot update, replay execution, sync apply, or mutation.
- Detailed command/output behavior belongs in validation rules.

## Human-context Only로 남길 내용

다음 항목은 runtime rules에 넣지 않는다.

- fixture inventory details
- exact test filenames
- future sandbox architecture details
- helper implementation internals
- target detection heuristic field count
- migration note examples
- future provider-specific rule file speculation beyond a short deferral note

## 병렬화 및 번들 평가

Rule promotion 전에는 audit 결론이 필요하므로 `.ai/rules` promotion은 이 감사와 병렬로 묶으면 안 된다.

감사 이후에는 일부 병렬화가 가능하다.

권장 후속 순서:

1. Sequential: provider execution trace validation runtime rule promotion
2. Bundled with 1: docs index update and rule promotion report
3. Parallel design-only track: sandbox architecture planning audit
4. Sequential after sandbox/provider boundary decisions: any provider execution or mock helper runtime work

Sandbox architecture planning은 design-only라면 rule promotion과 별도 후속 작업으로 병렬 진행할 수 있다. 다만 sandbox planning은 execution authorization으로 읽히면 안 되며 provider execution, replay execution, generated content, sync apply, mutation을 계속 금지해야 한다.

## 권장 다음 작업

1. `validation.rules.md`와 `sync.rules.md`에 provider execution trace validation behavior를 승격한다.
2. 승격 보고서를 작성하고 docs index를 함께 갱신한다.
3. 별도 design-only track으로 sandbox architecture planning audit를 진행할지 결정한다.

## 계속 차단되는 기능

- provider execution
- sandbox execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply/mutation
