# Rules Directory

This directory contains the shared rule system for Codex CLI, Claude Code, Gemini CLI, and future AI CLI tools.

## Entry Point

`rules.md` is the global rule contract and the first shared rule file agents must read.

Root files such as `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are adapters. They point tools to this rule system but do not replace it.

## Structure

| Path | Purpose |
|---|---|
| `rules.md` | Global rule contract, priority, adapter policy, selective loading, and migration map. |
| `domains/` | Domain-specific rules for documentation, development, and HR work. |
| `operations/` | Runtime-facing operation rules for workflow, validation, agent behavior, activation, context loading, registry architecture, and documentation governance. |

## Loading Policy

1. Read `.ai/rules/rules.md` first.
2. Load only the domain rules relevant to the task.
3. Load only the operation rules relevant to the task.

Do not load every rule file by default.

## Maintenance Boundary

README files are navigation aids. Durable behavior belongs in the smallest relevant rule file.

Rules files and rules directories must be normal files and directories. Symbolic links are prohibited.
