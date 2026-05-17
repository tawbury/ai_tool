---
name: skill-creator
description: Create or update reusable AI skills for shared .ai usage or tool-specific skill systems. Use when the user wants a new skill, skill refactor, bundled scripts/references/assets, or packaging/validation guidance.
---

# Skill Creator

Create effective AI skills with concise instructions and bundled resources.

## Core Principles

- Keep the entry skill file concise.
- Put detailed examples and long references in `references/`.
- Put deterministic or repeated procedures in `scripts/`.
- Put reusable output assets or templates in `assets/`.
- Preserve tool-specific behavior only when the skill explicitly targets that tool.
- Prefer `.ai/skills/` as the shared source for multi-CLI usage.

## Workflow

1. Understand concrete user examples and trigger conditions.
2. Decide whether the skill is shared or tool-specific.
3. Plan bundled resources: scripts, references, and assets.
4. Create or update the skill entry file.
5. Add or update resources.
6. Validate frontmatter, references, scripts, and resource paths.
7. Iterate based on real usage.

## Bundled Resources

The original skill creator resources are preserved here:

- `scripts/init_skill.py`
- `scripts/package_skill.py`
- `scripts/quick_validate.py`
- `references/output-patterns.md`
- `references/workflows.md`
- `LICENSE.txt`

Use the scripts when deterministic creation or packaging is needed. Read the references only when output patterns or workflow design details are needed.

## Shared `.ai` Skill Format

For this repository, prefer an entry file named `<skill_name>.skill.md` under the relevant `.ai/skills/` folder.

Use this frontmatter shape:

```yaml
---
name: skill-name
description: What the skill does and when to use it.
---
```

The body should define the workflow, inputs, outputs, constraints, validation, and references.
