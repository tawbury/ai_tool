---
description: "Global rule contract for multi-AI CLI orchestration"
globs: "**/*"
alwaysApply: true
---

# Global Rules
*Last Updated: 2026-05-17*
*Version: 3.2.0*

## Purpose

This file is the global rule contract for Codex CLI, Claude Code, Gemini CLI, and future AI CLI tools used in this project.

Agents must read this file first, then load only the additional domain and operational rule files that are relevant to the current task.

## Source of Truth

- `.ai/rules/rules.md` is the single source of truth for shared project-wide AI rules.
- Root adapter files such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are discovery adapters only.
- Shared rule bodies must not be copied into root adapters.
- Tool-specific behavior belongs only in the corresponding adapter file or the tool runtime instructions.

## Rule Priority

When instructions conflict, apply this priority order:

1. Latest explicit user request
2. Runtime system or developer instructions for the active AI CLI
3. `.ai/rules/rules.md`
4. Task-relevant domain rules in `.ai/rules/domains/`
5. Task-relevant operational rules in `.ai/rules/operations/`
6. Root or tool-specific adapter files

## Root Adapter Policy

- `AGENTS.md` is the root adapter for Codex and generic AI CLI agents.
- `CLAUDE.md` is the root adapter for Claude Code.
- `GEMINI.md` is the root adapter for Gemini CLI.
- Adapters must remain thin and must point agents back to this file.
- Adapters must not become secondary rule sources or detailed rule indexes.

## Rule Layers

The shared AI system has these main layers:

```text
.ai/
  commands/
    README.md
    *.command.md

  rules/
    README.md
    rules.md

    domains/
      documentation.rules.md
      development.rules.md
      hr.rules.md

    operations/
      workflow.rules.md
      validation.rules.md
      agent.rules.md
      activation.rules.md
      context-loading.rules.md
      registry.rules.md
      observability.rules.md
      sync.rules.md
      documentation-governance.rules.md
```

- `commands/` contains reusable multi-CLI command definitions.
- `rules.md` defines the global contract only.
- `domains/` contains business or work-domain rules.
- `operations/` contains execution, validation, workflow, agent governance, activation, context loading, registry, observability, sync safety, and documentation governance rules.

## Shared Command Policy

- Reusable AI commands must be stored under `.ai/commands/`.
- Tool-specific command systems, such as Claude Code slash commands, may wrap or reference `.ai/commands/` entries, but must not become the canonical command source.
- When a user asks to run a named shared command, first read `.ai/commands/README.md`, then read the matching `.ai/commands/*.command.md` file.
- Shared command files define cross-CLI intent, inputs, workflow, validation, and reporting requirements.
- Tool adapters may describe how to invoke commands in that tool, but shared command behavior belongs only in `.ai/commands/`.

## Selective Loading

Load the minimum sufficient rule set for the current task.

- Always start with this file.
- Load a domain rule only when the task touches that domain.
- Load an operational rule only when the task requires that execution behavior or governance.
- Do not load all domain and operational files by default.

Typical loading examples:

| Task | Domain rules | Operational rules |
|---|---|---|
| Development architecture document | `documentation.rules.md`, `development.rules.md` | `workflow.rules.md`, `validation.rules.md` |
| Development runtime issue | `development.rules.md` | `validation.rules.md` |
| HR role evaluation report | `documentation.rules.md`, `hr.rules.md` | `workflow.rules.md`, `validation.rules.md` |
| Agent collaboration or escalation design | None unless domain-specific | `agent.rules.md`, `workflow.rules.md` |
| Shared command execution | Domain rules required by the command | `workflow.rules.md`, `validation.rules.md`, and command-specific files in `.ai/commands/` |
| Documentation governance or document authority task | `documentation.rules.md` when editing docs | `documentation-governance.rules.md` |
| Activation contract design or validation | None unless domain-specific | `activation.rules.md`, `validation.rules.md` |
| Semantic context loading or budget behavior | None unless domain-specific | `context-loading.rules.md`, `validation.rules.md` |
| Registry architecture or registry reference design | None unless domain-specific | `registry.rules.md`, `validation.rules.md` |
| Runtime observability, event taxonomy, or trace model design | None unless domain-specific | `observability.rules.md`, `validation.rules.md` |
| Sync, manifest safety, drift-stop, managed markers, or rollback preconditions | None unless domain-specific | `sync.rules.md`, `validation.rules.md` |

## Documentation Governance

- `.ai/` is the canonical runtime source of truth.
- `docs/specs/` contains detailed human-readable specifications. Specs are not always-load context.
- `docs/adr/` contains decision records, not runtime contracts.
- `docs/plan/` contains planning artifacts, not runtime contracts.
- `docs/reports/` contains audits, implementation reports, and cleanup reports, not runtime contracts.
- Runtime loaders and validators must not automatically consume audits, plans, ADRs, examples, philosophy, or human-review-only criteria.
- Durable runtime rules discovered in audits or plans become effective only after promotion into the smallest relevant `.ai/` source file or an active normative spec.
- Load `.ai/rules/operations/documentation-governance.rules.md` for document taxonomy, authority hierarchy, promotion, deprecation, supersession, or runtime consumption boundary tasks.

## Embedded Configuration Blocks

Markdown documents may include fenced `yaml` or `json` configuration blocks when structured metadata is useful for routing, validation, linking, or automation.

- Prefer fenced `yaml` blocks for project rules, agent routing, plan structure, and validation maps.
- Use fenced `json` blocks only for JSON Schema examples, strict external tool payloads, or API-oriented examples.
- Use JSONL only for append-only execution event logs when that data model is explicitly required.
- Configuration blocks support the surrounding rule or document body; they do not replace human-readable rules, role definitions, or decision rationale.
- Identify configuration blocks with HTML comment anchors:

````markdown
<!-- ai-config:start <name> <version> -->
```yaml
source_of_truth: .ai/rules/rules.md
```
<!-- ai-config:end -->
````

- `<name>` must use kebab-case, such as `agent-routing`, `plan-structure`, or `validation-map`.
- `<version>` must use a short version label, such as `v1`.
- Detailed agent routing belongs in `.ai/rules/operations/agent.rules.md`, not in this global file.

## Global File and Encoding Requirements

- Documents under `docs/` must be written in Korean.
- Documents under `.ai/` must be written in English.
- User-facing chat responses should be Korean unless the user explicitly requests another language.
- All files must be saved as UTF-8 without BOM.
- Do not mix languages within the same document unless the document explicitly requires technical identifiers or code.

## Symlink Policy

- Rule files and rule directories must be normal files and directories.
- Symbolic links are prohibited for rules files and rules directories.
- Cross-tool adapters must reference the shared rules by path rather than linking or duplicating rule bodies.

## Change Governance

- Global contract changes must be conservative and reviewed for cross-CLI impact.
- Domain rule changes must be checked against the relevant domain outputs, templates, skills, and validators.
- Operational rule changes must be checked for impact across all domains.
- README files are navigation and discovery aids; they must not duplicate rule bodies.
- New rule files should be added only when repeated maintenance need exists.
- When recurring improvements are discovered during real project use, update the smallest relevant shared rule file so future agents can apply the improvement without a repeated user instruction.
- Put project-wide behavior in this file, document behavior in `documentation.rules.md`, agent governance in `agent.rules.md`, workflow behavior in `workflow.rules.md`, and validation behavior in `validation.rules.md`.
- Keep tool-specific behavior in adapter files only.
- Record substantial rule changes in a Korean document under `docs/plan/` or `docs/reports/` when the change affects future project operation.

## Migration Map

This map is transitional. It exists to help agents find rules after the layered migration and should not become a permanent rule body index.

| Former rules area | New location |
|---|---|
| Language, content, document structure, template usage | `.ai/rules/domains/documentation.rules.md` |
| Development docs, build/runtime guidance, developer outputs | `.ai/rules/domains/development.rules.md` |
| HR evaluation inputs, outputs, and constraints | `.ai/rules/domains/hr.rules.md` |
| Roadmap, Task, Run Record, recovery flow | `.ai/rules/operations/workflow.rules.md` |
| Template, metadata, link, and execution validation | `.ai/rules/operations/validation.rules.md` |
| Agent roles, L1/L2 collaboration, context and escalation | `.ai/rules/operations/agent.rules.md` |
| Activation contract, active sets, semantic loader profile selection, and sync boundary | `.ai/rules/operations/activation.rules.md` |
| Semantic context loading, profile budgets, and extraction boundary | `.ai/rules/operations/context-loading.rules.md` |
| Registry architecture, relationship contracts, and future registry extraction boundary | `.ai/rules/operations/registry.rules.md` |
| Runtime observability, future event taxonomy, trace model, and provenance boundary | `.ai/rules/operations/observability.rules.md` |
| Sync/manifest safety, drift-stop policy, managed block markers, dry-run-first behavior, and rollback preconditions | `.ai/rules/operations/sync.rules.md` |
| Documentation taxonomy, authority, promotion, and runtime consumption boundary | `.ai/rules/operations/documentation-governance.rules.md` |
