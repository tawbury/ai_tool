# Sync Dry-run Result Schema

## 개요

이 문서는 future `aios sync --dry-run` 출력 스키마를 정의한다. 현재 `.ai OS`는 read-only 상태이며, 이 문서는 구현이 아니라 Phase 6 sync/manifest safety 설계를 구체화하는 결과 계약이다.

이 문서는 sync 실행, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation을 구현하지 않는다.

## 설계 목표

`aios sync --dry-run`은 future mutation 이전에 다음 질문에 결정적으로 답해야 한다.

- 어떤 항목이 생성 후보인가?
- 어떤 항목이 갱신 후보인가?
- 어떤 항목이 안전하게 건너뛰어지는가?
- 어떤 항목이 drift 때문에 중단되어야 하는가?
- 어떤 항목이 marker 또는 ownership conflict인가?
- 사용자가 복구하려면 어떤 정보를 봐야 하는가?

dry-run 결과는 실제 파일을 변경하지 않고, future sync가 수행했을 판단만 구조화한다.

## Top-level Schema

후보 schema version:

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "fail",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {},
  "results": [],
  "messages": [],
  "meta": {}
}
```

### Top-level Fields

| Field | Required | Type | 설명 |
|---|---:|---|---|
| `schema_version` | yes | string | dry-run result schema version. 초기 후보는 `aios.sync_dry_run.v0` |
| `status` | yes | string | 전체 결과 상태. `pass`, `warn`, `fail` 중 하나 |
| `root` | yes | string | dry-run을 평가한 repository root |
| `mode` | yes | string | 항상 `dry-run` |
| `manifest_path` | yes | string 또는 null | 사용하거나 preview한 manifest path. manifest persistence가 없으면 null 가능 |
| `summary` | yes | object | action, severity, stop counter |
| `results` | yes | array | entry별 dry-run result item 목록 |
| `messages` | yes | array | envelope v2와 호환되는 message 목록 |
| `meta` | yes | object | manifest version, command metadata, compatibility metadata |

## Result Item Schema

각 result item은 하나의 manifest entry 또는 orphan/unmanaged 관찰 결과를 표현한다.

```json
{
  "entry_id": "entry_codex_root_adapter_rules",
  "action": "drift-stop",
  "severity": "blocking",
  "stop_reason": "target-modified",
  "recovery_hint": "Review the target managed block and refresh the manifest only after confirming the change is intentional.",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "managed-block",
  "drift_state": "drifted",
  "hashes": {
    "expected_source_hash": "sha256:<manifest-source>",
    "actual_source_hash": "sha256:<current-source>",
    "expected_target_hash": "sha256:<manifest-target>",
    "actual_target_hash": "sha256:<current-target>",
    "generated_target_hash": "sha256:<preview-target>"
  },
  "marker": {
    "expected": true,
    "present": true,
    "count": 1,
    "entry_id": "entry_codex_root_adapter_rules",
    "integrity": "valid"
  },
  "details": {
    "message": "Target managed block changed since the manifest target hash was recorded."
  }
}
```

### Result Item Fields

| Field | Required | Type | 설명 |
|---|---:|---|---|
| `entry_id` | yes | string | manifest entry identity. orphan/unmanaged 항목은 stable synthetic id 가능 |
| `action` | yes | string | dry-run action enum |
| `severity` | yes | string | `informational`, `warning`, `blocking` |
| `stop_reason` | yes | string 또는 null | stop 또는 conflict 이유. safe action이면 null |
| `recovery_hint` | yes | string 또는 null | 사람이 취할 수 있는 복구 방향 |
| `source_path` | yes | string 또는 null | source of truth path |
| `target_path` | yes | string | target path |
| `ownership` | yes | string | `runtime-managed`, `user-owned`, `mixed-boundary` |
| `sync_mode` | yes | string | `observe-only`, `managed-block`, `whole-file`, `disabled` |
| `drift_state` | yes | string | `clean`, `drifted`, `missing`, `orphaned`, `unmanaged`, `conflicted` |
| `hashes` | yes | object | source, target, generated preview hash 정보 |
| `marker` | yes | object 또는 null | managed block marker 관찰 정보 |
| `details` | yes | object | action별 보조 정보 |

## Action Enum

| Action | Severity 기본값 | 의미 |
|---|---|---|
| `create` | informational | target 또는 managed block 생성 후보 |
| `update` | informational | clean target에서 generated content 갱신 후보 |
| `skip` | informational 또는 warning | 변경 없음, disabled, observe-only, unmanaged target skip |
| `conflict` | blocking | marker, ownership, source, manifest entry 문제로 future write 불가 |
| `drift-stop` | blocking | target 또는 managed block이 manifest 기준에서 변경되어 write 중단 필요 |
| `orphan-warning` | warning | manifest entry 없이 managed marker가 발견됨 |

## Status Mapping

Top-level `status`는 result item과 message severity에서 결정한다.

| 조건 | Status |
|---|---|
| `blocking` severity가 하나 이상 있음 | `fail` |
| blocking은 없고 warning이 하나 이상 있음 | `warn` |
| safe `create`, `update`, `skip`만 있음 | `pass` |

세부 규칙:

- `conflict`와 `drift-stop`은 항상 `fail`을 만든다.
- `orphan-warning`은 blocking conflict가 없으면 `warn`을 만든다.
- `unmanaged-target`으로 인한 `skip`은 warning message가 있으면 `warn`, 단순 observe-only skip은 `pass`가 가능하다.
- source가 변경되었지만 target이 clean인 update candidate는 기본적으로 `pass` 또는 informational message이다.

## Summary Counters

`summary`는 사람이 빠르게 위험도를 판단할 수 있도록 action과 severity를 모두 센다.

```json
{
  "total": 5,
  "create": 1,
  "update": 1,
  "skip": 1,
  "conflict": 1,
  "drift_stop": 1,
  "orphan_warning": 0,
  "blocking": 2,
  "warnings": 0,
  "informational": 3
}
```

필수 counter:

- `create`
- `update`
- `skip`
- `conflict`
- `drift_stop`
- `orphan_warning`
- `blocking`
- `warnings`

권장 counter:

- `total`
- `informational`
- `runtime_managed`
- `mixed_boundary`
- `user_owned`
- `observe_only`
- `managed_block`
- `whole_file`

## Message Mapping to Envelope v2

Future `aios sync --dry-run --json --envelope-v2`는 dry-run native schema를 envelope v2 payload로 감쌀 수 있어야 한다.

Mapping:

| Dry-run field | Envelope v2 field |
|---|---|
| `schema_version` | `meta.legacy_schema_version` 또는 `payload.schema_version` |
| `status` | `status` |
| `root` | `root` |
| `manifest_path` | `target` 또는 `meta.manifest_path` |
| `summary` | `summary` |
| `results` | `payload.results` |
| `messages` | `messages` |
| `mode` | `meta.dry_run: true` |

Message 후보:

```json
{
  "code": "target-modified",
  "severity": "blocking",
  "status": "fail",
  "message": "Target managed block changed since the manifest target hash was recorded.",
  "path": "AGENTS.md",
  "line": null,
  "details": {
    "entry_id": "entry_codex_root_adapter_rules",
    "action": "drift-stop",
    "recovery_hint": "Review the target managed block and refresh the manifest only after confirming the change is intentional."
  }
}
```

Message 규칙:

- `conflict`, `drift-stop`, `orphan-warning`, warning `skip`은 message를 생성한다.
- safe `create`와 `update`는 summary와 result item에만 있어도 된다.
- 모든 blocking message는 `status: fail`로 정규화한다.
- 모든 warning message는 `status: warn`으로 정규화한다.

## Hash Object

`hashes`는 가능한 값을 명시하되, 아직 계산되지 않은 값은 null로 둔다.

```json
{
  "expected_source_hash": "sha256:<manifest-source>",
  "actual_source_hash": "sha256:<current-source>",
  "expected_target_hash": "sha256:<manifest-target>",
  "actual_target_hash": "sha256:<current-target>",
  "expected_managed_block_hash": "sha256:<manifest-block>",
  "actual_managed_block_hash": "sha256:<current-block>",
  "generated_target_hash": "sha256:<preview-target>",
  "generated_managed_block_hash": "sha256:<preview-block>"
}
```

규칙:

- `expected_*` 값은 manifest 또는 manifest preview에서 온다.
- `actual_*` 값은 현재 filesystem 관찰값에서 온다.
- `generated_*` 값은 future generator preview에서 온다.
- Phase 6에서는 실제 generator가 없으므로 schema contract만 정의한다.

## Marker Object

`marker`는 `mixed-boundary`와 `managed-block` mode에서 managed boundary를 설명한다.

```json
{
  "expected": true,
  "present": true,
  "count": 1,
  "entry_id": "entry_codex_root_adapter_rules",
  "begin_line": 4,
  "end_line": 12,
  "integrity": "valid",
  "problems": []
}
```

Marker integrity enum:

- `not-expected`
- `valid`
- `missing`
- `duplicated`
- `corrupted`
- `unknown`

규칙:

- marker가 필요 없는 whole-file entry는 `marker.expected: false` 또는 `marker: null`을 사용할 수 있다.
- marker가 expected인데 없으면 기본 action은 `conflict`이다.
- marker가 duplicated 또는 corrupted이면 항상 blocking conflict이다.

## Sample Outputs

### Clean Update Candidate

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "pass",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {
    "total": 1,
    "create": 0,
    "update": 1,
    "skip": 0,
    "conflict": 0,
    "drift_stop": 0,
    "orphan_warning": 0,
    "blocking": 0,
    "warnings": 0,
    "informational": 1
  },
  "results": [
    {
      "entry_id": "entry_codex_root_adapter_rules",
      "action": "update",
      "severity": "informational",
      "stop_reason": null,
      "recovery_hint": null,
      "source_path": ".ai/rules/rules.md",
      "target_path": "AGENTS.md",
      "ownership": "mixed-boundary",
      "sync_mode": "managed-block",
      "drift_state": "clean",
      "hashes": {
        "expected_source_hash": "sha256:old-source",
        "actual_source_hash": "sha256:new-source",
        "expected_target_hash": "sha256:current-block",
        "actual_target_hash": "sha256:current-block",
        "generated_target_hash": "sha256:new-block"
      },
      "marker": {
        "expected": true,
        "present": true,
        "count": 1,
        "entry_id": "entry_codex_root_adapter_rules",
        "integrity": "valid"
      },
      "details": {
        "message": "Source changed and target managed block is clean."
      }
    }
  ],
  "messages": [],
  "meta": {
    "dry_run": true,
    "mutation_performed": false
  }
}
```

### Drift-stop

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "fail",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {
    "total": 1,
    "create": 0,
    "update": 0,
    "skip": 0,
    "conflict": 0,
    "drift_stop": 1,
    "orphan_warning": 0,
    "blocking": 1,
    "warnings": 0,
    "informational": 0
  },
  "results": [
    {
      "entry_id": "entry_codex_root_adapter_rules",
      "action": "drift-stop",
      "severity": "blocking",
      "stop_reason": "target-modified",
      "recovery_hint": "Review the target managed block and refresh the manifest only after confirming the change is intentional.",
      "source_path": ".ai/rules/rules.md",
      "target_path": "AGENTS.md",
      "ownership": "mixed-boundary",
      "sync_mode": "managed-block",
      "drift_state": "drifted",
      "hashes": {
        "expected_target_hash": "sha256:manifest-block",
        "actual_target_hash": "sha256:changed-block"
      },
      "marker": {
        "expected": true,
        "present": true,
        "count": 1,
        "entry_id": "entry_codex_root_adapter_rules",
        "integrity": "valid"
      },
      "details": {
        "message": "Target managed block changed since the manifest target hash was recorded."
      }
    }
  ],
  "messages": [
    {
      "code": "target-modified",
      "severity": "blocking",
      "status": "fail",
      "message": "Target managed block changed since the manifest target hash was recorded.",
      "path": "AGENTS.md",
      "line": null,
      "details": {
        "entry_id": "entry_codex_root_adapter_rules",
        "action": "drift-stop"
      }
    }
  ],
  "meta": {
    "dry_run": true,
    "mutation_performed": false
  }
}
```

### Marker-corrupted Conflict

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "fail",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {
    "total": 1,
    "create": 0,
    "update": 0,
    "skip": 0,
    "conflict": 1,
    "drift_stop": 0,
    "orphan_warning": 0,
    "blocking": 1,
    "warnings": 0,
    "informational": 0
  },
  "results": [
    {
      "entry_id": "entry_codex_root_adapter_rules",
      "action": "conflict",
      "severity": "blocking",
      "stop_reason": "marker-corrupted",
      "recovery_hint": "Repair marker boundaries manually after review.",
      "source_path": ".ai/rules/rules.md",
      "target_path": "AGENTS.md",
      "ownership": "mixed-boundary",
      "sync_mode": "managed-block",
      "drift_state": "conflicted",
      "hashes": {},
      "marker": {
        "expected": true,
        "present": true,
        "count": 1,
        "entry_id": "entry_codex_root_adapter_rules",
        "integrity": "corrupted",
        "problems": [
          "begin-end-entry-id-mismatch"
        ]
      },
      "details": {
        "message": "Managed block marker is malformed or internally inconsistent."
      }
    }
  ],
  "messages": [
    {
      "code": "marker-corrupted",
      "severity": "blocking",
      "status": "fail",
      "message": "Managed block marker is malformed or internally inconsistent.",
      "path": "AGENTS.md",
      "line": null,
      "details": {
        "entry_id": "entry_codex_root_adapter_rules",
        "action": "conflict"
      }
    }
  ],
  "meta": {
    "dry_run": true,
    "mutation_performed": false
  }
}
```

### Unmanaged Target Skip

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "warn",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {
    "total": 1,
    "create": 0,
    "update": 0,
    "skip": 1,
    "conflict": 0,
    "drift_stop": 0,
    "orphan_warning": 0,
    "blocking": 0,
    "warnings": 1,
    "informational": 0
  },
  "results": [
    {
      "entry_id": "observed_unmanaged_AGENTS_md",
      "action": "skip",
      "severity": "warning",
      "stop_reason": "unmanaged-target",
      "recovery_hint": "Do not insert managed markers automatically; define ownership explicitly before syncing this target.",
      "source_path": null,
      "target_path": "AGENTS.md",
      "ownership": "user-owned",
      "sync_mode": "observe-only",
      "drift_state": "unmanaged",
      "hashes": {},
      "marker": {
        "expected": false,
        "present": false,
        "count": 0,
        "entry_id": null,
        "integrity": "not-expected"
      },
      "details": {
        "message": "Target exists without a manifest entry or AIOS managed marker."
      }
    }
  ],
  "messages": [
    {
      "code": "unmanaged-target",
      "severity": "warning",
      "status": "warn",
      "message": "Target exists without a manifest entry or AIOS managed marker.",
      "path": "AGENTS.md",
      "line": null,
      "details": {
        "action": "skip"
      }
    }
  ],
  "meta": {
    "dry_run": true,
    "mutation_performed": false
  }
}
```

### Orphan-warning

```json
{
  "schema_version": "aios.sync_dry_run.v0",
  "status": "warn",
  "root": "D:\\development\\_templates\\ai_tool",
  "mode": "dry-run",
  "manifest_path": ".ai/manifest/aios.sync-manifest.json",
  "summary": {
    "total": 1,
    "create": 0,
    "update": 0,
    "skip": 0,
    "conflict": 0,
    "drift_stop": 0,
    "orphan_warning": 1,
    "blocking": 0,
    "warnings": 1,
    "informational": 0
  },
  "results": [
    {
      "entry_id": "orphan_entry_codex_root_adapter_rules",
      "action": "orphan-warning",
      "severity": "warning",
      "stop_reason": "orphaned-managed-block",
      "recovery_hint": "Review the marker manually; do not remove it automatically without an explicit decommission policy.",
      "source_path": null,
      "target_path": "AGENTS.md",
      "ownership": "mixed-boundary",
      "sync_mode": "managed-block",
      "drift_state": "orphaned",
      "hashes": {},
      "marker": {
        "expected": false,
        "present": true,
        "count": 1,
        "entry_id": "entry_codex_root_adapter_rules",
        "integrity": "valid"
      },
      "details": {
        "message": "AIOS managed marker exists without a matching manifest entry."
      }
    }
  ],
  "messages": [
    {
      "code": "orphaned-managed-block",
      "severity": "warning",
      "status": "warn",
      "message": "AIOS managed marker exists without a matching manifest entry.",
      "path": "AGENTS.md",
      "line": null,
      "details": {
        "action": "orphan-warning"
      }
    }
  ],
  "meta": {
    "dry_run": true,
    "mutation_performed": false
  }
}
```

## Compatibility

### Drift Stop Policy

이 schema는 `docs/plan/drift_detection_and_stop_policy.md`의 stop policy를 출력 형태로 고정한다.

정렬:

- `target-modified`는 `drift-stop`과 `blocking`으로 표현한다.
- marker failure는 `conflict`와 `blocking`으로 표현한다.
- `unmanaged-target`은 `skip`과 warning으로 표현한다.
- `orphaned-managed-block`은 `orphan-warning`과 warning으로 표현한다.

### Manifest Safety Design

이 schema는 manifest entry 후보 필드와 직접 연결된다.

정렬:

- `entry_id`, `source_path`, `target_path`, `ownership`, `sync_mode`는 managed entry에서 온다.
- `hashes.expected_*`는 manifest에서 온다.
- `hashes.actual_*`는 dry-run 관찰값이다.
- `marker`는 managed block contract의 관찰 결과이다.

### Envelope v2

Native dry-run schema는 backward-compatible JSON으로 유지할 수 있고, opt-in envelope v2에서는 `payload.results`로 들어간다.

Envelope v2 canonical status는 그대로 `pass`, `warn`, `fail`을 사용한다.

### Observability Events

Future event emission은 이 schema의 result item을 event detail로 재사용할 수 있다.

권장 event mapping:

| Result action | Event type |
|---|---|
| `create` | `runtime.sync.create_candidate_found` |
| `update` | `runtime.sync.update_candidate_found` |
| `skip` | `runtime.sync.entry_skipped` |
| `conflict` | `runtime.sync.conflict_detected` |
| `drift-stop` | `runtime.sync.stop_required` |
| `orphan-warning` | `runtime.sync.orphan_detected` |

Events are opt-in only and do not imply persistence, telemetry, or networking.

## Explicit Non-goals

이 schema 설계는 다음을 구현하지 않는다.

- actual sync execution
- filesystem mutation
- manifest persistence
- adapter generation
- auto-fix
- force
- rollback
- auto merge
- automatic conflict resolution
- background reconciliation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- source mutation

## Future Implementation Gate

Future `aios sync --dry-run` 구현 전 최소 조건:

- manifest schema가 확정되어야 한다.
- marker parser contract가 별도 테스트 가능해야 한다.
- drift stop policy가 runtime-facing rule로 승격되어야 한다.
- dry-run sample output이 envelope v2 sample과 함께 검증되어야 한다.
- 실제 mutation command는 dry-run schema와 stop policy가 통과한 뒤 별도 phase에서 설계해야 한다.
