# Sandbox Trace Fixture Risk Audit

> 이 보고서는 design-only risk audit이다. Sandbox trace fixture 계약은 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

이 감사는 `aios.sandbox_trace.v0` fixture 계약이 sandbox result evidence와 provider execution trace metadata를 연결할 때 발생할 수 있는 실행 권한 혼동, output approval 오해, 관계 검증 과신 위험을 식별하고 완화한다.

## 현재 경계

현재 `.ai OS`는 다음을 지원한다.

- provider capability static validation
- provider execution trace static validation
- sandbox policy static validation
- sandbox result static validation
- fixture-backed replay comparison
- fixture-backed sync dry-run preview comparison

현재 금지 상태:

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

Sandbox trace fixture는 위 금지 상태를 변경하지 않는다.

## 주요 위험

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Sandbox trace success가 execution authorization으로 오해됨 | sandbox launcher or subprocess execution이 조기 구현될 수 있음 | medium | 문서와 fixture index에 `sandbox_execution: false`, `subprocess_execution: false`를 고정한다. |
| Provider trace ref가 provider output approval로 오해됨 | generated output이나 update candidate를 부적절하게 신뢰할 수 있음 | medium | provider trace body 전체 검증과 output approval은 non-goal로 둔다. |
| Sandbox result와 trace relationship을 과신함 | trace_id/request_id match만으로 safety를 과대평가할 수 있음 | medium | relationship check는 linked evidence consistency만 확인한다고 명시한다. |
| Sandbox trace가 registry/discovery source로 사용됨 | 동적 로딩이나 provider discovery 경계가 흐려질 수 있음 | low | fixture directory와 index는 runtime registry가 아니라고 명시한다. |
| Unsafe observed output path가 target mutation처럼 보임 | target/source path 오염 또는 mutation 오해가 생길 수 있음 | medium | observed output refs는 safe relative 또는 sandbox temp refs로 제한한다. |
| Timestamp/duration evidence가 실제 execution proof로 오해됨 | fixture-only evidence를 runtime execution evidence로 착각할 수 있음 | medium | deterministic placeholder를 허용하고 fixture-only임을 명시한다. |
| Stale cross-reference | sandbox result와 provider trace fixture가 서로 다른 request/trace를 가리킬 수 있음 | medium | fixture bundle에서 request_id/trace_id relationship tests를 요구한다. |
| Missing provider trace ref를 failure로만 처리함 | edge case를 표현하지 못해 fixture가 과도하게 경직됨 | low | `provider_trace_ref: null` edge case를 허용한다. |
| Future validator가 full provider trace validation으로 확장됨 | provider execution trace validation output contract가 흔들릴 수 있음 | low | sandbox trace validator는 ref-level relationship만 다루고 full body validation은 별도 target에 맡긴다. |

## 관계 경계 위험

Sandbox trace는 세 artifact를 연결한다.

- sandbox policy: declared constraints
- sandbox result: observed sandbox-like result evidence
- provider execution trace: provider-like metadata evidence

위험은 이 연결이 “실행이 안전했다” 또는 “provider output이 승인됐다”로 해석되는 것이다. v0 계약은 다음을 보장하지 않는다.

- provider output correctness
- generated hash approval
- replay success
- sync apply readiness
- no-write system-wide proof
- sandbox launcher safety

v0 계약이 보장하는 것은 fixture relationship consistency뿐이다.

## Validation Risk Controls

Future fixture tests should enforce:

- required field presence.
- `schema_version: aios.sandbox_trace.v0`.
- status/failure-code mapping.
- safe relative refs.
- unsafe observed output path rejection.
- `network_disabled: true`.
- `mutation_performed: false`.
- `no_write_confirmed: true` for pass.
- provenance required.
- request_id and trace_id relationship matching when linked sandbox result data is available.

Tests must remain fixture-only and must not load providers, launch sandboxes, execute subprocesses, run replay, generate content, write snapshots, or mutate files.

## Runtime Rule Promotion Risk

This task does not modify `.ai/rules`.

Rule promotion should be deferred until at least one of these exists:

- sandbox trace fixture bundle and fixture tests
- sandbox trace validator helper
- `aios validate <sandbox-trace.json>` static integration
- output contract stabilization

Even after promotion, rules must describe static validation only unless a later execution gate explicitly approves sandbox or provider execution.

## Documentation Index Risk

The new plan and audit should be listed in `docs/index/document_status_registry.md` so future agents do not rediscover or duplicate the design. They should remain human context with task-load/lazy-load policy, not runtime contracts.

`docs/index/current_runtime_context.md` should continue to say sandbox execution remains blocked. It may recommend sandbox trace fixture-only bundle as the next static step.

## Parallelization Assessment

Safe to bundle in this task:

- sandbox trace fixture contract plan
- sandbox trace risk audit
- docs index updates

Safe future parallel design-only track:

- sandbox trace fixture bundle can follow this plan.
- sandbox trace validator helper must wait for fixture bundle completion.
- sandbox trace validate output contract must wait for helper completion.

Must remain sequentially blocked:

- sandbox launcher implementation
- subprocess execution implementation
- provider execution implementation
- replay execution implementation
- generated content creation
- snapshot update
- sync apply or mutation

## Recommendation

Proceed next with a sandbox trace fixture-only bundle and fixture contract tests. Keep sandbox trace validator helper, validate integration, and rule promotion as later sequential steps. Do not implement sandbox launcher or execution behavior.

## Conclusion

`aios.sandbox_trace.v0` is appropriate as a fixture-only bridge between sandbox result evidence and provider execution trace metadata. It is not an execution authorization layer, not a provider output approval layer, and not a mutation readiness signal.
