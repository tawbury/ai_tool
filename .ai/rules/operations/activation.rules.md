---
description: "Runtime activation contract rules"
globs: ".ai/**/*.yaml,.ai/**/*.yml"
alwaysApply: false
---

# Activation Rules
*Last Updated: 2026-05-23*
*Version: 1.1.0*

## Purpose

Activation files declare the runtime selection contract for a project.

They identify which agents, skills, workflows, validators, and semantic loader profile should be considered active for a runtime context.

## Supported Schema

Supported activation schema versions are:

- `aios.activation.v0`
- `aios.activation.v1`

The minimal supported v0 activation schema is:

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

The minimal supported v1 activation schema is:

```yaml
schema_version: aios.activation.v1
runtime_mode: validation
active_set:
  agents: []
  skills: []
  workflows: []
  validators: []
  rules: []
profiles:
  default_loader: minimal-worker
  agent_loader_overrides: {}
  workflow_loader_overrides: {}
rule_sets:
  default:
    domain_rules: []
    operation_rules: []
```

- `schema_version` must identify the activation contract version.
- `active_set.agents` references agent inventory names or canonical paths.
- `active_set.skills` references skill inventory names or canonical paths.
- `active_set.workflows` references workflow inventory names or canonical paths.
- `active_set.validators` references validator inventory names or canonical paths.
- `active_set.rules` is supported in v1 and references rule inventory names or canonical `.ai/rules/**/*.md` paths.
- `profiles.default_loader` must reference a supported semantic loader profile.
- `profiles.agent_loader_overrides` is supported in v1 and maps agent references to supported semantic loader profiles.
- `profiles.workflow_loader_overrides` is supported in v1 and maps workflow references to supported semantic loader profiles.
- `runtime_mode` is supported in v1 and must be one of `validation`, `context`, `review`, or `planning`.
- `rule_sets` is optional in v1 and groups domain and operation rule references for context selection.

## Version Compatibility

Activation v0 remains valid and must continue to validate without automatic migration.

Activation v1 adds runtime intent, rule references, loader overrides, and optional rule sets. Runtime tools must not rewrite v0 files into v1 files automatically.

## Inventory Relationship

Activation references must resolve against the `.ai` inventory.

- Agents resolve against `.ai/agents/*.agent.md`.
- Skills resolve against `.ai/skills/**/*.skill.md`.
- Workflows resolve against `.ai/workflows/*.workflow.md`.
- Validators resolve against `.ai/validators/**/*.md`.
- Rules resolve against `.ai/rules/**/*.md` when v1 `active_set.rules` or `rule_sets` references are present.

Unknown activation references are validation errors.

## Semantic Loader Relationship

`profiles.default_loader` selects the default semantic loading profile for future runtime context selection.

In v1, `profiles.agent_loader_overrides` and `profiles.workflow_loader_overrides` select semantic loader profiles for specific agents or workflows.

Loader overrides do not select workers, change worker behavior, dispatch agents, or execute workflows.

Activation does not load context by itself. The semantic loader remains responsible for extracting and filtering context.

## Runtime Mode

In v1, `runtime_mode` declares activation intent only.

Allowed values are:

- `validation`
- `context`
- `review`
- `planning`

`runtime_mode` does not execute work, dispatch workers, run workflows, or change orchestration behavior.

## Rule Sets

In v1, `rule_sets` groups rule references for future context selection.

Rule sets are hints about which existing domain and operation rules are relevant. They do not replace `.ai/rules/` as the source of truth and must not copy or rewrite rule bodies.

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
- load context

Future sync may use activation as an input, but sync behavior must be defined separately.

## Read-only Boundary

`aios activation` is read-only.

It may validate activation schema fields, inventory references, runtime mode values, rule references, duplicate references, empty activation categories, and semantic loader profile names. It must not modify activation files or referenced `.ai` files.

## Deferred Items

The following are intentionally deferred:

- activation file auto-generation
- activation auto-fix
- automatic v0 to v1 migration
- full YAML parsing beyond the supported activation subset
- activation-driven context loading
- sync target selection
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
