---
description: "Runtime sync and manifest safety rules"
globs: ".ai/**/*.md,.ai/**/*.yaml,.ai/**/*.yml,src/aios/**/*.py,aios/**/*.py"
alwaysApply: false
---

<!-- ai-governance:start runtime-policy v1 -->
# Sync Rules

## Purpose

Sync rules define the safety boundary for future `.ai OS` sync and manifest behavior.

Phase 6 is safety design only. These rules do not authorize sync implementation, file mutation, manifest persistence, adapter generation, rollback execution, force, or decommission.

## Source of Truth

`.ai/` remains the runtime source of truth.

A future manifest is a state record for provenance, drift detection, dry-run explanation, and rollback preconditions. It is not a replacement source of truth and must not override `.ai/` rules, activation files, agents, validators, workflows, or inventories.

Future sync is assumed to be one-way from `.ai/` source material toward managed targets unless a separate bidirectional design is approved.

## Ownership Model

Future sync planning must classify targets by ownership:

- `runtime-managed`: the whole target may be managed by AIOS policy.
- `user-owned`: the target is observed only and must not be written by sync.
- `mixed-boundary`: user-owned content and runtime-managed blocks coexist in one file.

Mixed-boundary targets may only consider the managed block inside valid markers. Marker-external content is user-owned.

## Drift States

Future dry-run and manifest checks should use these drift states:

- `clean`: current managed content matches the last recorded managed state.
- `drifted`: current managed content differs from the last recorded managed state.
- `missing`: an expected target or managed block is absent.
- `orphaned`: a managed marker exists without a matching manifest entry.
- `unmanaged`: a target exists without managed ownership.

## Default Drift-stop Policy

Future sync must fail closed.

- `target-modified` requires `drift-stop`.
- `marker-missing`, `marker-duplicated`, and `marker-corrupted` require `conflict`.
- `source-missing` requires `conflict`.
- `ownership-violation` requires `conflict`.
- `unmanaged-target` is warning/skip only.
- `orphaned-managed-block` is warning only until a decommission policy exists.

No future write may proceed from a blocking drift or conflict state.

## Dry-run-first Policy

Future sync must provide dry-run before mutation.

Dry-run output should report:

- action: `create`, `update`, `skip`, `conflict`, `drift-stop`, or `orphan-warning`
- severity: informational, warning, or blocking
- stop reason
- recovery hint
- source and target paths
- ownership and sync mode
- drift state
- hashes and marker details when available

Blocking results must produce a failing command status. Warning-only results should produce a warning status. Safe create/update/skip candidates may pass.

## Managed Block Markers

Managed block markers define the only writable boundary inside mixed-boundary targets.

Canonical marker shape:

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_example marker_version=0 generated_by=aios.sync.v0 -->
Managed content.
<!-- AIOS:END managed-block entry_id=entry_example marker_version=0 -->
```

Rules:

- Exactly one begin/end pair is allowed per `entry_id`.
- Begin and end markers must have the same `entry_id` and `marker_version`.
- Marker lines are not part of the managed content hash.
- Marker integrity is checked before content hash comparison.
- Marker-like text inside Markdown code fences must not be parsed as a marker unless a future explicit policy allows it.
- Missing, duplicated, malformed, nested, or mismatched markers are blocking conflicts.

Insertion requires an explicit anchor and first-create policy. Update requires a valid marker and clean managed hash. Removal is forbidden until decommission is separately designed.

## Rollback and Transaction Preconditions

Rollback cannot be an afterthought. Future mutation must preserve rollback evidence before writing.

Future transaction records should preserve:

- transaction identity and timestamps
- command, mode, root, and manifest version
- entry id, action, target path, ownership, and sync mode
- pre-hash and post-hash
- pre-image or reversible patch reference
- marker boundary information
- entry status

Future rollback is allowed only when:

- a transaction record exists
- a pre-image or reversible patch exists
- the current target still matches the recorded post-hash
- the marker boundary is still valid
- user-owned content outside the managed boundary will not be rolled back

Rollback is forbidden when transaction evidence is missing, the target changed after the transaction, markers are corrupted, ownership mismatches, or mixed-boundary external content would be modified.

Rollback must also be dry-run-first.

## Activation Boundary

Activation v1 may influence future sync planning inputs, such as active rules or source selection, only after a separate sync selection design exists.

Activation does not authorize writes, change ownership, bypass drift-stop, repair markers, write manifests, generate adapters, or execute sync.

## Envelope and Observability Compatibility

Future sync and rollback results should map to envelope v2:

- `command`: `sync` or `rollback`
- `status`: `pass`, `warn`, or `fail`
- `summary`: action and severity counts
- `messages`: conflicts, drift stops, warnings, and rollback forbidden reasons
- `payload`: dry-run results, manifest preview, or transaction details
- `meta`: dry-run flag, manifest version, transaction id, and optional trace id

Future observability events must be opt-in and read-only. Candidate sync events include dry-run started, marker checked, drift detected, conflict detected, stop required, transaction started, transaction completed, and rollback precondition failed.

## Non-goals

These rules do not authorize:

- sync execution
- manifest persistence
- transaction log persistence
- rollback execution
- adapter generation
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
