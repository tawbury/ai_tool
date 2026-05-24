# Real preview replay fixture bundle 보고서

## 개요

Future real preview provider validation을 준비하기 위해 fixture-only replay bundle을 추가했다. 이번 작업은 concrete JSON fixtures와 schema/contract tests만 추가했으며, real provider execution, adapter execution, generated content generation, sync apply, mutation은 구현하지 않았다.

## 추가한 fixture layout

새 fixture root:

```text
tests/fixtures/sync/real_previews/replay/
  inputs/
  outputs/
  manifests/
  provider_snapshots/
```

추가한 replay manifest:

- `tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json`

추가한 provider snapshot:

- `tests/fixtures/sync/real_previews/replay/provider_snapshots/aios_preview_example_0_1_0.json`

## 추가한 replay cases

다음 required replay cases를 input/output fixture로 추가했다.

- `whole_file_lf`
- `whole_file_crlf`
- `whole_file_trailing_newline`
- `whole_file_bom`
- `managed_block_lf`
- `managed_block_crlf`
- `mixed_boundary`
- `unavailable_adapter`
- `unavailable_nondeterministic`
- `unavailable_timeout`

## 추가한 테스트

새 테스트:

- `tests/test_real_preview_replay_fixtures.py`

검증 범위:

- replay manifest parse
- `aios.preview_replay_manifest.v0` schema version
- `aios.preview_provider_snapshot.v0` schema version
- manifest와 provider snapshot의 provider id/version 일치
- unique case ids
- fixture path relative/safe check
- referenced input/output fixture existence
- non-empty replay dimensions
- `aios.real_preview.input.v0` input fixtures
- `aios.real_preview.output.v0` output fixtures
- placeholder hash 금지
- `sha256:<lowercase-hex>` hash format
- available output deterministic true
- unavailable output generated hashes null
- unavailable reason coverage:
  - `adapter-unavailable`
  - `nondeterministic-output`
  - `provider-timeout`
- provider metadata presence
- provenance presence
- explicit source path ordering

## Index updates

Documentation index maintenance rules에 따라 다음을 갱신했다.

- `docs/index/document_status_registry.md`
  - replay fixture contract를 historical/superseded로 조정
  - replay fixture bundle report를 completed implementation report로 추가
- `docs/index/phase_6_8_summary.md`
  - replay JSON fixtures와 schema/contract tests 구현 완료로 갱신
  - 다음 권장 방향을 replay validation integration design으로 갱신
- `docs/index/current_runtime_context.md`
  - replay manifest/provider snapshot schema가 fixture/test contract임을 명시
  - 다음 방향을 replay validation integration planning으로 갱신

## Read-only boundary

이번 작업은 read-only boundary를 유지했다.

구현하지 않은 항목:

- real provider implementation
- adapter runtime
- generated content generation
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

## 검증

수행 대상 검증:

- `python -m pytest tests/test_real_preview_replay_fixtures.py`
- `python -m pytest tests/test_generated_preview_fixtures.py`
- `python -m pytest tests/test_generated_preview_provider.py`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Real preview replay fixture-only bundle은 provider execution 없이 deterministic replay validation의 입력 계약을 고정했다. 다음 단계는 runtime provider 구현이 아니라 replay manifest/provider snapshot validation integration을 설계하는 것이다.
