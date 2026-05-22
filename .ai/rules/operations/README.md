# Operational Rules

Operational rules define execution behavior and governance that can be reused across domains.

## Current Operational Rules

- `workflow.rules.md`: execution flow, roadmap/task/run-record loop, metadata-first linking, and recovery.
- `validation.rules.md`: validation behavior, validator references, and failure handling.
- `agent.rules.md`: agent roles, L1/L2 collaboration, escalation, and context management.
- `activation.rules.md`: runtime activation contract, inventory reference validation, semantic loader profile selection, and sync boundary.
- `registry.rules.md`: registry architecture, relationship layer boundaries, future extraction criteria, and read-only registry non-goals.

## Add an Operational Rule When

- The behavior applies across multiple domains.
- The behavior controls execution, validation, coordination, recovery, audit, or tooling.
- Keeping the behavior in a domain file would cause duplication.

Do not add an operational rule for behavior that belongs to only one business domain.

## Boundary

Operational rules may be referenced by domain rules. They must not define domain-specific artifact standards.
