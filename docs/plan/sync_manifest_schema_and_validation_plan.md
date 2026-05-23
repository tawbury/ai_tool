# Sync Manifest Schema and Validation Plan

## 개요

이 문서는 future `.ai OS` sync dry-run이 사용할 manifest schema와 validation boundary를 정밀화한다. Phase 7 `aios sync --dry-run` 구현 전 gate로 작성하며, runtime code를 변경하지 않는다.

현재 시스템은 read-only이다. 이 문서는 manifest generation, manifest persistence, sync apply, mutation, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Canonical Manifest Schema Candidate

초기 schema version은 다음으로 고정한다.

```text
aios.sync_manifest.v0
```

권장 top-level shape:

```json
{
  "schema_version": "aios.sync_manifest.v0",
  "repository_id": "repo_ai_tool",
  "generated_at": "2026-05-23T00:00:00Z",
  "source_root": ".ai",
  "target_root": ".",
  "managed_entries": []
}
```

주의:

- 이전 Phase 6 문서의 `manifest_version` 후보는 `schema_version`으로 정규화한다.
- future compatibility를 위해 `manifest_version` 별칭을 읽을 수는 있지만, canonical field는 `schema_version`이다.
- manifest는 state record이며 source of truth가 아니다. `.ai/`가 계속 source of truth이다.

## Top-level Fields

| Field | Required | Nullable | Type | 설명 |
|---|---:|---:|---|---|
| `schema_version` | yes | no | string | manifest schema version. `aios.sync_manifest.v0` |
| `repository_id` | yes | no | string | repository identity. stable configured or derived id |
| `generated_at` | yes | no | string | ISO 8601 UTC timestamp |
| `source_root` | yes | no | string | source root. 초기 값은 `.ai` |
| `target_root` | yes | no | string | target root. 초기 값은 `.` |
| `managed_entries` | yes | no | array | managed entry list |
| `meta` | no | yes | object | future extension metadata |

Optional future fields:

- `created_by`
- `generator_version`
- `activation_reference`
- `trace_id`
- `notes`

## Managed Entry Schema

권장 entry shape:

```json
{
  "entry_id": "entry_codex_root_adapter_rules",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "ownership": "mixed-boundary",
  "sync_mode": "mixed-boundary",
  "source_hash": "sha256:<source-content>",
  "target_hash": "sha256:<managed-content>",
  "marker": {
    "marker_version": "0",
    "marker_style": "markdown-html-comment",
    "entry_id": "entry_codex_root_adapter_rules"
  },
  "generated": {
    "generated_by": "aios.sync.v0",
    "generated_at": "2026-05-23T00:00:00Z"
  }
}
```

### Entry Fields

| Field | Required | Nullable | Type | 설명 |
|---|---:|---:|---|---|
| `entry_id` | yes | no | string | stable manifest entry identity |
| `source_path` | yes | no | string | repository-relative source path |
| `target_path` | yes | no | string | repository-relative target path |
| `ownership` | yes | no | string | ownership enum |
| `sync_mode` | yes | no | string | sync mode enum |
| `source_hash` | yes | no | string | expected source hash |
| `target_hash` | yes | yes | string 또는 null | expected target or managed block hash |
| `marker` | conditional | yes | object 또는 null | marker metadata for mixed-boundary or managed block targets |
| `generated` | yes | no | object | generated metadata |
| `meta` | no | yes | object | future entry metadata |

Conditional rules:

- `marker` is required when `sync_mode` is `managed-block` or `mixed-boundary`.
- `marker` must be null or omitted when `sync_mode` is `whole-file`.
- `target_hash` may be null for first-create candidates only if a future first-create policy explicitly allows it.
- `source_hash` must not be null.

## Generated Metadata Schema

```json
{
  "generated_by": "aios.sync.v0",
  "generated_at": "2026-05-23T00:00:00Z",
  "generator_version": "0"
}
```

| Field | Required | Nullable | Type | 설명 |
|---|---:|---:|---|---|
| `generated_by` | yes | no | string | generator identity |
| `generated_at` | yes | no | string | ISO 8601 UTC timestamp |
| `generator_version` | no | yes | string | optional generator version |

Generated metadata is provenance only. It must not authorize writes.

## Required Fields

Top-level required:

- `schema_version`
- `repository_id`
- `generated_at`
- `source_root`
- `target_root`
- `managed_entries`

Managed entry required:

- `entry_id`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `source_hash`
- `target_hash`
- `generated`

Generated metadata required:

- `generated_by`
- `generated_at`

Marker metadata required when present:

- `marker_version`
- `marker_style`
- `entry_id`

## Optional Fields

Optional fields are allowed only when consumers can ignore them safely.

Top-level optional:

- `meta`
- `created_by`
- `generator_version`
- `activation_reference`
- `trace_id`

Entry optional:

- `meta`
- `source_paths`
- `target_block_id`
- `adapter`
- `activation_reference`
- `trace_id`

Rule:

- Unknown fields should be warnings in `aios validate <manifest>` for v0 unless they shadow known field names or change required semantics.
- Unknown fields must not alter sync dry-run behavior.

## Nullable Fields

Allowed nullable fields:

- top-level `meta`
- entry `target_hash` only for explicit first-create candidate policy
- entry `marker` only when `sync_mode` is `whole-file`
- optional metadata fields

Disallowed null:

- `schema_version`
- `repository_id`
- `generated_at`
- `source_root`
- `target_root`
- `managed_entries`
- `entry_id`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `source_hash`
- `generated.generated_by`
- `generated.generated_at`

## Enum Values

### Ownership Enum

Allowed values:

- `runtime-managed`
- `user-owned`
- `mixed-boundary`

Rules:

- `runtime-managed` may pair with `whole-file`.
- `mixed-boundary` may pair with `managed-block` or `mixed-boundary`.
- `user-owned` must not produce write candidates. It may appear only for observe/skip style manifest entries if future policy allows it.

### Sync Mode Enum

Allowed values:

- `whole-file`
- `managed-block`
- `mixed-boundary`

Rules:

- `whole-file` means the whole target content is the managed hash boundary.
- `managed-block` means a marker-delimited block is the managed hash boundary.
- `mixed-boundary` means a marker-delimited block exists inside a file that also has user-owned content.

Compatibility note:

- Earlier plans used `observe-only` and `disabled` as possible modes. For `aios.sync_manifest.v0`, they are not part of the core sync mode enum. If observation-only entries are needed later, they should be represented by a separate field or a v1 schema revision.

## Marker Metadata Schema

```json
{
  "marker_version": "0",
  "marker_style": "markdown-html-comment",
  "entry_id": "entry_codex_root_adapter_rules"
}
```

| Field | Required | Nullable | Type | 설명 |
|---|---:|---:|---|---|
| `marker_version` | yes | no | string | supported marker contract version |
| `marker_style` | yes | no | string | marker syntax style |
| `entry_id` | yes | no | string | marker-bound entry identity |

Allowed `marker_style` values:

- `markdown-html-comment`
- `hash-line-comment`
- `yaml-line-comment`

Rules:

- `marker.entry_id` must equal the managed entry `entry_id`.
- `marker_version` initial value is `"0"`.
- unsupported marker version is a schema error or runtime conflict depending on when it is detected.
- marker metadata does not prove target marker exists; the marker parser must still inspect the target file.

## Path Validation Policy

Paths must be repository-relative.

Rules:

- absolute paths are schema errors.
- parent traversal using `..` is a schema error.
- empty paths are schema errors.
- paths must use `/` as canonical separator in manifest JSON.
- `source_path` must be under `source_root`.
- `target_path` must be under `target_root`.
- path normalization must not allow escaping repository root.
- duplicate target paths are warnings or errors depending on ownership and sync mode; duplicate same `entry_id` is an error.

Recommended normalization:

- convert `\` to `/` for validation diagnostics only.
- preserve manifest string in output.
- resolve against repository root only after schema path checks pass.

## Hash Field Policy

Hash string format:

```text
<algorithm>:<hex-digest>
```

Initial supported algorithm:

- `sha256`

Rules:

- hash algorithm prefix is required.
- digest must be lowercase hex.
- unsupported algorithm is schema error.
- `source_hash` is hash of source content or source bundle.
- `target_hash` is hash of whole target for `whole-file`.
- `target_hash` is hash of marker inner content for `managed-block` and `mixed-boundary`.

### Observed vs Normalized Hash Boundary

Manifest schema must record what hash policy was used before implementation begins.

Initial plan recommendation:

- use observed UTF-8 bytes for source and target content.
- exclude marker lines from managed block hash.
- do not normalize CRLF/LF implicitly in v0.
- record any future normalization policy under `meta.hash_policy` if needed.

Rationale:

- observed bytes preserve exact drift.
- implicit normalization can hide file changes.
- marker exclusion keeps marker metadata changes separate from managed content drift.

## Future Extension Policy

Extension rules:

- v0 readers must ignore unknown optional `meta` fields.
- fields outside `meta` should be conservative warnings.
- required semantic changes require a new `schema_version`.
- enum additions require either v1 or explicit v0 compatibility note.
- deprecated fields must remain readable for at least one compatibility period after v1 is introduced.

Do not add extension fields that authorize mutation without a runtime-facing rule update.

## Manifest Validation Strategy

### `aios validate <manifest>`

Future `aios validate <manifest>` should validate manifest files as first-class runtime targets.

Scope:

- schema version
- required fields
- nullability
- enum values
- path shape
- hash format
- duplicate `entry_id`
- marker metadata shape
- ownership/sync_mode compatibility
- source path existence may be warning or error depending on policy

Non-scope:

- drift detection
- target hash comparison
- marker parsing in target files
- dry-run action classification
- file mutation

### Sync Internal Validation

`aios sync --dry-run` must validate manifest schema before runtime evaluation.

Internal validation scope:

- all schema validation required by `aios validate <manifest>`
- source existence check
- target existence check
- marker parsing
- hash comparison
- drift/conflict classification

Invalid schema stops runtime evaluation.

### Schema Validation vs Runtime Evaluation

Schema validation answers:

- Is the manifest structurally valid?
- Are paths safe?
- Are enum and hash fields well-formed?
- Is marker metadata internally consistent?

Runtime evaluation answers:

- Do sources exist now?
- Do targets exist now?
- Are markers present and valid now?
- Do current hashes match manifest hashes?
- Is the result create, update, skip, conflict, drift-stop, or orphan-warning?

Boundary:

- invalid manifest structure -> schema error
- valid manifest but current target drifted -> runtime conflict or drift-stop
- valid manifest but source missing -> runtime conflict unless `aios validate <manifest>` policy elevates it

## Fail vs Warn Conditions

Schema error:

- missing required field
- invalid schema version
- invalid enum value
- invalid path shape
- parent traversal
- invalid hash format
- duplicate `entry_id`
- marker.entry_id mismatch
- marker required but missing
- unsupported marker_style

Warning:

- unknown optional field outside `meta`
- duplicate target path with non-writing ownership, if future policy allows it
- source path missing during validate-only mode, if configured as static warning
- target path missing during validate-only mode
- future schema alias such as `manifest_version` used instead of `schema_version`

Runtime conflict:

- source missing during sync dry-run
- marker missing for expected existing block
- marker duplicated
- marker corrupted
- ownership violation

Drift-stop:

- target hash mismatch
- managed block hash mismatch

## Invalid Manifest Classification

### Usage Error

Usage error means CLI invocation is wrong.

Examples:

- `--manifest` provided without a path
- manifest path points outside repository after path resolution
- `--envelope-v2` used without `--json`

Exit code: 2.

### Schema Error

Schema error means the manifest file was found but is structurally invalid.

Examples:

- missing `schema_version`
- unsupported schema version
- missing `managed_entries`
- invalid path traversal
- invalid hash format
- invalid ownership enum

Exit code:

- `aios validate <manifest>`: existing validate fail policy.
- `aios sync --dry-run`: status `fail`, exit code 1.

### Runtime Conflict

Runtime conflict means the manifest is structurally valid but current repository state prevents safe sync planning.

Examples:

- source missing
- marker corrupted
- target modified
- ownership violation

Exit code:

- `aios sync --dry-run`: status `fail`, exit code 1.
- `aios validate <manifest>` should not perform full drift evaluation unless explicitly designed.

## Envelope v2 Mapping for Manifest Validation

Future `aios validate <manifest> --json --envelope-v2` mapping:

- `schema_version`: `aios.command_result.v2`
- `command`: `validate`
- `status`: `pass`, `warn`, or `fail`
- `root`: repository root
- `target`: manifest path
- `summary`: schema errors, warnings, info counts
- `messages`: manifest validation messages
- `payload.results`: validation results
- `meta.legacy_schema_version`: current validate schema
- `meta.manifest_schema_version`: manifest `schema_version` when available

Future `aios sync --dry-run --json --envelope-v2` mapping:

- `command`: `sync`
- `status`: dry-run status
- `target`: manifest path or repository root
- `summary`: dry-run action and severity counts
- `messages`: schema errors, runtime conflicts, drift stops, warnings
- `payload.results`: dry-run results
- `meta.dry_run`: true
- `meta.manifest_schema_version`: manifest `schema_version`

## Explicit Non-goals

This plan does not implement:

- manifest generation
- manifest persistence
- sync apply
- mutation
- transaction log persistence
- rollback execution
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation

## Phase 7 Gate Decision

This plan satisfies the manifest schema precision gate for Phase 7 planning.

Before runtime implementation starts, two related gates still need separate documents:

- managed block parser fixture plan
- hash normalization and insertion anchor decision, unless folded into the parser fixture plan
