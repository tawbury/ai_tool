# Agents Directory

This directory stores shared AI agent definition files in `.agent.md` format.

Agent files are intended for multi-AI CLI usage. Tool-specific agent systems may wrap or reference these files, but shared agent behavior belongs here.

## Active Agents

| File | Agent Role | Primary Responsibility |
|---|---|---|
| `pm.agent.md` | Project Manager | Product strategy, roadmap planning, and stakeholder coordination. |
| `developer.agent.md` | Developer | Software design, implementation, testing, and technical review. |
| `contents-creator.agent.md` | Contents Creator | Visual, text, video, and interactive content creation. |
| `finance.agent.md` | Finance | Financial analysis, budgeting, forecasting, and risk assessment. |
| `hr.agent.md` | Human Resources | HR evaluation, role management, and agent orchestration. |
| `brand-logo-finder.agent.md` | Brand Logo Finder | Brand domain lookup and Brandfetch-based logo asset discovery. |

## Agent File Requirements

- Use YAML frontmatter.
- Include `domain_rules`, `operation_rules`, and `validators`.
- Keep detailed rules in `.ai/rules/`, not copied into agent files.
- Keep executable skills in `.ai/skills/`, not copied into agent files.
- Use `.ai/rules/operations/agent.rules.md` as the shared routing index.

## Tool-Specific Agent Assets

Tool-specific agent definitions from `.claude/agents/` should be migrated here when they are useful across AI CLI tools. Preserve functionality, but adapt frontmatter and body structure to the shared `.agent.md` format.
