# Replay validation runtime rule promotion 보고서

## 개요

Replay manifest/provider snapshot 정적 검증 동작을 runtime-facing governance rules로 승격했다. 이번 작업은 문서 규칙 반영만 수행했으며 runtime code, fixture, test behavior는 변경하지 않았다.

## 변경 파일

업데이트한 runtime-facing rules:

- `.ai/rules/operations/sync.rules.md`
- `.ai/rules/operations/validation.rules.md`

업데이트한 docs indexes:

- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

## Sync Rules 반영 내용

`sync.rules.md`에 다음을 추가했다.

Supported commands:

- `python -m aios validate <replay-manifest.json>`
- `python -m aios validate <replay-manifest.json> --json`
- `python -m aios validate <replay-manifest.json> --json --envelope-v2`

Supported schemas:

- `aios.preview_replay_manifest.v0`
- `aios.preview_provider_snapshot.v0`
- `aios.real_preview.input.v0`
- `aios.real_preview.output.v0`

Replay validation boundary:

- static validation only
- replay manifest, provider snapshot, referenced input/output fixture validation
- hash format validation
- placeholder hash rejection
- provenance and provider metadata presence validation
- unavailable output generated hash null policy
- no provider execution
- no adapter execution
- no generated content generation
- no actual provider output comparison
- no snapshot update
- no replay CLI
- no sync apply or mutation authorization

Output contract:

- native validate JSON uses `target.kind: replay-manifest`
- envelope v2 uses `command: validate`
- `payload.results` and `messages` preserve replay validator details

## Validation Rules 반영 내용

`validation.rules.md`에는 domain-independent pointer만 추가했다.

- `aios validate` may include runtime JSON/YAML targets such as activation files, sync manifests, and replay manifests.
- Replay manifest validation is static-only.
- Provider execution, adapter execution, generated content generation, snapshot update, file write, sync apply, and mutation remain forbidden.
- Sync-specific schema details and replay safety boundaries belong in `sync.rules.md`.

## 수정하지 않은 파일

`.ai/rules/operations/README.md`는 수정하지 않았다. 기존 설명이 `sync.rules.md`와 `validation.rules.md`의 역할을 충분히 안내하고 있어 별도 목록 변경이 필요하지 않았다.

## Read-only Boundary

이번 promotion은 다음을 구현하거나 승인하지 않는다.

- provider execution
- adapter execution
- generated content generation
- actual provider output replay comparison
- snapshot update
- replay CLI
- sync apply
- target mutation
- manifest persistence
- transaction persistence
- rollback execution
- marker insertion, repair, deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- source mutation

## Index Updates

Documentation index maintenance rules에 따라 다음을 반영했다.

- `docs/index/document_status_registry.md`
  - replay validation promotion audit를 superseded/historical로 조정
  - promotion report를 completed implementation report로 추가
  - sync rules 설명에 replay validation runtime rules를 반영
- `docs/index/phase_6_8_summary.md`
  - replay validation rule promotion 완료 상태와 다음 방향을 갱신
- `docs/index/current_runtime_context.md`
  - sync rules runtime area와 다음 안전 방향을 갱신

## 검증

수행 대상:

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json`
- `python -m pytest tests/test_replay_validate_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Replay manifest validation은 이제 `.ai OS`의 공식 read-only validation capability로 runtime governance rules에 반영되었다. 다음 안전한 방향은 real provider를 실행하지 않는 replay comparison validator 설계 여부를 결정하는 것이다.
