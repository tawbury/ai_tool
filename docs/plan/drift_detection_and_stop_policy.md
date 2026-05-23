# Drift Detection and Stop Policy

## 개요

이 문서는 `.ai OS` Phase 6에서 future sync/manifest 기능을 구현하기 전에 필요한 drift detection, conflict classification, stop policy를 정의한다.

현재 시스템은 read-only이다. 이 문서는 future behavior의 안전 계약이며, sync 실행, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation을 구현하지 않는다.

## 목표

### Destructive Overwrite 방지

미래 sync는 target이 변경되었거나 ownership이 불명확할 때 자동으로 덮어쓰면 안 된다.

원칙:

- drift 감지 시 기본 행동은 stop이다.
- conflict 자동 해결은 금지한다.
- force 정책은 future explicit opt-in으로만 허용한다.

### User-owned Content 보존

사용자 소유 영역은 sync 대상이 아니다.

원칙:

- `user-owned` target은 write 후보가 될 수 없다.
- `mixed-boundary` target에서는 managed block 내부만 future write 후보가 될 수 있다.
- marker 외부 content는 비교 대상이 될 수 있어도 수정 대상이 아니다.

### Managed Boundary Integrity 보존

managed block marker가 불명확하면 future sync는 target을 안전하게 해석할 수 없다.

원칙:

- begin/end marker pair는 정확히 하나여야 한다.
- marker의 `entry_id`는 manifest entry와 일치해야 한다.
- marker 손상, 중복, 누락은 blocking conflict이다.

### Deterministic Dry-run 보장

같은 source, target, manifest input은 같은 dry-run result를 만들어야 한다.

원칙:

- 비교 순서를 고정한다.
- action, severity, stop_reason, recovery_hint를 안정적으로 산출한다.
- dry-run은 쓰기를 수행하지 않는다.

## Drift Comparison Model

미래 dry-run은 entry별로 다음 순서로 비교한다.

### 1. Manifest Entry Validation

확인 항목:

- `entry_id`
- `source_path` 또는 `source_paths`
- `target_path`
- `source_hash`
- `target_hash`
- `ownership`
- `sync_mode`

실패 예:

- 필수 필드 누락
- 지원하지 않는 ownership
- 지원하지 않는 sync_mode

기본 결과:

- action: `conflict`
- severity: `blocking`
- stop_reason: `manifest-entry-invalid`

### 2. Source Hash Comparison

확인 항목:

- source path 존재 여부
- 현재 source hash
- manifest의 expected source hash
- future source bundle hash

상태:

- source 존재 및 hash 일치: 계속 진행
- source 존재 및 hash 변경: source changed로 기록하고 target 상태 평가 계속
- source 없음: `source-missing`

source hash 변경은 그 자체로 항상 conflict는 아니다. source가 변경된 경우 clean target이면 update 후보가 될 수 있다.

### 3. Target Existence Comparison

확인 항목:

- target path 존재 여부
- target ownership
- sync_mode

상태:

- target 없음: `missing`
- target 있음: 다음 단계 진행
- target이 manifest 없이 존재: `unmanaged-target`

### 4. Marker Integrity Comparison

`mixed-boundary` 또는 `managed-block` mode에서 확인한다.

확인 항목:

- begin marker 존재
- end marker 존재
- begin/end marker `entry_id` 일치
- manifest entry_id와 marker entry_id 일치
- 동일 entry_id marker 중복 여부
- marker nesting 또는 overlap 여부

실패 상태:

- `marker-missing`
- `marker-duplicated`
- `marker-corrupted`

marker integrity 실패는 blocking이다.

### 5. Managed Block Hash Comparison

`mixed-boundary` 또는 `managed-block` mode에서 managed block 내부 content를 비교한다.

확인 항목:

- 현재 managed block hash
- manifest target_hash
- future generated managed content hash

상태:

- 현재 managed hash가 manifest target_hash와 일치: clean
- 현재 managed hash가 manifest target_hash와 다름: `target-modified`
- generated hash가 현재 managed hash와 같음: skip 후보
- generated hash가 다르고 target clean: update 후보

### 6. Whole Target Hash Comparison

`runtime-managed` 또는 `whole-file` mode에서 target 전체를 비교한다.

확인 항목:

- 현재 target hash
- manifest target_hash
- future generated target hash

상태:

- 현재 target hash가 manifest target_hash와 일치: clean
- 현재 target hash가 manifest target_hash와 다름: `target-modified`

## Drift Severity Levels

| Severity | 의미 | 기본 처리 |
|---|---|---|
| `informational` | 쓰기 안전성에 직접 영향 없음 | report only |
| `warning` | 주의가 필요하지만 기본 dry-run은 계속 가능 | warn and continue |
| `blocking` | 안전한 쓰기 판단 불가 또는 user content 위험 | drift-stop or conflict |

## Conflict Taxonomy

| Conflict code | Severity | 의미 | 기본 action |
|---|---|---|---|
| `marker-missing` | blocking | expected managed marker가 없음 | `conflict` |
| `marker-duplicated` | blocking | 같은 entry marker가 여러 개 있음 | `conflict` |
| `marker-corrupted` | blocking | begin/end 불일치, nesting, malformed marker | `conflict` |
| `target-modified` | blocking | target managed 영역 또는 runtime-managed target이 manifest hash와 다름 | `drift-stop` |
| `source-missing` | blocking | source path가 없음 | `conflict` |
| `ownership-violation` | blocking | user-owned 영역을 쓰기 후보로 판단하려 함 | `conflict` |
| `unmanaged-target` | warning | target은 있으나 manifest/marker ownership이 없음 | `skip` |
| `orphaned-managed-block` | warning | manifest entry 없이 managed marker가 존재 | `orphan-warning` |

## Default Stop Policy

### Always Stop

다음 상태는 future write를 반드시 중단한다.

| State | Action | Stop reason |
|---|---|---|
| marker missing for managed-block entry | `conflict` | `marker-missing` |
| duplicated marker | `conflict` | `marker-duplicated` |
| corrupted marker | `conflict` | `marker-corrupted` |
| target modified since manifest | `drift-stop` | `target-modified` |
| source missing | `conflict` | `source-missing` |
| ownership violation | `conflict` | `ownership-violation` |
| invalid manifest entry | `conflict` | `manifest-entry-invalid` |

### Allow Create

다음 상태는 dry-run에서 `create` 후보가 될 수 있다.

| State | 조건 |
|---|---|
| target missing | ownership이 `runtime-managed`이고 policy가 whole-file create를 허용 |
| managed block missing in existing mixed-boundary target | insertion anchor가 명확하고 policy가 block create를 허용 |

주의:

- marker missing이 항상 create는 아니다.
- expected existing managed block이 사라진 경우는 conflict가 기본이다.
- 최초 생성인지 기존 managed block 손실인지 manifest entry와 policy로 구분해야 한다.

### Allow Update

다음 상태는 dry-run에서 `update` 후보가 될 수 있다.

| State | 조건 |
|---|---|
| clean target, source changed | 현재 target hash가 manifest target_hash와 일치 |
| clean managed block, generated content changed | marker integrity 통과 및 managed block hash 일치 |

### Warn Only

다음 상태는 기본적으로 쓰기를 하지 않고 경고만 한다.

| State | Action |
|---|---|
| unmanaged target | `skip` |
| orphaned managed block | `orphan-warning` |
| source hash changed but target unchanged | `update` 후보가 될 수 있으나 dry-run에서 명확히 표시 |

## Future Force Policy Boundary

Force는 Phase 6에서 구현하지 않는다. 미래 설계 시 다음 제한을 반드시 적용해야 한다.

- force는 explicit opt-in이어야 한다.
- force는 기본값이 될 수 없다.
- force는 conflict taxonomy별로 허용 범위를 따로 정의해야 한다.
- force는 user-owned content를 덮어쓸 수 없다.
- force는 marker-corrupted, marker-duplicated, ownership-violation을 자동 해결하면 안 된다.
- force 사용 시 dry-run과 사용자 확인이 선행되어야 한다.
- force는 rollback precondition이 없으면 허용하면 안 된다.

금지:

- implicit overwrite
- automatic conflict resolution
- automatic marker repair
- automatic merge
- background reconciliation

## Mixed-boundary Protection Rules

`mixed-boundary`는 가장 주의해야 하는 ownership이다.

규칙:

1. Marker 외부 content는 절대 future write 대상이 아니다.
2. Marker 외부 content hash 변경은 기본적으로 informational이다.
3. Marker 내부 content hash 변경은 manifest target_hash와 비교해 drift를 판정한다.
4. begin/end marker가 정확히 하나의 pair가 아니면 blocking conflict이다.
5. marker가 target file 안에서 overlap되거나 nested되면 `marker-corrupted`이다.
6. marker entry_id가 manifest entry_id와 다르면 `marker-corrupted`이다.
7. managed block removal은 기본 금지이며, decommission policy가 별도로 필요하다.

## Future Dry-run Reporting Expectations

Dry-run result item은 다음 필드를 포함해야 한다.

```json
{
  "entry_id": "entry_codex_root_adapter_rules",
  "action": "drift-stop",
  "severity": "blocking",
  "stop_reason": "target-modified",
  "recovery_hint": "Review the target managed block and regenerate the manifest only after confirming the change is intentional.",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "drift_state": "drifted",
  "details": {
    "expected_target_hash": "sha256:<manifest>",
    "actual_target_hash": "sha256:<current>"
  }
}
```

필수 기대 필드:

- `action`
- `severity`
- `stop_reason`
- `recovery_hint`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `drift_state`

## Recovery Hints

| Stop reason | Recovery hint |
|---|---|
| `marker-missing` | Confirm whether this is first creation or accidental marker removal. Do not write until ownership is clear. |
| `marker-duplicated` | Remove ambiguity manually or split entries before sync can proceed. |
| `marker-corrupted` | Repair marker boundaries manually after review. |
| `target-modified` | Review target changes and update manifest only after confirming intent. |
| `source-missing` | Restore source or remove the manifest entry through an explicit decommission path. |
| `ownership-violation` | Change ownership policy or remove the entry; do not write user-owned content. |
| `manifest-entry-invalid` | Fix manifest schema before evaluating sync. |

## Envelope v2 Compatibility

Future dry-run output should map to envelope v2.

Mapping:

- `command`: `sync`
- `status`: `fail` if any blocking conflict exists, `warn` if only warnings exist, `pass` if all clean or skipped safely
- `target`: repository or manifest path
- `summary`: action and severity counts
- `messages`: conflict, drift-stop, orphan-warning, unmanaged-target messages
- `payload.results`: dry-run result items
- `meta`: `dry_run: true`, manifest version, optional trace id

## Observability Event Compatibility

Future event taxonomy should include:

| Event type | Trigger |
|---|---|
| `runtime.sync.drift_check_started` | drift comparison begins |
| `runtime.sync.marker_checked` | marker integrity checked |
| `runtime.sync.drift_detected` | target hash mismatch found |
| `runtime.sync.conflict_detected` | blocking conflict found |
| `runtime.sync.stop_required` | stop policy selected |
| `runtime.sync.dry_run_result_emitted` | dry-run item emitted |

Events must be opt-in and must not imply persistence or networking.

## Activation v1 Compatibility

Activation v1 may narrow future sync planning inputs, but it must not bypass drift-stop policy.

Rules:

- activation active sets do not override ownership.
- activation rule sets do not authorize target writes.
- loader profile overrides do not affect sync drift detection.
- activation-driven sync requires a separate future design.

## Explicit Non-goals

This policy does not implement:

- real sync execution
- manifest persistence
- file mutation
- adapter generation
- auto merge
- automatic conflict resolution
- rollback implementation
- background reconciliation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source mutation

## Phase 7 Gate

Phase 7 implementation must not start until this policy is promoted into runtime-facing rules and validated against manifest and dry-run schema examples.
