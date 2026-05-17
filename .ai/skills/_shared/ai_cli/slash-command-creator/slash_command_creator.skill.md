---
name: slash-command-creator
description: Create slash commands or shared command wrappers for AI CLI tools. Use when the user asks to create, update, or standardize command prompts, including Claude Code slash commands and shared .ai/commands definitions.
---

# Slash Command Creator

Create command prompts for AI CLI tools while preserving shared command behavior under `.ai/commands/`.

## Decision Rule

- For multi-CLI behavior, create or update `.ai/commands/*.command.md`.
- For a single tool convenience wrapper, create the tool-specific command file and make it reference the canonical `.ai/commands/` file.
- Do not duplicate shared workflow bodies in tool-specific command folders.

## Claude Code Slash Command Support

Claude Code slash command references and initialization scripts are preserved in this folder.

- Frontmatter reference: `references/frontmatter.md`
- Examples: `references/examples.md`
- Initializer script: `scripts/init_command.py`

Use these resources when the user specifically targets Claude Code slash commands.

## Shared Command Requirements

Shared command files under `.ai/commands/` must define:

- purpose
- inputs
- required rule loading
- workflow
- validation requirements
- output/reporting requirements

## Workflow

1. Identify whether the command is shared or tool-specific.
2. For shared commands, create `.ai/commands/<name>.command.md`.
3. For tool-specific wrappers, keep the wrapper minimal and point to the shared command file.
4. Validate command references and example invocation.
5. Update `.ai/commands/README.md` when adding a shared command.
