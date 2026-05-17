# Skills Directory

This directory stores reusable AI skills.

Skills are grouped by agent domain. Cross-agent skills live under `_shared/`.

## Directory Structure

| Directory | Purpose |
|---|---|
| `_shared/` | Skills and frameworks used by multiple agents. |
| `_shared/ai_cli/` | Shared AI CLI tooling skills adapted from tool-specific assets. |
| `pm/` | Product and project management skills. |
| `developer/` | Software development and technical review skills. |
| `contents-creator/` | Visual, text, video, and interactive content skills. |
| `finance/` | Financial analysis and management skills. |
| `hr/` | HR evaluation, role management, and organization skills. |

## Skill File Rules

- Use `.skill.md` for shared skill entry files.
- Keep skill entry files concise.
- Put long examples and references in `references/`.
- Put deterministic procedures in `scripts/`.
- Put reusable output resources in `assets/`.
- Do not copy global rule bodies into skill files.

## Shared AI CLI Skills

The `_shared/ai_cli/` folder contains functionality migrated from `.claude/skills/` when the skill can be useful across AI CLI tools.

Tool-specific behavior is preserved as references, scripts, or clearly labeled target behavior, while the canonical shared skill entry lives under `.ai/skills/`.

## Loading Guidance

- Load only the skill required by the current task.
- Load references only when the skill entry file says they are needed.
- Prefer scripts for deterministic, repeated operations.
- Use `.ai/skills/_shared/skill_index.md` for broad skill discovery.
