---
description: "Runtime registry architecture rules"
globs: ".ai/rules/operations/*.md,.ai/templates/*.yaml,.ai/templates/*.yml"
alwaysApply: false
---

# Registry Rules
*Last Updated: 2026-05-23*
*Version: 1.0.0*

## Purpose

Registry architecture defines relationship contracts among discovered `.ai` runtime assets.

It connects inventory, activation, validation, and semantic loading without executing workflows, dispatching workers, generating adapters, or syncing files.

## Layer Boundaries

- Inventory is the discovery layer. It finds agents, skills, workflows, validators, rules, and commands.
- Registry is the relationship layer. It describes how discovered assets relate to agents, validators, workflows, rules, and loader profiles.
- Activation is the active selection layer. It selects active agents, skills, workflows, validators, and loader profiles.
- Validate is the integrity checker. It may check registry schema, references, duplicates, and loader profile names.
- Load-context is the context extraction layer. It applies semantic loader profiles when explicitly invoked.

## Current Policy

The embedded `agent-routing` YAML block in `.ai/rules/operations/agent.rules.md` remains the short-term routing index.

Do not extract it into standalone registry files until the extraction criteria are met.

## Future Extraction Criteria

Standalone registry files may be introduced later under `.ai/registry/` only when:

- more than one runtime command needs the same machine-readable relationship table;
- drift between embedded YAML, agent frontmatter, validator index, workflow files, or activation files becomes a real maintenance risk;
- `aios validate` can check registry reference integrity read-only;
- the schema and source-of-truth precedence are documented before implementation.

Candidate files are:

- `.ai/registry/agents.yaml`
- `.ai/registry/validators.yaml`
- `.ai/registry/workflows.yaml`

## Minimum Future Schema Expectations

Future agent registry entries should include:

- `id`
- `file`
- `default_domain_rules`
- `default_operation_rules`
- `validators`
- optional `default_loader`, `primary_use_cases`, and `tools`

Future validator registry entries should include:

- `id`
- `file`
- `target_kinds`
- `executable`
- optional `dependencies`, `default_loader`, and `severity_policy`

Future workflow registry entries should include:

- `id`
- `file`
- `validators`
- optional `agents`, `default_loader`, and `executable`

Registry references should resolve through inventory names or canonical `.ai` paths.

Semantic loader profile references must match supported loader profiles.

## Read-only Boundary

Registry rules are read-only runtime contracts.

Registry consumers may inspect files, resolve references, and report integrity issues. They must not modify `.ai` files, generate registry files, rewrite embedded YAML, or auto-fix references.

## Non-goals

Registry architecture does not implement:

- sync
- manifest generation
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser implementation
- registry auto-fix
- activation file generation

## Validation

When registry files exist in the future, validation should check:

- schema version validity
- required fields
- duplicate ids
- duplicate file references
- inventory reference resolution
- semantic loader profile validity
- target kind validity

Until standalone registry files exist, validate the current registry-like sources through existing inventory, activation, agent, workflow, and validator index checks.

## Related Rules

- `.ai/rules/operations/agent.rules.md`
- `.ai/rules/operations/activation.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/workflow.rules.md`
