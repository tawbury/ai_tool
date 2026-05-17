---
name: Contents Creation Framework
type: skill-framework
id: SKILL-CONTENTS-CREATION-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Contents Creation Framework Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Universal contents creation principles & methodologies
- Cross-media consistency & quality standards enforcement
- Contents lifecycle management & optimization strategies
- **Scope**: Foundational framework that provides universal creation principles applicable across all media types while maintaining media-specific specialization
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Contents requirements & objectives
- Target audience specifications & platform constraints
- Media type specifications & technical requirements
- Quality standards & brand guidelines

### Output
**Unified Output Schema**:
- Contents creation methodologies & best practices
- Cross-media consistency guidelines & standards
- Quality assurance frameworks & evaluation criteria
- Lifecycle management strategies & optimization plans
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the creation mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| VISUAL_CREATION | visual, image, design, graphic, brand, 3d, motion |
| TEXT_CREATION | text, writing, ebook, content, article, story |
| INTERACTIVE_DESIGN | interactive, ux, ui, prototype, wireframe, user |
| VIDEO_PRODUCTION | video, film, animation, editing, storyboard |
| BUSINESS_STRATEGY | marketing, business, strategy, monetization, audience |
| UNIFIED_CREATION | (default — no specific keywords matched) |

### Universal Contents Creation Pipeline

#### Phase 1: Requirements Analysis & Planning
1. Contents requirements analysis & objective definition
2. Target audience specification & platform constraint evaluation
3. Media type assessment & technical requirement identification
4. Quality standards establishment & brand guideline alignment

#### Phase 2: Mode-Specific Creation Methodology

| Mode | Focus Areas |
|------|------------|
| VISUAL_CREATION | Visual design principles, color theory, typography, visual hierarchy, brand consistency, cross-platform adaptation |
| TEXT_CREATION | Writing fundamentals, content structure, audience tone/style, readability standards, cross-format adaptation |
| INTERACTIVE_DESIGN | UX principles, interaction design, usability/accessibility, prototyping, user testing |
| VIDEO_PRODUCTION | Visual storytelling, narrative structure, production workflows, audio-visual sync, platform optimization |
| BUSINESS_STRATEGY | Content strategy, audience development, monetization, cross-platform business alignment |
| UNIFIED_CREATION | Comprehensive methodology, integrated cross-media strategies, holistic QA, end-to-end lifecycle |

#### Phase 3: Quality Assurance & Standards
1. Universal quality standards application & evaluation
2. Cross-media consistency verification & validation
3. Brand guideline compliance & identity maintenance
4. Performance measurement & optimization implementation

#### Phase 4: Lifecycle Management & Optimization
1. Contents performance monitoring & analytics
2. Audience engagement tracking & optimization
3. Cross-media synergy evaluation & enhancement
4. Continuous improvement & strategy refinement

### Level-Specific Execution

| Level | Capabilities |
|-------|-------------|
| L1 (Junior) | Basic creation principles, template-based content, cross-media consistency maintenance, basic monitoring |
| L2 (Senior) | Advanced strategies, custom framework development, cross-media synergy optimization, creative leadership |
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Universal content management systems & platforms
- Cross-media design tools & creation software
- Quality assurance frameworks & testing tools
- Analytics platforms & performance monitoring systems
- Brand management systems & guideline repositories
- Collaboration tools & workflow management platforms
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### OUT Scope (Universal)
- Technical development & software implementation
- Engineering decisions & system architecture
- Database management & infrastructure operations
- Code development & deployment processes
- DevOps & technical maintenance

### Contents Creation Constraints
- Contents creation & media production only
- Cross-media consistency & quality standards
- Brand identity maintenance & strategic alignment
- Audience engagement & value delivery
- Modern contents creation best practices

### Mode-Specific Constraints

| Mode | Constraint |
|------|-----------|
| VISUAL_CREATION | Visual media only, no technical implementation |
| TEXT_CREATION | Text content only, no platform development |
| INTERACTIVE_DESIGN | User experience only, no system design |
| VIDEO_PRODUCTION | Video media only, no streaming infrastructure |
| BUSINESS_STRATEGY | Business strategy only, no financial implementation |
| UNIFIED_CREATION | Combined constraints with enhanced scope protection |

### Quality & Standards Constraints
- Contents quality standards & best practices
- Cross-media consistency & brand alignment
- Audience-centric approach & value proposition
- Ethical content creation & cultural sensitivity
- Innovation & creative excellence standards
<!-- END_BLOCK -->
