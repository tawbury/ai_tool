# Real preview replay fixture contract

## 개요

이 문서는 future real preview provider validation을 구현하기 전에 필요한 replay fixture 계약을 정의한다. Deterministic replay architecture는 동일 input과 provider version에서 동일 output을 요구한다. 이 계약은 그 검증에 사용할 fixture layout, manifest schema, provider snapshot schema, required cases, comparison rules를 고정한다.

이번 문서는 설계만 수행한다. Provider implementation, adapter runtime, generated content generation, sync apply, mutation은 포함하지 않는다.

## Fixture layout

권장 fixture root:

```text
tests/fixtures/sync/real_previews/replay/
  inputs/
  outputs/
  manifests/
  provider_snapshots/
```

Directory roles:

- `inputs/`: provider input fixtures using `aios.real_preview.input.v0`.
- `outputs/`: expected provider output fixtures using `aios.real_preview.output.v0`.
- `manifests/`: replay manifest files that bind cases to input/output fixtures.
- `provider_snapshots/`: provider identity and output-affecting configuration snapshots.

Fixtures must be read-only test inputs. They must not imply provider execution, adapter execution, sync apply, or snapshot auto-update.

## Replay manifest schema

Replay manifest schema:

```json
{
  "schema_version": "aios.preview_replay_manifest.v0",
  "provider": {
    "provider_id": "aios.preview.example",
    "provider_version": "0.1.0"
  },
  "hash_policy": {
    "version": "aios.hash_policy.v0",
    "algorithm": "sha256",
    "encoding": "observed-utf8-bytes",
    "line_endings": "preserve",
    "trailing_newline": "preserve",
    "managed_block_marker_lines": "exclude"
  },
  "cases": [
    {
      "case_id": "whole_file_lf",
      "input_fixture": "inputs/whole_file_lf_input.json",
      "expected_output_fixture": "outputs/whole_file_lf_output.json",
      "replay_dimensions": ["whole-file", "LF"]
    }
  ]
}
```

Required top-level fields:

- `schema_version`
- `provider`
- `provider.provider_id`
- `provider.provider_version`
- `hash_policy`
- `cases`

Required case fields:

- `case_id`
- `input_fixture`
- `expected_output_fixture`
- `replay_dimensions`

Rules:

- `schema_version` must equal `aios.preview_replay_manifest.v0`.
- `case_id` values must be unique.
- Fixture paths must be repository-relative to replay root.
- Fixture paths must not contain parent traversal.
- `replay_dimensions` must not be empty.
- Provider id/version must match the provider snapshot.
- Hash policy must match expected output provider metadata.

## Provider snapshot schema

Provider snapshot schema:

```json
{
  "schema_version": "aios.preview_provider_snapshot.v0",
  "provider_id": "aios.preview.example",
  "provider_version": "0.1.0",
  "deterministic_capable": true,
  "supported_sync_modes": ["whole-file", "managed-block", "mixed-boundary"],
  "hash_policy": "aios.hash_policy.v0",
  "output_affecting_config": {
    "template_set": "default",
    "normalization": "observed-utf8-bytes",
    "line_endings": "preserve"
  }
}
```

Required fields:

- `schema_version`
- `provider_id`
- `provider_version`
- `deterministic_capable`
- `supported_sync_modes`
- `hash_policy`
- `output_affecting_config`

Rules:

- `deterministic_capable` must be `true` for replay suites that expect available output.
- `supported_sync_modes` must include every sync mode used by replay cases.
- `hash_policy` must be `aios.hash_policy.v0` unless a future policy is explicitly designed.
- `output_affecting_config` must include any provider configuration that can change generated hashes.

## Required replay cases

The initial replay suite must include these cases.

| Case id | Dimension | Purpose | Expected output |
| --- | --- | --- | --- |
| `whole_file_lf` | whole-file, LF | whole-file generated target hash stability | available |
| `whole_file_crlf` | whole-file, CRLF | CRLF preservation and hash distinction | available |
| `whole_file_trailing_newline` | whole-file, trailing newline | trailing newline preserved in hash | available |
| `whole_file_bom` | whole-file, BOM | BOM bytes preserved in hash | available |
| `managed_block_lf` | managed-block, LF | managed inner content hash stability | available |
| `managed_block_crlf` | managed-block, CRLF | managed block CRLF preservation | available |
| `mixed_boundary` | mixed-boundary | user-owned external content excluded | available |
| `unavailable_adapter` | unavailable | adapter unavailable classification | unavailable |
| `unavailable_nondeterministic` | unavailable | nondeterministic output blocked | unavailable |
| `unavailable_timeout` | unavailable | timeout classification | unavailable |

Additional future cases may include:

- unsupported sync mode
- activation unresolved
- generation disabled
- marker invalid
- provider version migration

## Replay comparison contract

Replay validation must compare these fields exactly.

Required exact matches:

- `schema_version`
- `entry_id`
- `preview_available`
- `generated_content_kind`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `provider_metadata`
- `provenance`
- `unavailable_reason`
- `deterministic`

Hash comparison:

- Exact string equality only.
- No hash normalization.
- No line ending normalization during comparison.
- Non-null hashes must use `sha256:<lowercase-hex>`.

Provenance comparison:

- Source path order must match exactly.
- Source hash values must match exactly.
- Activation reference must match exactly.
- Rule context reference must match exactly.
- `generated_by` must match exactly.

Provider metadata comparison:

- Provider id must match exactly.
- Provider version must match exactly.
- Hash policy must match exactly.
- Supported sync mode metadata must match exactly when present.
- Output-affecting config references must match the provider snapshot.

Unavailable output comparison:

- `preview_available` must be `false`.
- Generated hash fields must be `null`.
- `unavailable_reason` must match exactly.
- Provider metadata must be present.
- Deterministic flag must match exactly.

## Failure codes

Replay validation should use these failure codes.

- `replay-hash-mismatch`
- `replay-provenance-mismatch`
- `replay-provider-metadata-mismatch`
- `replay-unavailable-reason-mismatch`
- `replay-deterministic-flag-mismatch`
- `replay-schema-mismatch`
- `replay-fixture-missing`
- `replay-provider-version-drift`

Failure policy:

- Replay mismatch is a validation failure.
- Fixture missing is a validation failure.
- Provider version drift without explicit migration note is a validation failure.
- Automatic retry is forbidden.

## Fixture validation rules

Fixture validation must enforce:

- no placeholder hashes
- all non-null hashes use `sha256:<lowercase-hex>`
- source path order is stable and explicit
- unavailable outputs have null generated hashes
- provider metadata is present in every output
- provider snapshot exists for the replay manifest provider
- case ids are unique
- fixture paths are relative and safe
- replay dimensions are non-empty

Placeholder examples that must be rejected:

- `sha256:<source>`
- `sha256:<generated>`
- `sha256:TODO`
- `sha256:placeholder`

## Snapshot update policy

Replay snapshots must not update automatically.

Rules:

- No automatic snapshot update.
- Output-affecting provider changes require provider version bump.
- Intentional snapshot changes require migration note.
- Same provider version must preserve exact expected outputs.
- Snapshot updates must be reviewed as source changes.

Migration note should include:

- provider id
- old provider version
- new provider version
- affected cases
- reason for output drift
- hash policy impact
- confirmation that mutation remains blocked

## Non-goals

This contract does not implement or authorize:

- provider implementation
- adapter runtime
- generated content generation
- sync apply
- target mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, or deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- orchestration
- workflow execution
- `.ai/registry/`
- auto-fix
- source mutation

## Future implementation sequence

Recommended next implementation sequence:

1. Add replay fixture JSON files.
2. Add replay fixture schema tests.
3. Add replay manifest validation helpers.
4. Add provider snapshot validation helpers.
5. Add fixture-backed replay validation.
6. Only after replay validation is stable, consider a real provider implementation plan.

## 결론

Replay fixture contract는 real preview provider validation의 first gate다. Fixture layout, manifest schema, provider snapshot, required cases, exact comparison rules, failure codes, snapshot update policy를 먼저 고정해야 provider implementation이 deterministic behavior를 증명할 수 있다. 이 계약은 read-only validation 준비이며 sync apply나 mutation을 승인하지 않는다.
