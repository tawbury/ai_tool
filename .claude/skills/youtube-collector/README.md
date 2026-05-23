# YouTube Collector Skill

This is the Claude Code local copy of the YouTube Collector skill.

## Current Status

The shared, reusable version lives under:

` .ai/skills/_shared/ai_cli/youtube-collector/ `

Use the shared `.ai` version for canonical project behavior. Keep this `.claude` copy only for Claude Code compatibility.

## Contents

| Path | Purpose |
|---|---|
| `SKILL.md` | Claude Code skill entrypoint. |
| `README.md` | Compatibility README. |
| `scripts/` | YouTube collection helper scripts. |
| `references/` | Data schema and supporting references. |

## Boundary

Do not store API keys in this repository. Use user-level configuration for credentials and keep generated collection output out of committed source unless explicitly required.
