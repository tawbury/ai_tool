# Skills Directory

This directory contains reusable AI skill definitions.

## Structure

| Path | Purpose |
|---|---|
| `_shared/` | Cross-agent skills and shared frameworks. |
| `_shared/ai_cli/` | Shared AI CLI tooling skills adapted from tool-specific assets. |
| `_shared/contents_creator_frameworks/` | Shared frameworks for content creation strategy and quality. |
| `developer/` | Software development and technical review skills. |
| `pm/` | Product and project management skills. |
| `hr/` | HR evaluation and organization skills. |
| `finance/` | Finance, forecasting, portfolio, and risk skills. |
| `contents-creator/` | Content creation skills grouped by medium and business use case. |

## File Rules

- Shared skill entries use the `.skill.md` suffix.
- Keep skill files focused on reusable behavior.
- Put deterministic procedures in `scripts/` when a skill owns executable helpers.
- Put long references in `references/` when needed.
- Do not copy global rule bodies into skill files.

## Loading

Load only the skill required for the task. Use `_shared/skill_index.md` for broad discovery.
