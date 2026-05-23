# Managed Block Parser Risk Audit

## 개요

이 문서는 future managed block parser와 insertion anchor 계약의 위험을 감사한다. 목적은 Phase 7 `aios sync --dry-run` 구현 전에 parser가 판단해야 할 것과 판단하면 안 되는 것을 분리하고, fixture coverage로 fail-closed 동작을 보장하는 것이다.

현재 시스템은 read-only이다. 이 감사는 parser implementation, sync execution, manifest persistence, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## 감사 범위

감사 대상:

- marker detection ambiguity
- begin/end pairing failure
- duplicate marker handling
- nested marker handling
- malformed marker handling
- code fence false positive
- orphan marker handling
- insertion anchor ambiguity
- first-create misclassification
- parser responsibility creep
- drift-stop boundary confusion

## Risk Matrix

| Risk | 영향 | 완화 |
|---|---|---|
| code fence marker-looking text를 실제 marker로 인식 | 문서 예시가 managed block으로 오인됨 | fenced code block exclusion fixture |
| duplicate marker를 하나만 선택 | 잘못된 block update | duplicate는 conflict |
| nested marker 허용 | managed boundary 오판 | nested는 corrupted conflict |
| malformed marker를 부분 파싱 | user-owned content 침범 | malformed는 conflict |
| marker missing을 create로 오판 | 삭제된 marker를 자동 복구 | first-create policy와 anchor 필요 |
| anchor-looking line만으로 create 허용 | unmanaged target 침범 | manifest entry와 ownership 필요 |
| parser가 hash drift를 판단 | 책임 혼합 | parser는 structure만 보고, hash layer가 drift-stop 판단 |
| orphan marker 자동 삭제 | user intent 손상 | orphan-warning only |

## Marker Detection Risk

### Risk

Parser가 너무 느슨하면 일반 주석, 문서 예시, code block 안 text를 marker로 오인할 수 있다.

### Mitigation

- supported marker style을 명시한다.
- marker line은 `AIOS:BEGIN`, `AIOS:END`, `managed-block` token을 모두 포함해야 한다.
- required attributes는 `entry_id`, `marker_version`이다.
- fenced code block 안 marker-looking text는 기본적으로 무시한다.

## Pairing Risk

### Risk

Begin/end marker를 line order만으로 느슨하게 pairing하면 mismatched entry 또는 reversed marker가 valid로 처리될 수 있다.

### Mitigation

- begin/end `entry_id` 일치 필수.
- begin/end `marker_version` 일치 필수.
- begin line은 end line보다 앞서야 한다.
- mismatch, reversed, missing side는 conflict이다.

## Duplicate Marker Risk

### Risk

같은 `entry_id`가 여러 block에 나타나면 어떤 block이 authoritative한지 결정할 수 없다.

### Mitigation

- same `entry_id`는 exactly one pair만 허용한다.
- duplicate begin 또는 duplicate end는 conflict이다.
- parser가 임의로 첫 번째 또는 마지막 marker를 선택하면 안 된다.

## Nested and Overlap Risk

### Risk

Nested marker는 inner block과 outer block의 ownership boundary를 섞는다. Overlap은 content span을 안정적으로 계산할 수 없게 만든다.

### Mitigation

- nested marker는 `marker-corrupted`.
- overlapped marker는 `marker-corrupted`.
- nested flag와 problem code를 output에 남긴다.

## Malformed Marker Risk

### Risk

Malformed marker를 partial parse하면 entry_id나 marker_version이 없는 상태에서도 managed boundary로 취급될 수 있다.

### Mitigation

- malformed syntax는 `marker-malformed`.
- parser는 repair를 시도하지 않는다.
- dry-run action은 conflict이다.

## Code Fence Risk

### Risk

Phase 6/7 문서 자체가 marker examples를 포함한다. Parser가 fenced code block 안 marker-looking text를 실제 marker로 읽으면 docs가 sync target이 되었을 때 false positive가 발생한다.

### Mitigation

- Markdown fenced code block exclusion을 parser responsibility로 둔다.
- fixture에 fenced marker-looking text를 포함한다.
- unclosed fence 정책은 구현 전 명시해야 한다. 기본 권장값은 fail closed 또는 marker candidate ignore이다.

## Orphan Risk

### Risk

Manifest에 없는 marker를 발견했을 때 parser 또는 dry-run이 자동 삭제를 계획하면 user intent를 손상할 수 있다.

### Mitigation

- orphan marker는 warning only.
- action은 `orphan-warning`.
- auto-removal은 non-goal.
- decommission policy 전까지 orphan은 report only이다.

## Insertion Anchor Risk

### Missing Anchor

Risk:

- target이 존재하는 mixed-boundary file에 anchor 없이 marker를 삽입하면 user-owned content 위치를 침범할 수 있다.

Mitigation:

- target exists + first-create managed block requires anchor.
- missing anchor is blocking conflict `anchor-missing`.

### Duplicate Anchor

Risk:

- 같은 `entry_id` anchor가 여러 개 있으면 insertion 위치가 불명확하다.

Mitigation:

- duplicate same entry anchor is blocking conflict `anchor-duplicated`.
- parser must not choose one.

### Anchor in Code Fence

Risk:

- documentation example anchor가 실제 insertion point로 오인될 수 있다.

Mitigation:

- code fence 안 anchor-looking text는 무시하거나 conflict detail로만 보고한다.
- valid anchor는 fence 밖에 있어야 한다.

### Unmanaged Target Anchor

Risk:

- unmanaged file에 사용자가 쓴 anchor-looking line이 있으면 sync가 managed block creation candidate로 오판할 수 있다.

Mitigation:

- manifest entry required.
- ownership must allow managed block insertion.
- first-create policy required.
- unmanaged target remains warning/skip, not create.

## First-create Misclassification Risk

### Risk

Expected existing marker가 missing인 상태와 initial create 상태가 구분되지 않으면 accidental marker deletion을 create candidate로 오판할 수 있다.

### Mitigation

First-create requires:

- manifest entry explicitly allows first-create.
- target_hash null is allowed by first-create policy.
- no existing marker for same entry exists.
- anchor exists when target file exists.
- ownership and sync_mode are compatible.

Any ambiguity becomes conflict.

## Parser Responsibility Creep Risk

### Risk

Parser가 marker insertion, hash comparison, drift-stop, repair, mutation까지 담당하면 safety boundary가 흐려진다.

### Mitigation

Parser responsibility:

- detect marker facts.
- preserve line numbers.
- report structural integrity and problems.

Parser non-responsibility:

- marker insertion.
- marker repair.
- hash comparison.
- action emission.
- file mutation.

## Drift-stop Boundary Risk

### Risk

Parser structural failures and content hash drift를 모두 drift-stop으로 처리하면 복구 방식이 혼동된다.

### Mitigation

- parser structural failure -> `conflict`.
- valid marker + hash mismatch -> `drift-stop`.
- parser invalid state에서는 hash-based update candidate를 만들지 않는다.

## Fixture Coverage Risk

### Risk

Happy-path fixture만 있으면 fail-closed behavior가 구현되지 않을 수 있다.

### Mitigation

Required fixture categories:

- valid marker pair
- missing end marker
- duplicate begin marker
- duplicate end marker
- nested marker
- malformed marker
- mismatched entry_id
- unsupported marker version
- fenced code block marker-looking text
- multiple independent managed blocks
- unmanaged file
- valid anchor
- missing anchor
- duplicate anchor
- anchor inside code fence

## Validation Command Risk

### Risk

Future validation commands가 parser-only tests와 dry-run integration tests를 분리하지 않으면 failure source가 불명확하다.

### Mitigation

- parser unit tests should verify parser output model.
- dry-run tests should verify action/severity/stop_reason mapping.
- envelope tests should verify message/status mapping.

## Non-goal Risk

Parser fixture plan이 다음 구현을 허용하는 것으로 오해되면 안 된다.

- parser auto-repair
- marker rewrite
- marker insertion
- mutation
- sync apply
- manifest persistence
- rollback execution
- force
- decommission

완화:

- parser non-responsibilities를 명시한다.
- insertion anchor는 future dry-run candidate boundary일 뿐 write authorization이 아니라고 명시한다.

## 감사 결론

Managed block parser의 핵심 위험은 false positive와 ambiguous boundary이다. 따라서 parser는 느슨하게 복구하거나 추측하지 않고, structural ambiguity를 conflict로 보고해야 한다.

권장 결론:

- supported marker styles는 3개로 제한한다.
- same `entry_id`는 exactly one begin/end pair만 허용한다.
- code fence 안 marker-looking text는 marker가 아니다.
- marker structural failure는 conflict이다.
- hash mismatch만 drift-stop이다.
- insertion anchor는 first-create candidate의 필요조건일 뿐 충분조건이 아니다.
- parser implementation 전 fixture layout과 expected JSON을 먼저 작성해야 한다.
