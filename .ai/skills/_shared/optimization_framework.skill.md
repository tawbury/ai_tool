---
name: Unified Optimization Framework
type: skill-framework
id: SKILL-OPTIMIZATION-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [developer, finance, contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Unified Optimization Framework

**Purpose**: Cross-agent optimization framework providing standardized optimization patterns for all domains.

---

<!-- BLOCK:CORE_LOGIC -->
## Core Logic

Unified optimization system supporting multiple domains:

| Mode | Domain | Primary Agent |
|------|--------|--------------|
| PERFORMANCE | System/code performance optimization | Developer |
| COST | Cost reduction and efficiency | Finance |
| CONTENT | SEO/UX content optimization | Contents-Creator |
| PROCESS | Workflow/process optimization | All Agents |

### Mode Detection Rules

Select the optimization mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| PERFORMANCE | performance, speed, latency, throughput, memory |
| COST | cost, budget, expense, efficiency, reduction |
| CONTENT | SEO, UX, engagement, conversion, readability |
| PROCESS | workflow, process, automation, efficiency, productivity |

Default mode: PROCESS (when no keywords match).
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output Specification

### Input
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| target_area | string | Yes | Area to optimize |
| current_metrics | object | Yes | Current performance baseline |
| constraints | object | No | Optimization constraints |
| priority | enum | No | SPEED / QUALITY / COST |
| mode | enum | No | Auto-detected if not specified |

### Output
| Field | Type | Description |
|-------|------|-------------|
| recommendations | array | Prioritized optimization actions |
| expected_improvement | object | Predicted improvement metrics |
| implementation_plan | array | Step-by-step implementation |
| risk_assessment | object | Potential risks and mitigations |
| mode_used | string | Optimization mode applied |
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Standard 8-Step Pattern
All optimization modes follow this pattern:

1. **Analyze** — Evaluate current state and metrics
2. **Identify** — Find optimization opportunities
3. **Prioritize** — Rank by impact and feasibility
4. **Design** — Create optimization strategies
5. **Validate** — Test strategies against constraints
6. **Implement** — Execute optimization changes
7. **Monitor** — Track improvement metrics
8. **Report** — Document results and learnings

### Mode-Specific Techniques

| Mode | Analysis Methods | Strategies |
|------|-----------------|------------|
| PERFORMANCE | Profiling, benchmarking, bottleneck detection | Caching, lazy loading, code optimization, resource pooling |
| COST | Cost breakdown, variance analysis, benchmark comparison | Consolidation, automation, renegotiation, elimination |
| CONTENT | SEO audit, UX analysis, A/B testing | Keyword optimization, structure improvement, load optimization |
| PROCESS | Workflow mapping, bottleneck analysis, time study | Automation, parallel processing, elimination, simplification |

### Prioritization Matrix
| Impact | Effort: Low | Effort: Medium | Effort: High |
|--------|-------------|----------------|--------------|
| High | **Priority 1** | Priority 2 | Priority 3 |
| Medium | Priority 2 | Priority 3 | Priority 4 |
| Low | Priority 3 | Priority 4 | Do Not Do |
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICAL_REQUIREMENTS -->
## Technical Requirements

### Baseline Requirements
- Documented current state metrics
- Defined success criteria
- Established measurement methodology

### Performance Standards by Mode
| Mode | Key Metric | Target Improvement |
|------|------------|-------------------|
| PERFORMANCE | Response time | >= 20% faster |
| COST | Total cost | >= 15% reduction |
| CONTENT | Engagement | >= 10% increase |
| PROCESS | Cycle time | >= 25% reduction |

### Monitoring Requirements
- Before/after comparison metrics
- Continuous monitoring post-implementation
- Rollback capability for all changes
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Out of Scope
- Actual implementation execution (analysis only)
- Budget approval decisions
- Personnel changes
- Third-party vendor negotiations

### Quality Gates
- All recommendations must have measurable KPIs
- Risk assessment required for high-impact changes
- Stakeholder approval required before implementation

### Agent-Specific Constraints
| Mode | Agent | Limitations |
|------|-------|-------------|
| PERFORMANCE | Developer | No infrastructure purchases |
| COST | Finance | No contract terminations |
| CONTENT | Contents-Creator | No brand guideline changes |
| PROCESS | All | No organizational restructuring |
<!-- END_BLOCK -->

<!-- BLOCK:RELATED_SKILLS -->
## Related Skills

| Agent | Related Skill File | Mode |
|-------|-------------------|------|
| Developer | `.ai/skills/developer/dev_performance_optimization.skill.md` | PERFORMANCE |
| Finance | `.ai/skills/finance/cost_optimization.skill.md` | COST |
| Contents-Creator | `.ai/skills/contents-creator/text/contents_optimization.skill.md` | CONTENT |
<!-- END_BLOCK -->
