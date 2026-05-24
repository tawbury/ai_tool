# Replay manifest validate 통합 보고서

## 개요

Real preview provider의 deterministic replay 준비를 위해 replay manifest와 provider snapshot 정적 검증을 `aios validate <replay_manifest.json>`에 통합했다. 이번 작업은 fixture와 schema 무결성만 확인하며 provider 실행, adapter 실행, generated content 생성, replay 비교 실행, snapshot 갱신, sync apply, mutation은 구현하지 않았다.

## 변경 사항

추가한 런타임 모듈:

- `src/aios/sync/replay.py`

추가한 validate 통합:

- `src/aios/validate/validators/replay_manifest.py`
- `src/aios/validate/engine.py`
- `src/aios/validate/targets.py`

추가한 테스트:

- `tests/test_validate_replay_manifest.py`

## 검증 범위

`aios.preview_replay_manifest.v0` manifest에 대해 다음을 정적으로 검증한다.

- required fields
- provider id/version
- hash policy
- case id uniqueness
- fixture path safety
- referenced input/output fixture existence
- non-empty replay dimensions
- input fixture schema version
- output fixture schema version
- hash format
- placeholder hash rejection
- unavailable output generated hash null policy
- provider metadata presence
- provenance presence

Provider snapshot에 대해 다음을 정적으로 검증한다.

- `aios.preview_provider_snapshot.v0` schema version
- provider id/version match
- deterministic capability field
- supported sync modes
- hash policy match
- output-affecting config presence

## Target Detection

`aios validate <path>`는 JSON 파일의 `schema_version: aios.preview_replay_manifest.v0`를 기준으로 replay manifest를 인식한다. `schema_version`이 누락된 경우에도 `provider`, `hash_policy`, `cases`를 갖춘 replay-manifest-shaped JSON은 schema error validation 대상으로 인식한다.

Unrelated JSON은 replay manifest로 오분류하지 않는다.

## Read-only Boundary

이번 통합은 static validation만 수행한다.

구현하지 않은 항목:

- provider execution
- adapter execution
- generated content generation
- provider output replay comparison
- snapshot update
- replay CLI
- `aios validate` 외 별도 command
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
  - replay manifest validate integration report를 completed implementation report로 추가
- `docs/index/phase_6_8_summary.md`
  - replay validation integration report와 `aios validate <replay-manifest.json>` 지원을 추가
- `docs/index/current_runtime_context.md`
  - replay manifest validation command와 schema 상태를 갱신

## 검증

수행 대상:

- `python -m pytest tests/test_real_preview_replay_fixtures.py`
- `python -m pytest tests/test_validate_replay_manifest.py`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json`
- `python -m aios validate --json --summary-only`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Replay manifest와 provider snapshot은 이제 provider를 실행하지 않고도 `aios validate`에서 정적 무결성을 확인할 수 있다. Real preview provider 구현은 여전히 차단되어 있으며, 다음 안정화 후보는 replay validate JSON/envelope 출력 계약 테스트다.
