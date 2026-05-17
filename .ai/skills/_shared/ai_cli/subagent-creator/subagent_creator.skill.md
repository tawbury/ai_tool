---
name: subagent-creator
description: Create specialized AI subagents or agent definition files. Use when the user asks for a new agent, subagent, role-specific assistant, delegation worker, reviewer, or task-specific AI workflow.
---

# Subagent Creator

Create specialized AI agent definitions for shared `.ai/agents/` usage or tool-specific subagent systems.

## Decision Rule

- For multi-CLI project agents, create `.ai/agents/<name>.agent.md`.
- For a single tool runtime subagent, create the tool-specific file only when requested or required.
- Keep shared role, scope, routing, and validation metadata in `.ai/agents/`.

## Shared `.ai` Agent Format

Use YAML frontmatter:

```yaml
---
name: Agent Name
type: agent
version: 1.0.0
updated: YYYY-MM-DD
role: Short role
level: L1
tools: []
domain_rules: []
operation_rules:
  - .ai/rules/operations/agent.rules.md
  - .ai/rules/operations/workflow.rules.md
  - .ai/rules/operations/validation.rules.md
validators: []
---
```

The body should define identity, scope, responsibilities, workflow, output format, and cross-agent collaboration.

## Claude Code Subagent Support

Claude Code subagent assets and references are preserved in this folder.

- Template: `assets/subagent-template.md`
- Available tools reference: `references/available-tools.md`
- Examples: `references/examples.md`

Use these resources when the requested target is Claude Code.

## Workflow

1. Gather purpose, trigger conditions, required capabilities, and scope.
2. Choose shared `.ai/agents/` or tool-specific target.
3. Write concise frontmatter metadata.
4. Define the system prompt or agent body.
5. Add routing and validator references where applicable.
6. Validate that the agent does not duplicate global rule bodies.
