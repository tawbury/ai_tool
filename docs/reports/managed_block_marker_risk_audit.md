# Managed Block Marker Risk Audit

## 개요

이 문서는 `.ai OS` Phase 6 managed block marker contract의 위험을 감사한다. marker는 future mixed-boundary sync에서 user-owned content와 runtime-managed content를 구분하는 핵심 경계이므로, marker 설계가 모호하면 destructive overwrite 위험이 커진다.

현재 시스템은 read-only이다. 이 감사는 parser, sync execution, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, rollback, force, source mutation을 구현하지 않는다.

## 감사 범위

감사 대상:

- marker syntax ambiguity
- entry identity mismatch
- marker duplication
- nested or overlapping marker
- marker examples being parsed as real markers
- code fence false positive
- hash boundary ambiguity
- insertion ambiguity
- update without drift protection
- unsafe removal
- dry-run mapping loss
- envelope v2 and observability compatibility loss

## Risk Matrix

| Risk | 영향 | 권장 완화 |
|---|---|---|
| marker syntax가 느슨함 | parser가 user content를 managed content로 오판 | canonical line-oriented syntax 사용 |
| `entry_id` mismatch 허용 | 잘못된 block update | begin/end/manifest `entry_id` 일치 필수 |
| duplicate marker 허용 | 어느 block을 갱신할지 불명확 | same `entry_id`는 exactly one pair |
| nested marker 허용 | block boundary 오판 | nested/overlap은 `marker-corrupted` |
| code fence 예시를 marker로 파싱 | 문서 예시가 실제 block으로 오인 | code fence 내부 marker-looking text 무시 |
| marker line을 hash에 포함 | provenance metadata 변경이 content drift로 오판 | marker line 제외, content only hash |
| marker line을 검증하지 않음 | identity 손상 누락 | marker integrity check를 hash check 전에 수행 |
| insertion anchor 없음 | user-owned 영역에 삽입 | explicit anchor 없으면 conflict |
| marker missing을 create로 처리 | 삭제된 marker를 자동 복구하며 user intent 침해 | first-create policy 없으면 conflict |
| orphan marker 자동 삭제 | 과거 managed content 손실 | orphan-warning only |

## Syntax Risks

### Loose Syntax Risk

위험:

- 여러 comment style과 spacing을 모두 허용하면 parser behavior가 예측하기 어려워진다.
- 사람이 쓴 일반 주석을 marker로 오인할 수 있다.

정책:

- canonical syntax는 `AIOS:BEGIN managed-block`과 `AIOS:END managed-block` token을 포함해야 한다.
- marker line은 한 줄 전체를 차지해야 한다.
- future parser는 허용된 comment style만 인식해야 한다.

### Attribute Parsing Risk

위험:

- `entry_id` 또는 `marker_version`이 누락되어도 marker로 받아들이면 identity가 약해진다.

정책:

- `entry_id`와 `marker_version`은 required이다.
- malformed attribute syntax는 `marker-corrupted`이다.
- unknown optional attribute는 future policy 전까지 warning 또는 corrupted 중 하나로 명시해야 한다.

## Identity Risks

### Entry ID Mismatch

위험:

- begin marker와 end marker가 서로 다른 entry를 가리키면 managed block boundary가 신뢰할 수 없다.
- marker `entry_id`가 manifest entry와 다르면 다른 target을 덮어쓸 수 있다.

정책:

- begin marker `entry_id`, end marker `entry_id`, manifest entry `entry_id`가 모두 동일해야 한다.
- mismatch는 blocking conflict이다.

### Marker Version Mismatch

위험:

- begin과 end가 서로 다른 marker syntax version을 갖는 경우 parser 의미가 불명확하다.

정책:

- begin/end `marker_version`은 동일해야 한다.
- unsupported version은 conflict로 처리한다.

## Boundary Risks

### Duplicate Marker

위험:

- 같은 `entry_id` marker가 두 개 이상 있으면 어느 block이 authoritative한지 알 수 없다.

정책:

- same `entry_id`는 exactly one begin/end pair만 허용한다.
- duplicate는 `marker-duplicated` conflict이다.

### Nested Marker

위험:

- nested marker는 outer block content와 inner block identity를 혼합한다.
- parser가 한 block을 다른 block 일부로 오판할 수 있다.

정책:

- nested marker는 `marker-corrupted`이다.
- overlap도 `marker-corrupted`이다.

### Missing Begin or End

위험:

- begin만 있거나 end만 있으면 managed content 범위가 무한히 확장되거나 잘못 축소될 수 있다.

정책:

- missing begin/end는 `marker-corrupted`이다.
- expected marker가 전혀 없으면 first-create policy 여부에 따라 `marker-missing` conflict 또는 create candidate이다.

## Code Fence Risks

### Documentation Example False Positive

위험:

- plan/report 문서 안에 marker 예시가 있을 때 future parser가 예시를 실제 marker로 오인할 수 있다.

정책:

- Markdown fenced code block 안의 marker-looking text는 기본적으로 marker로 파싱하지 않는다.
- code fence 안 marker parsing은 explicit allow policy가 없으면 금지한다.

### Ambiguous Fence Parsing

위험:

- unclosed fence가 있으면 marker가 fence 안인지 밖인지 판단하기 어렵다.

정책:

- implementation은 unclosed fence를 fail closed 하거나 marker candidate를 무시하는 정책을 명시해야 한다.
- marker가 target file에 필요한 상황에서 fence ambiguity가 있으면 conflict로 처리하는 것이 안전하다.

## Hash Boundary Risks

### Including Marker Lines in Hash

위험:

- `generated_by` 변경, marker version migration, whitespace change가 managed content drift로 오판된다.

정책:

- managed block hash는 marker lines를 제외한 inner content만 대상으로 한다.
- marker identity와 syntax는 별도 integrity check로 검증한다.

### Excluding Marker Lines Without Integrity Check

위험:

- marker line이 손상되어도 hash가 같으면 update candidate로 잘못 분류될 수 있다.

정책:

- marker integrity check를 hash comparison보다 먼저 수행한다.
- marker corrupted 상태에서는 hash comparison을 update 근거로 사용하지 않는다.

### Line Ending Drift

위험:

- Windows/Unix line ending 차이가 hash churn을 만든다.
- 반대로 normalization이 실제 byte drift를 숨길 수 있다.

정책:

- Phase 6 계약에서는 hash boundary만 확정하고 normalization은 future manifest schema에서 결정한다.
- 초기 후보는 observed bytes 기반 hash이며, normalization은 별도 호환성 검토가 필요하다.

## Insertion Risks

### Anchor Ambiguity

위험:

- explicit insertion anchor가 없으면 marker를 어디에 넣어야 할지 알 수 없다.
- 잘못된 위치에 block을 넣으면 user-owned content 흐름을 손상시킨다.

정책:

- insertion은 explicit anchor가 있을 때만 dry-run create candidate가 된다.
- anchor가 없거나 둘 이상이면 conflict이다.

### Marker Missing as Create

위험:

- 사용자가 marker를 제거했는데 future sync가 이를 first-create로 오판할 수 있다.

정책:

- expected existing block의 marker missing은 기본 conflict이다.
- first-create는 manifest entry나 policy가 명확히 표시해야 한다.

## Update Risks

### Update Without Clean Hash

위험:

- marker가 valid라는 이유만으로 update하면 사용자가 managed block 내부를 수정한 내용을 덮어쓸 수 있다.

정책:

- update candidate는 marker valid와 target managed block hash match가 모두 필요하다.
- hash mismatch는 `drift-stop`이다.

### Marker External Content Drift

위험:

- mixed-boundary 파일에서 marker 밖 user-owned content 변경을 blocking drift로 처리하면 사용자의 정상 편집을 막는다.

정책:

- marker 밖 content는 managed block hash 대상이 아니다.
- marker 밖 변경은 informational 또는 ignored로 유지한다.

## Removal Risks

### Orphan Auto-removal

위험:

- manifest entry가 없어졌다는 이유로 marker block을 삭제하면 사람이 보존한 generated content가 사라질 수 있다.

정책:

- orphan marker는 `orphan-warning`만 생성한다.
- removal은 decommission policy가 설계될 때까지 금지한다.

### Decommission Confusion

위험:

- decommission이 없는데 removal sample을 제공하면 future implementation이 자동 삭제를 구현할 수 있다.

정책:

- marker contract는 removal forbidden을 명시한다.
- decommission은 별도 future design이다.

## Dry-run Mapping Risks

### Marker State Collapse

위험:

- marker state를 valid/missing 정도로만 표현하면 duplicated와 corrupted의 복구 방식이 사라진다.

정책:

- dry-run marker integrity는 `valid`, `missing`, `duplicated`, `corrupted`, `not-expected`, `unknown`을 유지한다.
- result item에는 `problems` 배열을 포함한다.

### Wrong Action Mapping

위험:

- `marker.missing`을 항상 create로 처리하거나 `marker.corrupted`를 drift-stop으로 처리하면 복구 경로가 틀어진다.

정책:

- marker structural failure는 conflict이다.
- hash mismatch만 drift-stop이다.
- first-create policy가 명확한 marker missing만 create candidate이다.

## Envelope v2 Risks

### Line Number Loss

위험:

- message에 line이 없으면 사용자가 marker를 찾기 어렵다.

정책:

- parser output은 begin_line과 end_line을 보존해야 한다.
- envelope v2 message `line`은 가능한 경우 begin_line을 사용한다.

### Code Vocabulary Drift

위험:

- marker parser code와 dry-run stop_reason code가 다르면 consumer가 중복 처리해야 한다.

정책:

- marker failure code는 stop policy와 동일하게 `marker-missing`, `marker-duplicated`, `marker-corrupted`를 사용한다.

## Observability Risks

### Event Detail Insufficiency

위험:

- future event가 marker state를 자세히 담지 않으면 trace만 보고 stop 이유를 알 수 없다.

정책:

- marker event detail은 `entry_id`, `target_path`, `begin_line`, `end_line`, `integrity`, `problems`를 포함해야 한다.
- event emission은 opt-in이며 persistence, telemetry, networking을 암시하지 않는다.

## Non-goal Risks

Marker contract가 다음 구현으로 오해되면 안 된다.

- parser implementation
- file mutation
- auto marker repair
- decommission
- rollback
- force
- sync execution
- manifest persistence
- adapter generation
- auto-fix
- source mutation

완화:

- 문서에 read-only boundary를 반복 명시한다.
- removal forbidden과 auto repair 금지를 명시한다.
- parser expectation은 implementation requirement가 아니라 future contract로 표현한다.

## 감사 결론

managed block marker는 mixed-boundary safety의 최소 경계이다. 안전한 future sync를 위해 marker contract는 느슨한 convenience보다 보수적인 fail-closed 동작을 우선해야 한다.

권장 결론:

- canonical marker는 line-oriented begin/end pair이다.
- `entry_id`와 `marker_version`은 필수이다.
- same `entry_id`는 exactly one pair만 허용한다.
- code fence 내부 marker-looking text는 기본적으로 무시한다.
- marker line은 managed block hash에서 제외한다.
- marker integrity는 hash comparison보다 먼저 검사한다.
- insertion은 explicit anchor가 있을 때만 create candidate이다.
- update는 marker valid와 target hash match가 모두 필요하다.
- removal은 decommission policy 전까지 금지한다.
