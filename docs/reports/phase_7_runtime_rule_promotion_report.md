# Phase 7 Runtime Rule Promotion Report

## 개요

이 문서는 Phase 7 read-only sync runtime v0의 구현 동작을 공식 runtime governance rule로 승격한 작업을 기록한다. 변경 대상은 `.ai/rules/operations/sync.rules.md`이며, 운영 규칙 목록의 설명을 현재 상태에 맞추기 위해 `.ai/rules/operations/README.md`도 함께 갱신했다.

이번 작업은 문서와 규칙 승격만 수행했다. 런타임 코드, CLI 동작, sync dry-run classification, manifest validation policy는 변경하지 않았다.

## 승격 근거

승격 근거는 다음 Phase 7 산출물이다.

- `docs/reports/phase_7_read_only_runtime_completion_audit.md`
- `docs/reports/phase_7_stabilization_output_contract_report.md`

두 문서는 Phase 7 v0가 다음 범위에서 완료되고 안정화되었음을 확인했다.

- `aios sync --dry-run --manifest <path>`
- native `aios.sync_dry_run.v0` JSON output
- envelope v2 sync output
- `aios validate <sync-manifest.json>`
- manifest/hash foundation
- managed marker parser
- drift-stop evaluation
- orphan-warning evaluation
- read-only invariant

## 변경 내용

### Sync Rules

`.ai/rules/operations/sync.rules.md`를 Phase 6 safety design 중심 문서에서 Phase 7 read-only runtime v0 계약 문서로 갱신했다.

반영한 주요 항목은 다음과 같다.

- 공식 지원 명령:
  - `python -m aios sync --dry-run --manifest <path>`
  - `python -m aios sync --dry-run --manifest <path> --json`
  - `python -m aios sync --dry-run --manifest <path> --json --envelope-v2`
  - `python -m aios validate <sync-manifest.json>`
  - `python -m aios validate <sync-manifest.json> --json`
  - `python -m aios validate <sync-manifest.json> --json --envelope-v2`
- usage/config error policy:
  - `aios sync` without `--dry-run` exits with code `2`
  - `aios sync --dry-run` without `--manifest` exits with code `2`
  - `--envelope-v2` without `--json` exits with code `2`
- read-only invariant:
  - manifest load, source/target read, hash computation, marker parsing, classification, output emission only 허용
  - target mutation, manifest write, transaction log write, marker insertion/repair/delete 금지
- manifest contract:
  - `schema_version: aios.sync_manifest.v0`
  - required top-level fields
  - managed entry fields
  - ownership enum
  - sync mode enum
  - path safety and hash format policy
- hash policy:
  - observed UTF-8 bytes
  - no CRLF/LF normalization
  - trailing newline/whitespace preservation
  - marker begin/end line exclusion for managed block hash
- marker rules:
  - supported marker styles
  - marker integrity classifications
  - code fence exclusion
  - blocking marker conflict conditions
- dry-run result contract:
  - native `aios.sync_dry_run.v0`
  - `meta.dry_run: true`
  - `meta.mutation_performed: false`
  - action/status/exit code policy
- drift-stop and conflict policy:
  - `source-missing`
  - `target-modified`
  - `marker-missing`
  - `marker-duplicated`
  - `marker-corrupted`
  - `orphan-warning`
- envelope v2 mapping:
  - sync dry-run mapping
  - sync manifest validate mapping
- mutation blocked section:
  - sync apply와 모든 mutation은 future readiness gate 전까지 차단
- future expansion boundary:
  - generated preview
  - repository-wide unmanaged/orphan scan
  - transaction/rollback
  - sync apply architecture
  - adapter generation

### Operations README

`.ai/rules/operations/README.md`의 `sync.rules.md` 설명을 future-only safety boundary에서 현재 read-only sync dry-run runtime과 manifest validation을 포함하는 설명으로 갱신했다.

## 비범위

이번 작업은 다음을 수행하지 않았다.

- runtime code 변경
- CLI behavior 변경
- 새 command 추가
- sync apply 구현
- target mutation 구현
- manifest persistence 구현
- transaction log persistence 구현
- rollback execution 구현
- marker insertion, repair, deletion 구현
- adapter generation 구현
- generated preview 구현
- default manifest discovery 구현
- activation-driven sync selection 구현
- repository-wide unmanaged scan 구현
- force 또는 decommission 구현

## 검증 계획

요청된 검증은 다음과 같다.

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_clean_skip.json --json`
- `python -m aios validate tests/fixtures/sync/manifests/valid_whole_file.json --json`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Phase 7 read-only sync runtime v0의 구현 동작이 `.ai/rules/operations/sync.rules.md`에 공식 runtime governance contract로 반영되었다. sync apply와 mutation은 여전히 명시적으로 차단되어 있으며, 향후 확장은 별도 설계와 readiness gate 이후에만 진행해야 한다.
