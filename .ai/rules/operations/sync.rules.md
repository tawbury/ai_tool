---
description: "Runtime sync dry-run and manifest safety rules"
globs: ".ai/**/*.md,.ai/**/*.yaml,.ai/**/*.yml,src/aios/**/*.py,aios/**/*.py"
alwaysApply: false
---

<!-- ai-governance:start runtime-policy v2 -->
# Sync Rules

## Purpose

Sync rules define the read-only runtime contract for `.ai OS` sync manifest validation and dry-run evaluation.

Phase 8 v0 supports read-only sync evaluation with optional fixture-backed generated preview comparison. These rules authorize inspection, manifest validation, marker parsing, hash comparison, fixture preview comparison, dry-run result reporting, and envelope output. They do not authorize sync apply, file mutation, manifest persistence, rollback execution, adapter generation, real preview providers, generated content creation, force, or decommission.

## Supported Runtime Commands

The supported Phase 8 v0 commands are:

- `python -m aios sync --dry-run --manifest <path>`
- `python -m aios sync --dry-run --manifest <path> --json`
- `python -m aios sync --dry-run --manifest <path> --json --envelope-v2`
- `python -m aios sync --dry-run --manifest <path> --json --preview-provider fixture --preview-fixtures <path>`
- `python -m aios sync --dry-run --manifest <path> --json --envelope-v2 --preview-provider fixture --preview-fixtures <path>`
- `python -m aios validate <sync-manifest.json>`
- `python -m aios validate <sync-manifest.json> --json`
- `python -m aios validate <sync-manifest.json> --json --envelope-v2`

`aios sync` requires `--dry-run`. `aios sync --dry-run` requires `--manifest <path>`. `--envelope-v2` requires `--json`. Preview support is opt-in only and requires both `--preview-provider fixture` and `--preview-fixtures <path>`.

Usage and configuration errors must exit with code `2`, including provider without fixtures, fixtures without provider, and unsupported preview provider.

## Source of Truth

`.ai/` remains the runtime source of truth.

A sync manifest is a state record for provenance, drift detection, dry-run explanation, and future rollback preconditions. It is not a replacement source of truth and must not override `.ai/` rules, activation files, agents, validators, workflows, or inventories.

Sync planning is assumed to be one-way from `.ai/` source material toward managed targets unless a separate bidirectional design is approved.

## Read-only Invariant

Phase 8 v0 sync runtime must remain read-only.

Allowed read-only actions:

- load a manifest JSON file
- validate manifest schema and static fields
- read source and target files
- compute observed UTF-8 byte hashes
- parse managed markers and insertion anchors
- load fixture preview input/output mappings when explicitly configured
- compare generated preview hashes against clean target hashes
- classify dry-run actions and warnings
- emit human, native JSON, and envelope v2 output

Forbidden actions:

- create, update, delete, or rewrite target files
- write manifests
- write transaction logs
- insert, repair, or delete markers
- generate adapters or preview content
- execute real preview providers
- execute workers or workflows
- auto-fix source or target files

## Manifest Contract

Supported sync manifest schema:

- `schema_version: aios.sync_manifest.v0`

Required top-level fields:

- `schema_version`
- `repository_id`
- `generated_at`
- `source_root`
- `target_root`
- `managed_entries`

Required managed entry fields:

- `entry_id`
- `source_path`
- `target_path`
- `ownership`
- `sync_mode`
- `source_hash`
- `target_hash`
- `generated`

Supported ownership values:

- `runtime-managed`
- `user-owned`
- `mixed-boundary`

Supported sync modes:

- `whole-file`
- `managed-block`
- `mixed-boundary`

Manifest paths must be repository-relative, non-empty, and must not use parent traversal. Hashes must use `sha256:<lowercase-hex>`. `managed-block` and `mixed-boundary` entries require marker metadata. `whole-file` entries must not use marker metadata.

`aios validate <sync-manifest.json>` performs schema and static validation only. It must not perform source existence checks, target existence checks, marker parsing, hash comparison, drift classification, generated preview comparison, or sync action planning.

## Hash Policy

Phase 8 v0 continues to use observed UTF-8 bytes.

Rules:

- Do not normalize CRLF/LF.
- Preserve trailing newlines and whitespace.
- Include BOM bytes if present.
- Use only `sha256`.
- Exclude begin/end marker lines from managed block content hashes.
- Include managed block inner content exactly as observed.

## Marker Rules

Supported marker styles:

- `markdown-html-comment`
- `hash-line-comment`
- `yaml-line-comment`

Supported marker integrity classifications include:

- `valid`
- `begin-missing`
- `end-missing`
- `begin-duplicated`
- `end-duplicated`
- `marker-malformed`
- `marker-nested`
- `entry-id-mismatch`
- `marker-version-unsupported`

Rules:

- Exactly one begin/end pair is allowed per `entry_id`.
- Begin and end markers must bind the same `entry_id` and `marker_version`.
- Marker integrity is checked before content hash comparison.
- Marker-like text inside Markdown code fences must not be parsed as a marker.
- Missing, duplicated, malformed, nested, mismatched, or unsupported markers are blocking conflicts.
- Insertion anchors may be parsed for future planning, but the runtime must not insert content.

## Dry-run Evaluation

`aios sync --dry-run --manifest <path>` evaluates manifest entries without writing files.

Native JSON output uses:

- `schema_version: aios.sync_dry_run.v0`
- `status: pass|warn|fail`
- `mode: dry-run`
- `summary`
- `results`
- `messages`
- `meta.dry_run: true`
- `meta.mutation_performed: false`

Supported actions:

- `create`
- `update`
- `skip`
- `conflict`
- `drift-stop`
- `orphan-warning`

Status policy:

- Blocking conflicts produce `status: fail` and exit code `1`.
- Warning-only results produce `status: warn` and exit code `0`.
- Safe informational results produce `status: pass` and exit code `0`.

## Fixture Preview Support

Generated preview comparison is opt-in and fixture-backed only.

Rules:

- There is no default preview provider.
- The only supported provider is `--preview-provider fixture`.
- `--preview-fixtures <path>` must point to fixture mappings used by the fixture provider.
- Preview is a read-only comparison input, not generated content creation.
- Preview must never read or write target files directly.
- Preview must never execute adapters, workers, workflows, or model calls.
- Missing preview mapping or unavailable preview output must not create an update candidate.

Preview can classify a clean target as an update candidate:

- `action: update`
- `severity: informational`
- `meta.mutation_performed: false`

An update candidate is not write authorization. It only reports that the clean target differs from the fixture-backed generated preview hash.

Native preview fields may include:

- `hashes.generated_target_hash`
- `hashes.generated_managed_block_hash`
- `details.preview`
- `details.preview_unavailable_reason`
- `meta.preview_provider`
- `meta.preview_policy`

Expected preview metadata:

- `meta.preview_provider: fixture`
- `meta.preview_policy: read-only-fixture`

Preview unavailable means no update candidate. The runtime preserves the existing dry-run result and records the unavailable reason when available.

## Drift-stop and Conflict Policy

The runtime must fail closed.

- `source-missing` is a blocking `conflict`.
- `source-missing` beats preview comparison.
- Missing target with `whole-file` and `runtime-managed` ownership may be a read-only `create` candidate.
- Missing target for `managed-block` or `mixed-boundary` without explicit first-create support is a blocking `conflict`.
- Valid marker plus target hash match is `skip` when no preview is configured or generated preview is unavailable.
- Valid marker plus target hash match may become read-only `update` when an explicitly configured fixture preview provides a different generated managed block hash.
- Valid marker plus target hash mismatch is blocking `drift-stop` with `target-modified`.
- Whole-file target hash mismatch is blocking `drift-stop` with `target-modified`.
- Missing expected marker is blocking `conflict` with `marker-missing`.
- Duplicated marker is blocking `conflict` with `marker-duplicated`.
- Malformed, nested, mismatched, or unsupported marker is blocking `conflict` with `marker-corrupted` or a specific marker code when available.
- Orphan marker detection, when safely available from the manifest target scope, is `orphan-warning`.

Precedence:

- source-missing beats preview
- marker conflict beats preview
- drift-stop beats preview
- preview unavailable means no update candidate

No write may proceed from any blocking drift or conflict state.

## Envelope v2 Compatibility

Sync dry-run and sync manifest validation support envelope v2 when `--json --envelope-v2` is used.

Sync envelope mapping:

- `command: sync`
- `target.kind: sync-manifest`
- `meta.legacy_schema_version: aios.sync_dry_run.v0`
- `payload.results`: dry-run results
- `messages`: blocking and warning dry-run messages
- `meta.dry_run: true`
- `meta.mutation_performed: false`
- `meta.preview_provider: fixture` when fixture preview is configured
- `meta.preview_policy: read-only-fixture` when fixture preview is configured

Preview metadata and generated hash fields must be preserved in `payload.results`.

Validate envelope mapping:

- `command: validate`
- `target.kind: sync-manifest`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `payload.results`: validation results
- `messages`: validation messages with validator, field, and entry id details when available

## Mutation Blocked

Sync apply and all mutation remain blocked.

Mutation requires a future readiness gate that explicitly approves:

- sync apply architecture
- manifest persistence lifecycle
- transaction log storage
- rollback dry-run and rollback execution preconditions
- marker insertion, update, repair, deletion, and decommission policy
- generated preview contract
- real preview provider contract
- force policy, if any

Until that gate exists, AIOS sync must remain read-only. Fixture preview update candidates do not satisfy the mutation readiness gate.

## Activation Boundary

Activation v1 may influence future sync planning inputs only after a separate sync selection design exists.

Activation does not authorize writes, change ownership, bypass drift-stop, repair markers, write manifests, generate adapters, choose preview providers, create preview content, discover default manifests, or execute sync apply.

## Future Expansion Boundary

Future work must be designed separately before implementation:

- real generated preview provider contract
- repository-wide unmanaged and orphan scan
- default manifest discovery
- manifest preview generation
- activation-driven sync selection
- transaction and rollback implementation
- sync apply architecture
- adapter generation
- force and decommission

Each expansion must preserve the read-only boundary until an explicit mutation gate is approved.

## Non-goals

These rules do not authorize:

- sync apply
- target file mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion, or rewrite
- adapter generation
- real preview provider execution
- generated preview content creation
- default manifest discovery
- manifest preview generation
- repository-wide unmanaged scan
- activation-driven sync selection
- orchestration
- worker execution or dispatch
- workflow execution
- registry parser implementation
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation
<!-- ai-governance:end -->
