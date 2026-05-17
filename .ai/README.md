# AI System Directory

This directory contains shared AI system commands, rules, agents, skills, workflows, validators, and templates.

## Source of Truth

- Global rule entrypoint: `.ai/rules/rules.md`
- Codex adapter: `AGENTS.md`
- Claude Code adapter: `CLAUDE.md`
- Gemini CLI adapter: `GEMINI.md`

Root adapters are discovery files only. They must not duplicate shared rule bodies.

## Rule Layers

| Path | Purpose |
|---|---|
| `commands/` | Reusable multi-CLI command definitions |
| `rules/rules.md` | Global rule contract |
| `rules/domains/` | Business or work-domain rules |
| `rules/operations/` | Execution, validation, workflow, and agent governance rules |

## Supported AI CLI Tools

- Codex CLI
- Claude Code
- Gemini CLI

## Structure

| Path | Purpose |
|---|---|
| `agents/` | Agent role definitions |
| `commands/` | Shared command definitions for all AI CLI tools |
| `rules/` | Layered shared rules |
| `skills/` | Reusable skill definitions |
| `templates/` | Document and workflow templates |
| `validators/` | Validation rules and validator documents |
| `workflows/` | Operational workflow definitions |

## Symlink Policy

Rules files and rules directories must be normal files and directories. Do not use symbolic links.
