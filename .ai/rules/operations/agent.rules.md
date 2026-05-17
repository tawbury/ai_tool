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

### Agent Routing Configuration

The following embedded configuration block is the common routing index for agent selection and default context loading. It does not replace the detailed role and skill definitions in `.ai/agents/*.agent.md`.

<!-- ai-config:start agent-routing v1 -->
```yaml
source_of_truth: .ai/rules/rules.md
agents:
  - agent: developer
    file: .ai/agents/developer.agent.md
    default_domain_rules:
      - .ai/rules/domains/development.rules.md
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/developer_skill_validator.md
    primary_use_cases:
      - software architecture
      - implementation
      - code review
  - agent: hr
    file: .ai/agents/hr.agent.md
    default_domain_rules:
      - .ai/rules/domains/hr.rules.md
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/hr_skill_validator.md
    primary_use_cases:
      - HR evaluation
      - role management
      - performance review
  - agent: pm
    file: .ai/agents/pm.agent.md
    default_domain_rules:
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/pm_skill_validator.md
    primary_use_cases:
      - product strategy
      - roadmap planning
      - stakeholder coordination
  - agent: contents-creator
    file: .ai/agents/contents-creator.agent.md
    default_domain_rules:
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/contents_creator_skill_validator.md
    primary_use_cases:
      - content creation
      - visual production
      - content strategy
  - agent: finance
    file: .ai/agents/finance.agent.md
    default_domain_rules:
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/finance_skill_validator.md
    primary_use_cases:
      - financial analysis
      - budget management
      - financial risk assessment
```
<!-- ai-config:end -->

### L1/L2 Collaboration

- L1 agents focus on task execution, document creation, template compliance, and basic quality checks.
- L2 agents focus on planning, review, approval, strategic decisions, and rationale.
- Critical documents and critical decisions require L2 review when the workflow calls for L1/L2 separation.
- L1 may escalate complex issues to L2 with justification.

### Agent Boundaries

- Agents operate within their defined scope and relevant domain rules.
- Agent-specific domain expertise belongs in `.ai/agents/` and `.ai/skills/`.
- This file defines shared governance only.
- Agent frontmatter declares loading metadata through `domain_rules`, `operation_rules`, and `validators`.
- Agent frontmatter must not copy rule bodies or skill bodies.
- If an agent has no dedicated domain rule yet, use the existing relevant shared domain rule and create a new domain rule only when repeated maintenance need exists.

### Context and Efficiency

- Load only relevant templates, skills, domain rules, and operational rules per task.
- Execute independent tasks in parallel when safe and supported by the active AI CLI.
- Group similar operations when doing so reduces repeated context and tool overhead.

### Continuous Improvement

- When real project usage reveals a recurring agent routing, validation, or context-loading improvement, update this shared rule or the relevant agent frontmatter so future executions inherit it automatically.
- Do not require repeated user instructions for recurring behavior that can be safely encoded as shared governance.
- Keep improvements at the smallest durable layer: global behavior in `rules.md`, agent governance here, document behavior in `documentation.rules.md`, and individual role details in `.ai/agents/*.agent.md`.

## Validation

- Check that agent work loads only relevant rule files.
- Check that L1/L2 review expectations are followed when applicable.
- Check that agent-specific behavior is not copied into the global rule contract.
- Check that the `agent-routing` configuration block has matching anchors and includes `agent`, `file`, `default_domain_rules`, `default_operation_rules`, `validators`, and `primary_use_cases` for each listed agent.
- Check that each referenced agent file, rule file, and validator file exists, unless the reference is explicitly marked as a future candidate.
- Check that each `.ai/agents/*.agent.md` frontmatter is valid YAML and declares `domain_rules`, `operation_rules`, and `validators`.

## Related Rules

- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/domains/development.rules.md`
- `.ai/rules/domains/hr.rules.md`
