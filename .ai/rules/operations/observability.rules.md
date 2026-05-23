---
description: "Runtime observability and future event trace rules"
globs: ".ai/**/*.md,.ai/**/*.yaml,.ai/**/*.yml,src/aios/**/*.py,aios/**/*.py"
alwaysApply: false
---

# Observability Rules

## Purpose

Runtime observability defines how AIOS commands should describe what happened without changing source files or executing workflows.

The current runtime exposes final command results through JSON outputs and optional envelope v2. Future runtime events and traces may add ordered observation records, but they must remain read-only.

## Envelope v2 vs Runtime Events

- Envelope v2 is the final command result shape.
- Runtime events are future opt-in records of command progress, warnings, exclusions, references, and provenance.
- Events must complement envelope v2, not replace it.
- Existing JSON output must remain valid without event output.

## Future Event Categories

Future event taxonomy should stay grouped by runtime concern:

- Command lifecycle: command started, completed, failed.
- Phase lifecycle: phase started, completed, failed.
- Inventory: discovery started, item discovered, discovery completed.
- Validation: target selected, validator started, result, warning, failed, completed.
- Activation: parsed, schema invalid, reference resolved, missing reference, invalid loader profile, duplicate reference, empty set.
- Context loading: profile selected, chunk extracted, chunk excluded, budget warning, provenance recorded.

## Event Schema Expectations

Future event objects should include these fields when applicable:

- `event_id`
- `trace_id`
- `parent_trace_id`
- `timestamp`
- `event_type`
- `command`
- `phase`
- `status`
- `severity`
- `code`
- `target`
- `provenance`
- `details`

Use stable machine-readable values for `event_type`, `status`, `severity`, and `code`.

## Trace Model

- A single command run should have one primary `trace_id`.
- Future command chains may connect child traces with `parent_trace_id`.
- Trace relationships must describe command and phase relationships only; they must not imply worker execution or workflow orchestration.
- Event records should be reducible to envelope v2 `messages`, `summary`, and `meta` where practical.

## Provenance Preservation

Events that refer to files should preserve provenance using canonical repository paths and line ranges when known.

Context-loading events should preserve semantic layer, extraction method, line range, exclusion reason, and budget details when applicable.

Activation events should preserve reference type, reference value, resolution status, and canonical path when known.

## Future CLI Policy

Future event output must be opt-in. Candidate options:

- `--trace`
- `--emit-events`
- `--event-format jsonl`

Do not mix result JSON and event JSONL in a way that breaks machine consumers. If event persistence is ever needed, design it separately.

## Read-only Boundary

Observability must not mutate source files, activation contracts, inventories, rule files, workflows, or generated adapters.

## Non-goals

These rules do not authorize:

- event emission implementation
- event persistence
- telemetry or networking
- analytics pipelines
- distributed tracing
- sync
- manifest generation
- adapter generation
- orchestration
- worker execution or dispatch
- workflow execution
- registry parser implementation
- `.ai/registry/`
- auto-fix
- source mutation
