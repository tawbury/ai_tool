# Phase 7 Sync Dry-run 작업 분해

## 개요

이 문서는 Phase 7 `aios sync --dry-run` 런타임 구현을 시작하기 전 마지막 readiness bundle 산출물이다. 목적은 이미 완료된 Phase 6-7 설계를 구현 가능한 번들 단위, 모듈 경계, fixture 목록, 검증 명령으로 고정하는 것이다.

현재 시스템은 read-only 상태다. 이 문서는 런타임 코드를 수정하지 않으며 sync 실행, manifest persistence, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## 구현 전제

Phase 7의 첫 런타임 구현은 `aios sync --dry-run` only다.

허용 범위:

- manifest 파일 읽기
- manifest schema validation
- source/target existence evaluation
- hash 계산
- managed marker parsing
- drift/conflict classification
- native dry-run result 구성
- JSON 출력
- envelope v2 opt-in mapping
- human summary 출력

금지 범위:

- target file mutation
- manifest write
- transaction log write
- rollback execution
- marker insertion
- marker repair
- adapter generation
- force/decommission
- source mutation

## 번들 경계

### Bundle 1: Manifest/Hash Foundation

목표:

- sync dry-run의 입력 검증과 hash 기반 비교의 foundation을 만든다.

포함:

- `src/aios/sync/` package 생성
- manifest model
- manifest loader
- manifest schema validator
- path safety validator
- hash string validator
- hash calculation helper
- native result primitive 일부
- manifest/hash fixture

제외:

- marker parser
- CLI command registration
- dry-run evaluator orchestration
- envelope v2 wiring
- target mutation
- manifest write

완료 기준:

- manifest schema valid/invalid fixture가 통과한다.
- hash v0 policy fixture가 통과한다.
- `python -m compileall -q src/aios aios`가 통과한다.

### Bundle 2: Managed Marker Parser

목표:

- managed block marker를 read-only analyzer로 파싱한다.

포함:

- marker style detection
- begin/end marker parsing
- marker attribute parsing
- begin/end pairing
- code fence exclusion
- duplicate/nested/malformed classification
- insertion anchor parsing
- parser output model
- marker fixture

제외:

- marker insertion
- marker repair
- marker deletion
- dry-run action final classification
- CLI wiring
- file mutation

완료 기준:

- valid marker fixture가 `valid`로 분류된다.
- malformed, duplicate, nested, unsupported marker fixture가 conflict-ready parser state로 분류된다.
- code fence 안의 marker-looking text가 실제 marker로 처리되지 않는다.

### Bundle 3: Sync Dry-run CLI Evaluation

목표:

- `python -m aios sync --dry-run`을 read-only evaluator로 연결한다.

포함:

- CLI command registration
- `--dry-run` required policy
- `--manifest <path>` input
- `--json`
- `--envelope-v2`
- manifest validation before evaluation
- source/target existence checks
- marker parser integration
- hash comparison
- drift/conflict classification
- native `aios.sync_dry_run.v0` output
- envelope v2 mapping
- human output

제외:

- sync apply
- manifest write
- transaction logs
- rollback execution
- adapter generation
- force
- decommission
- source mutation

완료 기준:

- valid, conflict, drift-stop, orphan-warning fixture가 native JSON으로 재현된다.
- `--envelope-v2`는 `--json` 없이 사용하면 exit code 2로 실패한다.
- inspect/validate/inventory 기존 회귀 검증이 통과한다.

## 정확한 구현 순서

1. `src/aios/sync/__init__.py`를 추가한다.
2. `src/aios/sync/manifest.py`에 manifest dataclass와 schema validation을 둔다.
3. `src/aios/sync/hash.py`에 v0 hash policy helper를 둔다.
4. `src/aios/sync/result.py`에 native result, message, summary helper를 둔다.
5. manifest/hash fixture와 unit test를 추가한다.
6. `src/aios/sync/markers.py`에 marker parser를 둔다.
7. marker fixture와 parser unit test를 추가한다.
8. `src/aios/sync/dry_run.py`에 evaluator pipeline을 둔다.
9. 기존 CLI entrypoint에 `sync` command를 연결한다.
10. envelope v2 mapping을 연결한다.
11. end-to-end dry-run fixture tests를 추가한다.
12. 기존 runtime command regression을 수행한다.

## 모듈 레이아웃 후보

```text
src/aios/sync/
  __init__.py
  manifest.py
  hash.py
  markers.py
  result.py
  dry_run.py
```

### `manifest.py`

책임:

- manifest JSON load
- schema version validation
- required field validation
- enum validation
- nullability validation
- path safety validation
- marker metadata validation
- ownership/sync_mode compatibility validation

비책임:

- manifest write
- manifest generation
- drift evaluation
- marker parsing in target files

### `hash.py`

책임:

- `sha256:<lowercase-hex>` validation
- observed UTF-8 bytes hash calculation
- whole-file hash calculation
- managed block inner content hash calculation
- v0 hash policy metadata helper

비책임:

- automatic normalization
- line ending conversion
- BOM removal
- manifest mutation

### `markers.py`

책임:

- supported marker style parsing
- begin/end/anchor detection
- attribute parsing
- code fence exclusion
- pairing
- malformed/duplicated/nested classification
- parser output model

비책임:

- marker insertion
- marker repair
- marker deletion
- hash comparison
- action classification

### `result.py`

책임:

- native `aios.sync_dry_run.v0` result shape
- summary counters
- message normalization
- status derivation
- exit code derivation
- envelope v2 payload helper

비책임:

- CLI parsing
- filesystem evaluation
- marker parsing

### `dry_run.py`

책임:

- evaluation pipeline
- manifest entry iteration
- source/target checks
- parser/hash integration
- drift/conflict classification
- deterministic result ordering

비책임:

- file mutation
- manifest write
- transaction log write
- rollback execution

## Fixture 레이아웃

```text
tests/fixtures/sync/
  manifests/
  sources/
  targets/
  markers/
  hash/
  expected/
```

## 최소 Fixture Inventory

### Manifest Fixtures

| 파일 | 범주 | 예상 결과 |
|---|---|---|
| `tests/fixtures/sync/manifests/valid_whole_file.json` | valid schema | pass |
| `tests/fixtures/sync/manifests/valid_managed_block.json` | valid schema | pass |
| `tests/fixtures/sync/manifests/valid_mixed_boundary.json` | valid schema | pass |
| `tests/fixtures/sync/manifests/missing_schema_version.json` | schema error | fail |
| `tests/fixtures/sync/manifests/unsupported_schema_version.json` | schema error | fail |
| `tests/fixtures/sync/manifests/missing_managed_entries.json` | schema error | fail |
| `tests/fixtures/sync/manifests/invalid_ownership.json` | schema error | fail |
| `tests/fixtures/sync/manifests/invalid_sync_mode.json` | schema error | fail |
| `tests/fixtures/sync/manifests/invalid_hash_format.json` | schema error | fail |
| `tests/fixtures/sync/manifests/path_parent_traversal.json` | schema error | fail |
| `tests/fixtures/sync/manifests/duplicate_entry_id.json` | schema error | fail |
| `tests/fixtures/sync/manifests/marker_entry_id_mismatch.json` | schema error | fail |

### Hash Fixtures

| 파일 | 범주 | 예상 결과 |
|---|---|---|
| `tests/fixtures/sync/hash/lf_file.txt` | LF bytes | hash exact |
| `tests/fixtures/sync/hash/crlf_file.txt` | CRLF bytes | hash differs from LF |
| `tests/fixtures/sync/hash/same_content_lf.txt` | semantic same LF | hash differs from CRLF pair |
| `tests/fixtures/sync/hash/same_content_crlf.txt` | semantic same CRLF | hash differs from LF pair |
| `tests/fixtures/sync/hash/trailing_newline_present.txt` | trailing newline | hash differs from absent pair |
| `tests/fixtures/sync/hash/trailing_newline_absent.txt` | no trailing newline | hash differs from present pair |
| `tests/fixtures/sync/hash/utf8_korean_text.md` | UTF-8 Korean | hash exact |
| `tests/fixtures/sync/hash/utf8_without_bom.md` | UTF-8 no BOM | accepted |
| `tests/fixtures/sync/hash/utf8_with_bom.md` | UTF-8 BOM | warning candidate, hash includes BOM if evaluated |
| `tests/fixtures/sync/hash/marker_metadata_changed_same_inner.md` | marker metadata changed | inner hash unchanged |
| `tests/fixtures/sync/hash/marker_inner_content_changed.md` | inner content changed | inner hash changed |

### Marker Fixtures

| 파일 | 범주 | 예상 결과 |
|---|---|---|
| `tests/fixtures/sync/markers/valid/valid_markdown_pair.md` | valid marker | integrity `valid` |
| `tests/fixtures/sync/markers/valid/valid_hash_line_pair.txt` | valid marker | integrity `valid` |
| `tests/fixtures/sync/markers/valid/valid_yaml_line_pair.yaml` | valid marker | integrity `valid` |
| `tests/fixtures/sync/markers/valid/multiple_independent_blocks.md` | valid multiple | deterministic order |
| `tests/fixtures/sync/markers/invalid/missing_end_marker.md` | malformed | `end-missing`, conflict |
| `tests/fixtures/sync/markers/invalid/duplicate_begin_marker.md` | duplicate | `begin-duplicated`, conflict |
| `tests/fixtures/sync/markers/invalid/duplicate_end_marker.md` | duplicate | `end-duplicated`, conflict |
| `tests/fixtures/sync/markers/invalid/nested_marker.md` | nested | `marker-nested`, conflict |
| `tests/fixtures/sync/markers/invalid/malformed_marker.md` | malformed | `marker-malformed`, conflict |
| `tests/fixtures/sync/markers/invalid/mismatched_entry_id.md` | mismatch | `entry-id-mismatch`, conflict |
| `tests/fixtures/sync/markers/invalid/unsupported_marker_version.md` | unsupported | `marker-version-unsupported`, conflict |
| `tests/fixtures/sync/markers/ignored/fenced_code_marker_ignored.md` | code fence | real marker ignored |
| `tests/fixtures/sync/markers/ignored/unmanaged_file.md` | no marker | no parser conflict unless expected |
| `tests/fixtures/sync/markers/anchors/valid_anchor.md` | anchor | first-create candidate possible |
| `tests/fixtures/sync/markers/anchors/missing_anchor.md` | anchor missing | `anchor-missing`, conflict |
| `tests/fixtures/sync/markers/anchors/duplicate_anchor.md` | anchor duplicated | `anchor-duplicated`, conflict |
| `tests/fixtures/sync/markers/anchors/anchor_inside_code_fence.md` | invalid anchor | conflict |

### End-to-end Dry-run Fixtures

| 파일 | 범주 | 예상 결과 |
|---|---|---|
| `tests/fixtures/sync/manifests/e2e_clean_update.json` | clean update | status `pass`, action `update` |
| `tests/fixtures/sync/manifests/e2e_clean_skip.json` | no change | status `pass`, action `skip` |
| `tests/fixtures/sync/manifests/e2e_create_whole_file.json` | create candidate | status `pass`, action `create` |
| `tests/fixtures/sync/manifests/e2e_source_missing.json` | runtime conflict | status `fail`, action `conflict` |
| `tests/fixtures/sync/manifests/e2e_marker_missing.json` | marker conflict | status `fail`, action `conflict` |
| `tests/fixtures/sync/manifests/e2e_marker_corrupted.json` | marker conflict | status `fail`, action `conflict` |
| `tests/fixtures/sync/manifests/e2e_drift_stop.json` | target modified | status `fail`, action `drift-stop` |
| `tests/fixtures/sync/manifests/e2e_unmanaged_target.json` | unmanaged skip | status `warn`, action `skip` |
| `tests/fixtures/sync/manifests/e2e_orphan_marker.json` | orphan warning | status `warn`, action `orphan-warning` |

## CLI 동작 계약

### `--dry-run` required policy

- `python -m aios sync`는 Phase 7에서 usage error로 실패해야 한다.
- exit code는 2다.
- message는 sync apply가 구현되지 않았고 `--dry-run`이 필요하다는 사실을 명확히 해야 한다.

### `--manifest <path>` behavior

- Phase 7 첫 구현은 explicit manifest file input을 우선한다.
- manifest path는 repository-relative 또는 repository 내부 resolved path여야 한다.
- repository 밖으로 나가는 path는 usage error 또는 schema/path error로 실패해야 한다.
- manifest 파일은 읽기만 한다.

### Missing manifest behavior

- `python -m aios sync --dry-run`에서 `--manifest`가 없으면 첫 구현에서는 clear usage/config error로 실패한다.
- exit code는 2를 권장한다.
- default manifest discovery나 manifest preview generation은 첫 구현에 포함하지 않는다.

### Unsupported mode behavior

- `sync`가 `--dry-run` 없이 호출되면 unsupported mode다.
- `--apply`, `--write`, `--force`, `--rollback`, `--decommission` 같은 옵션은 첫 구현에서 제공하지 않는다.
- 알 수 없는 옵션은 기존 CLI 관례에 따라 usage error로 처리한다.

### Exit code expectations

| 조건 | Status | Exit code |
|---|---|---:|
| safe create/update/skip only | `pass` | 0 |
| warning only | `warn` | 0 |
| blocking conflict or drift-stop | `fail` | 1 |
| invalid CLI usage | none or fail-shaped usage output | 2 |
| `--envelope-v2` without `--json` | usage error | 2 |

## Read-only invariant checklist

미래 구현 번들은 다음을 매번 확인해야 한다.

- target file을 생성하지 않는다.
- target file을 수정하지 않는다.
- target file을 삭제하지 않는다.
- manifest를 생성하지 않는다.
- manifest를 수정하지 않는다.
- transaction log를 생성하지 않는다.
- rollback state를 쓰지 않는다.
- marker begin/end line을 삽입하지 않는다.
- marker anchor를 삽입하지 않는다.
- marker를 repair하지 않는다.
- adapter 파일을 생성하지 않는다.
- `.ai/registry/`를 생성하지 않는다.
- auto-fix를 수행하지 않는다.
- source file을 수정하지 않는다.

## 구현 freeze boundary

첫 runtime implementation에서 확장하면 안 되는 범위:

- manifest preview generation
- default manifest discovery
- manifest persistence
- sync apply
- marker insertion
- marker repair
- transaction log
- rollback dry-run
- rollback execution
- force policy
- decommission policy
- adapter generation
- activation-driven sync selection
- registry parser
- workflow execution
- worker dispatch
- live telemetry/event persistence

## 검증 매트릭스

### Bundle 1 Validation

```bash
python -m pytest tests/test_sync_manifest.py
python -m pytest tests/test_sync_hash.py
python -m compileall -q src/aios aios
python -m aios inspect
python -m aios validate
git diff --check
git diff --cached --check
```

### Bundle 2 Validation

```bash
python -m pytest tests/test_sync_markers.py
python -m compileall -q src/aios aios
python -m aios inspect
python -m aios validate
git diff --check
git diff --cached --check
```

### Bundle 3 Validation

```bash
python -m pytest tests/test_sync_dry_run.py
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_update.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_drift_stop.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_orphan_marker.json --json --envelope-v2
python -m aios sync --envelope-v2
python -m aios inspect
python -m aios validate
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

Expected:

- `python -m aios sync --envelope-v2`는 `--json` 없이 사용되므로 exit code 2로 실패해야 한다.
- `python -m aios sync`는 `--dry-run`이 없으므로 exit code 2로 실패해야 한다.
- warning-only dry-run은 exit code 0이어야 한다.
- blocking dry-run은 exit code 1이어야 한다.

## 의존성 그래프

```text
inventory/shared primitives
  -> manifest path and source reference validation

manifest schema contract
  -> manifest.py
  -> dry_run.py

hash normalization policy
  -> hash.py
  -> dry_run.py

managed marker contract
  -> markers.py
  -> dry_run.py

dry-run result schema
  -> result.py
  -> CLI JSON output
  -> envelope v2 mapping

envelope v2
  -> result.py adapter boundary only
```

관계:

- manifest validation은 inventory/shared primitives를 재사용할 수 있다.
- parser는 marker contract와 fixture에 의존한다.
- evaluator는 manifest, parser, hash, result에 의존한다.
- envelope v2 integration은 evaluator 내부 정책이 아니라 result serialization boundary에 둔다.

## Phase 7 runtime implementation entry criteria

다음 조건이 충족되면 Phase 7 runtime implementation에 진입할 수 있다.

- 본 작업 분해 문서가 완료되었다.
- `docs/reports/phase_7_bundle_readiness_audit.md`가 Phase 7 entry를 승인한다.
- Bundle 1-3 경계가 명확하다.
- 최소 fixture inventory가 확정되었다.
- CLI missing manifest behavior가 확정되었다.
- read-only invariant checklist가 확정되었다.
- validation matrix가 번들별로 확정되었다.

## Phase 7 runtime implementation stop/review criteria

다음 조건이 발생하면 구현을 중단하고 review 또는 추가 설계를 수행해야 한다.

- write operation이 필요해진다.
- manifest persistence가 필요해진다.
- marker insertion 또는 repair가 필요해진다.
- default manifest discovery가 필수로 보인다.
- generated preview content가 없으면 evaluation이 불가능해진다.
- 기존 envelope v2 contract와 sync result mapping이 충돌한다.
- drift/conflict taxonomy에 없는 blocking state가 발견된다.
- fixture 없이 정책 결정을 구현해야 한다.
- activation이나 registry parser가 dry-run input으로 필요해진다.

## Phase 7 readiness summary

완료된 게이트:

- manifest schema precision
- manifest validation boundary
- managed block parser contract
- insertion anchor contract
- hash normalization decision
- dry-run output schema
- envelope v2 mapping
- drift/conflict taxonomy
- read-only sync safety boundary

남은 리스크:

- 실제 fixture 파일은 아직 생성되지 않았다.
- CLI wiring은 기존 command structure를 읽고 보수적으로 붙여야 한다.
- first implementation에서 default manifest discovery를 욕심내면 범위가 커진다.
- generated preview hash는 adapter generation이 없으므로 초기 구현에서 null 또는 unavailable로 제한해야 한다.

승인된 첫 runtime slice:

- Bundle 1: Manifest/Hash Foundation

Bundle 1은 read-only helper와 fixture만 추가해야 하며, CLI-visible sync command를 아직 추가하지 않아도 된다.
