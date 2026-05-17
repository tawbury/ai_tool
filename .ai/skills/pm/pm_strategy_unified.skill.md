---
name: PM Strategy Unified
type: skill
id: SKILL-PM-STRATEGY-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: pm
used_by: [pm]
tools: [claude-code, codex, gemini-cli]
---

# PM Strategy Unified Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified product strategy management with intelligent domain switching
- Strategic planning, roadmap management, growth strategy, and global expansion
- Single entry point for all product strategy needs with automatic domain detection
- **Scope**: Comprehensive product strategy engine that replaces 6 specialized strategy skills with intelligent routing
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Business objectives & requirements
- Product vision & strategic direction
- Market & competitive analysis results
- Resources & constraint information

### Output
**Unified Output Schema**:
- Strategic planning documents & product roadmaps
- Growth strategies & user acquisition programs
- Global product strategies & localization roadmaps
- Product launch strategies & rollout plans
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| STRATEGIC_PLANNING | planning, strategic, objectives, timeline, resources |
| ROADMAP_MANAGEMENT | roadmap, milestone, timeline, feature, priority |
| PRODUCT_GROWTH | growth, acquisition, retention, pmf, expansion |
| GLOBAL_STRATEGY | global, international, localization, expansion, market |
| PRODUCT_LAUNCH | launch, rollout, market entry, go-to-market, timing |
| (default) | (no specific keywords matched) |

### Unified Product Strategy Pipeline

#### Phase 1: Strategic Analysis & Foundation
1. Business objective analysis & strategic direction setting
2. Market & competitive environment analysis integration
3. Product vision specification & objective setting
4. Resources & constraint condition evaluation

#### Phase 2: Mode-Specific Strategy Development

**STRATEGIC_PLANNING Mode**:
- Strategic planning & roadmap creation
- Complex objectives → executable plans transformation
- Structural thinking/organization (strategic → tactical)
- Risk assessment & mitigation planning

**ROADMAP_MANAGEMENT Mode**:
- Product roadmap creation/maintenance/communication
- Product evolution visualization & priority balancing
- Strategic timeline management & sequencing
- Stakeholder expectation alignment

**PRODUCT_GROWTH Mode**:
- Product growth strategy establishment & execution
- User acquisition & retention optimization
- Product-market fit (PMF) strengthening & expansion
- Growth indicator tracking & optimization

**GLOBAL_STRATEGY Mode**:
- Global product strategy establishment & localization
- Domestic product → global market expansion
- Cultural/legal/technical difference consideration
- Regulatory compliance & global rollout

**PRODUCT_LAUNCH Mode**:
- Product launch strategy establishment & execution
- Product development → market entry transformation
- Successful rollout & market expansion
- Launch success indicators & timing optimization

**UNIFIED_STRATEGY Mode**:
- Comprehensive product strategy implementation
- Integrated planning + roadmap + growth + global + launch
- End-to-end product strategy development
- Full-stack product optimization

#### Phase 3: Strategy Implementation & Execution
1. Strategic plan execution & milestone tracking
2. Roadmap communication & stakeholder management
3. Growth program implementation & optimization
4. Global expansion execution & localization

#### Phase 4: Monitoring & Optimization
1. Strategy performance monitoring & KPI tracking
2. Market response analysis & adjustment
3. Competitive landscape monitoring & response
4. Continuous strategy optimization & improvement

### Level-Specific Execution

#### Junior Product Manager (L1)
- Basic strategic planning & roadmap creation
- Simple growth strategy implementation
- Standard market analysis & competitive review
- Basic launch planning & execution

#### Senior Product Manager (L2)
- Advanced strategic planning & complex roadmap management
- Sophisticated growth strategy & global expansion
- Complex market analysis & competitive positioning
- Strategic product leadership & market timing
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Product management tools (Jira, Asana, Productboard)
- Analytics platforms (Google Analytics, Mixpanel, Amplitude)
- Market research tools & competitive intelligence platforms
- Roadmap management software & visualization tools
- Collaboration tools & stakeholder management systems
- Data analysis & reporting frameworks
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Scope Protection

**Purpose**: Physical isolation of technical implementation in product strategy

**Scope Validation**: Validate scope before processing. Reject if forbidden patterns are detected.

### OUT Scope (Universal)
- Technical development & implementation ❌
- Engineering decisions & architecture ❌
- Database design & infrastructure management ❌
- Code development & testing ❌
- DevOps & deployment operations ❌

### Product Strategy Constraints
- Product strategy & planning only
- Market analysis & competitive intelligence
- User experience & business value focus
- Strategic decision making & prioritization
- Modern product management best practices

### Mode-Specific Constraints
**STRATEGIC_PLANNING**: Strategic planning only, no tactical execution
**ROADMAP_MANAGEMENT**: Roadmap creation only, no feature development
**PRODUCT_GROWTH**: Growth strategy only, no technical implementation
**GLOBAL_STRATEGY**: Global expansion only, no localization development
**PRODUCT_LAUNCH**: Launch strategy only, no technical deployment
**UNIFIED_STRATEGY**: Combined constraints with enhanced scope protection

### Quality & Standards Constraints
- Product management standards & best practices
- Data-driven decision making & analytics
- User-centric approach & value proposition
- Market alignment & competitive positioning
- Strategic thinking & business acumen
<!-- END_BLOCK -->
