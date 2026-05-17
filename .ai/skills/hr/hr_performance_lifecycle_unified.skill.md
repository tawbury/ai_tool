---
name: HR Performance Lifecycle Unified
type: skill
id: SKILL-HR-PERF-LIFECYCLE-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: hr
used_by: [hr]
tools: [claude-code, codex, gemini-cli]
---

# HR Performance Lifecycle Unified Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified performance lifecycle management with intelligent phase switching
- Performance evaluation, analysis, and improvement in integrated workflow
- Single entry point for all performance lifecycle needs with automatic phase detection
- **Scope**: Comprehensive performance lifecycle engine that replaces 2 specialized performance skills with intelligent routing between evaluation (WHAT), analysis (WHY), and improvement (HOW)
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Performance data (evaluations, ratings, goals, achievements)
- Context information (role requirements, business objectives, feedback)
- Analysis parameters (timeframe, scope, depth, focus areas)
- Improvement requirements (resources, constraints, priorities)

### Output
**Unified Output Schema**:
- Performance evaluation results & ratings
- Performance analysis reports & insights
- Performance improvement plans & recommendations
- Performance calibration results & optimization strategies
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Phase Detection Rules

Select the performance phase by matching keywords in the input:

| Phase | Keywords |
|-------|----------|
| PERFORMANCE_EVALUATION | evaluate, rate, assess, measure, review, what |
| PERFORMANCE_ANALYSIS | analyze, diagnose, interpret, investigate, why |
| PERFORMANCE_IMPROVEMENT | improve, enhance, optimize, develop, how |
| UNIFIED_LIFECYCLE | (default — no specific keywords matched) |

### Unified Performance Lifecycle Pipeline

#### Phase 1: Performance Data Collection & Validation
1. Performance evaluation data collection
2. Goal achievement records compilation
3. 360-degree feedback data integration
4. Performance improvement plan outcomes review

#### Phase 2: Phase-Specific Processing

**PERFORMANCE_EVALUATION Phase**:
- Performance rating & assessment execution
- Goal achievement measurement & validation
- Objective performance criteria application
- Fair evaluation process implementation

**PERFORMANCE_ANALYSIS Phase**:
- Performance trend analysis & interpretation
- Root cause analysis of performance variations
- Performance pattern identification & diagnosis
- Strategic performance insight generation

**PERFORMANCE_IMPROVEMENT Phase**:
- Performance gap identification & assessment
- Improvement opportunity analysis & prioritization
- Intervention strategy development & planning
- Performance optimization roadmap creation

**UNIFIED_LIFECYCLE Mode**:
- End-to-end performance management process
- Integrated evaluation → analysis → improvement workflow
- Comprehensive performance lifecycle management
- Holistic performance optimization strategy

#### Phase 3: Performance Intelligence & Analytics

**Descriptive Analytics**:
- Performance distribution analysis
- Performance trend identification
- Comparative performance analysis
- Performance variance assessment

**Predictive Analytics**:
- Performance prediction modeling
- At-risk employee identification
- Performance improvement forecasting
- Success probability modeling

**Prescriptive Analytics**:
- Performance optimization recommendations
- Intervention strategy optimization
- Resource allocation recommendations
- Performance improvement planning

#### Phase 4: Performance Management & Planning
1. Performance calibration & normalization
2. Improvement plan development & prioritization
3. Resource allocation & timeline planning
4. Success measurement & evaluation frameworks

### Level-Specific Execution

#### Junior Performance Manager (L1)
- Basic performance evaluation execution
- Simple performance analysis & reporting
- Standard improvement plan templates
- Basic performance tracking

#### Senior Performance Manager (L2)
- Advanced performance modeling & analysis
- Complex performance calibration
- Strategic performance optimization
- Predictive performance management
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Performance management system integration
- Goal tracking & measurement platforms
- Feedback collection & analysis systems
- Performance analytics & modeling tools
- Calibration & normalization frameworks
- Predictive modeling & machine learning platforms
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Performance Management Protection

**Forbidden Patterns** (must not appear in task content):
- Bias indicators: subjective, personal, biased, preferential, discriminatory
- Unfair practices: individual judgment, personal opinion, unfair treatment
- Misconduct: manipulation, favoritism, nepotism, harassment

**Scope Validation**: Fair evaluation scope must be validated. Reject if performance bias is detected.

### OUT Scope (Universal)
- Individual performance ratings without evidence ❌
- Subjective performance judgments ❌
- Unfair or discriminatory evaluation practices ❌
- Personal performance counseling without data ❌
- Legal performance management decisions ❌

### Performance Lifecycle Constraints
- Evidence-based evaluation & analysis only
- Objective criteria application & consistency
- Fairness & transparency in all processes
- Data-driven decision making & insights
- Equal opportunity & non-discrimination

### Mode-Specific Constraints
**PERFORMANCE_EVALUATION**: No subjective ratings, evidence-based only
**PERFORMANCE_ANALYSIS**: No speculation, data-driven interpretation only
**PERFORMANCE_IMPROVEMENT**: No unrealistic expectations, achievable plans only
**UNIFIED_LIFECYCLE**: Combined constraints with enhanced fairness protection

### Quality & Ethics Constraints
- Performance evaluation fairness & accuracy
- Analysis methodology rigor & validity
- Improvement plan feasibility & relevance
- Performance management confidentiality & privacy
- Continuous improvement & learning orientation
<!-- END_BLOCK -->
