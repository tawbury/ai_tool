# Phase 8 preview sync 런타임 규칙 승격 보고서

## 개요

Phase 8 fixture-backed generated preview 통합 동작을 공식 sync 런타임 운영 규칙에 반영했다. 이번 변경은 문서 승격 작업이며 런타임 코드나 CLI 동작은 변경하지 않았다.

## 반영한 런타임 계약

`.ai/rules/operations/sync.rules.md`를 Phase 8 v0 기준으로 갱신했다.

- `--preview-provider fixture`와 `--preview-fixtures <path>` 조합을 opt-in preview 경로로 명시했다.
- 기본 preview provider는 없으며 fixture-backed provider만 지원된다고 명시했다.
- preview는 read-only 비교 입력이며 generated content creation이나 adapter execution이 아니라고 정리했다.
- clean target에서 fixture preview hash가 다를 때 `action: update`, `severity: informational`이 될 수 있음을 명시했다.
- `update` 후보는 쓰기 권한이 아니며 `meta.mutation_performed: false`를 유지해야 한다고 명시했다.
- preview unavailable은 update 후보를 만들지 않고 기존 dry-run 결과를 보존한다고 명시했다.
- source-missing, marker conflict, drift-stop이 preview보다 우선한다는 precedence 규칙을 추가했다.
- native JSON과 envelope v2에서 preview metadata와 generated hash fields가 보존되어야 함을 명시했다.
- preview 설정 오류는 exit code `2`를 유지한다고 명시했다.

`.ai/rules/operations/README.md`의 sync rules 설명도 fixture preview comparison을 포함하도록 짧게 갱신했다.

## 유지한 차단 경계

다음 항목은 계속 금지 상태로 유지했다.

- real preview provider execution
- adapter execution
- generated preview content creation
- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- default preview provider
- activation-driven preview selection

## 영향 범위

이번 변경은 `.ai/` 운영 규칙과 보고서만 수정한다. `src/aios/` 런타임 코드, sync dry-run evaluator, preview provider, fixtures, 테스트 동작은 변경하지 않았다.

## 검증

다음 검증을 수행 대상으로 삼았다.

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/e2e_preview_whole_file_clean.json --json --preview-provider fixture --preview-fixtures tests/fixtures/sync/previews`
- `python -m pytest tests/test_sync_preview_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
