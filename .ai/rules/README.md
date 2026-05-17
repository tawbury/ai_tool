# Rules Directory

This directory contains the layered rule system for Codex CLI, Claude Code, Gemini CLI, and future AI CLI tools.

## Source of Truth

`rules.md` is the global rule contract and the first rule file agents must read.

Root files such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are adapters. They help tools discover the shared rule entrypoint, but they are not rule sources.

## Layers

```text
.ai/rules/
  rules.md
  domains/
  operations/
```

- `rules.md`: global contract, priority, adapter policy, symlink policy, and selective loading rules.
- `domains/`: business or work-domain rules.
- `operations/`: execution, validation, workflow, and agent governance rules.

## Selective Loading

Load the minimum sufficient rule set for the current task.

1. Always read `.ai/rules/rules.md` first.
2. Load only relevant domain rules from `.ai/rules/domains/`.
3. Load only relevant operational rules from `.ai/rules/operations/`.

## Current Rule Files

Domain rules:

- `domains/documentation.rules.md`
- `domains/development.rules.md`
- `domains/hr.rules.md`

Operational rules:

- `operations/workflow.rules.md`
- `operations/validation.rules.md`
- `operations/agent.rules.md`

## Adding New Rules

Add a new domain rule only when there is repeated domain-specific maintenance need, such as durable outputs, validation criteria, or approval flow.

Add a new operational rule only when the behavior applies across multiple domains.

Do not create placeholder rule files for future domains before they are needed.

## Adapter Policy

Adapters must stay thin. They should point agents to `.ai/rules/rules.md` and should not duplicate shared rule bodies.

## Symlink Policy

Rules files and rules directories must be normal files and directories. Symbolic links are prohibited.

## Encoding Policy

All rule files must be saved as UTF-8 without BOM.
