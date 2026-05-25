# Validation Rules

## Scope

Use this file for validation behavior, validator selection, validation failure handling, and verification reporting.

## Load When

Load this rule when a task creates, edits, reviews, or verifies code, rules, templates, documents, workflows, skills, or reports.

## Responsibilities

- Define common validation behavior.
- Define how validators are discovered and referenced.
- Define validation failure handling.
- Keep validation behavior domain-independent.

## Rules

### Validator References

- Use `.ai/validators/validator_index.md` to discover available validators when needed.
- Use document-specific validators when available:
  - `.ai/validators/task_validator.md`
  - `.ai/validators/report_validator.md`
  - `.ai/validators/architecture_validator.md`
  - `.ai/validators/spec_validator.md`
  - `.ai/validators/prd_validator.md`
  - `.ai/validators/decision_validator.md`
  - `.ai/validators/meta_validator.md`
  - `.ai/validators/structure_validator.md`
- Use skill validators for agent/skill-related work when applicable.

### Validation Process

1. Check structure against the relevant template or expected shape.
2. Check metadata completeness and format when metadata exists.
3. Check content language against folder policy.
4. Check internal links and references.
5. Run executable validation scripts if the project provides them.
6. Report validation results and any validation that could not be run.

### Runtime JSON Targets

`aios validate` may include runtime JSON/YAML targets such as activation files, sync manifests, replay manifests, provider capability declarations, and provider execution traces.

Replay manifest validation is static-only by default. Opt-in replay comparison is allowed only through fixture-backed validation, such as `--replay-compare fixture`, and must preserve no-flag static validation behavior.

Replay validation and comparison must not execute providers, execute adapters, generate content, update snapshots, write files, or authorize sync apply/mutation. Sync-specific schema details, replay comparison output details, and replay safety boundaries belong in `.ai/rules/operations/sync.rules.md`.

Provider capability validation is supported for:

- `python -m aios validate <provider-capability.json>`
- `python -m aios validate <provider-capability.json> --json`
- `python -m aios validate <provider-capability.json> --json --envelope-v2`

Provider capability validation uses target kind `provider-capability` and schema `aios.provider_capability.v0`.

Provider capability validation is static-only. It validates declaration shape and safety flags only.

Provider capability JSON/envelope output must preserve non-execution metadata where applicable:

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

Provider capability validation must not execute providers, launch sandboxes, discover or register providers, execute adapters, generate content, update snapshots, write files, or authorize sync apply/mutation.

Provider execution trace validation is supported for:

- `python -m aios validate <provider-trace.json>`
- `python -m aios validate <provider-trace.json> --json`
- `python -m aios validate <provider-trace.json> --json --envelope-v2`

Provider execution trace validation uses target kind `provider-execution-trace` and schema `aios.provider_execution_trace.v0`.

Provider execution trace validation is static-only. It validates parsed JSON structure and safety evidence only.

Provider execution trace JSON/envelope output must preserve non-execution metadata where applicable:

- `provider_execution: false`
- `sandbox_execution: false`
- `mutation_performed: false`

Provider execution trace validation must preserve `provider_mode` when it is available.

Provider execution trace validation must not execute providers, launch sandboxes, dynamically load providers, discover or register providers, execute adapters, generate content, update snapshots, execute replay, write files, or authorize sync apply/mutation.

### Failure Handling

- On template validation failure, identify the missing or invalid structure.
- On language policy violation, correct it when safe; otherwise report the violation.
- On metadata failure, list missing or invalid fields.
- On executable validation failure, stop blind retries and inspect the error.

## Validation

- This file is validated by applying it to changed rule, document, template, or workflow files.
- Validation behavior must remain domain-independent.

## Related Rules

- `.ai/rules/domains/documentation.rules.md`
- `.ai/rules/domains/development.rules.md`
- `.ai/rules/domains/hr.rules.md`
- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/agent.rules.md`
