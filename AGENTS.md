# Agent Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

All AI CLI agents should:

1. Read `.ai/rules/rules.md` before editing files.
2. Follow the latest explicit user request first.
3. Keep tool-specific behavior in adapter files only.
4. Do not create symbolic links for rules files.
5. Add domain-specific rules only when there is a real maintenance need.

This file is the root adapter for Codex and other generic AI CLI agents.
