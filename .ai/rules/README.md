# Rules Directory

This directory contains the shared rules for the project.

## Source of Truth

`rules.md` is the single source of truth for all shared AI CLI behavior.

Root files such as `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` are adapters. Tool-specific files such as `.cursor/rules/rules.md`, `.windsurf/rules/rules.md`, and `.github/copilot-instructions.md` are also adapters.

## Extension Policy

Do not create extra rule files until there is a real maintenance need.

If a rules area becomes too large, split it into a domain-specific file at that time and reference it from `rules.md`.

## Symlink Policy

Rules files and rules directories must be normal files and directories. Symbolic links are prohibited.
