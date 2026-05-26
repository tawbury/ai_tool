# Sandbox Trace Validate Output Contract Risk Audit

## 목적

이 감사는 future `aios validate <sandbox-trace.json>` 출력 계약이 기존 validate target detection과 output contracts를 흔들지 않고, sandbox/provider execution authorization으로 오해되지 않도록 위험을 식별한다.

이 보고서는 runtime code를 구현하지 않으며 `.ai/rules`를 수정하지 않는다.

## 현재 상태

완료된 항목:

- sandbox trace fixture-only bundle
- `aios.sandbox_trace.v0` valid/invalid/edge fixtures
- sandbox trace fixture contract tests
- `validate_sandbox_trace_data(data)` helper
- helper unit tests

아직 구현되지 않은 항목:

- `aios validate <sandbox-trace.json>`
- native JSON output mapping
- envelope v2 mapping
- runtime rule promotion

계속 금지되는 항목:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply
- mutation

## 주요 위험

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| sandbox trace가 sandbox result로 오분류됨 | 기존 sandbox result output contract가 흔들릴 수 있음 | medium | detection priority를 sandbox result 이후 sandbox trace로 고정한다. |
| provider execution trace와 sandbox trace heuristic 충돌 | provider trace target kind가 잘못 바뀔 수 있음 | medium | provider execution trace detection을 sandbox trace보다 우선한다. |
| unrelated JSON이 sandbox-trace로 분류됨 | generic validate behavior regression 발생 | medium | shaped heuristic은 최소 field count와 anchor field를 함께 요구한다. |
| success output이 execution approval로 오해됨 | sandbox/provider execution이 승인된 것처럼 보일 수 있음 | high | native details와 envelope meta에 execution flags false를 고정한다. |
| invalid trace의 `mutation_performed: true`가 command metadata로 전파됨 | validate command가 mutation을 수행한 것처럼 보일 수 있음 | medium | command-level metadata는 항상 `mutation_performed: false`를 사용한다. |
| helper issue details 손실 | output contract tests가 실패하거나 디버깅이 어려워짐 | medium | helper issue code/message/field를 보존하는 mapping을 요구한다. |
| referenced body validation으로 범위 확장 | file IO, target coupling, latency 증가 | medium | sandbox trace target은 parsed trace structure만 검증한다고 명시한다. |
| envelope v2 message churn | 기존 envelope consumers에 영향 | low | `payload.results`에 native results를 보존하고 messages는 기존 mapping 방식에 맞춘다. |

## Target Detection Risk

Sandbox trace는 sandbox result, provider execution trace와 필드가 일부 겹친다. 따라서 priority가 중요하다.

권장 priority:

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy
7. sandbox result
8. sandbox trace

Sandbox trace를 sandbox result보다 먼저 감지하면 `trace_id`, `request_id`, `status`, `failure_code` 같은 공통 필드 때문에 sandbox result를 오분류할 수 있다.

## Output Contract Risk

Native JSON and envelope v2 outputs must preserve non-execution metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

이 metadata는 validate command의 runtime behavior를 설명한다. Invalid trace document가 `mutation_performed: true`를 포함하더라도 command-level metadata는 false여야 한다.

## Static-only Boundary Risk

Sandbox trace는 sandbox result와 provider trace를 연결하는 bridge이므로 referenced files를 검증하고 싶은 유혹이 있다. 그러나 이 output contract 단계에서는 full linked body validation을 포함하지 않는다.

Future validate integration should not:

- open referenced provider traces for full validation
- open referenced sandbox results for full validation
- compare provider output
- approve generated content
- launch sandbox
- execute subprocess/provider/replay

Cross-fixture relationship checks can remain in fixture contract tests until a separate relationship validator design exists.

## Compatibility Risk

Required regression checks:

- sandbox result detection unchanged
- sandbox policy detection unchanged
- provider execution trace detection unchanged
- provider capability detection unchanged
- replay manifest detection unchanged
- sync manifest detection unchanged
- unrelated JSON not misclassified
- `--envelope-v2` without `--json` remains exit code `2`

## Documentation Index Risk

The new output contract plan and risk audit should be listed in `docs/index/document_status_registry.md`. They remain human context and do not become runtime contracts until a later `.ai/rules` promotion task.

`docs/index/current_runtime_context.md` should continue to indicate that `aios validate <sandbox-trace.json>` integration is a future sequential step and sandbox execution remains blocked.

## Recommendation

Proceed next with sandbox trace validate integration only after this output contract is accepted. Bundle integration with output contract tests if requested, but do not combine with sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, or mutation.

## Conclusion

The sandbox trace validate output contract is safe to design now because it only defines static validation output. The main safeguards are strict target detection priority, preserved helper issue codes, explicit non-execution metadata, and no linked-body execution or approval behavior.
