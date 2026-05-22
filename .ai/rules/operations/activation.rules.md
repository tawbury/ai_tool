---
description: "Runtime activation contract rules"
globs: ".ai/**/*.yaml,.ai/**/*.yml"
alwaysApply: false
---

# Activation Rules
*Last Updated: 2026-05-23*
*Version: 1.0.0*

## Purpose

Activation files declare the runtime selection contract for a project.

They identify which agents, skills, workflows, validators, and semantic loader profile should be considered active for a runtime context.

## Supported Schema

The minimal supported activation schema is:

```yaml
schema_version: aios.activation.v0
active_set:
  agents: []
  skills: []
  workflows: []
  validators: []
profiles:
  default_loader: minimal-worker
```

- `schema_version` must identify the activation contract version.
- `active_set.agents` references agent inventory names or canonical paths.
- `active_set.skills` references skill inventory names or canonical paths.
- `active_set.workflows` references workflow inventory names or canonical paths.
- `active_set.validators` references validator inventory names or canonical paths.
- `profiles.default_loader` must reference a supported semantic loader profile.

## Inventory Relationship

Activation references must resolve against the `.ai` inventory.

- Agents resolve against `.ai/agents/*.agent.md`.
- Skills resolve against `.ai/skills/**/*.skill.md`.
- Workflows resolve against `.ai/workflows/*.workflow.md`.
- Validators resolve against `.ai/validators/**/*.md`.

Unknown activation references are validation errors.

## Semantic Loader Relationship

`profiles.default_loader` selects the default semantic loading profile for future runtime context selection.

Activation does not load context by itself. The semantic loader remains responsible for extracting and filtering context.

## Sync Boundary

Activation is not sync selection.

Activation must not:

- copy files
- write manifests
- generate adapters
- insert managed blocks
- perform drift detection
- dispatch workers
- execute workflows

Future sync may use activation as an input, but sync behavior must be defined separately.

## Read-only Boundary

`aios activation` is read-only.

It may validate activation schema fields, inventory references, and semantic loader profile names. It must not modify activation files or referenced `.ai` files.

## Deferred Items

The following are intentionally deferred:

- activation file auto-generation
- activation auto-fix
- full YAML parsing
- activation-driven context loading
- sync target selection
- adapter generation
- orchestration
- worker execution
