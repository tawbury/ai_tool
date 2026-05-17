# Agent Rules

## Scope

Use this file for common agent roles, collaboration, escalation, context management, and cross-agent governance.

## Load When

Load this rule when the task involves agent assignment, L1/L2 review, escalation, cross-agent coordination, or context/performance management.

## Responsibilities

- Define available agent roles at a high level.
- Define L1/L2 collaboration expectations.
- Define escalation and review behavior.
- Define context and execution efficiency principles.

## Rules

### Available Agents

- `hr`: HR evaluation and management.
- `developer`: technical development and implementation.
- `contents-creator`: content creation and management.
- `finance`: financial analysis and management.
- `pm`: project management and coordination.

Agent context files:

- `.ai/agents/hr.agent.md`
- `.ai/agents/developer.agent.md`
- `.ai/agents/contents-creator.agent.md`
- `.ai/agents/finance.agent.md`
- `.ai/agents/pm.agent.md`

### L1/L2 Collaboration

- L1 agents focus on task execution, document creation, template compliance, and basic quality checks.
- L2 agents focus on planning, review, approval, strategic decisions, and rationale.
- Critical documents and critical decisions require L2 review when the workflow calls for L1/L2 separation.
- L1 may escalate complex issues to L2 with justification.

### Agent Boundaries

- Agents operate within their defined scope and relevant domain rules.
- Agent-specific domain expertise belongs in `.ai/agents/` and `.ai/skills/`.
- This file defines shared governance only.

### Context and Efficiency

- Load only relevant templates, skills, domain rules, and operational rules per task.
- Execute independent tasks in parallel when safe and supported by the active AI CLI.
- Group similar operations when doing so reduces repeated context and tool overhead.

## Validation

- Check that agent work loads only relevant rule files.
- Check that L1/L2 review expectations are followed when applicable.
- Check that agent-specific behavior is not copied into the global rule contract.

## Related Rules

- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/domains/development.rules.md`
- `.ai/rules/domains/hr.rules.md`
