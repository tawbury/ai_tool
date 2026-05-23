# Dry-run Preview Integration Risk Audit

## 개요

이 문서는 fixture-backed generated preview output을 `aios sync --dry-run`에 통합할 때의 위험을 분석한다. 현재 provider는 read-only로 격리되어 있고 dry-run은 preview를 소비하지 않는다. 다음 구현 전 preview comparison이 기존 Phase 7 safety behavior를 약화하지 않도록 risk boundary를 정리한다.

이번 감사는 문서 작업만 수행한다. 런타임 코드, CLI, `.ai` rules는 변경하지 않는다.

## Risk Matrix

| 위험 | 심각도 | 가능성 | 설명 | 완화 |
| --- | --- | --- | --- | --- |
| Default preview activation | High | Medium | preview가 기본으로 켜지면 기존 dry-run behavior가 조용히 바뀐다. | preview는 opt-in으로만 허용하고 no default provider 정책을 둔다. |
| Drift-stop bypass | High | Medium | generated hash가 존재한다는 이유로 drifted target을 update 후보로 오분류할 수 있다. | target hash vs manifest hash 비교를 preview보다 먼저 수행한다. |
| Marker conflict bypass | High | Medium | invalid marker 상태에서 preview hash를 비교하면 managed boundary를 잘못 신뢰할 수 있다. | marker integrity validation이 preview보다 우선한다. |
| Source-missing confusion | High | Low | source가 없는데 fixture output만으로 update 후보가 만들어질 수 있다. | source existence/hash check가 preview보다 우선한다. |
| Fixture mapping ambiguity | Medium | Medium | manifest entry와 preview input fixture 연결이 불명확하면 잘못된 output이 적용될 수 있다. | explicit entry_id -> input fixture mapping을 요구하고 missing mapping은 no-update로 처리한다. |
| Update candidate interpreted as apply | High | Medium | `action: update`가 write authorization으로 오해될 수 있다. | severity informational, `mutation_performed: false`, rule/report messaging으로 boundary를 고정한다. |
| Preview unavailable noise | Medium | Medium | unavailable 상태가 너무 많은 warning을 만들어 dry-run UX를 악화할 수 있다. | unavailable message는 선택적으로 emit하고 blocking reason은 기존 결과가 우선한다. |
| Envelope metadata loss | Medium | Medium | envelope v2에서 preview provenance가 누락되면 downstream 검증이 어려워진다. | payload result details와 meta에 provider/policy/provenance를 보존한다. |
| Existing output contract regression | High | Low | preview integration이 기존 `sync --dry-run` 기본 출력 shape를 깨뜨릴 수 있다. | preview flag 없을 때 기존 output contract tests를 그대로 유지한다. |
| Provider boundary creep | High | Medium | fixture provider 통합이 real adapter execution으로 확장될 수 있다. | next slice는 fixture provider only로 제한하고 real provider는 non-goal로 둔다. |

## 핵심 위험

### Default Preview Activation

Preview integration이 default behavior가 되면 기존 Phase 7 dry-run output이 바뀐다. 현재 output contract tests는 preview 없는 기본 behavior를 고정하고 있다.

완화:

- preview는 opt-in flag로만 활성화한다.
- no default preview provider 정책을 유지한다.
- preview flag가 없으면 기존 결과와 exit code가 변하지 않아야 한다.

### Precedence Regression

가장 큰 안전 위험은 generated preview가 기존 blocking state보다 먼저 적용되는 것이다.

우선순위는 반드시 다음 순서를 따른다.

1. Manifest schema error
2. Source missing
3. Target missing policy
4. Marker conflict
5. Drift-stop
6. Preview comparison

이 순서가 깨지면 drifted target이나 invalid marker가 update candidate로 잘못 분류될 수 있다.

### Fixture Mapping Ambiguity

Fixture-backed provider는 filename mapping을 사용한다. Dry-run integration에서는 manifest entry와 fixture input 사이의 mapping이 추가로 필요하다. 이 mapping이 암묵적이면 wrong fixture가 적용될 위험이 있다.

완화:

- entry_id -> input fixture mapping을 explicit하게 둔다.
- missing mapping은 preview unavailable 또는 no-update로 처리한다.
- mapping mismatch는 update candidate가 아니라 usage/config error 또는 no-update 후보로 검토한다.

### Update Candidate Semantics

`action: update`는 기존 result enum에 존재하지만 아직 dry-run에서 사용하지 않는다. Preview integration이 이를 사용하면 사용자가 sync apply 가능 상태로 오해할 수 있다.

완화:

- `update`는 read-only candidate다.
- severity는 `informational`이다.
- `meta.mutation_performed`는 항상 `false`다.
- message text와 details는 write authorization이 아님을 명확히 해야 한다.

### Preview Unavailable Reporting

Preview unavailable은 대부분 실패가 아니다. 하지만 이유를 숨기면 update candidate가 왜 나오지 않았는지 알 수 없다.

완화:

- `details.preview_unavailable_reason`을 보존한다.
- warning은 `unsupported-sync-mode`, `activation-unresolved` 같은 사용자가 조치할 수 있는 경우에 제한한다.
- `adapter-unavailable`과 `generation-disabled`는 info로 충분할 수 있다.
- `source-missing`과 marker invalid는 기존 blocking message가 우선한다.

### Envelope v2 Consistency

Envelope v2는 downstream tooling의 안정적인 entry point다. Preview metadata가 native result에는 있고 envelope에는 없다면 tooling이 근거를 잃는다.

완화:

- generated hashes는 `payload.results[].hashes`에 보존한다.
- preview details는 `payload.results[].details.preview`에 보존한다.
- provider/policy는 `meta.preview_provider`, `meta.preview_policy`에 보존한다.
- unavailable reason은 messages 또는 details 중 최소 하나에 보존한다.

## Implementation Readiness

다음 조건이 충족되어야 preview integration 구현을 시작할 수 있다.

- fixture-backed provider tests가 통과한다.
- existing sync output contract tests가 통과한다.
- CLI flag design이 확정된다.
- entry_id -> input fixture mapping 방식이 확정된다.
- preview unavailable severity policy가 확정된다.
- envelope v2 mapping tests가 준비된다.

현재 충족된 조건:

- fixture-backed provider exists
- fixture schema tests exist
- sync output contract tests exist

아직 남은 조건:

- CLI flag implementation decision
- dry-run evaluator injection boundary
- entry mapping fixture/index policy
- update candidate output contract tests
- envelope v2 preview mapping tests

## Non-goal Boundary

다음은 다음 integration implementation에서도 계속 금지해야 한다.

- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- adapter generation
- real generated content creation
- default preview provider
- activation-driven preview selection
- repository-wide scan
- force
- decommission

## Recommended Next Bundle

권장 다음 bundle은 "fixture-backed dry-run preview integration"이다.

포함:

- opt-in preview CLI flags
- fixture provider injection into dry-run evaluator
- explicit fixture mapping
- clean-target-only update candidate classification
- native JSON preview fields
- envelope v2 preview metadata
- contract tests

제외:

- real provider
- adapter execution
- generated content creation
- sync apply
- mutation

## 결론

Dry-run preview integration은 구현 준비가 거의 되었지만, 반드시 opt-in fixture-backed path로 시작해야 한다. 핵심 안전 조건은 preview comparison이 source, marker, drift-stop evaluation 이후에만 실행되는 것이다. Preview unavailable은 no-update여야 하고, update candidate는 informational read-only planning result로만 취급해야 한다.
