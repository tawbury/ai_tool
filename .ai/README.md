# AI System Directory

This directory is the source area for shared AI system rules, agents, skills, workflows, validators, and templates.

## Source of Truth

- Shared rules: `.ai/rules/rules.md`
- Codex adapter: `AGENTS.md`
- Claude Code adapter: `CLAUDE.md`
- Gemini CLI adapter: `GEMINI.md`

## Supported AI CLI Tools

- Codex
- Claude Code
- Gemini CLI

Rules files and rules directories must be normal files and directories. Do not use symbolic links.

## Structure

| Path | Purpose |
|---|---|
| `agents/` | Agent role definitions |
| `rules/` | Shared rules source |
| `skills/` | Reusable skill definitions |
| `templates/` | Document and workflow templates |
| `validators/` | Validation rules and validator documents |
| `workflows/` | Operational workflow definitions |
| `install/` | Installation mapping for currently supported CLI tools |
| `export/` | Export helpers for chat or session contexts |
