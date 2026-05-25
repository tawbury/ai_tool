# Provider Capability Validation Rule Promotion Audit

> 이 문서는 human context용 감사 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 provider capability validation behavior를 runtime governance rules로 승격할지 판단한다.

## 목적

`aios validate <provider-capability.json>` 정적 검증은 구현되었고 native JSON/envelope v2 출력 계약도 안정화되었다. 이 감사는 해당 동작이 runtime-facing rules로 승격할 만큼 내구성이 있는지 확인하고, 승격한다면 어느 규칙 파일에 무엇을 최소 반영할지 결정한다.

## 검토 대상

- `docs/reports/provider_capability_validate_output_contract_report.md`
- `docs/reports/provider_capability_validate_integration_report.md`
- `docs/plan/provider_capability_validate_output_contract_plan.md`
- `.ai/rules/operations/sync.rules.md`
- `.ai/rules/operations/validation.rules.md`

## 현재 구현 상태

| 항목 | 상태 |
| --- | --- |
| Provider capability helper | 구현됨 |
| Provider capability fixtures | 구현됨 |
| `aios validate <provider-capability.json>` | 구현됨 |
| Native JSON output contract | 안정화됨 |
| Envelope v2 output contract | 안정화됨 |
| Non-execution metadata | 보존됨 |
| Provider execution | 금지 |
| Sandbox execution | 금지 |
| Registry/discovery | 금지 |
| Adapter/generated content/snapshot update | 금지 |
| Sync apply/mutation | 차단 |

## Rule Promotion Readiness

Provider capability validation은 rule promotion 준비가 되었다.

근거:

- 명령 동작이 CLI에 구현되어 있다.
- target kind가 `provider-capability`로 고정되어 있다.
- static-only boundary가 result details와 envelope meta에 드러난다.
- output contract tests가 valid/invalid, shaped JSON detection, unrelated JSON non-misclassification, sync/replay priority, envelope v2, usage error를 고정한다.
- provider execution, sandbox execution, discovery/registry, adapter execution, generated content, snapshot update, sync apply/mutation이 모두 금지 상태로 유지된다.

남은 위험:

- capability validation이 provider 실행 승인처럼 오해될 수 있다.
- provider capability는 sync/replay safety와 관련이 있지만 validation behavior 자체는 domain-independent다.
- 너무 상세한 fixture inventory를 runtime rules에 넣으면 규칙이 테스트 구현 세부사항으로 오염될 수 있다.

## Promotion Target Assessment

### `.ai/rules/operations/validation.rules.md`

권장 primary target이다.

이유:

- `aios validate <provider-capability.json>`는 validate command behavior다.
- target kind, static-only validation, JSON/envelope output boundary는 validation layer에 속한다.
- provider capability validation은 future provider safety와 관련되지만 sync dry-run command 자체는 아니다.

Promote 내용:

- supported target: provider capability JSON
- target kind: `provider-capability`
- native JSON/envelope v2 support
- static-only boundary
- non-execution metadata
- provider/sandbox/registry/discovery/adapter/generated content/snapshot/sync apply/mutation 금지

### `.ai/rules/operations/sync.rules.md`

권장 secondary pointer다.

이유:

- provider capability는 future preview/replay provider safety gate와 관련된다.
- sync rules는 이미 replay validation, preview provider, provider execution forbidden boundary를 다룬다.
- 그러나 capability validation의 주된 명령은 `aios validate`이며, sync rules에 자세한 output contract를 반복하면 과부하가 생긴다.

Promote 내용:

- provider capability validation is available as static validation for future provider safety
- it does not authorize provider execution, sandbox execution, adapter execution, generated content, snapshot update, sync apply/mutation
- details remain in validation rules

### 둘 다 하지 않는 선택

비권장이다.

이유:

- 기능은 이미 구현되어 있고 output contracts가 안정화되었다.
- runtime-facing rules가 실제 supported command를 모르면 다음 작업자가 provider capability validation을 human-context-only 기능으로 오해할 수 있다.

## Promote Now vs Defer

권장: 지금 승격한다.

Defer할 이유가 약하다. provider execution은 여전히 금지되어 있고, 이번 promotion은 실행 권한을 여는 것이 아니라 static validation boundary를 runtime rules에 고정하는 작업이다.

## Promoted Scope

승격해야 할 내용:

- supported command:
  - `python -m aios validate <provider-capability.json>`
  - `python -m aios validate <provider-capability.json> --json`
  - `python -m aios validate <provider-capability.json> --json --envelope-v2`
- target kind:
  - `provider-capability`
- schema:
  - `aios.provider_capability.v0`
- static-only validation boundary
- non-execution metadata:
  - `provider_execution: false`
  - `sandbox_execution: false`
  - `mutation_performed: false`
- forbidden:
  - provider execution
  - sandbox execution
  - provider registry/discovery
  - adapter execution
  - generated content
  - snapshot update
  - sync apply/mutation

## Human-context Only

다음은 runtime rules에 넣지 않는다.

- fixture inventory details
- valid/invalid fixture filename list
- exact test file names
- provider isolation architecture details
- future sandbox execution design
- deterministic mock provider design
- future provider registry/discovery ideas

## Exact Suggested Rule Changes

### `validation.rules.md`

`Runtime JSON Targets` 섹션에 다음 내용을 추가한다.

```markdown
`aios validate` supports provider capability JSON targets:

- `python -m aios validate <provider-capability.json>`
- `python -m aios validate <provider-capability.json> --json`
- `python -m aios validate <provider-capability.json> --json --envelope-v2`

Provider capability validation uses target kind `provider-capability` and schema `aios.provider_capability.v0`.

Provider capability validation is static-only. It validates declaration shape and safety flags, and must preserve `provider_execution: false`, `sandbox_execution: false`, and `mutation_performed: false` in JSON/envelope output where applicable.

Provider capability validation must not execute providers, launch sandboxes, discover/register providers, execute adapters, generate content, update snapshots, write files, or authorize sync apply/mutation.
```

### `sync.rules.md`

Provider/replay safety area에 짧은 섹션 또는 pointer를 추가한다.

```markdown
## Provider Capability Validation

Provider capability validation is available through `aios validate <provider-capability.json>` as a static-only readiness check for future preview/replay provider safety.

It does not authorize provider execution, sandbox execution, registry/discovery, adapter execution, generated content, snapshot update, sync apply, or mutation. Detailed validation command behavior belongs in `.ai/rules/operations/validation.rules.md`.
```

## Recommendation

Split promotion을 권장한다.

1. Primary: `.ai/rules/operations/validation.rules.md`
2. Secondary short pointer: `.ai/rules/operations/sync.rules.md`

이번 감사는 rule 변경을 수행하지 않는다. 후속 작업에서 위 최소 변경안을 적용하는 것이 적절하다.

## 결론

Provider capability validation은 runtime governance rule promotion에 충분히 안정화되었다. 승격은 provider execution을 여는 작업이 아니라 이미 구현된 static validation command와 non-execution boundary를 공식화하는 작업이어야 한다.

Provider execution, sandbox execution, registry/discovery, adapter execution, generated content, snapshot update, sync apply/mutation은 계속 금지 상태로 유지한다.
