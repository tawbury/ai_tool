# Gemini CLI Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

Before making changes:

1. Read `.ai/rules/rules.md`.
2. Follow the latest explicit user request first.
3. Apply Gemini CLI runtime instructions when they are stricter than project rules.
4. Treat this file as an adapter, not as the rule source.

Do not create symbolic links for rules files. Rules adapters must be normal files or directories.
