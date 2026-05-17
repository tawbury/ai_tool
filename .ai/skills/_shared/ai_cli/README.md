# Shared AI CLI Skills

This directory contains shared skills adapted from tool-specific AI CLI assets.

The skills in this folder are usable by multiple AI CLI tools. When a skill targets a specific tool feature, such as Claude Code hooks or slash commands, the skill preserves that behavior while keeping the canonical reusable definition under `.ai/`.

## Skills

| Skill | Entry File | Purpose |
|---|---|---|
| Hook Creator | `hook-creator/hook_creator.skill.md` | Create lifecycle hook configurations for AI CLI tools, with Claude Code hook support preserved. |
| Skill Creator | `skill-creator/skill_creator.skill.md` | Create or update reusable AI skills with bundled references, scripts, and assets. |
| Slash Command Creator | `slash-command-creator/slash_command_creator.skill.md` | Create tool-specific slash commands and shared command wrappers. |
| Subagent Creator | `subagent-creator/subagent_creator.skill.md` | Create specialized AI subagents or agent definition files. |
| YouTube Collector | `youtube-collector/youtube_collector.skill.md` | Register YouTube channels, collect video metadata/transcripts, and prepare summary data. |

## Resource Policy

- Keep scripts, references, and assets inside each skill folder.
- Keep the `.skill.md` entry file concise and use progressive disclosure.
- Preserve tool-specific implementation details in references or scripts when needed.
- Prefer shared `.ai/commands/` and `.ai/agents/` outputs when the requested artifact should work across AI CLI tools.
