# 제공자 실행 trace validate output contract 리스크 감사

> 이 문서는 human context 감사 보고서이다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 감사는 future `aios validate <provider-trace.json>` 출력이 provider execution 승인으로 오해되는 위험을 검토한다.

## 목적

Provider execution trace validator helper가 존재하지만 아직 `aios validate`와 연결되어 있지 않다. Validate integration을 설계하기 전에 출력 계약이 static-only boundary를 분명히 보존하는지 검토해야 한다.

## 현재 기준선

| Area | State |
| --- | --- |
| Trace schema plan | 완료 |
| Trace fixture bundle | 완료 |
| Trace validator helper | parsed dict only |
| `aios validate <provider-trace.json>` | 미구현 |
| Provider execution | 금지 |
| Sandbox execution | 금지 |
| Dynamic loading | 금지 |
| Registry/discovery | 금지 |
| Adapter execution | 금지 |
| Generated content | 금지 |
| Replay execution | 금지 |
| Sync apply/mutation | 금지 |

## 주요 리스크

| Risk | Impact | Control |
| --- | --- | --- |
| Trace validate success를 execution approval로 오해 | provider execution 금지 약화 | success message와 metadata에 `provider_execution: false` 명시 |
| Invalid trace의 `mutation_performed: true`가 command mutation처럼 보임 | validate command read-only 경계 혼동 | envelope/native metadata는 command-level `mutation_performed: false` 유지 |
| Trace-shaped heuristic이 unrelated JSON을 오분류 | 기존 validate UX 훼손 | 명확한 field count와 `trace_id`/`provider_mode` 조건 사용 |
| Provider capability JSON과 trace JSON 충돌 | target detection regression | capability detection을 trace detection보다 우선 |
| Replay manifest validation regression | replay validation 계약 흔들림 | replay manifest detection을 trace detection보다 우선 |
| Failure code가 command failure reason으로 오해 | runtime issue triage 혼동 | failure_code는 trace content evidence라고 명시 |
| Envelope v2 metadata가 execution path처럼 보임 | runtime capability 과대해석 | `provider_execution`, `sandbox_execution`, `mutation_performed` 명시 |
| Static validation이 replay execution처럼 보임 | future provider 실행 착각 | no replay execution/non-goals 반복 |

## Detection risk controls

Detection은 보수적이어야 한다.

권장:

- `schema_version: aios.provider_execution_trace.v0`는 명확히 trace target이다.
- schema가 없거나 틀린 경우에도 trace-shaped JSON만 trace로 분류한다.
- 최소 field count와 `trace_id` 또는 `provider_mode` 존재 조건을 요구한다.
- sync/replay/provider capability target detection 이후에 trace detection을 수행한다.

금지:

- `provider_id` 하나만으로 trace target을 판정하지 않는다.
- 모든 JSON validation fallback을 trace validator로 넘기지 않는다.
- malformed JSON을 trace validation issue로 변환하지 않는다.

## Output risk controls

Native JSON:

- target kind는 `provider-execution-trace`로 명시한다.
- success code는 `provider_execution_trace_checked`로 제한한다.
- success details에 non-execution metadata를 포함한다.
- issue code는 helper issue code를 보존한다.

Envelope v2:

- command는 `validate`다.
- target kind는 `provider-execution-trace`다.
- meta에 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`를 포함한다.
- `provider_mode`는 trace content를 설명하는 metadata일 뿐 실행 mode selection이 아니다.

## Static-only boundary

Validate integration은 다음을 수행하지 않아야 한다.

- provider execution
- sandbox launch
- dynamic provider loading
- registry/discovery
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply
- file mutation

이 경계는 success/failure output 모두에 동일하게 적용된다.

## Exit code risk

Trace content validation failure는 exit code `1`이 맞다. Usage/config error는 exit code `2`를 유지한다. 단, trace 내부 `failure_code`가 있다고 해서 CLI usage error가 되어서는 안 된다. 이는 trace document content의 일부이며, validator는 해당 field의 enum과 semantics만 검증한다.

## Compatibility risk

기존 validate target과 충돌하지 않도록 다음 회귀 테스트가 필요하다.

- sync manifest target detection unchanged
- replay manifest target detection unchanged
- provider capability target detection unchanged
- unrelated JSON not misclassified
- envelope v2 without `--json` still exit code `2`

## 결론

Provider execution trace validate output contract는 설계해도 안전하다. 다음 구현 slice는 validate integration과 output contract tests가 적절하다. 이 통합은 static-only validation이어야 하며 provider execution, sandbox execution, replay execution, adapter execution, generated content creation, snapshot update, sync apply, mutation을 계속 차단해야 한다.
