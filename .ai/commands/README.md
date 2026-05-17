# Shared AI Commands

## Purpose

This directory contains reusable command definitions for all supported AI CLI tools.

Shared commands are canonical project assets. Tool-specific command systems may reference these files, but they must not duplicate or replace the command behavior.

## Command Loading

When a user asks an AI CLI to run a shared command:

1. Read `.ai/rules/rules.md`.
2. Read this README.
3. Read the requested `.ai/commands/*.command.md` file.
4. Load only the rule files required by that command.
5. Execute the command workflow exactly as defined.

## Command File Rules

- Command files must use the suffix `.command.md`.
- Command files must be written in English because they live under `.ai/`.
- Command files must define purpose, inputs, workflow, validation, and reporting requirements.
- Command files must not contain tool-specific syntax as the canonical behavior.
- Tool-specific adapters may provide convenience wrappers that point back to these command files.

## Available Commands

| Command | File | Purpose |
|---|---|---|
| `implement-design` | `.ai/commands/implement-design.command.md` | Execute implementation from an existing design document, validate design alignment, remediate gaps until the achievement rate is above the threshold, then write a report. |

## Invocation Guidance

Use the command name in natural language if the active AI CLI does not support shared command invocation directly.

Examples:

- `Run shared command implement-design for docs/plan/example_design.md`
- `공통 명령 implement-design를 docs/plan/example_design.md 기준으로 실행해줘`

If a tool-specific command wrapper exists, that wrapper must read and follow the canonical command file in this directory.
