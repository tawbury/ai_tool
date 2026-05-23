# Sync Manifest Validation Boundary Audit

## 개요

이 문서는 future sync manifest validation boundary의 위험을 감사한다. 목적은 Phase 7 `aios sync --dry-run` 구현 전에 schema validation, runtime evaluation, command usage error를 분리해 구현 중 임의 결정이 발생하지 않도록 하는 것이다.

현재 시스템은 read-only이다. 이 감사는 manifest generation, manifest persistence, sync apply, mutation, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## 감사 범위

감사 대상:

- schema_version vs manifest_version 혼선
- required/optional/nullability 불명확성
- ownership/sync_mode enum drift
- unsafe path handling
- hash policy ambiguity
- marker metadata와 target marker parsing 혼동
- `aios validate <manifest>`와 `aios sync --dry-run` 책임 혼합
- invalid manifest classification ambiguity
- envelope v2 mapping loss

## Risk Matrix

| Risk | 영향 | 완화 |
|---|---|---|
| schema field name 혼선 | 구현마다 다른 manifest shape 사용 | canonical field를 `schema_version`으로 고정 |
| nullable field 남용 | consumer가 unsafe default 사용 | nullable 허용 필드 제한 |
| enum 확장 임의 결정 | dry-run classification 불안정 | v0 enum 고정, 확장은 v1에서 처리 |
| parent traversal 허용 | repo 밖 파일 관찰 위험 | repository-relative only, `..` 금지 |
| hash normalization 미정 | cross-platform drift 판정 흔들림 | v0 권장 정책 문서화 |
| marker metadata를 실제 marker로 오해 | target 상태 검증 누락 | metadata와 parser result 분리 |
| validate와 dry-run 경계 혼합 | validate가 drift evaluation까지 수행 | schema validation과 runtime evaluation 분리 |
| invalid manifest를 usage error로 오분류 | exit code와 message 혼란 | usage/schema/runtime conflict taxonomy 유지 |

## Schema Naming Risk

### Risk

Phase 6 초안에는 `manifest_version` 후보가 있었고, command result envelope와 다른 runtime documents는 `schema_version`을 사용한다. 두 이름이 혼재하면 future implementation과 JSON consumer가 서로 다른 필드를 기대할 수 있다.

### Mitigation

- canonical field는 `schema_version`이다.
- value는 `aios.sync_manifest.v0`이다.
- `manifest_version`은 future compatibility alias로만 고려한다.
- alias 사용은 warning으로 처리하는 것이 적절하다.

## Required Field Risk

### Risk

required field가 명확하지 않으면 dry-run evaluator가 missing field에 대해 unsafe default를 사용할 수 있다.

예:

- missing `ownership`을 `runtime-managed`로 가정하면 user-owned content를 write candidate로 오판할 수 있다.
- missing `target_hash`를 clean으로 가정하면 drift-stop이 누락된다.

### Mitigation

- top-level required field를 고정한다.
- managed entry required field를 고정한다.
- `target_hash` null은 explicit first-create policy가 있을 때만 허용한다.
- missing required field는 schema error이다.

## Nullable Field Risk

### Risk

nullable field가 많으면 implementation이 null을 허용 가능한 상태로 오해할 수 있다.

### Mitigation

- core identity, path, enum, source_hash는 null 금지.
- `target_hash` null은 first-create candidate policy에만 제한한다.
- `marker` null은 `whole-file` sync mode에서만 허용한다.

## Enum Drift Risk

### Risk

이전 문서에서 `observe-only`, `disabled`, `managed-block`, `whole-file` 같은 후보가 섞여 있었다. Phase 7 v0 manifest에서 enum이 넓으면 dry-run 구현 범위가 커진다.

### Mitigation

v0 ownership enum:

- `runtime-managed`
- `user-owned`
- `mixed-boundary`

v0 sync mode enum:

- `whole-file`
- `managed-block`
- `mixed-boundary`

`observe-only`와 `disabled`는 v0 core sync mode에서 제외한다. 필요하면 future schema revision에서 별도 field로 설계한다.

## Path Validation Risk

### Risk

manifest path가 absolute path 또는 parent traversal을 허용하면 dry-run이 repository 밖 파일을 읽거나 상태를 노출할 수 있다.

### Mitigation

- repository-relative only.
- absolute path 금지.
- `..` parent traversal 금지.
- empty path 금지.
- manifest canonical separator는 `/`.
- resolve는 schema path check 후 수행.
- path normalization이 repository root escape를 허용하면 안 된다.

## Hash Policy Risk

### Risk

hash policy가 불분명하면 같은 파일이 OS나 line ending에 따라 drifted로 보이거나, 실제 drift가 숨겨질 수 있다.

### Mitigation

- hash format은 `sha256:<hex>`로 고정한다.
- algorithm prefix는 required이다.
- digest는 lowercase hex이다.
- v0 권장 정책은 observed UTF-8 bytes 기반이다.
- marker lines는 managed block hash에서 제외한다.
- CRLF/LF normalization은 implicit 적용하지 않는다.

Residual risk:

- observed bytes policy는 cross-platform churn을 만들 수 있다. 이 위험은 hash fixture와 line ending test로 관리해야 한다.

## Marker Metadata Risk

### Risk

manifest marker metadata가 있다고 해서 target marker가 실제로 존재하거나 valid라고 볼 수 없다.

### Mitigation

- manifest `marker`는 expected metadata이다.
- actual marker state는 marker parser가 target file에서 별도로 산출한다.
- `marker.entry_id`는 entry `entry_id`와 같아야 한다.
- marker metadata mismatch는 schema error이다.
- actual marker missing/duplicated/corrupted는 runtime conflict이다.

## Validation Boundary Risk

### `aios validate <manifest>`

Risk:

- validate가 target hash comparison까지 수행하면 dry-run과 역할이 겹친다.

Boundary:

- validate는 schema, path safety, enum, hash format, duplicate entry, marker metadata consistency를 검사한다.
- validate는 full drift evaluation을 하지 않는다.
- source/target existence는 정책에 따라 warning 또는 info가 될 수 있지만 drift-stop classification은 sync dry-run의 책임이다.

### `aios sync --dry-run`

Risk:

- sync dry-run이 schema validation 없이 runtime evaluation을 시작하면 invalid manifest가 unsafe classification을 만들 수 있다.

Boundary:

- sync dry-run은 manifest schema validation을 먼저 수행한다.
- schema error가 있으면 runtime evaluation을 중단한다.
- structurally valid manifest에 대해서만 source, target, marker, hash evaluation을 수행한다.

## Invalid Classification Risk

### Usage Error

CLI usage error와 manifest schema error를 구분해야 한다.

Usage error examples:

- missing option value
- invalid CLI option combination
- `--envelope-v2` without `--json`

Exit code: 2.

### Schema Error

Manifest file 내용이 invalid인 경우이다.

Examples:

- unsupported schema version
- missing required field
- invalid enum
- invalid path traversal
- invalid hash format

Exit code:

- validate command: validate fail policy
- sync dry-run: status `fail`, exit code 1

### Runtime Conflict

Manifest는 valid하지만 현재 repository state가 safe sync를 막는 경우이다.

Examples:

- source missing
- marker corrupted
- target hash mismatch
- ownership violation

Exit code:

- sync dry-run: status `fail`, exit code 1

## Envelope v2 Mapping Risk

### Risk

Manifest validation output과 sync dry-run output이 envelope v2에서 서로 다른 message shape를 사용하면 consumers가 중복 처리해야 한다.

### Mitigation

- `status`는 `pass`, `warn`, `fail`을 사용한다.
- schema errors and runtime conflicts are messages.
- `meta.manifest_schema_version`을 포함한다.
- validate는 `command: validate`, sync dry-run은 `command: sync`로 구분한다.
- native payload는 `payload.results`에 둔다.

## Non-goal Risk

Manifest schema precision이 다음 구현을 허용하는 것으로 오해되면 안 된다.

- manifest generation
- manifest persistence
- sync apply
- mutation
- rollback execution
- adapter generation
- force
- decommission
- source mutation

완화:

- plan과 audit 모두 explicit non-goals를 유지한다.
- schema는 read-only validation과 dry-run evaluation의 input contract로만 사용한다.

## 감사 결론

Manifest schema precision gate는 다음 원칙으로 통과 가능하다.

- canonical field는 `schema_version`.
- schema version은 `aios.sync_manifest.v0`.
- required/nullability/enum/path/hash/marker metadata 정책을 명확히 둔다.
- schema validation과 runtime evaluation을 분리한다.
- invalid manifest는 usage error, schema error, runtime conflict로 분류한다.
- `aios validate <manifest>`는 schema validation을 담당하고 drift-stop은 `aios sync --dry-run`의 runtime evaluation으로 둔다.

남은 Phase 7 gate:

- managed block parser fixture plan
- hash normalization fixture confirmation
- insertion anchor contract
