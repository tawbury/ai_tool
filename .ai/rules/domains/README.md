# Domain Rules

Domain rules define business or work-domain standards: what is being produced, where domain-specific artifacts live, and which domain-specific constraints apply.

## Current Domain Rules

- `documentation.rules.md`: document structure, language, metadata, and template usage.
- `development.rules.md`: development artifacts, development documentation, and build/runtime guidance.
- `hr.rules.md`: HR evaluation inputs, outputs, constraints, and related skills.

## Add a Domain Rule When

- The domain has repeated rules that do not belong in an existing domain file.
- The domain has durable outputs, validation criteria, or approval flow.
- Adding the file improves selective loading and reduces irrelevant context.

Do not create a domain rule for one-off requests.

## Boundary

Domain rules may reference operational rules, but they must not duplicate workflow, validation, or agent governance rule bodies.
