---
name: Unified Research Framework
type: skill-framework
id: SKILL-RESEARCH-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [pm, contents-creator, finance]
tools: [claude-code, codex, gemini-cli]
---

# Unified Research Framework

**Purpose**: Cross-agent research framework providing standardized research patterns for all domains.

---

<!-- BLOCK:CORE_LOGIC -->
## Core Logic

Unified research system supporting multiple domains:

| Mode | Domain | Primary Agent |
|------|--------|--------------|
| USER | User research and experience insights | PM |
| MARKET | Market research and competitive analysis | PM, Finance |
| AUDIENCE | Audience research and behavior analysis | Contents-Creator |
| TREND | Trend analysis and forecasting | Finance |

### Mode Detection Rules

Select the research mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| USER | user, customer, persona, journey, experience, usability |
| MARKET | market, competitor, industry, positioning, share |
| AUDIENCE | audience, reader, viewer, demographic, segment |
| TREND | trend, forecast, prediction, future, emerging |

Default mode: MARKET (when no keywords match).
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output Specification

### Input
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| research_objective | string | Yes | What to research |
| scope | object | Yes | Research boundaries |
| data_sources | array | No | Primary/secondary sources |
| methodology | enum | No | QUALITATIVE / QUANTITATIVE / MIXED |
| mode | enum | No | Auto-detected if not specified |

### Output
| Field | Type | Description |
|-------|------|-------------|
| findings | array | Key research findings |
| insights | array | Actionable insights |
| recommendations | array | Strategic recommendations |
| data_summary | object | Summarized research data |
| confidence_level | string | HIGH / MEDIUM / LOW |
| mode_used | string | Research mode applied |
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Standard Research Process
1. **Planning** — Define objectives, scope, methodology
2. **Data Collection** — Gather primary and secondary data
3. **Data Analysis** — Process and analyze collected data
4. **Synthesis** — Combine findings into insights
5. **Reporting** — Document and present findings

### Mode-Specific Methods

| Mode | Qualitative Methods | Quantitative Methods |
|------|-------------------|---------------------|
| USER | Interviews, focus groups, observation, diary studies | Surveys, A/B testing, analytics, heatmaps |
| MARKET | Expert interviews, case studies, SWOT analysis | Market sizing, share analysis, benchmarking |
| AUDIENCE | Persona development, journey mapping, community analysis | Demographic analysis, behavior tracking, segmentation |
| TREND | Expert panels, scenario planning, Delphi method | Time series, regression, leading indicators |

### Data Source Categories
| Category | Examples | Reliability |
|----------|----------|-------------|
| Primary | Interviews, Surveys, Experiments | High |
| Secondary | Reports, Publications, Databases | Medium-High |
| Tertiary | Aggregators, Summaries | Medium |

### Analysis Framework
| Type | Methods | Output |
|------|---------|--------|
| Qualitative | Thematic analysis, Coding, Pattern matching | Themes, Patterns |
| Quantitative | Statistical analysis, Regression, Clustering | Metrics, Correlations |
| Mixed | Triangulation, Cross-validation | Comprehensive insights |
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICAL_REQUIREMENTS -->
## Technical Requirements

### Sample Size Guidelines
| Research Type | Minimum Sample | Recommended |
|---------------|----------------|-------------|
| Qualitative interviews | 8-12 | 15-20 |
| Quantitative surveys | 100 | 300+ |
| A/B tests | 1,000 per variant | 5,000+ |
| Trend analysis | 24 time points | 36+ |

### Data Quality Standards
- Source credibility verification
- Data recency (within 12 months for market data)
- Sample representativeness validation
- Bias assessment and mitigation

### Documentation Requirements
- Research methodology documentation
- Data collection instruments
- Analysis procedures
- Limitations and assumptions
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Out of Scope
- Direct customer contact (research design only)
- Personal data collection without consent
- Competitor intelligence gathering (unethical methods)
- Real-time data collection systems

### Ethical Guidelines
- Informed consent required for primary research
- Data privacy compliance (GDPR, etc.)
- Transparent methodology reporting
- Conflict of interest disclosure

### Agent-Specific Constraints
| Mode | Agent | Limitations |
|------|-------|-------------|
| USER | PM | No customer relationship management |
| MARKET | PM/Finance | No competitive intelligence operations |
| AUDIENCE | Contents-Creator | No direct audience engagement |
| TREND | Finance | No investment recommendations |
<!-- END_BLOCK -->

<!-- BLOCK:RELATED_SKILLS -->
## Related Skills

| Agent | Related Skill File | Mode |
|-------|-------------------|------|
| PM | `.ai/skills/pm/pm_analytics_unified.skill.md` | USER |
| Contents-Creator | `.ai/skills/contents-creator/text/audience_analytics.skill.md` | AUDIENCE |
| Contents-Creator | `.ai/skills/contents-creator/business/ebook_market_analysis.skill.md` | MARKET |
| Finance | `.ai/skills/finance/market_trend_analysis.skill.md` | TREND |
| Finance | `.ai/skills/finance/business_intelligence.skill.md` | MARKET |
<!-- END_BLOCK -->
