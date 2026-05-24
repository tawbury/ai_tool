# Documentation Governance Rules

## Scope

Use this file when a task creates, updates, classifies, promotes, deprecates, or interprets documents under `docs/`.

## Responsibilities

- Define runtime-facing document governance rules.
- Prevent plans, audits, ADRs, reports, examples, and philosophy from being treated as runtime contracts.
- Define how durable documentation insights become effective runtime rules.

## Document Taxonomy

- `spec`: detailed human-readable specification.
- `adr`: architectural decision record.
- `plan`: planning artifact for future or active work.
- `audit`: observational diagnosis, findings, and recommendations.
- `historical`: retained past state, migration note, or superseded context.
- `reference`: navigation, examples, background, or supporting material.

## Authority Hierarchy

Runtime authority is ordered as follows:

1. Latest explicit user request.
2. Active runtime system or developer instructions.
3. `.ai/rules/rules.md`.
4. Task-relevant `.ai/rules/domains/*.rules.md`.
5. Task-relevant `.ai/rules/operations/*.rules.md`.
6. Task-relevant `.ai/commands/*.command.md`, `.ai/agents/*.agent.md`, `.ai/skills/**/*.skill.md`, `.ai/workflows/**/*.workflow.md`, and `.ai/validators/**/*.md` executable contract sections.
7. Active normative specs under `docs/specs/`, when explicitly relevant.
8. ADRs, plans, audits, reports, historical notes, and reference documents as human context only.

## Runtime Consumption Boundary

- `.ai/` is the canonical runtime source of truth.
- `docs/specs/` contains detailed human-readable specifications. Specs are not always-load context.
- `docs/adr/` contains decision records. ADRs are not runtime contracts.
- `docs/plan/` contains planning artifacts. Plans are not runtime contracts.
- `docs/reports/` contains audits, implementation reports, and cleanup reports. Reports are not runtime contracts.
- Runtime loaders and validators must not automatically consume plans, reports, ADRs, examples, philosophy, or human-review-only criteria.
- Runtime loaders and validators may consume active specs only when explicitly relevant and only as supporting context unless the spec has been promoted into `.ai/`.

## Promotion Rule

- Audit or plan insights become effective runtime rules only after promotion into the smallest relevant `.ai/` source file or an active normative spec.
- Durable runtime behavior belongs in `.ai/rules/`, `.ai/commands/`, `.ai/agents/`, `.ai/skills/`, `.ai/workflows/`, or `.ai/validators/`.
- Do not rely on `docs/plan/`, `docs/reports/`, or `docs/adr/` as the only source for runtime behavior.

## Documentation Index Maintenance

- `docs/index/` files are summary-first human context, not runtime contracts.
- `.ai/rules/` remains the canonical runtime authority.
- New `docs/plan/*` or `docs/reports/*` artifacts must consider whether `docs/index/document_status_registry.md` needs a new or updated entry.
- Phase-level or runtime-impacting work must consider whether `docs/index/phase_6_8_summary.md` or a future phase summary needs an update.
- Runtime-facing behavior changes must consider whether `docs/index/current_runtime_context.md` needs an update.
- Index maintenance must not make docs indexes always-load runtime contracts.
- Index maintenance must not add automatic docs loading.

## Selective Loading

- Load this rule only for documentation governance, document taxonomy, runtime consumption boundary, promotion, deprecation, or supersession tasks.
- Do not load this rule for ordinary code, validation, workflow, skill, or report-writing tasks unless the task explicitly concerns documentation governance.

## Related Documents

- `docs/specs/documentation_governance_spec.md`
- `docs/adr/0001-documentation-governance.md`
- `docs/plan/documentation_migration_plan.md`
- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`
