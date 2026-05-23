# Sync Manifest Safety Design

## 개요

이 문서는 `.ai OS` Roadmap v1.2 Phase 6의 sync/manifest safety architecture를 설계한다. Phase 6은 read-only safety design 단계이며, 이 문서는 future sync behavior의 안전 계약을 정의한다.

이번 문서는 구현 지시가 아니다. `aios sync`, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation은 구현하지 않는다.

## 설계 목표

### Reproducibility

미래 sync는 같은 source state와 같은 sync policy에서 같은 dry-run 결과를 산출해야 한다.

요구 사항:

- source path와 target path를 명시한다.
- source hash와 target hash를 기록한다.
- 생성 주체와 생성 시점을 기록한다.
- managed entry별 sync mode와 ownership을 기록한다.

### Provenance

모든 managed output은 어떤 `.ai` source에서 유래했는지 추적 가능해야 한다.

요구 사항:

- source root와 target root를 구분한다.
- entry별 source path를 보존한다.
- generated_by와 generator version 후보를 기록한다.
- future envelope v2 또는 event trace와 연결할 수 있는 식별자를 허용한다.

### Drift Detection

미래 sync는 대상 파일이 마지막 관리 상태에서 벗어났는지 먼저 판정해야 한다.

요구 사항:

- clean, drifted, missing, orphaned, unmanaged 상태를 구분한다.
- drifted 상태에서는 기본적으로 쓰기를 멈춘다.
- user-owned 영역은 자동 수정하지 않는다.
- mixed-boundary 파일은 managed block 내부와 외부를 분리해 판단한다.

### Rollback Support

Rollback은 Phase 6에서 구현하지 않는다. 다만 미래 구현이 rollback할 수 있도록 precondition을 설계한다.

요구 사항:

- 이전 target hash가 기록되어야 한다.
- managed block identity가 안정적이어야 한다.
- transaction log 설계가 Phase 7 전에 별도 문서화되어야 한다.

### Managed Ownership Boundary

미래 sync는 `.ai` source of truth와 target file의 소유 경계를 명확히 해야 한다.

요구 사항:

- runtime-managed 영역만 자동 변경 후보가 될 수 있다.
- user-owned 영역은 보존 대상이다.
- mixed-boundary 파일은 안정적인 marker로 managed 영역만 식별한다.

### Non-destructive Update Policy

미래 sync의 기본 정책은 비파괴적이어야 한다.

요구 사항:

- dry-run 없이 쓰기 금지.
- drift 감지 시 기본 중단.
- conflict 자동 병합 금지.
- target 삭제 또는 managed block 제거는 별도 명시 정책 없이는 금지.

## Future Manifest Schema Candidate

초기 후보 스키마:

```json
{
  "manifest_version": "aios.sync_manifest.v0",
  "repository_id": "repo_derived_or_configured_id",
  "generated_at": "2026-05-23T00:00:00Z",
  "source_root": ".ai",
  "target_root": ".",
  "managed_entries": []
}
```

### Top-level Fields

| Field | Required | 설명 |
|---|---|---|
| `manifest_version` | yes | manifest schema version. 초기 후보는 `aios.sync_manifest.v0` |
| `repository_id` | yes | repository identity. future implementation에서 stable derivation 또는 설정값으로 결정 |
| `generated_at` | yes | manifest 생성 시각 |
| `source_root` | yes | source of truth root. 현재 후보는 `.ai` |
| `target_root` | yes | target root. repository root 또는 future adapter root |
| `managed_entries` | yes | managed entry 목록 |

## Managed Entry Structure

초기 후보 구조:

```json
{
  "entry_id": "entry_codex_root_adapter",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "source_hash": "sha256:<source-content-or-source-bundle>",
  "target_hash": "sha256:<managed-target-content>",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "generated_by": "aios.sync.v0",
  "generated_at": "2026-05-23T00:00:00Z"
}
```

### Entry Fields

| Field | Required | 설명 |
|---|---|---|
| `entry_id` | yes | stable entry identity |
| `source_path` | yes | canonical source path |
| `target_path` | yes | target path |
| `source_hash` | yes | source content 또는 source bundle hash |
| `target_hash` | yes | 마지막 known managed target hash |
| `ownership` | yes | ownership model |
| `sync_mode` | yes | sync mode |
| `generated_by` | yes | generator identity |
| `generated_at` | yes | entry 생성 또는 갱신 시각 |

### Optional Future Fields

향후 필요한 경우 다음 필드를 추가할 수 있다.

| Field | 목적 |
|---|---|
| `source_paths` | 여러 source를 하나의 target으로 합성하는 경우 |
| `target_block_id` | managed block identity |
| `adapter` | Codex, Claude, Gemini 등 target adapter 종류 |
| `activation_reference` | activation v1 active set과 연결 |
| `trace_id` | future observability trace 연결 |
| `dry_run_last_seen_at` | 마지막 dry-run 관측 시각 |

## Ownership Model

### runtime-managed

전체 target이 AIOS에 의해 관리되는 상태이다.

정책:

- target 전체 hash를 비교한다.
- drift가 있으면 기본 중단한다.
- user edits가 예상되는 파일에는 사용하지 않는다.

적합 예:

- future generated artifact only file
- machine-generated manifest-derived output

### user-owned

target이 사용자의 소유이며 AIOS가 변경하면 안 되는 상태이다.

정책:

- sync write 대상이 아니다.
- inventory, validation, dry-run observation 대상이 될 수는 있다.
- 자동 수정, 삭제, managed block 삽입 금지.

적합 예:

- 사람이 작성하는 문서
- root adapter 중 완전 수동 관리 파일

### mixed-boundary

target 파일 안에 user-owned 영역과 runtime-managed block이 공존하는 상태이다.

정책:

- stable marker로 managed block을 식별한다.
- managed block 내부만 hash 비교와 update 후보가 된다.
- marker 외부 user content는 보존한다.
- marker 누락, 중복, 손상은 conflict 또는 drift-stop으로 처리한다.

적합 예:

- future root adapter managed section
- future tool-specific wrapper with user-owned notes

## Sync Mode Candidate

| sync_mode | 의미 |
|---|---|
| `observe-only` | target 상태만 관측하고 쓰지 않음 |
| `managed-block` | target 내부 managed block만 future update 후보 |
| `whole-file` | target 전체가 runtime-managed인 경우만 future update 후보 |
| `disabled` | manifest에 기록하지만 sync 대상에서 제외 |

Phase 6에서는 mode를 설계만 한다. 실행하지 않는다.

## Drift Model

| Drift state | 의미 | 기본 dry-run 행동 |
|---|---|---|
| `clean` | source hash와 target managed hash가 manifest 기대값과 일치 | update 가능 후보 |
| `drifted` | target managed 영역이 마지막 known target hash와 다름 | `drift-stop` |
| `missing` | target 또는 managed block이 없음 | `create` 또는 `conflict`, policy에 따름 |
| `orphaned` | manifest entry는 없지만 AIOS managed marker가 있음 | `orphan-warning` |
| `unmanaged` | target은 있으나 AIOS ownership marker 또는 manifest entry가 없음 | `skip` |

## Dry-run Result Schema

미래 dry-run 후보 구조:

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "warn",
  "root": "D:\\development\\_templates\\ai_tool",
  "summary": {
    "create": 0,
    "update": 1,
    "skip": 3,
    "conflict": 0,
    "drift_stop": 0,
    "orphan_warning": 0
  },
  "results": []
}
```

### Dry-run Result Item

```json
{
  "entry_id": "entry_codex_root_adapter",
  "action": "drift-stop",
  "drift_state": "drifted",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "message": "Target managed block changed since last manifest hash.",
  "details": {
    "expected_target_hash": "sha256:<old>",
    "actual_target_hash": "sha256:<current>"
  }
}
```

### Dry-run Actions

| Action | 의미 |
|---|---|
| `create` | target 또는 managed block 생성 후보 |
| `update` | clean 상태에서 managed content 갱신 후보 |
| `skip` | 변경 없음 또는 정책상 제외 |
| `conflict` | marker 손상, ownership 불명확, policy 충돌 |
| `drift-stop` | drift 감지로 쓰기 중단 |
| `orphan-warning` | manifest 없는 managed marker 발견 |

## Managed Block Contract

### Stable Markers

후보 marker:

```markdown
<!-- BEGIN AIOS MANAGED BLOCK: entry_id=entry_codex_root_adapter version=0 -->
Generated content
<!-- END AIOS MANAGED BLOCK: entry_id=entry_codex_root_adapter -->
```

요구 사항:

- begin/end marker는 같은 `entry_id`를 가져야 한다.
- marker는 사람이 쉽게 식별할 수 있어야 한다.
- marker 자체는 generator가 안정적으로 파싱할 수 있어야 한다.
- marker 형식 변경은 manifest version 변경 또는 migration plan이 필요하다.

### Identity Strategy

`entry_id`는 다음 조합에서 안정적으로 파생하는 것을 권장한다.

- target adapter kind
- target path
- managed purpose
- source bundle identity

예:

- `entry_codex_root_adapter_rules`
- `entry_claude_root_adapter_rules`
- `entry_gemini_root_adapter_rules`

### Insertion Rules

삽입은 future implementation에서만 가능하다.

후보 정책:

- target이 user-owned이면 삽입 금지.
- target이 mixed-boundary이고 insertion anchor가 명확할 때만 dry-run create 후보로 표시.
- anchor가 없으면 conflict.
- 삽입 전 diff를 dry-run에 표시.

### Update Rules

후보 정책:

- marker가 정확히 하나의 begin/end pair로 존재해야 한다.
- 현재 managed block hash가 manifest target_hash와 일치해야 한다.
- 일치하지 않으면 drift-stop.
- marker 외부 content는 절대 변경하지 않는다.

### Removal Rules

후보 정책:

- 기본적으로 managed block 제거 금지.
- 제거는 별도 explicit decommission mode가 설계된 후에만 가능하다.
- orphaned marker는 경고만 출력한다.

## Rollback Expectations

Rollback은 Phase 6에서 구현하지 않는다.

미래 rollback precondition:

- 이전 target_hash가 manifest 또는 transaction log에 존재해야 한다.
- update 전 target snapshot 또는 reversible patch가 있어야 한다.
- mixed-boundary 파일에서는 marker 외부 content를 rollback 대상으로 삼지 않아야 한다.
- rollback 자체도 dry-run을 먼저 제공해야 한다.

## Activation v1 Compatibility

Activation v1은 future sync의 selection input 후보가 될 수 있다.

가능한 관계:

- `active_set.agents`가 adapter generation 후보를 좁힐 수 있다.
- `active_set.rules`와 `rule_sets`가 managed content source bundle을 좁힐 수 있다.
- `profiles.*loader*`는 sync behavior가 아니라 context selection policy이므로 manifest update를 직접 제어하지 않는다.

중요:

- activation은 sync selection 자체가 아니다.
- activation file을 자동 생성하거나 수정하지 않는다.
- activation-driven sync는 별도 Phase 설계 없이는 금지한다.

## Envelope v2 Compatibility

미래 dry-run 명령은 envelope v2와 호환되어야 한다.

후보 mapping:

- `command`: `sync`
- `status`: `pass`, `warn`, `fail`
- `target`: repository 또는 manifest target
- `summary`: action count
- `messages`: conflict, drift-stop, orphan-warning
- `payload`: dry-run results and manifest preview
- `meta`: `dry_run: true`, `manifest_version`, `trace_id`

## Observability Compatibility

미래 event taxonomy는 다음 event 후보를 포함할 수 있다.

| Event type | 의미 |
|---|---|
| `runtime.sync.dry_run_started` | dry-run 시작 |
| `runtime.sync.entry_evaluated` | managed entry 평가 |
| `runtime.sync.drift_detected` | drift 감지 |
| `runtime.sync.conflict_detected` | conflict 감지 |
| `runtime.sync.orphan_detected` | orphan marker 감지 |
| `runtime.sync.dry_run_completed` | dry-run 완료 |

이벤트는 opt-in이어야 하며 persistence나 networking을 의미하지 않는다.

## Explicit Non-goals

이 설계는 다음을 구현하지 않는다.

- real sync execution
- file mutation
- manifest persistence
- adapter generation
- auto-merge
- auto-conflict resolution
- background sync
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source mutation

## Phase 7 Entry Preconditions

Phase 7 구현 진입 전 최소 조건:

- manifest schema가 별도 검증되었다.
- dry-run result schema가 확정되었다.
- managed block marker contract가 검증되었다.
- drift-stop policy가 runtime-facing rule로 승격되었다.
- rollback precondition이 transaction log 설계와 연결되었다.
- `aios inspect`와 `aios validate` clean baseline이 유지된다.
