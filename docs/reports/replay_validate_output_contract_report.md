# Replay validate output contract 보고서

## 개요

Replay manifest/provider snapshot 정적 검증이 `aios validate <replay_manifest.json>`에 통합된 뒤, native validate JSON과 envelope v2 출력 형태를 고정하는 contract test를 추가했다. 이번 작업은 출력 안정화만 수행했으며 validation classification, provider execution, adapter execution, generated content generation, replay output comparison, sync apply, mutation 동작은 추가하지 않았다.

## 추가 테스트

추가 파일:

- `tests/test_replay_validate_output_contract.py`

고정한 출력 계약:

- valid replay manifest native JSON
  - `schema_version: aios.validate.result.v0`
  - `status: pass`
  - `target.kind: replay-manifest`
  - `replay_manifest_checked` info result
  - `schema_version`, `provider_id`, `provider_version`, `cases` details
- invalid replay manifest native JSON
  - `status: fail`
  - representative failure code 보존
  - `field`, `case_id` details 보존
- valid replay manifest envelope v2
  - `command: validate`
  - `target.kind: replay-manifest`
  - `payload.results` 보존
  - `messages` info data 보존
  - `meta.legacy_schema_version` 보존
- invalid replay manifest envelope v2
  - failure message 보존
  - replay validator details 보존
- unrelated JSON
  - replay manifest로 오분류하지 않음

## Read-only Boundary

이번 작업에서 구현하지 않은 항목:

- provider execution
- adapter execution
- generated content generation
- replay output comparison
- replay CLI
- snapshot auto-update
- sync apply
- target mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- orchestration
- workflow execution
- `.ai/registry/`
- auto-fix
- source mutation

## Index Updates

Documentation index maintenance rules에 따라 다음을 갱신했다.

- `docs/index/document_status_registry.md`
  - replay validate output contract report를 completed implementation report로 추가
- `docs/index/phase_6_8_summary.md`
  - replay validation JSON/envelope output contract 안정화 완료를 반영
- `docs/index/current_runtime_context.md`
  - 다음 권장 방향을 replay governance/rule promotion 검토로 갱신

## 검증

수행 대상:

- `python -m pytest tests/test_replay_validate_output_contract.py`
- `python -m pytest tests/test_validate_replay_manifest.py`
- `python -m pytest tests/test_real_preview_replay_fixtures.py`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json --envelope-v2`
- `python -m aios validate --json --summary-only`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Replay manifest validation의 native JSON과 envelope v2 출력 계약이 테스트로 고정되었다. 다음 안전한 작업 후보는 replay validation governance rule promotion 필요성 검토이며, real provider execution과 mutation/apply는 계속 차단 상태다.
