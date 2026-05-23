# Phase 7 Bundle 1 Manifest/Hash 구현 보고서

## 개요

이 문서는 Phase 7 Bundle 1 `Manifest/Hash Foundation` 구현 결과를 기록한다. 이번 번들은 future `aios sync --dry-run`을 위한 read-only 기반 모듈만 추가했으며, CLI-visible `sync` 명령은 추가하지 않았다.

현재 시스템은 계속 read-only 상태다. 이번 작업은 sync 실행, manifest persistence, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않았다.

## 구현 범위

추가된 runtime foundation:

- `src/aios/sync/__init__.py`
- `src/aios/sync/manifest.py`
- `src/aios/sync/hash.py`

추가된 테스트:

- `tests/test_sync_manifest.py`
- `tests/test_sync_hash.py`

추가된 fixture:

- `tests/fixtures/sync/manifests/valid_whole_file.json`
- `tests/fixtures/sync/manifests/valid_managed_block.json`
- `tests/fixtures/sync/manifests/valid_mixed_boundary.json`
- `tests/fixtures/sync/hash/lf_file.txt`
- `tests/fixtures/sync/hash/crlf_file.txt`
- `tests/fixtures/sync/hash/same_content_lf.txt`
- `tests/fixtures/sync/hash/same_content_crlf.txt`
- `tests/fixtures/sync/hash/trailing_newline_present.txt`
- `tests/fixtures/sync/hash/trailing_newline_absent.txt`
- `tests/fixtures/sync/hash/utf8_korean_text.md`
- `tests/fixtures/sync/hash/utf8_without_bom.md`

## Manifest Foundation

`src/aios/sync/manifest.py`는 `aios.sync_manifest.v0` schema의 read-only validation helper를 제공한다.

구현된 항목:

- canonical `schema_version` 검증
- `manifest_version` alias warning detection
- top-level required field 검증
- managed entry required field 검증
- generated metadata required field 검증
- ownership enum 검증
- sync mode enum 검증
- marker style enum 검증
- marker metadata required 조건 검증
- `marker.entry_id`와 entry `entry_id` 일치 검증
- duplicate `entry_id` 검증
- repository-relative path 검증
- absolute path 금지
- parent traversal 금지
- empty path 금지
- JSON path `/` separator 요구
- `source_path`가 `source_root` 아래인지 검증
- hash string format 검증
- `target_hash: null` error 처리

의도적으로 제외한 항목:

- marker parser
- target file marker inspection
- drift classification
- manifest persistence
- `aios validate <manifest>` 통합
- sync CLI evaluation

## Hash Foundation

`src/aios/sync/hash.py`는 v0 hash policy helper를 제공한다.

구현된 정책:

- `sha256:<lowercase-hex>` format validation
- observed bytes 기반 hash
- file bytes를 `rb` 성격으로 읽는 whole-file hash
- CRLF/LF normalization 없음
- trailing newline과 whitespace 보존
- BOM bytes 포함
- marker parser 없이 inner content bytes를 직접 받는 managed-block helper

의도적으로 제외한 항목:

- automatic normalization
- line ending conversion
- BOM 제거
- marker begin/end line parsing
- generated preview hash 생성

## 테스트 범위

Manifest tests:

- valid whole-file manifest
- valid managed-block manifest
- valid mixed-boundary manifest
- missing `schema_version`
- unsupported `schema_version`
- missing `managed_entries`
- invalid ownership
- invalid sync mode
- invalid hash format
- parent traversal path
- absolute path
- duplicate `entry_id`
- `marker.entry_id` mismatch
- marker required for managed-block
- marker forbidden for whole-file
- `target_hash: null`
- `manifest_version` alias warning

Hash tests:

- valid/invalid hash string format
- LF와 CRLF hash 차이
- trailing newline present/absent hash 차이
- UTF-8 Korean text deterministic hash
- UTF-8 BOM bytes included in hash
- managed block inner bytes hash helper

## Read-only Boundary

이번 번들은 다음을 수행하지 않았다.

- runtime target file 생성/수정/삭제
- manifest 생성/수정/삭제
- transaction log 생성
- marker 삽입
- marker repair
- sync CLI 추가
- rollback 실행
- adapter generation
- source mutation

테스트 fixture 파일은 `tests/fixtures/` 아래에만 추가되었다.

## 다음 번들

다음 구현 범위는 Bundle 2 `Managed Marker Parser`다.

Bundle 2에서 다룰 항목:

- marker style detection
- begin/end marker parsing
- code fence exclusion
- duplicate/nested/malformed marker classification
- insertion anchor parsing
- parser output model

Bundle 2에서도 계속 금지되는 항목:

- marker insertion
- marker repair
- sync apply
- manifest persistence
- CLI dry-run evaluator

## 검증 결과

실행한 검증:

```bash
python -m pytest tests/test_sync_manifest.py
python -m pytest tests/test_sync_hash.py
python -m compileall -q src/aios aios
python -m aios inspect
python -m aios validate
git diff --check
git diff --cached --check
```

최종 커밋 전 모든 검증이 통과해야 한다.
