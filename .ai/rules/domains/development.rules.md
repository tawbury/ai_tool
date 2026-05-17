# Development Rules

## Scope

Use this file for software development, development documentation, code-related work, build/run guidance, and development-domain outputs.

## Load When

Load this rule when the task involves code, architecture, specifications, PRDs, decisions, Docker, Makefile, build, run, deployment, or development validation.

## Responsibilities

- Define development-domain artifact locations.
- Define development documentation expectations.
- Define build, run, Docker, Makefile, and runtime guidance.
- Define development-specific references to skills, workflows, templates, and validators.

## Rules

### Development Artifacts

- Architecture documents belong under `docs/dev/archi/`.
- Specifications belong under `docs/dev/spec/`.
- Product requirements belong under `docs/dev/PRD/`.
- Decision records belong under `docs/dev/decision/`.

### Development Templates

- Use `.ai/templates/architecture_template.md` for architecture documents.
- Use `.ai/templates/spec_template.md` for technical specifications.
- Use `.ai/templates/prd_template.md` for product requirements.
- Use `.ai/templates/decision_template.md` for decision records.

### Development Execution

- Before running build or test commands, inspect available project entrypoints such as `docker-compose.yml`, `Makefile`, package scripts, or repository documentation.
- If Docker or container configuration exists, prefer the project-defined container workflow over assuming the local host environment.
- On Docker build or image conflicts, stop infinite retries, inspect the error, and provide a concrete resolution path.
- Keep development changes scoped to the requested behavior.

### Development References

- Developer agent: `.ai/agents/developer.agent.md`
- Developer skills: `.ai/skills/developer/`
- Development workflows:
  - `.ai/workflows/integrated_development.workflow.md`
  - `.ai/workflows/code_quality_validation.workflow.md`
  - `.ai/workflows/deploy_automation.workflow.md`

## Validation

- Use the relevant validator in `.ai/validators/` when a document type has one.
- Use `.ai/rules/operations/validation.rules.md` for validation behavior.
- For code changes, run the project-specific verification path when available.
- Report any verification that could not be run.

## Related Rules

- `.ai/rules/domains/documentation.rules.md`
- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/agent.rules.md`
