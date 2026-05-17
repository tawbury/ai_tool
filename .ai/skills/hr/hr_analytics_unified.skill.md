---
name: HR Unified Analytics
type: skill
id: SKILL-HR-ANALYTICS-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: hr
used_by: [hr]
tools: [claude-code, codex, gemini-cli]
---

# HR Unified Analytics Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified HR analytics with intelligent mode switching
- Multi-domain analysis (Talent/Performance/Productivity/Structure/SkillGap) → strategic insights
- Single entry point for all HR analytics needs with automatic domain detection
- **Scope**: Comprehensive analytics engine that replaces 6 specialized analysis skills with intelligent routing
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Analysis target data (agent performance, talent metrics, productivity indicators, org structure, skill inventory)
- Context parameters (time range, scope, objective)
- Analysis requirements (report type, insight depth, recommendation level)

### Output
**Unified Output Schema**:
- Comprehensive analysis reports with domain-specific insights
- Strategic recommendations & action plans
- Predictive models & trend analysis
- Visualization-ready data summaries
- Implementation roadmaps
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the analytics mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| TALENT | talent, capability, growth, potential, acquisition |
| PERFORMANCE | performance, evaluation, rating, achievement, goal |
| PRODUCTIVITY | productivity, efficiency, output, resource, utilization |
| STRUCTURE | structure, organization, hierarchy, reporting, decision |
| SKILL_GAP | skill, gap, capability, inventory, mapping |
| GENERAL | (default — no specific keywords matched) |

### Unified Analysis Pipeline

#### Phase 1: Data Ingestion & Validation
1. Multi-source data collection & integration
2. Data quality verification & cleansing
3. Schema standardization & normalization
4. Meta information filtering (physical isolation)

#### Phase 2: Mode-Specific Analysis

**TALENT Mode**:
- Capability & performance correlation analysis
- Growth pattern identification & prediction
- Talent acquisition opportunity analysis
- Development requirements derivation

**PERFORMANCE Mode**:
- Performance trend analysis & calibration
- Root cause analysis of performance variations
- Predictive performance modeling
- Strategic performance optimization

**PRODUCTIVITY Mode**:
- Efficiency indicator calculation & benchmarking
- Bottleneck identification & analysis
- Resource utilization optimization
- Productivity improvement strategy

**STRUCTURE Mode**:
- Organization structure mapping & visualization
- Decision-making efficiency analysis
- Structural problem diagnosis
- Optimization recommendation generation

**SKILL_GAP Mode**:
- Current vs target skill capability analysis
- Gap impact assessment & prioritization
- Development requirement derivation
- Skill mapping strategy formulation

**GENERAL Mode**:
- Cross-domain HR data analysis
- Integrated insights generation
- Holistic HR strategy recommendations

#### Phase 3: Insight Generation & Synthesis
1. Pattern recognition & trend analysis
2. Predictive modeling & forecasting
3. Strategic insight derivation
4. Recommendation prioritization

#### Phase 4: Output Generation
1. Domain-specific report generation
2. Executive summary creation
3. Visualization data preparation
4. Implementation roadmap development

### Level-Specific Execution

#### Junior Analyst (L1)
- Basic data analysis & reporting
- Simple trend identification
- Standard template application
- Basic recommendation generation

#### Senior Analyst (L2)
- Advanced predictive modeling
- Complex pattern recognition
- Strategic insight generation
- Cross-domain synthesis
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Unified analytics platform (multi-domain support)
- Statistical analysis & machine learning frameworks
- Data visualization & reporting systems
- Mode detection & routing algorithms
- Meta information filtering systems
- Cross-domain data integration tools
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Meta Information Protection

**Forbidden Meta Patterns** (must not appear in analysis scope):
- System metadata: connection, tracking, management, id, timestamp, metadata
- Internal config: system, internal, admin, config

**Scope Validation**: Analysis scope must be validated. Meta information must be physically isolated from analysis to prevent inference bias.

### OUT Scope (Universal)
- Actual HR decisions & interventions 
- Personal information exposure & legal judgments 
- External data utilization & benchmarking 
- Implementation execution & program management 

### Analysis Constraints (Mode-Agnostic)
- Internal data utilization only
- Statistical & evidence-based analysis
- Personal information protection & anonymity
- Objective conclusion derivation
- Meta information independence (physically enforced)

### Mode-Specific Constraints
**TALENT**: No individual hiring decisions, ethical AI compliance
**PERFORMANCE**: No individual performance ratings, fairness assurance  
**PRODUCTIVITY**: No individual monitoring, aggregate metrics only
**STRUCTURE**: No organizational disruption recommendations
**SKILL_GAP**: No capability evaluations, development suggestions only
<!-- END_BLOCK -->