---
description: "Runtime context loading and semantic loader budget rules"
globs: ".ai/**/*.md,.ai/**/*.yaml,.ai/**/*.yml"
alwaysApply: false
---

# Context Loading Rules
*Last Updated: 2026-05-23*
*Version: 1.0.0*

## Purpose

Semantic loading extracts runtime context from `.ai` source files by semantic layer.

`aios load-context` is a read-only context extraction command. It does not execute work, dispatch workers, run workflows, sync files, or summarize content.

## Supported Profiles

Supported semantic loader profiles are:

- `minimal-worker`
- `reviewer`
- `strategist`
- `validation-runtime`

Profiles define include and exclude layer defaults. They are context selection policies, not worker behavior policies.

## Budget Model

Semantic loader budget v0 uses character counts.

This is an estimate for context bundle size. It is not tokenizer-based model API token counting.

- Soft budget: warning threshold for included context chars.
- Hard budget: maximum included context chars before lower-priority chunks are excluded.
- `--max-chars`: CLI hard budget override. It does not change the profile soft budget.

## Profile Budgets

| Profile | Soft chars | Hard chars |
|---|---:|---:|
| `validation-runtime` | 6000 | 10000 |
| `minimal-worker` | 12000 | 20000 |
| `reviewer` | 24000 | 40000 |
| `strategist` | 36000 | 60000 |

## Budget Warnings

- `budget_soft_exceeded`: included chars exceed the profile soft budget.
- `budget_hard_exceeded`: chunks were excluded because included chars exceeded the hard budget.
- `budget_excluded_low_priority`: lower-priority chunks were excluded by budget filtering.

Budget warnings do not fail `aios load-context`.

## Exclusion Policy

Semantic profile include/exclude rules run first.

Budget filtering runs after profile filtering.

When context exceeds the hard budget, the loader excludes lower-priority chunks before truncation. Highest-priority layers are:

- `executable_contract`
- `structural_rules`
- `runtime_policy`

Content truncation is not implemented yet. `truncated_chunks` must remain `0` until truncation is explicitly implemented.

## Provenance

Loaded and budget-excluded chunks must preserve provenance:

- path
- semantic layer
- line range
- extraction method
- confidence
- char count when available
- exclusion reason when excluded

Budget-excluded chunks must be reported with reason `budget_excluded_low_priority`.

## Activation Relationship

Activation v1 may declare:

- `profiles.default_loader`
- `profiles.agent_loader_overrides`
- `profiles.workflow_loader_overrides`

These fields select semantic loader profiles. They do not load context by themselves, change worker behavior, or dispatch agents.

Activation-driven context loading is deferred.

## Read-only Boundary

Context loading may read `.ai` source files, extract sections, apply profile filters, apply budget filters, and report warnings.

It must not modify source files, activation files, registry files, rules, workflows, validators, or agents.

## Non-goals

Context loading budget rules do not implement:

- live model token counting
- semantic summarization
- content truncation
- orchestration
- worker execution
- workflow execution
- sync
- manifest generation
- adapter generation
- registry parser
- `.ai/registry/`
- auto-fix

## Related Rules

- `.ai/rules/operations/activation.rules.md`
- `.ai/rules/operations/registry.rules.md`
- `.ai/rules/operations/validation.rules.md`
