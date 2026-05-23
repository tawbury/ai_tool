# Validators Directory

This directory contains validator documents and the validator index used by the shared AI runtime.

## Index

`validator_index.md` is the canonical index for validator references.

## Validator Groups

| Files | Purpose |
|---|---|
| `_base/*.md` | Base validator guidance for documents, skills, mappings, and agent skills. |
| `meta_validator.md`, `structure_validator.md` | Common document structure and metadata checks. |
| `task_validator.md`, `anchor_validator.md`, `architecture_validator.md`, `spec_validator.md`, `prd_validator.md`, `decision_validator.md`, `report_validator.md` | Document-type validators. |
| `skill_validator.md`, `skill_loading_validator.md`, `skill_execution_validator.md` | Skill structure, loading, and execution guidance. |
| `pm_skill_validator.md`, `developer_skill_validator.md`, `finance_skill_validator.md`, `hr_skill_validator.md`, `contents_creator_skill_validator.md` | Agent-specific skill validators. |
| `l2_review_validator.md`, `mentorship_validator.md`, `cross_agent_validator.md`, `senior_decision_validator.md` | Review, mentorship, senior decision, and cross-agent validators. |

## Runtime Relationship

`aios validate` checks validator index integrity and validates runtime targets. Validator documents remain read-only guidance; validation does not auto-fix files.
