# Phase 7 Sync Dry-run Implementation Plan

## 개요

이 문서는 Roadmap v1.2 Phase 7의 첫 구현 후보인 future `aios sync --dry-run`을 계획한다. Phase 6 safety design은 완료되었지만, Phase 7 implementation은 아직 시작하지 않는다. 이 문서는 구현 전 scope, CLI, input, output, evaluation pipeline, module boundary, test strategy, pre-implementation gate를 고정하기 위한 planning artifact이다.

현재 시스템은 read-only이다. 이 문서는 runtime code를 변경하지 않으며 sync execution, manifest persistence, transaction logs, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Phase 7 Implementation Scope

Phase 7의 첫 구현 범위는 `aios sync --dry-run` only이다.

허용 범위:

- read-only evaluation
- manifest file 또는 manifest preview load
- `.ai` source file 존재 확인
- target file 존재 확인
- marker parsing
- source/target hash 계산
- drift/conflict classification
- native JSON output
- envelope v2 output
- human summary output
- exit code policy 적용

금지 범위:

- target file mutation
- manifest write
- transaction log write
- rollback execution
- adapter generation
- force update
- decommission
- source mutation

## CLI Shape

초기 CLI 후보:

```bash
python -m aios sync --dry-run
python -m aios sync --dry-run --json
python -m aios sync --dry-run --json --envelope-v2
```

미래 선택 옵션:

```bash
python -m aios sync --dry-run --manifest <path>
```

CLI 정책:

- `sync`는 `--dry-run` 없이 실행되면 명확한 error를 반환해야 한다.
- `--dry-run`은 read-only evaluation만 수행한다.
- `--json --envelope-v2`는 기존 envelope v2 규칙을 따른다.
- `--envelope-v2`는 다른 명령과 동일하게 `--json`을 요구해야 한다.
- `--manifest <path>`가 없으면 default manifest candidate 또는 manifest preview strategy를 사용한다. 이 동작은 Phase 7 구현 전 별도 확정해야 한다.

## Input Sources

### Manifest File or Manifest Preview

`aios sync --dry-run`은 managed entry 목록을 필요로 한다.

가능한 input mode:

- explicit manifest file: `--manifest <path>`
- default manifest candidate path
- generated manifest preview

Phase 7 첫 구현 전 결정 필요:

- manifest persistence가 없을 때 dry-run이 어떤 manifest preview를 사용할지
- default manifest path가 존재하지 않을 때 status를 `fail`로 할지, preview unavailable로 처리할지
- manifest preview generator를 구현 범위에 포함할지

권장:

- Phase 7 첫 구현은 explicit fixture manifest 또는 read-only manifest file input을 우선한다.
- manifest write와 preview generation은 구현하지 않는다.

### `.ai` Source Files

source files는 manifest entry의 `source_path` 또는 `source_paths`에서 온다.

검사:

- path가 repository root 안에 있는지
- source가 존재하는지
- source hash가 manifest expected hash와 비교 가능한지

source missing은 blocking conflict이다.

### Target Files

target files는 manifest entry의 `target_path`에서 온다.

검사:

- target 존재 여부
- target ownership
- sync mode
- whole-file 또는 managed-block hash 대상

target 존재 여부는 create, skip, conflict, drift-stop classification에 영향을 준다.

### Marker Parser Result

mixed-boundary와 managed-block mode에서는 marker parser result가 필요하다.

필수 parser result:

- expected
- present
- count
- entry_id
- marker_version
- begin_line
- end_line
- integrity
- problems

marker structural failure는 hash comparison보다 먼저 conflict로 처리한다.

## Output Contract

### Native Schema

native JSON schema version:

```text
aios.sync_dry_run.v0
```

top-level fields:

- `schema_version`
- `status`
- `root`
- `mode`
- `manifest_path`
- `summary`
- `results`
- `messages`
- `meta`

result item fields:

- `entry_id`
- `action`
- `severity`
- `stop_reason`
- `recovery_hint`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `drift_state`
- `hashes`
- `marker`
- `details`

### Envelope v2 Mapping

`--json --envelope-v2` mapping:

- `schema_version`: `aios.command_result.v2`
- `command`: `sync`
- `status`: native status와 동일한 `pass`, `warn`, `fail`
- `root`: repository root
- `target`: manifest path 또는 repository root
- `summary`: dry-run summary counters
- `messages`: dry-run messages
- `payload.results`: dry-run result items
- `meta.dry_run`: true
- `meta.legacy_schema_version`: `aios.sync_dry_run.v0`
- `meta.manifest_path`: manifest path 또는 null

### Status Policy

status mapping:

| Condition | Status |
|---|---|
| any blocking result | `fail` |
| warning results only | `warn` |
| safe create/update/skip only | `pass` |

### Exit Code Policy

권장 exit code:

| Status | Exit code | 설명 |
|---|---:|---|
| `pass` | 0 | safe dry-run candidates only |
| `warn` | 0 | warnings exist but no blocking conflict |
| `fail` | 1 | blocking drift/conflict exists |
| CLI usage error | 2 | invalid option or `--envelope-v2` without `--json` |

주의:

- dry-run은 mutation command가 아니므로 warning은 실패가 아니다.
- blocking drift/conflict는 future write가 불가능하므로 fail exit가 적절하다.

## Evaluation Pipeline

### 1. Resolve Repository Root

기존 AIOS command pattern을 따른다.

결과:

- root path
- command target metadata

### 2. Load Manifest or Preview

입력:

- `--manifest <path>` 또는 default policy

검사:

- file exists
- readable
- supported schema version

실패:

- manifest missing: `fail` 또는 explicit planning decision 필요
- manifest invalid: `fail`

### 3. Validate Manifest Schema

검사:

- required top-level fields
- required managed entry fields
- enum values
- path shape
- hash shape
- ownership/sync mode compatibility

출력:

- blocking result 또는 command-level message

### 4. Evaluate Source Existence and Hashes

entry별 검사:

- source exists
- source hash computed
- expected source hash compared when available

classification:

- source missing -> `conflict`, blocking, `source-missing`
- source changed with clean target -> update candidate or informational detail

### 5. Inspect Target Existence

entry별 검사:

- target exists
- target missing
- target unmanaged

classification:

- target missing with first-create policy -> `create`
- target missing without policy clarity -> `conflict`
- unmanaged target -> `skip`, warning, `unmanaged-target`

### 6. Parse Markers

entry별 검사:

- marker expected by sync mode
- marker pair count
- entry_id match
- marker_version support
- nested/overlap/malformed conditions
- code fence exclusion policy

classification:

- valid marker -> hash comparison
- missing marker -> conflict or create depending on first-create policy
- duplicated marker -> conflict
- corrupted marker -> conflict

### 7. Compute Target Hashes

hash scope:

- `whole-file`: whole target hash
- `managed-block`: marker inner content hash
- `mixed-boundary`: marker inner content hash

Phase 7 implementation must not choose normalization implicitly. Hash normalization decision is a pre-implementation gate.

### 8. Classify Drift and Conflict

classification rules:

- target hash matches expected and generated differs -> `update`
- target hash matches expected and generated same -> `skip`
- target hash differs from expected -> `drift-stop`
- marker structural issue -> `conflict`
- ownership violation -> `conflict`
- orphan marker -> `orphan-warning`

### 9. Emit Dry-run Results

outputs:

- human output
- native JSON
- envelope v2 JSON

Result ordering should be deterministic:

1. manifest entry order
2. observed unmanaged/orphan findings by canonical path

## Implementation Module Candidates

후보 package:

```text
src/aios/sync/
  __init__.py
  manifest.py
  dry_run.py
  markers.py
  hash.py
  result.py
```

### `manifest.py`

책임:

- manifest file load
- manifest schema parsing
- managed entry model
- schema version validation
- enum validation

비책임:

- manifest write
- manifest persistence
- source generation

### `dry_run.py`

책임:

- evaluation pipeline orchestration
- entry ordering
- drift/conflict classification
- dry-run summary calculation

비책임:

- file mutation
- adapter generation
- transaction log write

### `markers.py`

책임:

- marker parser
- marker integrity result model
- code fence exclusion
- line number preservation
- marker state classification

비책임:

- marker insertion
- marker repair
- marker deletion

### `hash.py`

책임:

- source hash calculation
- target whole-file hash calculation
- managed block content hash calculation
- hash prefix formatting

비책임:

- hash normalization policy 결정

### `result.py`

책임:

- native `aios.sync_dry_run.v0` model
- message generation
- summary counters
- envelope v2 payload mapping helpers
- exit status derivation

비책임:

- CLI parsing
- execution of sync

## Pre-implementation Gates

Phase 7 implementation 전 반드시 완료해야 하는 planning gate:

### Manifest Schema Precision

필요 산출물:

- `docs/plan/sync_manifest_schema_and_validation_plan.md`

결정 항목:

- schema version
- required fields
- nullable fields
- enum values
- hash fields
- marker fields
- manifest validation strategy

### Marker Parser Fixture

필요 산출물:

- `docs/plan/managed_block_parser_fixture_plan.md`

결정 항목:

- valid fixture set
- invalid fixture set
- code fence policy fixture
- duplicate/nested/malformed examples
- expected parser output shape

### Hash Normalization Decision

결정 항목:

- observed bytes vs decoded text
- CRLF/LF normalization
- trailing newline policy
- marker line exclusion implementation detail

### Insertion Anchor Contract

결정 항목:

- anchor syntax
- first-create policy
- missing anchor conflict code
- duplicated anchor conflict code
- unmanaged target insertion ban

### Manifest Validation Strategy

결정 항목:

- `aios validate <manifest>` 지원 여부
- sync dry-run 내부 validation과 validate command의 역할 분리
- invalid manifest status and exit code
- manifest target discovery policy

## Future Tests and Validation Commands

Phase 7 구현 시 추가할 테스트 후보:

- manifest schema valid fixture
- manifest schema invalid fixture
- source missing fixture
- clean update candidate fixture
- target modified drift-stop fixture
- marker missing conflict fixture
- marker duplicated conflict fixture
- marker corrupted conflict fixture
- unmanaged target skip fixture
- orphan marker warning fixture
- fenced code block marker-looking text ignored fixture
- envelope v2 mapping fixture
- `--envelope-v2` without `--json` usage error fixture

미래 검증 명령 후보:

```bash
python -m aios sync --dry-run
python -m aios sync --dry-run --json
python -m aios sync --dry-run --json --envelope-v2
python -m aios sync --dry-run --manifest .ai/templates/sync-manifest.example.json --json
python -m aios sync --envelope-v2
python -m aios inspect
python -m aios validate
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
```

예상:

- `python -m aios sync --envelope-v2`는 `--json`이 없으므로 exit code 2.
- `python -m aios sync`는 `--dry-run`이 없으므로 Phase 7에서 clear error로 exit code 2.

## Explicit Non-goals

Phase 7 dry-run implementation plan은 다음을 구현하거나 허용하지 않는다.

- mutation
- sync apply
- manifest write
- manifest persistence
- transaction log persistence
- rollback execution
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation

## Implementation Readiness Decision

Phase 7 dry-run implementation planning은 시작 가능하다.

Phase 7 code implementation은 다음 문서가 완료된 뒤 시작해야 한다.

- sync manifest schema and validation plan
- managed block parser fixture plan
- hash normalization decision
- insertion anchor contract

이 gate가 없으면 implementation 중 임의 결정이 발생하고, sync safety contract가 흔들릴 수 있다.
