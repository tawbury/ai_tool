# Rollback Transaction Precondition Policy

## 개요

이 문서는 `.ai OS` Phase 6에서 future sync mutation 이전에 필요한 rollback 및 transaction safety precondition을 정의한다. 현재 시스템은 read-only이며, 이 문서는 transaction log persistence나 rollback execution 구현이 아니라 향후 mutation command가 만족해야 할 안전 계약이다.

이 문서는 sync execution, manifest persistence, transaction logs, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Rollback이 나중에 붙을 수 없는 이유

Rollback은 mutation 이후에 덧붙이는 보조 기능이 아니다. 어떤 변경을 되돌릴 수 있으려면 변경 전에 이미 다음 정보가 보존되어 있어야 한다.

- 변경 전 target hash
- 변경 후 target hash
- 변경 전 content 또는 reversible patch
- managed block marker boundary
- ownership 및 sync mode
- user-owned content와 managed content의 경계
- transaction identity와 entry별 상태

이 정보 없이 mutation이 먼저 발생하면 rollback은 추측이 된다. 추측 기반 rollback은 user-owned content를 덮어쓰거나, drifted target을 과거 상태로 오판하거나, mixed-boundary marker 밖 content까지 되돌릴 위험이 있다.

따라서 future sync mutation은 rollback precondition을 먼저 만족해야 하며, precondition을 만족하지 못하면 write 후보가 아니라 conflict 또는 drift-stop으로 남아야 한다.

## Transaction Goals

### Atomicity Expectation

future sync는 가능한 한 transaction 단위로 성공 또는 실패를 설명해야 한다.

Phase 6의 정책은 실제 atomic filesystem transaction을 구현하지 않는다. 다만 future implementation은 다음 기대를 만족해야 한다.

- entry별 write 결과가 transaction log에 남아야 한다.
- 전체 transaction status가 명확해야 한다.
- partial failure가 발생하면 어떤 entry가 applied, skipped, failed 상태인지 알 수 있어야 한다.
- rollback 가능 여부는 entry별로 판단해야 한다.

### Pre-image Preservation

rollback을 가능하게 하려면 mutation 전에 pre-image를 보존해야 한다.

pre-image 후보:

- full pre-content snapshot reference
- reversible patch reference
- managed block pre-content reference

mixed-boundary target에서는 marker 밖 user-owned content를 rollback 대상으로 삼지 않아야 한다.

### Managed Boundary Preservation

transaction은 write 시점의 managed boundary를 기록해야 한다.

필수 보존 정보:

- marker expected 여부
- marker entry_id
- marker version
- begin line
- end line
- marker integrity
- managed block hash boundary

rollback은 이 boundary가 여전히 유효할 때만 가능하다.

### Dry-run Parity

future mutation command와 rollback command는 모두 dry-run을 먼저 제공해야 한다.

원칙:

- sync write 전에 `sync --dry-run`과 동일한 판단이 가능해야 한다.
- rollback write 전에 `rollback --dry-run` 후보가 먼저 출력되어야 한다.
- dry-run result와 실제 command의 action vocabulary는 호환되어야 한다.

### Failure Recovery

transaction log는 실패 후 사람이 복구할 수 있는 충분한 정보를 제공해야 한다.

필수 정보:

- 어떤 entry가 시작되었는가
- 어떤 entry가 완료되었는가
- 어떤 entry가 실패했는가
- 실패 시점의 pre_hash와 post_hash
- rollback 가능 여부와 금지 이유

## Transaction Log Schema Candidate

후보 schema:

```json
{
  "transaction_id": "txn_20260523T120000Z_abcdef",
  "started_at": "2026-05-23T12:00:00Z",
  "completed_at": "2026-05-23T12:00:02Z",
  "command": "sync",
  "mode": "apply",
  "root": "D:\\development\\_templates\\ai_tool",
  "manifest_version": "aios.sync_manifest.v0",
  "entries": []
}
```

### Top-level Fields

| Field | Required | Type | 설명 |
|---|---:|---|---|
| `transaction_id` | yes | string | stable transaction identity |
| `started_at` | yes | string | transaction 시작 시각 |
| `completed_at` | yes | string 또는 null | 완료 시각. incomplete transaction은 null 가능 |
| `command` | yes | string | transaction을 만든 command. 후보: `sync` |
| `mode` | yes | string | `apply`, `rollback`, `dry-run-preview` 등 future mode |
| `root` | yes | string | repository root |
| `manifest_version` | yes | string 또는 null | 사용한 manifest version |
| `entries` | yes | array | transaction entry 목록 |

선택 후보:

- `schema_version`
- `manifest_path`
- `dry_run_result_ref`
- `envelope_v2_ref`
- `trace_id`
- `created_by`

## Transaction Entry Schema

후보 entry:

```json
{
  "entry_id": "entry_codex_root_adapter_rules",
  "action": "update",
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "pre_hash": "sha256:<pre-managed-block>",
  "post_hash": "sha256:<post-managed-block>",
  "pre_content_ref": ".ai/transactions/txn_.../entry_codex_root_adapter_rules.pre",
  "pre_patch_ref": null,
  "marker": {
    "entry_id": "entry_codex_root_adapter_rules",
    "marker_version": "0",
    "begin_line": 4,
    "end_line": 12,
    "integrity": "valid"
  },
  "status": "applied"
}
```

### Entry Fields

| Field | Required | Type | 설명 |
|---|---:|---|---|
| `entry_id` | yes | string | manifest entry identity |
| `action` | yes | string | applied action. 후보: `create`, `update`, `skip` |
| `target_path` | yes | string | target path |
| `ownership` | yes | string | `runtime-managed`, `user-owned`, `mixed-boundary` |
| `sync_mode` | yes | string | `managed-block`, `whole-file`, `observe-only`, `disabled` |
| `pre_hash` | yes | string 또는 null | mutation 전 hash |
| `post_hash` | yes | string 또는 null | mutation 후 hash |
| `pre_content_ref` | yes | string 또는 null | pre-image reference |
| `pre_patch_ref` | yes | string 또는 null | reversible patch reference |
| `marker` | yes | object 또는 null | marker boundary 정보 |
| `status` | yes | string | `planned`, `applied`, `skipped`, `failed`, `rolled-back`, `rollback-forbidden` |

규칙:

- mutation을 수행한 entry는 `pre_content_ref` 또는 `pre_patch_ref` 중 하나를 가져야 한다.
- `update`와 `create`는 `post_hash`를 기록해야 한다.
- `skip`은 `pre_hash`와 `post_hash`가 같거나 둘 다 null일 수 있다.
- mixed-boundary entry의 hash는 managed block boundary를 기준으로 한다.

## Rollback Preconditions

Rollback candidate가 되려면 다음 조건을 모두 만족해야 한다.

### Transaction Log Exists

조건:

- transaction log가 존재해야 한다.
- transaction_id가 명확해야 한다.
- rollback 대상 entry가 transaction log 안에 있어야 한다.

없으면:

- rollback forbidden
- stop reason: `transaction-log-missing`

### Pre-image or Reversible Patch Exists

조건:

- `pre_content_ref` 또는 `pre_patch_ref`가 존재해야 한다.
- reference가 읽을 수 있어야 한다.
- reference hash가 transaction metadata와 일치해야 한다.

없으면:

- rollback forbidden
- stop reason: `preimage-missing`

### Target Still Matches `post_hash`

조건:

- rollback 시점의 target managed block 또는 whole-file hash가 transaction `post_hash`와 일치해야 한다.

일치하지 않으면:

- rollback forbidden
- stop reason: `target-changed-after-transaction`

이 조건은 transaction 이후 사용자가 target을 수정한 상태에서 rollback이 덮어쓰는 것을 방지한다.

### Marker Boundary Still Valid

mixed-boundary rollback 조건:

- marker가 valid여야 한다.
- marker `entry_id`가 transaction entry와 일치해야 한다.
- marker version이 지원되어야 한다.
- begin/end boundary가 rollback 대상 범위를 안정적으로 정의해야 한다.

실패하면:

- rollback forbidden
- stop reason: `marker-invalid-after-transaction`

### User-owned Content Boundary Is Not Rolled Back

mixed-boundary rollback은 marker 내부 managed block만 되돌릴 수 있다.

금지:

- marker 밖 content rollback
- target whole-file rollback으로 user-owned content를 과거 상태로 되돌리기
- marker 외부 line ending 또는 formatting 되돌리기

위반하면:

- rollback forbidden
- stop reason: `user-owned-boundary-risk`

## Rollback Forbidden Cases

| Case | Stop reason | 설명 |
|---|---|---|
| transaction log 없음 | `transaction-log-missing` | rollback 근거가 없음 |
| pre-image 또는 patch 없음 | `preimage-missing` | 되돌릴 원본이 없음 |
| target이 transaction 이후 변경됨 | `target-changed-after-transaction` | rollback이 사용자 변경을 덮어쓸 수 있음 |
| marker가 transaction 이후 손상됨 | `marker-invalid-after-transaction` | rollback 범위가 불명확함 |
| ownership mismatch | `ownership-mismatch` | transaction 당시 ownership과 현재 ownership이 다름 |
| mixed-boundary 외부 content가 수정 대상이 됨 | `user-owned-boundary-risk` | user-owned content를 되돌릴 위험 |
| rollback 대상 action이 `skip` 또는 observe-only임 | `rollback-not-applicable` | 실제 mutation이 없었음 |
| transaction status가 incomplete이고 entry 상태가 불명확함 | `transaction-incomplete` | applied 여부가 불명확함 |

## Dry-run-first Rollback Policy

Rollback도 write command이므로 dry-run이 먼저다.

Future command expectation:

```text
aios rollback <transaction_id> --dry-run
```

후보 출력은 sync dry-run과 같은 vocabulary를 재사용한다.

Rollback dry-run result item 후보:

```json
{
  "entry_id": "entry_codex_root_adapter_rules",
  "action": "rollback",
  "severity": "informational",
  "stop_reason": null,
  "recovery_hint": null,
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "drift_state": "clean",
  "hashes": {
    "expected_post_hash": "sha256:<post>",
    "actual_target_hash": "sha256:<post>",
    "rollback_target_hash": "sha256:<pre>"
  },
  "marker": {
    "entry_id": "entry_codex_root_adapter_rules",
    "marker_version": "0",
    "integrity": "valid"
  },
  "details": {
    "transaction_id": "txn_20260523T120000Z_abcdef"
  }
}
```

Rollback dry-run status mapping:

- any forbidden case -> `fail`
- warnings only -> `warn`
- rollback candidates only -> `pass`

## Relationship to Existing Designs

### Sync Dry-run Schema

Transaction policy extends dry-run schema rather than replacing it.

Mapping:

- sync dry-run `action` becomes transaction entry `action` after apply.
- dry-run `hashes.actual_*` become transaction `pre_hash`.
- generated preview hash becomes transaction `post_hash` after apply.
- dry-run `marker` becomes transaction entry `marker`.
- dry-run `stop_reason` vocabulary is reused for rollback forbidden messages where possible.

### Manifest Schema

Transaction log records the manifest context used at mutation time.

Required links:

- `manifest_version`
- optional `manifest_path`
- entry `entry_id`
- entry `target_path`
- entry `ownership`
- entry `sync_mode`

Manifest changes after transaction must not silently change rollback meaning. Rollback uses transaction log facts first, then validates current filesystem safety.

### Managed Block Marker Contract

Rollback of mixed-boundary target depends on marker contract.

Rules:

- marker integrity check precedes rollback candidate creation.
- rollback hash boundary is marker inner content only.
- marker outside content is not rollback target.
- marker missing, duplicated, corrupted means rollback forbidden.

### Envelope v2

Future rollback dry-run and transaction inspection should map to envelope v2.

Mapping:

- `command`: `rollback` or `sync`
- `status`: `pass`, `warn`, `fail`
- `target`: transaction_id or manifest path
- `summary`: rollback candidate, forbidden, warning counts
- `messages`: forbidden rollback reasons
- `payload`: transaction entries or rollback dry-run results
- `meta`: `dry_run`, `transaction_id`, `manifest_version`

### Observability Events

Future opt-in events may include:

- `runtime.sync.transaction_started`
- `runtime.sync.transaction_entry_applied`
- `runtime.sync.transaction_failed`
- `runtime.sync.transaction_completed`
- `runtime.rollback.dry_run_started`
- `runtime.rollback.precondition_failed`
- `runtime.rollback.candidate_found`
- `runtime.rollback.completed`

Events must not imply persistence, telemetry, networking, or execution in Phase 6.

## Explicit Non-goals

이 정책은 다음을 구현하지 않는다.

- rollback implementation
- transaction persistence implementation
- transaction log writing
- force
- decommission
- actual sync execution
- manifest persistence
- adapter generation
- auto-fix
- automatic conflict resolution
- auto merge
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- source mutation

## Future Gate

Future mutation command가 가능하려면 다음이 먼저 별도 설계되어야 한다.

- transaction storage location and retention policy
- pre-image snapshot or patch format
- rollback dry-run result schema
- incomplete transaction recovery policy
- transaction log validation command
- runtime-facing sync operation rule promotion
