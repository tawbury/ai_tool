# 런타임 이벤트 및 트레이스 모델 계획

## 목적

AIOS 런타임 명령의 미래 관측성을 위해 이벤트 및 트레이스 모델을 설계한다. 현재 명령은 read-only이며, 이 계획은 실행, 저장, 네트워크 전송, 워커 디스패치, 워크플로 실행을 구현하지 않는다.

## 설계 원칙

- 기존 JSON 출력과 envelope v2를 변경하지 않는다.
- 이벤트는 opt-in으로만 노출한다.
- 이벤트는 명령 결과를 보완하며, 명령 결과를 대체하지 않는다.
- 모든 이벤트는 read-only 관측 기록이다.
- provenance는 path와 line 범위를 보존한다.
- 미래 orchestration과 command chain을 수용하되, 현재는 실행하지 않는다.

## 이벤트 taxonomy 후보

### 명령 생명주기

| Event type | 의미 |
|---|---|
| `runtime.command.started` | 명령 실행 시작 |
| `runtime.command.completed` | 명령 실행 완료 |
| `runtime.command.failed` | 명령 실행 실패 또는 crash성 종료 |

### 공통 phase

| Event type | 의미 |
|---|---|
| `runtime.phase.started` | 명령 내부 phase 시작 |
| `runtime.phase.completed` | 명령 내부 phase 완료 |
| `runtime.phase.failed` | phase 실패 |

### Inventory

| Event type | 의미 |
|---|---|
| `runtime.inventory.discovery_started` | inventory discovery 시작 |
| `runtime.inventory.item_discovered` | inventory item 발견 |
| `runtime.inventory.discovery_completed` | inventory discovery 완료 |

### Validation

| Event type | 의미 |
|---|---|
| `runtime.validation.target_selected` | validation target 선택 |
| `runtime.validation.started` | validator 실행 시작 |
| `runtime.validation.result` | validation result 발생 |
| `runtime.validation.warning` | warning severity 결과 |
| `runtime.validation.failed` | error severity 결과 또는 validator 실패 |
| `runtime.validation.completed` | validator 실행 완료 |

### Activation

| Event type | 의미 |
|---|---|
| `runtime.activation.parsed` | activation contract 파싱 완료 |
| `runtime.activation.schema_invalid` | schema validation error |
| `runtime.activation.reference_resolved` | activation reference 해소 |
| `runtime.activation.missing_reference` | activation reference 미해소 |
| `runtime.activation.loader_profile_invalid` | loader profile 미해소 |
| `runtime.activation.duplicate_reference` | duplicate activation reference warning |
| `runtime.activation.empty_set` | empty activation set info |

### Context Loading

| Event type | 의미 |
|---|---|
| `runtime.context.profile_selected` | semantic loader profile 선택 |
| `runtime.context.chunk_extracted` | context chunk 추출 |
| `runtime.context.excluded` | profile 또는 budget에 의해 chunk 제외 |
| `runtime.context.budget_soft_exceeded` | soft budget 초과 |
| `runtime.context.budget_hard_exceeded` | hard budget 초과로 제외 발생 |
| `runtime.context.provenance_recorded` | path/line 기반 provenance 기록 |

## 이벤트 스키마 후보

```json
{
  "schema_version": "aios.runtime_event.v0",
  "event_id": "evt_01H...",
  "trace_id": "trc_01H...",
  "parent_trace_id": null,
  "timestamp": "2026-05-23T12:34:56.000Z",
  "event_type": "runtime.validation.warning",
  "command": "validate",
  "phase": "validation",
  "status": "warn",
  "severity": "warning",
  "code": "weak_reference_path",
  "message": "Agent reference is not a canonical .ai path.",
  "target": {
    "kind": "agent",
    "label": "developer",
    "path": ".ai/agents/developer.agent.md"
  },
  "provenance": {
    "path": ".ai/agents/developer.agent.md",
    "line_start": 12,
    "line_end": 12
  },
  "details": {
    "validator": "agent",
    "reference": ".ai/validators/developer_skill_validator.md"
  }
}
```

## 필드 정의

| 필드 | 필수 | 설명 |
|---|---|---|
| `schema_version` | yes | 이벤트 스키마 버전. 초기 후보는 `aios.runtime_event.v0` |
| `event_id` | yes | 이벤트 단위 고유 ID |
| `trace_id` | yes | 같은 명령 또는 명령 체인을 묶는 trace ID |
| `parent_trace_id` | no | 부모 명령 또는 부모 phase trace ID |
| `timestamp` | yes | ISO 8601 UTC timestamp |
| `event_type` | yes | taxonomy의 안정적 이벤트 이름 |
| `command` | yes | `inspect`, `inventory`, `validate`, `activation`, `load-context` |
| `phase` | no | `discovery`, `validation`, `activation`, `context_loading`, `budget_filtering` 등 |
| `status` | no | `pass`, `warn`, `fail` |
| `severity` | no | `info`, `warning`, `error` |
| `code` | no | 안정적인 machine-readable code |
| `message` | no | 사람이 읽을 수 있는 설명 |
| `target` | no | envelope v2 target과 호환되는 대상 객체 |
| `provenance` | no | path와 line 범위 기반 출처 |
| `details` | no | 명령별 구조화 데이터 |

## Trace 모델

### 기본 trace

단일 명령 실행은 하나의 `trace_id`를 가진다.

```text
trace_id: trc_validate_...
  runtime.command.started
  runtime.inventory.discovery_started
  runtime.validation.target_selected
  runtime.validation.result
  runtime.command.completed
```

### parent trace

미래 command chain이나 orchestration에서는 부모 명령 trace를 자식 명령 trace의 `parent_trace_id`로 연결한다.

```text
trc_orchestration_root
  trc_inventory_child
  trc_activation_child
  trc_validate_child
  trc_load_context_child
```

현재 AIOS는 orchestration을 실행하지 않으므로, 이 관계는 미래 호환성 필드로만 정의한다.

### Provenance relationship

`provenance`는 이벤트가 참조한 원천 파일 범위를 표현한다.

```json
{
  "path": ".ai/rules/rules.md",
  "line_start": 1,
  "line_end": 182,
  "semantic_layer": "runtime_policy"
}
```

context chunk, excluded chunk, validate result, activation reference resolution은 모두 provenance를 가질 수 있다.

## Envelope v2와의 관계

Envelope v2는 명령의 최종 결과이고, 이벤트는 실행 중 관측 기록이다.

권장 관계:

- `runtime.command.completed` 이벤트의 `details.summary`는 envelope v2의 `summary`와 호환된다.
- message 기반 이벤트는 envelope v2 `messages[]`로 축약 가능해야 한다.
- envelope v2 `meta`에는 미래에 `trace_id`를 추가할 수 있다.
- 이벤트 스트림이 없어도 기존 envelope v2 출력은 완전해야 한다.

## Semantic loader provenance와의 관계

`load-context`의 chunk와 excluded item은 이미 path, semantic_layer, line_start, line_end, chars, reason을 가진다.

이벤트 변환 후보:

- chunk 포함: `runtime.context.chunk_extracted`
- profile 제외: `runtime.context.excluded` with `details.reason = "excluded_by_profile"`
- budget 제외: `runtime.context.excluded` with `details.reason = "budget_excluded_low_priority"`
- hard budget warning: `runtime.context.budget_hard_exceeded`
- soft budget warning: `runtime.context.budget_soft_exceeded`

콘텐츠 truncation은 현재 구현하지 않으므로 `truncated_chunks`는 0으로 유지된다.

## Activation validation과의 관계

Activation issue와 reference는 이벤트로 자연스럽게 변환할 수 있다.

| 현재 code 또는 상태 | 이벤트 후보 |
|---|---|
| unknown reference | `runtime.activation.missing_reference` |
| unknown loader profile | `runtime.activation.loader_profile_invalid` |
| duplicate reference | `runtime.activation.duplicate_reference` |
| empty category list | `runtime.activation.empty_set` |
| schema error | `runtime.activation.schema_invalid` |
| resolved reference | `runtime.activation.reference_resolved` |

이벤트는 activation file을 변형하지 않고, inventory resolution 결과만 기록한다.

## Future CLI compatibility

후보 옵션:

```powershell
python -m aios validate --json --envelope-v2 --trace
python -m aios load-context .ai/rules/rules.md --json --emit-events --event-format jsonl
```

옵션 의미:

| 옵션 | 의미 |
|---|---|
| `--trace` | envelope v2 `meta.trace_id`와 trace summary를 포함한다. |
| `--emit-events` | 이벤트 스트림을 출력한다. |
| `--event-format jsonl` | 이벤트를 JSON Lines로 출력한다. |

호환성 정책:

- 이벤트 출력은 opt-in이어야 한다.
- `--emit-events`는 기본 JSON 결과를 깨지 않아야 한다.
- 같은 stdout에 결과 JSON과 JSONL 이벤트를 섞지 않는 방향이 안전하다.
- 향후 필요하면 `--events-file <path>`를 별도 설계할 수 있지만, 이번 계획의 비목표이다.

## 비목표

이번 계획은 다음을 구현하지 않는다.

- runtime execution
- event persistence
- live telemetry
- analytics pipeline
- network logging
- distributed tracing
- sync
- manifest generation
- adapter generation
- orchestration
- worker dispatch
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source file mutation

## 완료 기준

- 현재 observable runtime output이 감사되었다.
- event taxonomy 후보가 정의되었다.
- event schema 후보가 정의되었다.
- trace_id, parent_trace_id, command chain, provenance 관계가 정의되었다.
- envelope v2, semantic loader, activation validation, future orchestration과의 관계가 정의되었다.
- future CLI compatibility가 opt-in 중심으로 제안되었다.
