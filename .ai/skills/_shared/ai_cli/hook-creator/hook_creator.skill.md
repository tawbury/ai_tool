---
name: hook-creator
description: Create and configure AI CLI lifecycle hooks. Use when the user wants automatic formatting, logging, notifications, file protection, custom permissions, or pre/post tool execution behavior. Preserves Claude Code hook support while keeping the reusable skill under .ai.
---

# Hook Creator

Create lifecycle hooks that execute shell commands at specific AI CLI events.

## Workflow

1. Identify the automation goal.
2. Identify the target AI CLI and whether it supports hooks.
3. Select the appropriate event and matcher.
4. Design a shell command that safely processes hook input.
5. Choose the correct storage location for the target tool.
6. Test the hook with a narrow case before broadening the matcher.

## Claude Code Hook Support

Claude Code hook behavior from the original tool-specific skill is preserved in this folder.

- Event reference: `references/hook-events.md`
- Example configurations: `references/examples.md`

Use these references when the target is Claude Code or when the user asks about events such as `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, or `SessionStart`.

## Common Configuration Shape

```json
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<ToolPattern>",
        "hooks": [
          {
            "type": "command",
            "command": "<shell-command>"
          }
        ]
      }
    ]
  }
}
```

## Safety Rules

- Keep matchers narrow until the hook is tested.
- Avoid destructive commands unless explicitly requested.
- Prefer project-local hooks for repository behavior and user-local hooks for personal preferences.
- Document tool-specific storage paths in the generated output.
