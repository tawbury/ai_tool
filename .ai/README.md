# AI Runtime Directory

This directory contains the shared runtime assets for AI CLI agents.

## Source of Truth

- Global rule entrypoint: `.ai/rules/rules.md`
- Runtime rules: `.ai/rules/`
- Root adapters: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`

Root adapters are discovery files only. Shared rule bodies live under `.ai/rules/`.

## Contents

| Path | Purpose |
|---|---|
| `agents/` | Shared agent definitions in `.agent.md` format. |
| `commands/` | Reusable command definitions for AI CLI agents. |
| `rules/` | Global, domain, and operation rules. |
| `skills/` | Reusable skill definitions grouped by domain. |
| `templates/` | Document templates and activation templates. |
| `validators/` | Validator documents and validator index. |
| `workflows/` | Workflow definitions and workflow reference files. |

## Runtime Commands

The `aios` module provides read-only inspection, inventory, validation, activation, and semantic context extraction commands.

```powershell
python -m aios inspect
python -m aios inventory
python -m aios validate
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios load-context .ai/rules/rules.md
```

## Boundary

This directory is runtime-facing, but the current system remains read-only. It does not perform sync, manifest generation, adapter generation, orchestration, worker execution, workflow execution, or auto-fix.
