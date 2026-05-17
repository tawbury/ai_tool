# Command: implement-design

## Purpose

Execute the post-design implementation phase from an existing design document.

This command starts after the plan document and implementation-ready design document already exist. It performs implementation, validates alignment against the design document, remediates incomplete items until the achievement rate is above the configured threshold, and then writes a Korean completion report under `docs/reports/`.

## Inputs

Required:

- `design_document`: Path to the implementation-ready design document.

Optional:

- `plan_document`: Path to the related plan document.
- `achievement_threshold`: Minimum achievement rate. Default: `90%`.
- `report_path`: Explicit report output path. Default: generate a descriptive file under `docs/reports/`.
- `scope_notes`: Additional user constraints for the implementation.

If an input is missing but can be inferred from the current request or document metadata, infer it and continue. Ask the user only when the design document cannot be identified safely.

## Required Rule Loading

Always load:

- `.ai/rules/rules.md`
- `.ai/rules/domains/documentation.rules.md`
- `.ai/rules/operations/workflow.rules.md`
- `.ai/rules/operations/validation.rules.md`

Load additional domain or agent rules only when the design document or implementation scope requires them.

## Workflow

### Phase 1: Context Intake

1. Read the design document.
2. Read the related plan document when provided or referenced in metadata.
3. Inspect the codebase or document tree paths referenced by the design.
4. Identify implementation targets, non-goals, constraints, validation requirements, and report requirements.
5. Preserve existing user changes. Do not revert unrelated work.

### Phase 2: Implementation Checklist

Create an internal checklist from the design document.

Each checklist item must include:

- `id`
- `requirement`
- `source_section`
- `implementation_target`
- `validation_method`
- `status`: `pending | implemented | blocked | out_of_scope`

Use the design document as the source of truth. If the design is ambiguous, choose the smallest implementation that satisfies the stated intent and record the assumption in the report.

### Phase 3: Implementation

1. Implement all in-scope checklist items.
2. Keep edits scoped to the design.
3. Update shared rules, commands, adapters, code, tests, or documents only when required by the design.
4. Do not create standalone manifests, schemas, JSON, JSONL, or new rule files unless the design explicitly requires them or the command discovers a documented maintenance need.
5. Do not create symbolic links.

### Phase 4: Design Alignment Validation

Validate implementation against the checklist.

For each item:

- Mark `implemented` when the repository now satisfies the requirement.
- Mark `blocked` only when implementation is impossible without missing information or external dependency.
- Mark `out_of_scope` only when the design explicitly excludes it.

Calculate achievement rate:

```text
achievement_rate = implemented_items / in_scope_items * 100
in_scope_items = total_items - out_of_scope_items
```

Blocked items count as not implemented.

### Phase 5: Remediation Loop

If `achievement_rate <= achievement_threshold`, repeat:

1. List every missing or blocked in-scope item.
2. Re-implement all items that can be completed without violating user constraints.
3. Re-run validation.
4. Recalculate achievement rate.

Stop only when one of these conditions is true:

- `achievement_rate > achievement_threshold`
- remaining gaps are genuinely blocked and documented with concrete reasons

The default threshold is strict: achievement must be greater than `90%`, not equal to `90%`.

### Phase 6: Report

After the threshold is exceeded, write a Korean report under `docs/reports/`.

The report must include:

- metadata
- source design document
- related plan document, if any
- changed files
- implementation summary
- checklist achievement table or summary
- final achievement rate
- validation commands/checks and results
- remaining gaps, if any
- final judgment

Use real Obsidian links in metadata and body references where applicable.

## Validation Requirements

Run the strongest available validation that is practical for the changed files.

Minimum validation:

- `git diff --check`
- UTF-8 without BOM check for changed text files
- referenced file existence check for metadata links and command/rule references
- no symbolic links created under rules, commands, or agent directories
- no unintended standalone manifest/schema/log files created

Additional validation should follow the design document and relevant validators.

## Output Requirements

In the final response to the user:

- State that the shared command completed.
- Provide the final achievement rate.
- Link the report file.
- Mention important validation results.
- Mention any remaining blocked items.

Keep the response concise.

## Tool-Specific Wrappers

AI CLI-specific commands may wrap this command, but wrappers must only point to this file and pass arguments. The canonical workflow is this `.ai/commands/implement-design.command.md` file.
