---
name: Unified Analytics Framework
type: skill-framework
id: SKILL-ANALYTICS-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [hr, pm, contents-creator, finance]
tools: [claude-code, codex, gemini-cli]
---

# Unified Analytics Framework

**Purpose**: Cross-agent analytics framework providing standardized analytics patterns for all domains.

---

<!-- BLOCK:CORE_LOGIC -->
## Core Logic

Unified analytics system supporting multiple analysis modes across agents:

| Mode | Domain | Primary Agent |
|------|--------|--------------|
| PRODUCT | Product/feature analytics | PM |
| AUDIENCE | User/audience analytics | Contents-Creator |
| TALENT | HR/talent analytics | HR |
| FINANCIAL | Financial/business analytics | Finance |
| CONTENT | Content performance analytics | Contents-Creator |

### Mode Detection Rules

Select the analytics mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| PRODUCT | product, feature, user engagement, conversion, funnel |
| AUDIENCE | audience, reader, viewer, subscriber, engagement |
| TALENT | employee, performance, retention, skill, workforce |
| FINANCIAL | revenue, cost, ROI, budget, profit, expense |
| CONTENT | content, views, shares, reach, impressions |

Default mode: PRODUCT (when no keywords match).
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output Specification

### Input
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| data_source | string | Yes | Data source identifier |
| analysis_type | enum | Yes | DESCRIPTIVE / PREDICTIVE / PRESCRIPTIVE |
| mode | enum | No | Auto-detected if not specified |
| time_range | object | No | Analysis time period |
| metrics | array | No | Specific metrics to analyze |

### Output
| Field | Type | Description |
|-------|------|-------------|
| insights | array | Key findings and patterns |
| recommendations | array | Actionable suggestions |
| visualizations | array | Chart/graph specifications |
| confidence_score | float | Analysis confidence (0-1) |
| mode_used | string | Analytics mode applied |
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Phase 1: Data Collection & Preparation
1. Identify data sources based on mode
2. Validate data completeness
3. Clean and normalize data
4. Handle missing values

### Phase 2: Analysis Execution

#### Metrics by Mode

| Mode | Key Metrics |
|------|------------|
| PRODUCT | DAU, MAU, retention, conversion, ARPU |
| AUDIENCE | engagement_rate, reach, growth_rate, demographics |
| TALENT | performance_score, turnover_risk, skill_gaps, satisfaction |
| FINANCIAL | revenue, margin, cash_flow, ROI, variance |
| CONTENT | views, shares, time_on_page, bounce_rate, CTR |

#### Analysis Methods by Type

| Type | Methods | Output |
|------|---------|--------|
| Descriptive | Aggregation, Visualization, Pattern Analysis | Current state summary |
| Predictive | Forecasting, Classification, Clustering | Future predictions |
| Prescriptive | Optimization, Recommendations, Simulation | Action recommendations |

### Phase 3: Insight Generation
1. Identify patterns and trends
2. Detect anomalies
3. Generate comparative analysis
4. Produce actionable recommendations
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICAL_REQUIREMENTS -->
## Technical Requirements

### Data Standards
- Minimum sample size: 100 records for statistical significance
- Time series: Minimum 30 data points for trend analysis
- Data freshness: Within 24 hours for real-time dashboards

### Performance Thresholds
| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Analysis time | <5s | 5-15s | >15s |
| Data load time | <2s | 2-5s | >5s |
| Memory usage | <100MB | 100-200MB | >200MB |

### Integration Points
- Database connections (SQL/NoSQL)
- API endpoints for real-time data
- Export formats: JSON, CSV, PDF
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Out of Scope
- Real-time streaming analytics (batch only)
- Raw data storage management
- Data source configuration
- External API management

### Agent-Specific Constraints
| Mode | Agent | Limitations |
|------|-------|-------------|
| PRODUCT | PM | No technical implementation |
| AUDIENCE | Contents-Creator | No marketing execution |
| TALENT | HR | No performance decisions |
| FINANCIAL | Finance | No actual transactions |
| CONTENT | Contents-Creator | No publishing decisions |

### Quality Standards
- Confidence score >= 0.7 for recommendations
- Minimum 3 data points for trend analysis
- All outputs must include data source citations
<!-- END_BLOCK -->

<!-- BLOCK:RELATED_SKILLS -->
## Related Skills

| Agent | Related Skill File | Mode |
|-------|-------------------|------|
| PM | `.ai/skills/pm/pm_analytics_unified.skill.md` | PRODUCT |
| Contents-Creator | `.ai/skills/contents-creator/text/audience_analytics.skill.md` | AUDIENCE |
| Contents-Creator | `.ai/skills/contents-creator/text/contents_analytics.skill.md` | CONTENT |
| HR | `.ai/skills/hr/hr_analytics_unified.skill.md` | TALENT |
| Finance | `.ai/skills/finance/business_intelligence.skill.md` | FINANCIAL |
| Finance | `.ai/skills/finance/financial_analysis.skill.md` | FINANCIAL |
<!-- END_BLOCK -->
