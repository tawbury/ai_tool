# Documentation Rules

## Scope

Use this file when creating, editing, reviewing, or validating project documents.

## Load When

Load this rule when the task touches document language, document structure, metadata, templates, internal links, or document output consistency.

## Responsibilities

- Define how documents are written and structured.
- Define language and encoding requirements for documentation.
- Define common template and metadata expectations.
- Define common Obsidian link rules.

This file does not own domain-specific artifact locations. Domain-specific output paths belong to the relevant domain rule, such as `development.rules.md` or `hr.rules.md`.

## Rules

### Language

- Documents under `docs/` must be written in Korean.
- Documents under `.ai/` must be written in English.
- Keep each document language-consistent.
- Technical identifiers, file paths, code, and template variables may remain in their original form.

### Encoding

- All files must be saved as UTF-8 without BOM.
- Be careful when using shell tooling that may write BOM or corrupt Korean text.

### Templates

- Use the relevant template from `.ai/templates/` when a suitable template exists.
- Preserve template structure while translating content to the required document language.
- Template variables such as `{{CURRENT_DATE}}`, `{{USER}}`, and `{{REVIEWER}}` remain unchanged.
- Required metadata fields must not be left empty.

### Metadata and Links

- Document relationships must be declared in metadata when metadata is present.
- Body text may explain relationships, but body text must not be the only relationship source.
- Use real Obsidian internal links such as `[[filename.md]]`.
- Wildcard links such as `[[task_*.md]]` are forbidden.

### Common Document Areas

- `docs/plan/`: planning and design documents, written in Korean.
- `docs/reports/`: reports and completion records, written in Korean.
- `docs/roadmap/`: roadmap documents, written in Korean.
- `.ai/templates/`: reusable templates, written in English.
- `.ai/validators/`: validation references, written in English.
- `.ai/workflows/`: workflow references, written in English.

## Validation

- Check document language against its folder.
- Check metadata completeness when the document has metadata.
- Check template structure when a template applies.
- Check internal links for real filenames.
- Check that the file is UTF-8 without BOM.

## Related Rules

- `.ai/rules/domains/development.rules.md`
- `.ai/rules/domains/hr.rules.md`
- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`
