# Phase 7 Bundle 2 Marker Parser 구현 보고서

## 개요

이 문서는 Phase 7 Bundle 2 `Managed Marker Parser` 구현 결과를 기록한다. 이번 번들은 future `aios sync --dry-run` evaluator가 사용할 read-only marker analyzer만 추가했다.

이번 작업은 sync CLI, dry-run evaluator orchestration, hash comparison, drift evaluation, marker insertion, marker repair, marker deletion, manifest persistence, rollback 실행, adapter generation을 구현하지 않았다.

## 구현 범위

추가된 runtime foundation:

- `src/aios/sync/markers.py`

갱신된 export:

- `src/aios/sync/__init__.py`

추가된 테스트:

- `tests/test_sync_markers.py`

추가된 fixture:

- `tests/fixtures/sync/markers/valid/valid_markdown_pair.md`
- `tests/fixtures/sync/markers/valid/valid_hash_line_pair.txt`
- `tests/fixtures/sync/markers/valid/valid_yaml_line_pair.yaml`
- `tests/fixtures/sync/markers/valid/multiple_independent_blocks.md`
- `tests/fixtures/sync/markers/invalid/missing_end_marker.md`
- `tests/fixtures/sync/markers/invalid/duplicate_begin_marker.md`
- `tests/fixtures/sync/markers/invalid/duplicate_end_marker.md`
- `tests/fixtures/sync/markers/invalid/nested_marker.md`
- `tests/fixtures/sync/markers/invalid/malformed_marker.md`
- `tests/fixtures/sync/markers/invalid/mismatched_entry_id.md`
- `tests/fixtures/sync/markers/invalid/unsupported_marker_version.md`
- `tests/fixtures/sync/markers/ignored/fenced_code_marker_ignored.md`
- `tests/fixtures/sync/markers/ignored/unmanaged_file.md`
- `tests/fixtures/sync/markers/anchors/valid_anchor.md`
- `tests/fixtures/sync/markers/anchors/missing_anchor.md`
- `tests/fixtures/sync/markers/anchors/duplicate_anchor.md`
- `tests/fixtures/sync/markers/anchors/anchor_inside_code_fence.md`

## Parser 기능

구현된 항목:

- Markdown HTML comment marker parsing
- hash-line comment marker parsing
- YAML line comment style hint classification
- begin marker parsing
- end marker parsing
- anchor parsing
- `entry_id` extraction
- `marker_version` extraction
- marker style classification
- begin/end pairing
- line number preservation
- content line span calculation
- multiple independent managed block ordering
- deterministic ordering
- code fence exclusion
- malformed marker classification
- duplicate begin/end classification
- nested marker classification
- mismatched entry_id classification
- unsupported marker version classification
- orphan state flagging when expected entry ids are provided
- missing/duplicated/inside-fence anchor classification

## Parser 비책임

이번 parser는 다음을 수행하지 않는다.

- marker insertion
- marker repair
- marker deletion
- hash comparison
- drift evaluation
- sync action classification
- file mutation
- manifest persistence
- CLI integration

## Code Fence 처리

구현된 정책:

- fenced code block 내부의 begin/end marker-looking text는 real marker로 처리하지 않는다.
- fenced code block 내부의 anchor-looking text는 invalid anchor로 보고한다.
- 닫히지 않은 fence는 parser-level `code-fence-ambiguous` problem으로 기록할 수 있다.

## 테스트 범위

테스트한 항목:

- valid markdown pair
- valid hash-line pair
- valid yaml-line pair
- multiple independent blocks deterministic ordering
- line number preservation
- missing end marker
- duplicate begin marker
- duplicate end marker
- nested marker
- malformed marker
- mismatched entry_id
- unsupported marker version
- fenced marker-looking text ignored
- unmanaged file no false marker
- orphan flag with expected entry ids
- valid anchor
- missing anchor
- duplicated anchor
- anchor inside code fence

## Read-only Boundary

이번 번들은 다음을 수행하지 않았다.

- runtime target file 생성/수정/삭제
- manifest 생성/수정/삭제
- marker 삽입
- marker repair
- marker 삭제
- sync CLI 추가
- dry-run evaluator 추가
- rollback 실행
- adapter generation
- source mutation

테스트 fixture 파일은 `tests/fixtures/` 아래에만 추가되었다.

## 다음 번들

다음 구현 범위는 Bundle 3 `Sync Dry-run CLI Evaluation`이다.

Bundle 3에서 다룰 항목:

- CLI command registration
- `--dry-run` required policy
- explicit `--manifest <path>` input
- manifest validation before evaluation
- source/target existence checks
- marker parser integration
- hash comparison
- drift/conflict classification
- native dry-run JSON output
- envelope v2 mapping

Bundle 3에서도 계속 금지되는 항목:

- sync apply
- manifest write
- transaction log persistence
- rollback execution
- marker insertion
- marker repair
- adapter generation
- force
- decommission

## 검증 결과

실행한 검증:

```bash
python -m pytest tests/test_sync_markers.py
python -m compileall -q src/aios aios
python -m aios inspect
python -m aios validate
git diff --check
git diff --cached --check
```

최종 커밋 전 모든 검증이 통과해야 한다.
