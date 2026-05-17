# Claude Code Instructions Template

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

Before making changes:

1. Read `.ai/rules/rules.md`.
2. Follow the latest explicit user request first.
3. Apply Claude Code runtime instructions when they are stricter than project rules.
4. Treat `CLAUDE.md` as an adapter, not as the rule source.

Do not create symbolic links for rules files. Rules adapters must be normal files or directories.

## Supported AI CLI Tools

- Codex
- Claude Code
- Gemini CLI

## Source Paths

| Path | Purpose |
|---|---|
| `.ai/rules/rules.md` | Shared rules source |
| `.ai/agents/` | Agent definitions |
| `.ai/skills/` | Skill definitions |
| `.ai/validators/` | Validation definitions |
| `.ai/workflows/` | Workflow definitions |
