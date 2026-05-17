# HR Rules

## Scope

Use this file for HR evaluation, role definition, HR reports, and HR-domain workflow decisions.

## Load When

Load this rule when the user requests a new role, position evaluation, HR report, level check, HR onboarding, or HR-domain document.

## Responsibilities

- Define HR-domain input and output locations.
- Define HR evaluation constraints.
- Define HR skill and validator references.
- Define HR report expectations.

## Rules

### HR Artifacts

- Role definition input: `docs/tasks/task_<role>_<dept>.md`.
- Evaluation output: `docs/reports/report_<role>_<dept>_<YYYYMMDD>.md`.
- HR task and report documents must be written in Korean.

### HR Evaluation Constraints

- Meta Isolation: never use metadata such as Expected Level to bias the final evaluation result.
- Pending Protocol: if criteria are insufficient, set status to `PENDING` and provide detailed improvement feedback.
- Reports should be structured and deterministic enough for other agents to consume.

### HR References

- HR agent: `.ai/agents/hr.agent.md`
- HR workflow: `.ai/workflows/hr_evaluation.workflow.md`
- HR skills:
  - `.ai/skills/hr/hr_onboarding.skill.md`
  - `.ai/skills/hr/hr_level_check.skill.md`
  - `.ai/skills/hr/hr_report_emit.skill.md`
- HR validators:
  - `.ai/validators/hr_skill_validator.md`
  - `.ai/validators/report_validator.md`
  - `.ai/validators/task_validator.md`

## Validation

- Check task structure with `.ai/validators/task_validator.md` when applicable.
- Check report structure with `.ai/validators/report_validator.md` when applicable.
- Use `.ai/rules/operations/validation.rules.md` for common validation behavior.
- Ensure HR-specific decisions do not duplicate workflow or validation rule bodies.

## Related Rules

- `.ai/rules/domains/documentation.rules.md`
- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/agent.rules.md`
