# Managed Block Marker Contract

## 개요

이 문서는 `.ai OS` Phase 6의 future mixed-boundary sync를 위한 managed block marker 계약을 정의한다. 현재 시스템은 read-only이며, 이 문서는 parser 구현이나 파일 변경이 아니라 향후 안전한 dry-run과 sync 설계를 위한 사전 계약이다.

이 문서는 sync execution, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, rollback, force, source mutation을 구현하지 않는다.

## Marker 목적

### Mixed-boundary Safety

mixed-boundary target은 user-owned content와 runtime-managed block이 같은 파일 안에 공존하는 상태이다. marker는 future sync가 어느 범위만 관리할 수 있는지 제한한다.

원칙:

- marker 밖 content는 user-owned로 취급한다.
- marker 안 content만 managed block 후보이다.
- marker 경계가 모호하면 future write는 중단한다.

### Managed Ownership Identity

marker는 target file 안에서 manifest entry와 managed block을 연결하는 local identity이다.

필수 identity:

- `entry_id`
- `marker_version`

선택 identity:

- `generated_by`

`entry_id`는 manifest managed entry의 `entry_id`와 정확히 일치해야 한다.

### Drift Detection

marker는 managed block hash를 계산할 경계를 제공한다.

drift detection은 다음을 구분해야 한다.

- marker가 유효하고 managed block hash가 manifest target hash와 일치함
- marker는 유효하지만 managed block hash가 manifest target hash와 다름
- marker가 없거나 중복되거나 손상됨

### Dry-run Explainability

dry-run result는 marker 상태를 사람이 이해할 수 있게 설명해야 한다.

예:

- `marker.valid`
- `marker.missing`
- `marker.duplicated`
- `marker.corrupted`

## Canonical Marker Syntax

canonical marker는 line-oriented comment syntax를 사용한다. begin marker와 end marker는 각각 한 줄 전체를 차지해야 한다.

### Markdown / HTML Comment Style

Markdown, HTML-compatible text, root adapter Markdown 파일의 기본 형식이다.

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 generated_by=aios.sync.v0 -->
Generated managed content.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

필수 속성:

- `entry_id`
- `marker_version`

선택 속성:

- `generated_by`

### Plain Text Style

plain text에서 comment syntax가 명확하지 않을 때 사용하는 후보 형식이다.

```text
# AIOS:BEGIN managed-block entry_id=entry_plain_text_rules marker_version=0 generated_by=aios.sync.v0
Generated managed content.
# AIOS:END managed-block entry_id=entry_plain_text_rules marker_version=0
```

plain text style은 target file format이 `#` line comment를 허용하거나 사람이 명확히 marker로 볼 수 있는 경우에만 future policy로 허용한다.

### YAML Comment Style

YAML target에서 필요할 경우 사용하는 후보 형식이다.

```yaml
# AIOS:BEGIN managed-block entry_id=entry_yaml_rules marker_version=0 generated_by=aios.sync.v0
generated:
  value: example
# AIOS:END managed-block entry_id=entry_yaml_rules marker_version=0
```

YAML comment style은 YAML parser가 marker lines를 comment로 보존하지 않을 수 있음을 고려해야 한다. future sync는 source text 기반으로 marker를 찾아야 하며 YAML object model만으로 marker를 판단하면 안 된다.

## Marker Attribute Rules

### `entry_id`

규칙:

- begin marker와 end marker에 모두 있어야 한다.
- begin marker와 end marker의 값이 동일해야 한다.
- manifest entry의 `entry_id`와 동일해야 한다.
- 공백을 포함하지 않는 stable identifier여야 한다.

권장 형식:

```text
entry_<target_kind>_<purpose>
```

예:

- `entry_codex_root_adapter_rules`
- `entry_claude_root_adapter_rules`
- `entry_gemini_root_adapter_rules`

### `marker_version`

규칙:

- begin marker와 end marker에 모두 있어야 한다.
- 초기 후보 값은 `0`이다.
- marker syntax가 breaking change를 갖는 경우 version을 올려야 한다.

### `generated_by`

규칙:

- begin marker에만 있어도 된다.
- end marker에는 없어도 된다.
- 값은 future generator identity를 표현한다.
- drift 판단의 필수 조건은 아니다.

## Valid Marker Examples

### Markdown Valid Example

```markdown
Before user-owned content.

<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 generated_by=aios.sync.v0 -->
Managed content.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->

After user-owned content.
```

유효 조건:

- begin/end pair가 정확히 하나이다.
- `entry_id`가 일치한다.
- `marker_version`이 일치한다.
- marker가 code fence 밖에 있다.

### Plain Text Valid Example

```text
Local notes above.

# AIOS:BEGIN managed-block entry_id=entry_plain_text_rules marker_version=0 generated_by=aios.sync.v0
Managed content.
# AIOS:END managed-block entry_id=entry_plain_text_rules marker_version=0

Local notes below.
```

### YAML Valid Example

```yaml
manual: true

# AIOS:BEGIN managed-block entry_id=entry_yaml_rules marker_version=0 generated_by=aios.sync.v0
generated:
  enabled: true
# AIOS:END managed-block entry_id=entry_yaml_rules marker_version=0
```

## Invalid Marker Examples

### Missing Begin

```markdown
Managed content.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

결과:

- marker integrity: `corrupted`
- action: `conflict`
- stop reason: `marker-corrupted`

### Missing End

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
Managed content.
```

결과:

- marker integrity: `corrupted`
- action: `conflict`
- stop reason: `marker-corrupted`

### Mismatched `entry_id`

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
Managed content.
<!-- AIOS:END managed-block entry_id=entry_other marker_version=0 -->
```

결과:

- marker integrity: `corrupted`
- action: `conflict`
- stop reason: `marker-corrupted`

### Duplicate Marker

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
First block.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->

<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
Second block.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

결과:

- marker integrity: `duplicated`
- action: `conflict`
- stop reason: `marker-duplicated`

### Nested Marker

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_outer marker_version=0 -->
Outer content.
<!-- AIOS:BEGIN managed-block entry_id=entry_inner marker_version=0 -->
Inner content.
<!-- AIOS:END managed-block entry_id=entry_inner marker_version=0 -->
<!-- AIOS:END managed-block entry_id=entry_outer marker_version=0 -->
```

결과:

- marker integrity: `corrupted`
- action: `conflict`
- stop reason: `marker-corrupted`

### Malformed Marker

```markdown
<!-- AIOS BEGIN entry_id entry_codex_root_adapter_rules -->
Managed content.
<!-- AIOS END -->
```

결과:

- marker integrity: `corrupted`
- action: `conflict`
- stop reason: `marker-corrupted`

## Parser Expectations

Future marker parser는 conservative parser여야 한다.

필수 기대:

- target file을 line-oriented text로 읽는다.
- line number를 보존한다.
- 같은 `entry_id`에 대해 정확히 하나의 begin/end pair만 허용한다.
- begin marker와 end marker의 `entry_id`와 `marker_version`을 비교한다.
- marker 안 content boundary를 byte 또는 line span으로 보존한다.
- ambiguity가 있으면 fail closed 한다.

### Exactly One Pair

각 manifest entry의 `entry_id`는 target file 안에서 다음 중 하나여야 한다.

- 정확히 하나의 valid begin/end pair
- 전혀 없음

둘 이상의 pair는 `marker-duplicated`이다. begin만 있거나 end만 있으면 `marker-corrupted`이다.

### Preserve Line Numbers

dry-run, envelope v2 message, observability event는 line number를 사용할 수 있어야 한다.

권장 marker object:

```json
{
  "expected": true,
  "present": true,
  "count": 1,
  "entry_id": "entry_codex_root_adapter_rules",
  "marker_version": "0",
  "begin_line": 4,
  "end_line": 12,
  "integrity": "valid",
  "problems": []
}
```

### Code Fence Policy

Markdown parser expectation:

- 기본적으로 fenced code block 안의 marker-looking text는 marker로 해석하지 않는다.
- code fence 안 marker parsing은 별도 explicit policy 없이는 허용하지 않는다.
- code fence boundary가 불명확하면 fail closed 하거나 marker candidate를 무시해야 한다. future implementation은 이 동작을 명시해야 한다.

이 정책은 문서가 marker 예시를 포함할 때 실제 managed block으로 오인하지 않기 위함이다.

### Fail Closed

다음 ambiguity는 모두 blocking conflict로 분류한다.

- overlapping marker
- nested marker
- mismatched `entry_id`
- mismatched `marker_version`
- malformed attribute syntax
- duplicate begin marker
- duplicate end marker
- begin/end order reversal

## Hash Boundary

### Recommended Policy

managed block hash는 marker line 자체를 제외하고 begin marker와 end marker 사이의 content만 포함한다.

즉, 다음 예에서 hash 대상은 `Managed content.` 줄뿐이다.

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
Managed content.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

### Rationale

marker line을 hash에서 제외하는 이유:

- marker metadata가 바뀌어도 managed content drift와 구분할 수 있다.
- `generated_by` 같은 provenance metadata 변경이 content drift로 오판되지 않는다.
- begin/end marker syntax migration을 content drift와 분리할 수 있다.

보완 규칙:

- marker line 자체의 무결성은 별도 marker integrity check로 검증한다.
- `entry_id` 또는 `marker_version` mismatch는 hash 비교 전에 blocking conflict이다.
- marker line 변경이 syntax 또는 identity를 깨뜨리면 `marker-corrupted`이다.

### Line Ending and Encoding

future hash policy는 deterministic해야 한다.

권장:

- UTF-8 text를 기준으로 한다.
- managed block content hash 계산 전 line ending normalization 여부를 manifest schema에 명시한다.
- 초기 설계 후보는 observed bytes 기반 hash를 권장한다. line ending normalization은 cross-platform churn을 줄일 수 있지만, 실제 파일 변경 감지를 약화시킬 수 있으므로 별도 결정이 필요하다.

## Insertion Policy

Insertion은 Phase 6에서 구현하지 않는다. future dry-run에서만 candidate로 표시할 수 있다.

조건:

- explicit insertion anchor가 있어야 한다.
- manifest entry가 first-create를 허용해야 한다.
- target ownership이 `mixed-boundary`이고 block insertion이 policy로 허용되어야 한다.
- target이 user-owned only이면 insertion candidate가 될 수 없다.

금지:

- marker가 missing이라는 이유만으로 자동 삽입하지 않는다.
- anchor가 불명확하면 `conflict`이다.
- unmanaged target에 자동 marker를 삽입하지 않는다.

## Update Policy

Update candidate가 되려면 다음 조건을 모두 만족해야 한다.

- marker가 valid이다.
- begin/end pair가 정확히 하나이다.
- marker `entry_id`가 manifest entry와 일치한다.
- marker `marker_version`이 지원된다.
- 현재 managed block hash가 manifest `target_hash` 또는 managed block hash와 일치한다.
- generated preview content가 현재 managed block content와 다르다.

하나라도 실패하면:

- marker 문제: `conflict`
- hash drift: `drift-stop`
- unsupported marker version: `conflict`

## Removal Policy

Removal은 forbidden이다.

이유:

- managed block이 더 이상 manifest에 없더라도 사용자가 의도적으로 보존했을 수 있다.
- 자동 삭제는 user-owned context를 훼손할 수 있다.
- decommission policy와 rollback precondition이 없으면 안전하게 제거할 수 없다.

결과:

- orphan marker는 `orphan-warning`만 생성한다.
- future removal은 explicit decommission policy가 설계된 뒤에만 가능하다.

## Dry-run Mapping

| Marker state | 조건 | Action | Severity | Stop reason |
|---|---|---|---|---|
| `valid` | target hash clean, generated content differs | `update` | informational | null |
| `valid` | target hash clean, no generated change | `skip` | informational | null |
| `valid` | managed block hash differs from manifest | `drift-stop` | blocking | `target-modified` |
| `missing` | first-create policy and explicit anchor exist | `create` | informational | null |
| `missing` | expected existing block | `conflict` | blocking | `marker-missing` |
| `duplicated` | same entry_id appears more than once | `conflict` | blocking | `marker-duplicated` |
| `corrupted` | malformed, mismatched, nested, overlapping | `conflict` | blocking | `marker-corrupted` |
| `not-expected` | marker found without manifest entry | `orphan-warning` | warning | `orphaned-managed-block` |

## Compatibility

### Sync Manifest Schema

Manifest entry와 marker는 다음 필드로 연결된다.

- `managed_entries[].entry_id` -> marker `entry_id`
- `managed_entries[].target_path` -> marker를 찾을 target file
- `managed_entries[].target_hash` -> marker content hash 비교 기준
- `managed_entries[].sync_mode` -> marker 필요 여부
- `managed_entries[].ownership` -> marker 밖 content 보호 정책

### Drift Stop Policy

Marker integrity check는 managed block hash check보다 먼저 수행한다.

정렬:

- marker missing, duplicated, corrupted는 conflict이다.
- marker valid 이후 hash mismatch만 drift-stop이다.
- marker 밖 content 변경은 mixed-boundary에서 blocking drift가 아니다.

### Sync Dry-run Schema

Dry-run result의 `marker` object는 이 계약의 parser 결과를 담는다.

필수 mapping:

- `marker.expected`
- `marker.present`
- `marker.count`
- `marker.entry_id`
- `marker.marker_version`
- `marker.begin_line`
- `marker.end_line`
- `marker.integrity`
- `marker.problems`

### Envelope v2

Marker conflict는 envelope v2 message로 변환되어야 한다.

예:

```json
{
  "code": "marker-corrupted",
  "severity": "blocking",
  "status": "fail",
  "message": "Managed block marker is malformed or internally inconsistent.",
  "path": "AGENTS.md",
  "line": 4,
  "details": {
    "entry_id": "entry_codex_root_adapter_rules",
    "marker_version": "0",
    "action": "conflict"
  }
}
```

### Observability Events

Future opt-in events may use marker parser output.

권장 event types:

- `runtime.sync.marker_checked`
- `runtime.sync.marker_missing`
- `runtime.sync.marker_duplicated`
- `runtime.sync.marker_corrupted`
- `runtime.sync.managed_block_hash_checked`
- `runtime.sync.stop_required`

Events must not imply persistence, telemetry, networking, or file mutation.

## Explicit Non-goals

이 계약은 다음을 구현하지 않는다.

- parser implementation
- sync execution
- file mutation
- manifest persistence
- adapter generation
- auto marker repair
- auto-fix
- decommission
- rollback
- force
- auto merge
- automatic conflict resolution
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- source mutation

## Future Gate

Future implementation 전에 필요한 후속 작업:

- marker parser test fixture 설계
- line ending과 hash normalization 최종 결정
- insertion anchor contract 설계
- decommission policy 별도 설계
- runtime-facing sync operation rule로 승격
