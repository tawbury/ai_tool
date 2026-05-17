# Workflow Rules

## Scope

Use this file for execution flow, metadata-first linking, run records, roadmap updates, and recovery behavior.

## Load When

Load this rule when the task involves roadmap work, task documents, run records, execution evidence, work recovery, or workflow consistency.

## Responsibilities

- Define the common execution loop.
- Define metadata-first document relationships.
- Define evidence requirements for completed work.
- Define recovery behavior after interruption or document issues.
- Define how shared commands participate in the execution workflow.

## Rules

### Metadata-First Linking

- Document relationships must be declared in metadata when metadata exists.
- If a relationship is absent from metadata fields such as Parent Document or Related Reference, it is operationally treated as absent.
- Body text may explain context but must not be the only relationship source.
- Use real Obsidian internal links such as `[[filename.md]]`.
- Wildcard links are forbidden.

### Operational Loop

- Core loop: Roadmap -> Task -> Run Record -> Roadmap update.
- Roadmap drives work selection and phase/session status.
- Task is the smallest executable unit and must reference its roadmap via metadata when using roadmap/task documents.
- Run Record is execution evidence and must reference the executed task and relevant roadmap when those documents exist.
- Roadmap updates must cite run records as evidence when roadmap tracking is used.

### Shared Command Execution

- Shared commands live under `.ai/commands/` and are reusable across AI CLI tools.
- When executing a shared command, read `.ai/commands/README.md` and the matching `.ai/commands/*.command.md` file before implementation.
- Treat the command file as the workflow contract for that command.
- Tool-specific command wrappers may invoke shared commands, but they must reference `.ai/commands/` rather than duplicate workflow bodies.
- If a shared command requires a report, write the report under `docs/reports/` in Korean unless the command specifies a stricter location.

### Recovery

- After session interruption, resume from the last valid roadmap, task, and run records when available.
- If a document is corrupted, isolate it and continue with valid documents.
- If workflow evidence is incomplete, record the gap rather than inventing evidence.

## Validation

- Check that metadata links use real filenames.
- Check that run records reference executed tasks when run records are created.
- Check that roadmap updates cite execution evidence when roadmap tracking is used.
- Check that shared command references point to real `.ai/commands/*.command.md` files.
- Check that tool-specific command wrappers do not become the canonical source for shared workflow behavior.

## Related Rules

- `.ai/rules/domains/documentation.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/agent.rules.md`
