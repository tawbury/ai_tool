# Rollback Transaction Risk Audit

## 개요

이 문서는 `.ai OS` Phase 6에서 future rollback 및 transaction precondition이 필요한 이유와 실패 위험을 감사한다. 현재 시스템은 read-only이며, 이 감사는 rollback implementation, transaction persistence, sync execution, force, decommission, source mutation을 구현하지 않는다.

Rollback은 mutation 이후의 편의 기능이 아니라 mutation 이전에 보존되어야 하는 safety data의 결과이다. transaction evidence 없이 rollback을 수행하면 user-owned content를 덮어쓰거나, transaction 이후 변경을 잃거나, managed block boundary를 오판할 수 있다.

## 감사 범위

감사 대상:

- transaction log 부재
- pre-image 부재
- target post_hash mismatch
- marker boundary 손상
- ownership mismatch
- mixed-boundary 외부 content rollback 위험
- incomplete transaction
- rollback dry-run 생략
- envelope v2 message 손실
- observability event detail 부족

## Risk Matrix

| Risk | 영향 | 권장 완화 |
|---|---|---|
| transaction log 없음 | rollback 근거 없음 | rollback forbidden |
| pre-image 또는 patch 없음 | 원상 복구 불가 | mutation 전 pre-image 필수 |
| target이 post_hash와 다름 | transaction 이후 사용자 변경 손실 | rollback forbidden |
| marker corrupted | rollback 범위 오판 | marker integrity check 선행 |
| ownership mismatch | user-owned content 침범 | rollback forbidden |
| mixed-boundary whole-file rollback | marker 밖 content 손실 | marker 내부만 rollback |
| incomplete transaction | applied 여부 불명확 | entry status 기반 recovery 필요 |
| dry-run 없이 rollback | destructive rollback 위험 | rollback dry-run-first |
| force로 rollback 강행 | conflict 우회 | force non-goal |

## Transaction Log Risks

### Missing Transaction Log

위험:

- 어떤 content가 변경되었는지 알 수 없다.
- 어떤 manifest version과 entry가 사용되었는지 알 수 없다.
- rollback target이 실제로 AIOS가 만든 변경인지 검증할 수 없다.

정책:

- transaction log가 없으면 rollback은 금지한다.
- stop reason은 `transaction-log-missing`이다.

### Incomplete Transaction Log

위험:

- command가 중간에 실패했을 때 일부 entry는 적용되고 일부는 적용되지 않았을 수 있다.
- 전체 transaction status만으로는 entry별 복구 가능성을 판단할 수 없다.

정책:

- transaction entry별 `status`가 필요하다.
- applied entry만 rollback candidate가 될 수 있다.
- status가 불명확하면 `transaction-incomplete`로 rollback forbidden이다.

### Log Tampering or Drift

위험:

- transaction log가 수정되면 pre_hash, post_hash, target_path 신뢰성이 깨진다.

정책:

- future transaction log validation이 필요하다.
- Phase 6에서는 persistence를 구현하지 않지만, schema에는 hash와 identity를 충분히 남겨야 한다.

## Pre-image Risks

### Missing Pre-image

위험:

- rollback 대상 content를 재구성할 수 없다.
- source에서 다시 생성한 content가 transaction 당시 pre-image와 같다고 보장할 수 없다.

정책:

- mutation entry는 `pre_content_ref` 또는 `pre_patch_ref`를 가져야 한다.
- 둘 다 없으면 `preimage-missing`이다.

### Patch-only Ambiguity

위험:

- reversible patch가 현재 target에 적용 가능한지 판단하기 어렵다.
- patch context가 drifted target에 잘못 적용될 수 있다.

정책:

- patch rollback도 target `post_hash` match가 필요하다.
- patch format은 future design에서 별도 검증해야 한다.

## Target Drift Risks

### Target Changed After Transaction

위험:

- transaction 이후 사용자가 target을 수정했는데 rollback이 이를 덮어쓸 수 있다.

정책:

- rollback 시점의 target hash는 transaction `post_hash`와 일치해야 한다.
- 일치하지 않으면 `target-changed-after-transaction`으로 forbidden이다.

### Whole-file vs Managed-block Hash Confusion

위험:

- mixed-boundary target에서 whole-file hash를 rollback 기준으로 삼으면 marker 밖 user-owned content 변경이 rollback을 막거나, 반대로 rollback 대상이 될 수 있다.

정책:

- mixed-boundary rollback은 managed block hash 기준이다.
- runtime-managed whole-file만 whole target hash 기준이다.

## Marker Boundary Risks

### Marker Missing After Transaction

위험:

- rollback할 managed block 범위가 사라진다.

정책:

- marker missing은 rollback forbidden이다.
- stop reason은 `marker-invalid-after-transaction`이다.

### Marker Corrupted After Transaction

위험:

- rollback 범위가 user-owned content까지 확장될 수 있다.

정책:

- marker corrupted, duplicated, nested, mismatched는 모두 rollback forbidden이다.
- marker repair는 auto-fix가 아니며 Phase 6 non-goal이다.

### Marker Moved

위험:

- marker line number가 바뀌었지만 entry_id와 content hash가 유지될 수 있다.
- line movement 자체는 반드시 위험하지 않지만, boundary integrity는 다시 확인해야 한다.

정책:

- rollback은 line number 자체보다 marker identity와 boundary validity를 우선한다.
- event와 message에는 current line number를 기록해야 한다.

## Ownership Risks

### Ownership Mismatch

위험:

- transaction 당시 mixed-boundary였던 target이 현재 user-owned로 정책 변경되었을 수 있다.
- rollback이 현재 ownership boundary를 침범할 수 있다.

정책:

- current ownership과 transaction ownership이 rollback-compatible해야 한다.
- mismatch는 `ownership-mismatch`로 forbidden이다.

### User-owned Boundary Rollback

위험:

- whole-file pre-image를 mixed-boundary target에 적용하면 marker 밖 content가 과거로 되돌아간다.

정책:

- mixed-boundary rollback은 marker 내부만 대상으로 한다.
- marker 밖 content를 바꾸는 rollback plan은 `user-owned-boundary-risk`이다.

## Dry-run Risks

### Rollback Without Dry-run

위험:

- rollback은 sync만큼 destructive할 수 있다.
- 사용자가 어떤 entry가 되돌아가는지 확인하지 못한다.

정책:

- rollback도 dry-run-first이다.
- rollback dry-run은 candidate와 forbidden case를 machine-readable하게 출력해야 한다.

### Vocabulary Divergence

위험:

- sync dry-run과 rollback dry-run이 서로 다른 action/status vocabulary를 쓰면 automation이 복잡해진다.

정책:

- top-level status는 `pass`, `warn`, `fail`을 유지한다.
- forbidden rollback은 blocking message와 `fail`이다.
- marker, ownership, hash stop reason은 기존 drift/dry-run vocabulary와 최대한 공유한다.

## Force Risks

### Force Over Rollback Preconditions

위험:

- force rollback은 transaction 이후 사용자 변경을 덮어쓸 수 있다.
- marker corruption을 무시하면 user-owned content가 손실될 수 있다.

정책:

- force는 Phase 6 non-goal이다.
- rollback forbidden case를 force로 우회하는 정책은 별도 future design 없이는 금지한다.

## Decommission Risks

### Rollback vs Decommission Confusion

위험:

- rollback은 이전 transaction을 되돌리는 것이고 decommission은 managed ownership을 종료하는 것이다.
- 둘을 혼동하면 orphan marker 삭제나 managed block removal을 rollback으로 처리할 수 있다.

정책:

- decommission은 non-goal이다.
- rollback은 transaction log에 기록된 applied mutation만 대상으로 한다.

## Envelope v2 Risks

### Missing Message Details

위험:

- rollback forbidden 이유가 payload 안에만 있고 messages에 없으면 client가 위험을 놓칠 수 있다.

정책:

- forbidden rollback은 envelope v2 message를 생성해야 한다.
- message details에는 `transaction_id`, `entry_id`, `target_path`, `stop_reason`이 있어야 한다.

### Status Ambiguity

위험:

- 일부 rollback candidate가 가능하고 일부가 forbidden일 때 전체 status가 모호할 수 있다.

정책:

- forbidden이 하나라도 있으면 top-level status는 `fail`이다.
- warnings only면 `warn`.
- candidates only면 `pass`.

## Observability Risks

### Event Trail Gaps

위험:

- transaction과 rollback precondition failure가 trace에 남지 않으면 사고 후 원인 분석이 어렵다.

정책:

- future opt-in events는 transaction lifecycle과 rollback precondition failure를 표현해야 한다.
- events는 persistence, telemetry, networking을 암시하지 않는다.

권장 event detail:

- `transaction_id`
- `entry_id`
- `target_path`
- `pre_hash`
- `post_hash`
- `actual_hash`
- `stop_reason`
- `marker.integrity`

## Non-goal Risks

이 문서가 다음 구현으로 오해되면 안 된다.

- rollback implementation
- transaction persistence implementation
- transaction log writing
- actual sync execution
- force
- decommission
- adapter generation
- auto-fix
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- source mutation

완화:

- schema는 candidate로 표현한다.
- persistence와 execution은 명시적으로 non-goal로 둔다.
- rollback은 future precondition policy로만 정의한다.

## 감사 결론

Rollback safety는 mutation 이전에 결정된다. transaction log, pre-image, post_hash validation, marker boundary validation이 없으면 rollback은 안전한 복구가 아니라 또 다른 destructive write가 된다.

권장 결론:

- future mutation은 transaction evidence 없이는 허용하지 않는다.
- rollback은 transaction log와 pre-image가 있을 때만 candidate가 된다.
- target이 transaction 이후 변경되면 rollback은 금지한다.
- mixed-boundary rollback은 marker 내부만 대상으로 한다.
- marker corrupted, ownership mismatch, user-owned boundary risk는 rollback forbidden이다.
- rollback도 dry-run-first 정책을 따른다.
