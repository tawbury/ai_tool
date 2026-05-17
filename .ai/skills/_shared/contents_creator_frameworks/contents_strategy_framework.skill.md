---
name: Contents Strategy Framework
type: skill-framework
id: SKILL-CONTENTS-STRATEGY-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Contents Strategy Framework Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Strategic contents planning and roadmap management across all media types
- Audience development and engagement optimization strategies
- Cross-media strategy alignment and business objective integration
- **Scope**: Strategic framework that provides comprehensive content strategy development, audience optimization, and cross-media alignment while enabling media-specific strategic execution
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Business objectives and strategic goals
- Target audience specifications and market analysis
- Content performance metrics and engagement data
- Platform requirements and distribution strategies

### Output
**Unified Output Schema**:
- Content strategies and roadmap development plans
- Audience development and engagement optimization strategies
- Cross-media alignment frameworks and execution plans
- Performance measurement and strategic optimization recommendations
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the strategy mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| AUDIENCE_STRATEGY | audience, user, reader, viewer, engagement |
| PLATFORM_STRATEGY | platform, channel, distribution, publishing, media |
| MONETIZATION_STRATEGY | monetization, revenue, business, profit, commercial |
| GROWTH_STRATEGY | growth, scale, expansion, reach, market |
| INTEGRATED_STRATEGY | (default — no specific keywords matched) |

### Universal Contents Strategy Pipeline

#### Phase 1: Strategic Analysis & Planning
1. Business objective analysis and strategic goal identification
2. Target audience specification and market landscape evaluation
3. Content performance assessment and competitive analysis
4. Platform requirement evaluation and distribution strategy planning

#### Phase 2: Mode-Specific Strategy Development

| Mode | Focus Areas |
|------|------------|
| AUDIENCE_STRATEGY | Audience development, user persona, content personalization, cross-media audience journey |
| PLATFORM_STRATEGY | Multi-platform distribution, platform adaptation, cross-platform consistency, platform performance |
| MONETIZATION_STRATEGY | Content monetization, business model development, cross-media revenue streams, market positioning |
| GROWTH_STRATEGY | Content growth, audience scaling, cross-media growth synergies, performance-based optimization |
| INTEGRATED_STRATEGY | Comprehensive cross-media strategy, integrated alignment, holistic business integration |

#### Phase 3: Strategy Implementation & Execution
1. Cross-media strategy implementation and coordination
2. Platform-specific execution and performance monitoring
3. Audience engagement tracking and optimization
4. Business objective alignment and strategic adjustment

#### Phase 4: Performance Measurement & Optimization
1. Strategy performance measurement and KPI tracking
2. Cross-media synergy evaluation and optimization
3. Audience engagement analysis and improvement
4. Strategic refinement and continuous improvement

### Level-Specific Execution

| Level | Capabilities |
|-------|-------------|
| L1 (Junior) | Basic strategy development, template-based frameworks, cross-media coordination, strategy reporting |
| L2 (Senior) | Advanced strategic planning, complex cross-media optimization, strategic leadership, continuous improvement |
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Strategy planning and management platforms
- Audience analytics and engagement monitoring tools
- Content performance measurement and optimization systems
- Cross-platform distribution and management platforms
- Business intelligence and strategic analytics tools
- Collaboration and workflow management systems
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### OUT Scope (Universal)
- Primary content creation and production
- Technical platform development and implementation
- Original media asset creation and design
- Software engineering and system architecture
- Financial management and budget execution

### Contents Strategy Constraints
- Strategy development and planning only
- Audience analysis and engagement optimization
- Platform strategy and distribution planning
- Business alignment and objective integration
- Modern strategic planning best practices

### Mode-Specific Constraints

| Mode | Constraint |
|------|-----------|
| AUDIENCE_STRATEGY | Audience strategy only, no content creation |
| PLATFORM_STRATEGY | Platform strategy only, no technical development |
| MONETIZATION_STRATEGY | Monetization strategy only, no financial execution |
| GROWTH_STRATEGY | Growth strategy only, no operational implementation |
| INTEGRATED_STRATEGY | Combined constraints with enhanced scope protection |

### Quality & Standards Constraints
- Strategic planning standards and best practices
- Audience-centric approach and value alignment
- Business objective integration and strategic coherence
- Ethical strategy development and cultural sensitivity
- Innovation and strategic excellence standards
<!-- END_BLOCK -->
