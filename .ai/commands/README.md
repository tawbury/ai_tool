# Shared AI Commands

This directory contains reusable command definitions for supported AI CLI tools.

## Current Commands

| Command | File | Purpose |
|---|---|---|
| `implement-design` | `implement-design.command.md` | Implement an existing design document, validate design alignment, remediate gaps, and write an implementation report. |

## Loading Order

When a user asks to run a shared command:

1. Read `.ai/rules/rules.md`.
2. Read this README.
3. Read the requested `.ai/commands/*.command.md` file.
4. Load only the rules required by that command.
5. Follow the command workflow exactly.

## Rules

- Command files use the `.command.md` suffix.
- Shared command files are written in English because they live under `.ai/`.
- Tool-specific wrappers may point to these files, but canonical command behavior stays here.
