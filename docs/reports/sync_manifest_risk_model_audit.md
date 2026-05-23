# Sync Manifest Risk Model Audit

## 개요

이 문서는 `.ai OS` Phase 6 Sync/Manifest Safety Design을 위한 위험 모델을 감사한다. 현재 시스템은 read-only이며, 이 감사는 future sync 구현 전에 어떤 실패 모드를 막아야 하는지 정의한다.

이번 감사는 구현이 아니다. sync, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation은 수행하지 않았다.

## 감사 기준

Phase 6 safety design은 다음 위험을 먼저 통제해야 한다.

- source of truth 혼동
- user-owned content 손실
- drift 무시
- managed block marker 손상
- manifest와 실제 파일 상태 불일치
- rollback 불가능한 update
- dry-run과 실제 실행 결과 불일치
- sync 구현이 adapter generation이나 orchestration으로 확장되는 범위 초과

## 주요 위험 매트릭스

| 위험 | 심각도 | 발생 가능성 | 완화 설계 |
|---|---:|---:|---|
| user-owned content 덮어쓰기 | High | Medium | ownership model, mixed-boundary marker, non-destructive update policy |
| drifted target에 쓰기 | High | Medium | target_hash 비교, default drift-stop |
| managed block marker 중복 또는 손상 | High | Medium | conflict action, 쓰기 중단 |
| manifest stale state | High | Medium | source_hash/target_hash, generated_at, dry-run 재평가 |
| orphaned managed block 방치 | Medium | Medium | orphan-warning action |
| source bundle 재현 불가 | Medium | Medium | source_path/source_paths와 source_hash 기록 |
| rollback 불가 | High | Medium | rollback precondition, transaction log future requirement |
| dry-run 결과와 실제 update divergence | High | Medium | Phase 7 전 dry-run contract 고정 |
| activation을 sync selection으로 오해 | Medium | Medium | activation compatibility boundary 명시 |
| event/trace가 persistence로 오해 | Low | Medium | observability opt-in, no persistence boundary |

## Source of Truth Risk

`.ai/`는 runtime source of truth이다. 미래 sync는 `.ai` source를 target에 반영할 수 있지만, target을 source of truth로 승격해서는 안 된다.

위험:

- target adapter 파일이 canonical rule source처럼 사용됨
- manifest가 `.ai` source보다 우선권을 가진다고 오해됨
- user-owned target edits가 `.ai`로 역전파된다고 오해됨

완화:

- manifest는 state record이지 source of truth가 아니다.
- sync는 one-way 후보로만 설계한다.
- reverse sync는 별도 설계 없이는 금지한다.

## Ownership Risk

미래 sync의 가장 큰 위험은 사람이 작성한 내용을 managed output이 덮어쓰는 것이다.

위험 상태:

- root adapter에 사용자 메모가 포함된 경우
- target 파일에 managed block과 user-owned content가 공존하는 경우
- marker가 손상되어 managed 영역을 잘못 식별하는 경우

완화:

- `runtime-managed`, `user-owned`, `mixed-boundary` ownership을 명시한다.
- user-owned는 쓰기 대상이 아니다.
- mixed-boundary는 marker 내부만 update 후보가 된다.
- marker가 불명확하면 conflict로 멈춘다.

## Drift Detection Risk

drift를 무시하면 사용자의 의도적 수정 또는 외부 도구 변경을 덮어쓸 수 있다.

필수 drift state:

- `clean`
- `drifted`
- `missing`
- `orphaned`
- `unmanaged`

기본 정책:

- `clean`: update 후보 가능
- `drifted`: drift-stop
- `missing`: policy에 따라 create 또는 conflict
- `orphaned`: orphan-warning
- `unmanaged`: skip

## Managed Block Risk

managed block은 mixed-boundary 안전성의 핵심이다.

위험:

- begin marker만 존재
- end marker만 존재
- 같은 entry_id marker가 여러 개 존재
- marker 안 content는 수정됐지만 manifest가 모름
- marker 밖 content를 generator가 수정함

완화:

- begin/end marker pair를 엄격히 검사한다.
- entry_id 중복은 conflict로 처리한다.
- marker 내부 hash가 manifest target_hash와 다르면 drift-stop.
- marker 외부 content는 update 대상에서 제외한다.

## Manifest Integrity Risk

manifest가 오래되거나 불완전하면 future sync가 잘못된 판단을 할 수 있다.

위험:

- source_hash가 실제 source와 다름
- target_hash가 현재 target과 다름
- generated_at만 있고 generator identity가 없음
- entry_id가 불안정함

완화:

- source_hash와 target_hash를 모두 필수로 둔다.
- generated_by를 필수로 둔다.
- entry_id는 stable derivation을 사용한다.
- manifest 자체도 future validate 대상이 되어야 한다.

## Dry-run Risk

dry-run은 future sync의 safety gate이다. dry-run이 불명확하면 실제 sync 구현이 위험해진다.

필수 action:

- `create`
- `update`
- `skip`
- `conflict`
- `drift-stop`
- `orphan-warning`

완화:

- 모든 action은 reason과 target을 가져야 한다.
- conflict와 drift-stop은 쓰기 금지 상태로 간주한다.
- dry-run summary는 action별 count를 제공한다.
- future envelope v2 mapping을 유지한다.

## Rollback Risk

Rollback은 구현하지 않지만, rollback 불가능한 update는 설계 단계에서 배제해야 한다.

위험:

- 이전 target 상태가 기록되지 않음
- mixed-boundary 파일 전체를 rollback해 user-owned content를 되돌림
- transaction log 없이 부분 update가 실패함

완화:

- rollback은 Phase 7 전 transaction log 설계가 필요하다.
- rollback 대상은 managed block 내부 또는 runtime-managed file로 제한한다.
- rollback도 dry-run first여야 한다.

## Activation Compatibility Risk

Activation v1은 active set과 loader profile을 선언한다. 이를 sync selection으로 바로 해석하면 범위가 커진다.

위험:

- activation active_set을 adapter generation 대상으로 오해
- loader profile override를 sync behavior로 오해
- activation file을 자동 수정하려는 구현 유혹

완화:

- activation은 future sync input 후보일 뿐이다.
- activation-driven sync는 별도 설계 없이는 금지한다.
- loader profile은 context loading policy이지 sync policy가 아니다.

## Observability Risk

Future event trace는 sync 판단의 설명력을 높일 수 있지만, persistence나 telemetry로 확장되면 현재 boundary를 벗어난다.

완화:

- event emission은 opt-in 후보로만 둔다.
- event persistence와 networking은 명시적 non-goal로 유지한다.
- dry-run result는 event stream 없이도 완전해야 한다.

## Phase 6 Safety Recommendations

1. Manifest schema와 dry-run schema를 별도 문서로 먼저 안정화한다.
2. managed block marker contract를 sample 중심으로 검증한다.
3. drift-stop을 기본 정책으로 고정한다.
4. user-owned content는 자동 변경 금지로 둔다.
5. Phase 7 구현 전 transaction log와 rollback precondition을 별도로 설계한다.

## Phase 7 진입 차단 조건

다음 중 하나라도 남아 있으면 Phase 7 구현에 진입하면 안 된다.

- dry-run schema 미확정
- managed block marker 불안정
- ownership model 미정
- drift-stop policy 미정
- rollback precondition 미정
- manifest validation 전략 부재
- inspect 또는 validate baseline 실패

## 결론

Phase 6은 시작 가능하지만, 구현이 아니라 안전 계약 설계로 제한되어야 한다. sync/manifest의 핵심 위험은 파일 쓰기 자체보다 ownership, drift, rollback 불명확성에서 발생한다.

따라서 future sync 구현은 dry-run, manifest integrity, managed block boundary, drift-stop, rollback precondition이 문서와 검증으로 고정된 뒤에만 검토해야 한다.
