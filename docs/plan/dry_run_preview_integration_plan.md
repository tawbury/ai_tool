# Dry-run Preview Integration Plan

## 개요

이 문서는 Phase 8 generated preview output을 `aios sync --dry-run`에 통합하기 전 설계 계획이다. 현재 fixture-backed provider는 `src/aios/sync/preview.py`에 isolated read-only layer로 존재하지만, dry-run evaluator는 preview output을 소비하지 않는다.

이번 계획은 구현하지 않는다. 런타임 코드, CLI behavior, `.ai` rules는 변경하지 않는다.

## 목적

Preview integration의 목적은 다음과 같다.

- read-only `update` candidate classification을 가능하게 한다.
- Phase 7의 drift-stop/conflict precedence를 유지한다.
- preview unavailable 상태에서는 update candidate를 만들지 않는다.
- generated hash와 provenance를 dry-run result와 envelope v2에 보존한다.
- adapter execution 없이 fixture-backed provider만 사용하는 초기 integration path를 정의한다.

## CLI/API Boundary

Preview는 기본 동작이 아니어야 한다.

권장 CLI shape:

```bash
python -m aios sync --dry-run --manifest <path> --preview-provider fixture --preview-fixtures <path>
python -m aios sync --dry-run --manifest <path> --json --preview-provider fixture --preview-fixtures <path>
python -m aios sync --dry-run --manifest <path> --json --envelope-v2 --preview-provider fixture --preview-fixtures <path>
```

정책:

- No default preview provider.
- `--preview-provider fixture`가 있을 때만 preview comparison을 수행한다.
- `--preview-fixtures <path>`는 fixture provider root를 가리킨다.
- fixture provider는 input fixture와 output fixture만 읽는다.
- adapter execution은 없다.
- generated content generation은 없다.
- sync apply 또는 mutation은 없다.

Usage guidance:

- `--preview-fixtures` without `--preview-provider fixture`는 usage/config error 후보로 둔다.
- `--preview-provider fixture` without `--preview-fixtures`는 usage/config error 후보로 둔다.
- unsupported provider name은 usage/config error 후보로 둔다.
- usage/config error는 기존 CLI 관례에 맞춰 exit code `2`를 사용한다.

## Provider Input Mapping

초기 fixture-backed integration은 manifest entry를 직접 generation input으로 변환하지 않는다. 대신 manifest entry와 fixture provider 사이의 explicit mapping이 필요하다.

권장 v0 mapping 후보:

```json
{
  "preview_inputs": {
    "entry_clean_skip": "managed_block_clean_input.json",
    "entry_whole_file": "whole_file_clean_input.json"
  }
}
```

구현 slice에서는 이 mapping을 `--preview-fixtures` 아래의 별도 index fixture 또는 manifest `generated` metadata에서 읽을 수 있다. 단, default discovery나 manifest schema 변경은 별도 결정 전까지 피한다.

안전한 초기 선택:

- fixture provider tests는 provider 자체 mapping을 유지한다.
- dry-run integration 구현 전에는 entry_id -> input fixture mapping 방식부터 별도 확정한다.
- mapping이 없으면 preview unavailable로 취급하고 no-update를 유지한다.

## Dry-run Evaluation Order

Preview comparison은 clean target에만 적용한다.

권장 evaluation order:

1. Manifest validation
2. Source existence check
3. Source hash calculation
4. Target existence check
5. Marker parsing, if marker is expected
6. Target hash or managed block hash calculation
7. Compare target hash with manifest `target_hash`
8. If target is clean, resolve preview input mapping
9. If preview provider is configured, load preview output
10. Compare generated hash with current clean target hash
11. Emit read-only result

Preview must not run before source/target/marker safety checks have established the current state.

## Update Candidate Rules

Whole-file:

- clean target + `generated_target_hash` differs from `actual_target_hash` -> `update`
- clean target + `generated_target_hash` matches `actual_target_hash` -> `skip`
- missing generated target hash -> preserve existing Phase 7 result

Managed block:

- clean managed block + `generated_managed_block_hash` differs from `actual_managed_block_hash` -> `update`
- clean managed block + `generated_managed_block_hash` matches `actual_managed_block_hash` -> `skip`
- missing generated managed block hash -> preserve existing Phase 7 result

Mixed-boundary:

- treat the managed inner block like managed-block.
- marker-external content remains user-owned and is never compared against generated preview.

General:

- `update` candidate severity is `informational`.
- `update` candidate status is `pass`.
- `update` candidate is not write authorization.
- `update` candidate must keep `meta.mutation_performed: false`.

## Preview Unavailable Rules

Preview unavailable must not create an update candidate.

Allowed behavior:

- Preserve existing Phase 7 result action, normally `skip` for clean target.
- Add `details.preview_unavailable_reason`.
- Optionally add an informational message when useful.
- Preserve `meta.preview_provider` and `meta.preview_policy`.

Unavailable reason handling:

- `adapter-unavailable`: no update; info or warning
- `source-missing`: existing source conflict wins
- `unsupported-sync-mode`: no update; warning
- `marker-invalid`: existing marker conflict wins
- `generation-disabled`: no update; info
- `activation-unresolved`: no update; warning

## Precedence Rules

Preview never repairs or bypasses safety states.

Precedence:

1. Invalid manifest schema beats preview.
2. `source-missing` conflict beats preview.
3. Target missing rules beat preview.
4. Marker conflict beats preview.
5. Drift-stop beats preview.
6. Orphan-warning can coexist with clean expected entry preview comparison.
7. Preview unavailable produces no update candidate.
8. Preview comparison only occurs for clean target state.

Examples:

- drifted target + generated hash exists -> still `drift-stop`
- marker corrupted + generated hash exists -> still `conflict`
- source missing + preview output exists -> still `conflict`
- adapter unavailable + clean target -> existing `skip`, with preview unavailable detail

## Native Result Schema Extension

`aios.sync_dry_run.v0` can be extended compatibly because current result fields already allow dictionaries.

Hashes:

- `hashes.generated_target_hash`
- `hashes.generated_managed_block_hash`

Details:

```json
{
  "preview": {
    "provider": "fixture",
    "preview_available": true,
    "generated_content_kind": "managed-block",
    "provenance": {
      "source_paths": [".ai/rules/operations/sync.rules.md"],
      "generated_by": "aios.generated_preview.v0"
    }
  },
  "preview_unavailable_reason": null
}
```

Update candidate result:

- `action: update`
- `severity: informational`
- `stop_reason: null`
- `recovery_hint: null`
- `drift_state: clean`

Preview unavailable result:

- existing Phase 7 action retained
- `details.preview_unavailable_reason` set
- generated hash fields remain `null`

## Message Policy

Update candidate messages:

- Optional in native output.
- If emitted, use code `update-candidate`.
- Severity should be `info`, status `pass`.
- Message must not imply that write is authorized.

Preview unavailable messages:

- Optional for informational reasons.
- Recommended for `unsupported-sync-mode` and `activation-unresolved`.
- Existing blocking messages remain primary for `source-missing` and marker conflicts.

## Envelope v2 Mapping

Envelope v2 should preserve preview metadata without changing existing payload shape.

Mapping:

- `payload.results[].hashes.generated_target_hash`
- `payload.results[].hashes.generated_managed_block_hash`
- `payload.results[].details.preview`
- `payload.results[].details.preview_unavailable_reason`
- `messages[]` includes update candidate or unavailable preview message if emitted
- `meta.preview_provider: fixture`
- `meta.preview_policy: read-only-fixture`

Status:

- update candidate alone keeps command `status: pass`.
- unavailable preview alone should not fail the command.
- blocking source/marker/drift states still produce `status: fail`.

## Fixture-backed Implementation Slice

Allowed initial implementation:

- Add opt-in CLI options for fixture preview.
- Pass fixture provider and mapping into dry-run evaluator.
- Read preview fixtures only.
- Populate generated hash fields and preview details.
- Classify `update` only when target is clean and generated hash differs.

Still forbidden:

- real provider
- adapter execution
- generated content generation
- target writes
- manifest writes
- marker insertion/repair/delete
- activation-driven preview selection
- default preview discovery

## Tests for Next Implementation

Required tests:

- clean whole-file target + generated hash differs -> `update`
- clean whole-file target + generated hash matches -> `skip`
- clean managed-block target + generated hash differs -> `update`
- drift-stop still fails with preview available
- marker conflict still fails with preview available
- preview unavailable preserves existing Phase 7 result and no update
- envelope v2 preserves generated hashes, preview details, provider meta
- fixture provider config errors exit with code `2`

Regression tests:

- existing `sync --dry-run --manifest <path>` behavior unchanged without preview flags
- existing native JSON shape still includes `meta.mutation_performed: false`
- existing output contract tests continue to pass

## Explicit Non-goals

This integration plan does not authorize:

- sync apply
- target mutation
- manifest write
- transaction log persistence
- rollback execution
- marker insertion, repair, or deletion
- adapter generation
- real generated content creation
- default preview provider
- default manifest discovery
- repository-wide scan
- activation-driven preview selection
- `.ai/registry/`
- auto-fix
- source mutation

## 결론

Dry-run preview integration should be opt-in, fixture-backed, and clean-target-only. Preview output may create read-only `update` candidates, but must never bypass source, marker, or drift-stop safety checks. The next implementation bundle should add fixture preview CLI/API integration without changing default dry-run behavior.
