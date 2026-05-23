# Drift Conflict Failure Mode Audit

## 개요

이 문서는 future `.ai OS` sync/manifest 기능에서 발생할 수 있는 drift와 conflict failure mode를 감사한다. 현재 시스템은 read-only이며, 이 감사는 mutation logic이 존재하기 전에 stop policy가 필요한 이유를 정리한다.

이번 감사는 구현이 아니다. sync execution, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation은 수행하지 않았다.

## 감사 범위

감사 대상 failure mode:

- source hash mismatch
- target hash mismatch
- managed block hash mismatch
- marker missing
- marker duplicated
- marker corrupted
- source missing
- ownership violation
- unmanaged target
- orphaned managed block
- force misuse
- mixed-boundary overwrite

## Failure Mode Matrix

| Failure mode | 위험 | 영향 | 권장 severity | 권장 action |
|---|---|---|---|---|
| source missing | source of truth 없음 | 잘못된 생성 또는 stale target 유지 | blocking | conflict |
| source changed | source hash 변경 | update 후보 발생 | informational 또는 warning | update candidate |
| target modified | user 또는 외부 도구 변경 가능성 | destructive overwrite 위험 | blocking | drift-stop |
| marker missing | managed boundary 식별 불가 | 잘못된 삽입 또는 덮어쓰기 위험 | blocking | conflict |
| marker duplicated | managed identity 모호 | 잘못된 block 업데이트 위험 | blocking | conflict |
| marker corrupted | begin/end 불일치 또는 malformed marker | parser 오판 위험 | blocking | conflict |
| ownership violation | user-owned 영역을 쓰기 후보로 판단 | user content 손실 | blocking | conflict |
| unmanaged target | manifest/marker가 없는 target | ownership 불명확 | warning | skip |
| orphaned managed block | manifest 없이 marker 존재 | stale managed content 방치 | warning | orphan-warning |
| force misuse | 명시 확인 없이 overwrite | destructive mutation | blocking | conflict |
| mixed-boundary overwrite | marker 외부 수정 | user content 손실 | blocking | conflict |

## Source Failure Modes

### Source Missing

상황:

- manifest entry가 `.ai/...` source를 가리키지만 파일이 없다.
- 여러 source bundle 중 일부가 없다.

위험:

- stale target을 정상으로 오판할 수 있다.
- 비어 있는 source로 target을 생성할 수 있다.

정책:

- blocking conflict.
- future sync는 쓰면 안 된다.
- recovery는 source 복구 또는 명시적 entry decommission이다.

### Source Changed

상황:

- source hash가 manifest source_hash와 다르다.

위험:

- target update가 필요할 수 있다.

정책:

- source 변경 자체는 conflict가 아니다.
- target이 clean이면 update candidate가 될 수 있다.
- target도 drifted이면 drift-stop이 우선한다.

## Target Failure Modes

### Target Modified

상황:

- 현재 target hash 또는 managed block hash가 manifest target_hash와 다르다.

위험:

- 사용자 또는 외부 도구가 target을 수정했을 수 있다.
- 자동 update는 사용자 변경을 덮어쓸 수 있다.

정책:

- blocking.
- action은 `drift-stop`.
- recovery는 변경 검토 후 manifest 갱신 또는 수동 복구다.

### Unmanaged Target

상황:

- target 파일은 존재하지만 manifest entry 또는 managed marker가 없다.

위험:

- ownership을 판단할 수 없다.

정책:

- warning.
- action은 `skip`.
- 자동 marker 삽입 금지.

## Marker Failure Modes

### Marker Missing

상황:

- manifest는 managed block을 기대하지만 target에 marker가 없다.

위험:

- 첫 생성인지, 사용자가 marker를 삭제했는지 구분이 필요하다.

정책:

- 기본은 blocking conflict.
- 최초 생성은 별도 create policy와 insertion anchor가 명확할 때만 후보가 될 수 있다.

### Marker Duplicated

상황:

- 같은 entry_id를 가진 begin/end marker가 여러 개 있다.

위험:

- 어떤 block을 갱신해야 하는지 결정할 수 없다.

정책:

- blocking conflict.
- 자동 선택 금지.

### Marker Corrupted

상황:

- begin marker만 있다.
- end marker만 있다.
- begin/end entry_id가 다르다.
- marker가 nested 또는 overlapped 되어 있다.
- marker syntax가 malformed 상태다.

위험:

- parser가 user-owned content를 managed block으로 오판할 수 있다.

정책:

- blocking conflict.
- 자동 repair 금지.

## Ownership Failure Modes

### Ownership Violation

상황:

- manifest ownership이 `user-owned`인데 create/update action이 산출된다.
- mixed-boundary target에서 marker 외부 content를 write 후보로 분류한다.
- whole-file update를 user-authored root adapter에 적용하려 한다.

위험:

- user-owned content 손실.

정책:

- blocking conflict.
- ownership policy를 수정하거나 entry를 제거해야 한다.

### Mixed-boundary Overwrite

상황:

- managed block 밖의 content가 generated output에 포함된다.
- generator가 target 전체를 재작성하려 한다.

위험:

- 사용자 메모, manual adapter note, tool-specific local setting 손실.

정책:

- blocking conflict.
- mixed-boundary에서는 marker 내부만 future write 대상이다.

## Orphan Failure Modes

### Orphaned Managed Block

상황:

- target에 AIOS managed marker가 있지만 manifest entry가 없다.

위험:

- 과거 sync 흔적 또는 수동 복사본일 수 있다.
- 자동 제거하면 사용자 의도를 훼손할 수 있다.

정책:

- warning.
- action은 `orphan-warning`.
- 자동 제거 금지.

## Force Misuse Failure Modes

Force policy는 future explicit opt-in 후보일 뿐이며 Phase 6에서는 구현하지 않는다.

위험:

- drift-stop 우회
- marker corruption 자동 repair
- user-owned content overwrite
- dry-run 없이 direct write

정책:

- force는 taxonomy별로 제한해야 한다.
- force는 rollback precondition이 없으면 허용하면 안 된다.
- marker duplicated/corrupted와 ownership violation은 force로 자동 해결하면 안 된다.

## Severity Audit

### Informational

예:

- source hash changed while target is clean
- user-owned target observed but not write candidate
- marker external content changed in mixed-boundary target

처리:

- report only 또는 update candidate 설명.

### Warning

예:

- unmanaged-target
- orphaned-managed-block
- disabled sync_mode entry observed

처리:

- skip 또는 orphan-warning.
- future write 없음.

### Blocking

예:

- target-modified
- marker-missing
- marker-duplicated
- marker-corrupted
- source-missing
- ownership-violation
- invalid manifest entry

처리:

- conflict 또는 drift-stop.
- future write 금지.

## Dry-run Reporting Risk

Dry-run이 충분한 복구 정보를 제공하지 않으면 사용자는 위험한 force를 선택할 가능성이 커진다.

필수 정보:

- action
- severity
- stop_reason
- recovery_hint
- source_path
- target_path
- ownership
- sync_mode
- expected/actual hash when available

## Compatibility Audit

### Envelope v2

Future sync dry-run은 envelope v2의 `messages`와 `payload.results`로 conflict를 표현할 수 있어야 한다.

권장:

- blocking conflict가 하나라도 있으면 status `fail`
- warning만 있으면 status `warn`
- 모두 clean/skip이면 status `pass`

### Observability Events

Future events는 drift 판단을 설명할 수 있어야 한다.

필요 event 후보:

- `runtime.sync.drift_detected`
- `runtime.sync.conflict_detected`
- `runtime.sync.stop_required`
- `runtime.sync.marker_checked`

이벤트는 opt-in이며 persistence나 networking을 의미하지 않는다.

### Activation v1

Activation v1은 source selection 후보일 수 있지만 drift policy를 우회할 수 없다.

주의:

- active_set은 ownership을 바꾸지 않는다.
- rule_sets는 write authority가 아니다.
- loader profile은 sync policy가 아니다.

## 결론

Drift와 conflict의 핵심 위험은 "target이 현재 안전하게 쓰기 가능한지"를 오판하는 데 있다. 따라서 future sync의 기본 정책은 보수적이어야 한다.

권장 결론:

- marker integrity failure는 conflict.
- target hash mismatch는 drift-stop.
- source missing은 conflict.
- unmanaged target은 skip.
- orphaned managed block은 warning.
- force는 explicit opt-in 설계 전까지 금지.
- mixed-boundary에서는 marker 내부만 future write 후보.

이 감사 결과는 Phase 6의 drift detection and stop policy 문서와 함께 Phase 7 구현 진입 전 runtime-facing rule 승격 후보가 된다.
