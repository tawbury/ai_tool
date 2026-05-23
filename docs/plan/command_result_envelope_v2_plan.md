# Command Result Envelope v2 계획

## 목적

AIOS runtime command의 future JSON output을 위한 통합 result envelope v2를 설계한다.

대상 command:

- `inspect`
- `inventory`
- `validate`
- `activation`
- `load-context`

현재 public JSON shape는 유지한다. 이 문서는 구현 계획이며 runtime code를 변경하지 않는다.

## 설계 원칙

- Backward compatibility를 우선한다.
- 기존 v0/v1 command schema는 즉시 변경하지 않는다.
- v2 envelope는 opt-in으로 시작한다.
- 모든 command는 같은 top-level field를 가져야 한다.
- command-specific data는 `payload` 아래에 둔다.
- warning/status naming은 v2에서 정규화한다.
- read-only command boundary를 유지한다.

## Unified Envelope v2 후보

```json
{
  "schema_version": "aios.command_result.v2",
  "command": "validate",
  "status": "pass",
  "root": "D:\\development\\_templates\\ai_tool",
  "target": {
    "kind": "repository",
    "label": "repository",
    "path": null
  },
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 5,
    "results": 5
  },
  "messages": [],
  "payload": {},
  "meta": {
    "legacy_schema_version": "aios.validate.result.v0",
    "summary_only": true
  }
}
```

## Top-level Fields

| Field | Required | 설명 |
|---|---|---|
| `schema_version` | yes | v2 envelope schema. 값은 `aios.command_result.v2` |
| `command` | yes | `inspect`, `inventory`, `validate`, `activation`, `load-context` |
| `status` | yes | canonical command status |
| `root` | yes | repository root |
| `target` | yes | command target object. repository command도 명시 |
| `summary` | yes | command summary |
| `messages` | yes | normalized message list |
| `payload` | yes | command-specific result body |
| `meta` | yes | schema compatibility, options, omitted counts 등 metadata |

## Canonical Status

v2 canonical status는 다음 세 가지이다.

- `pass`
- `warn`
- `fail`

Migration policy:

- 기존 `warning`은 v2에서 `warn`으로 변환한다.
- 기존 `info` check status는 command status가 아니라 message severity로 보존한다.
- 기존 `validate`의 `warn`은 그대로 유지한다.
- 기존 schema에서는 status 값을 바꾸지 않는다.

Compatibility:

- v0/v1 output은 기존 status convention을 유지한다.
- v2 envelope에서만 canonical status를 적용한다.
- `meta.legacy_status`를 둘 수 있다.

## Message Model

v2 message object는 다음 field를 가진다.

```json
{
  "code": "missing_reference_path",
  "severity": "error",
  "status": "fail",
  "message": "Reference does not exist.",
  "path": ".ai/agents/developer.agent.md",
  "line": 12,
  "details": {
    "field": "validators",
    "reference": ".ai/validators/developer_skill_validator.md"
  }
}
```

| Field | Required | 설명 |
|---|---|---|
| `code` | yes | stable machine-readable code |
| `severity` | yes | `error`, `warning`, `info` |
| `status` | yes | `fail`, `warn`, `pass` |
| `message` | yes | human-readable message |
| `path` | no | related path |
| `line` | no | related line |
| `details` | no | command-specific structured details |

Mapping rules:

- `inspect.checks[].id` -> `messages[].code`
- `inspect.checks[].source` -> `messages[].path`
- `validate.results[]` -> direct mapping with `validator` in details
- `activation.issues[]` -> direct mapping with `field`, `reference` in details
- `load-context.warnings[]` -> severity `warning`, status `warn`
- inventory may emit empty `messages` unless future integrity warnings exist

## Target Model

v2 target object 후보:

```json
{
  "kind": "repository",
  "label": "repository",
  "path": null
}
```

Command별 mapping:

- `inspect`: `{ "kind": "repository", "label": "repository", "path": null }`
- `inventory`: `{ "kind": "repository", "label": "repository", "path": null }`
- `validate`: existing `target` object를 보존하고 missing key를 보충
- `activation`: `{ "kind": "activation", "label": "<path>", "path": "<path>" }`
- `load-context`: `{ "kind": "file", "label": "<target>", "path": "<target>" }`

## Command-specific Payload Mapping

### Inspect

Current:

- top-level `checks`

v2:

```json
{
  "payload": {
    "checks": []
  }
}
```

`summary_only`인 경우:

- `payload.checks`는 omitted 가능
- `meta.omitted_payload.checks`에 omitted count 기록 가능

### Inventory

Current:

- top-level `items`

v2:

```json
{
  "payload": {
    "items": []
  }
}
```

`summary.counts`는 현행 유지 가능하다.

### Validate

Current:

- top-level `results`
- summary-only에서 `errors`, `warnings`, `info`

v2:

```json
{
  "messages": [],
  "payload": {
    "results": []
  }
}
```

`payload.results`는 compatibility용으로 둘 수 있고, normalized consumer는 `messages`를 사용한다.

### Activation

Current:

- top-level `issues`
- optional `activation`
- optional `references`

v2:

```json
{
  "messages": [],
  "payload": {
    "activation": {},
    "references": []
  }
}
```

`issues`는 `messages`로 정규화한다.

### Load-context

Current:

- top-level `warnings`
- top-level `budget`
- optional `chunks`
- optional `excluded`

v2:

```json
{
  "messages": [],
  "payload": {
    "chunks": [],
    "excluded": [],
    "budget": {}
  }
}
```

Budget은 command-specific payload에 두되, summary에 `chars`, `chunks`, `excluded`, `warnings` count를 유지한다.

## Summary Policy

`summary`는 command-specific key를 허용한다. 단 공통 count key는 가능한 같은 이름을 사용한다.

권장 공통 key:

- `errors`
- `warnings`
- `info`
- `results`
- `items`
- `chunks`
- `excluded`
- `chars`

Command별 특수 summary는 유지 가능하다.

예:

- inventory `counts`
- activation `inactive_counts`
- load-context budget summary는 payload budget에 유지

## Meta Field

`meta`는 compatibility와 output shaping 정보를 담는다.

후보:

```json
{
  "legacy_schema_version": "aios.semantic_loader.bundle.v0",
  "legacy_status": "warning",
  "summary_only": true,
  "include_content": false,
  "omitted_payload": {
    "chunks": 1,
    "excluded": 0
  }
}
```

## Migration Strategy

### Phase 1: Planning

- v2 envelope 문서를 확정한다.
- 기존 command output은 변경하지 않는다.

### Phase 2: Opt-in

Future CLI option 후보:

```powershell
python -m aios validate --json --envelope-v2
python -m aios load-context .ai/rules/rules.md --json --envelope-v2
```

정책:

- `--envelope-v2`는 `--json`과 함께만 유효하다.
- 기존 `--summary-only`, `--no-content`, `--include-pass` 의미는 유지한다.
- v2 output에는 `meta.summary_only` 등을 기록한다.

### Phase 3: Dual Support

- 기존 v0/v1 schema와 v2 envelope를 함께 지원한다.
- 문서와 report에서 v2 migration examples를 제공한다.
- downstream consumer가 v2로 이동할 시간을 둔다.

### Phase 4: Default 전환 후보

- compatibility 기간 후 v2를 default JSON으로 전환할 수 있다.
- 기존 schema는 `--legacy-json` 같은 opt-in으로 유지할 수 있다.
- 전환 전 ADR 또는 runtime rules update가 필요하다.

## Backward Compatibility

현재 public JSON shape는 바꾸지 않는다.

금지:

- 기존 schema_version 변경
- 기존 top-level field 제거
- 기존 status 값 변경
- 기존 summary-only 동작 변경

허용 후보:

- future opt-in `--envelope-v2`
- existing output에 breaking change 없는 additive metadata 추가
- documentation-only migration examples

## Non-goals

이 계획은 다음을 구현하지 않는다.

- schema migration implementation
- runtime code changes
- sync
- manifest
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source file mutation

## 완료 기준

- current command JSON shape 차이가 문서화된다.
- v2 envelope top-level field가 정의된다.
- canonical status와 message model이 정의된다.
- command-specific payload mapping이 정의된다.
- opt-in migration strategy가 정의된다.
- runtime code는 변경하지 않는다.
