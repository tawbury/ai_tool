---
name: Quality Assurance Framework
type: skill-framework
id: SKILL-QA-FRAMEWORK-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Quality Assurance Framework Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Universal quality standards & evaluation criteria across all media types
- Cross-media quality consistency and performance optimization
- Contents quality assurance methodologies and continuous improvement
- **Scope**: Comprehensive QA framework that ensures consistent quality standards across all media while enabling media-specific quality optimization and performance measurement
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Content assets across all media types and formats
- Quality standards and brand guidelines
- Performance metrics and evaluation criteria
- Platform-specific requirements and technical constraints

### Output
**Unified Output Schema**:
- Quality assessment reports and evaluation results
- Cross-media quality consistency analysis
- Performance optimization recommendations
- Quality improvement strategies and action plans
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the quality mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| VISUAL_QA | visual, image, design, graphic, brand, 3d, motion |
| TEXT_QA | text, writing, content, article, story, readability |
| INTERACTIVE_QA | interactive, ux, ui, prototype, usability, accessibility |
| VIDEO_QA | video, film, animation, audio, quality, streaming |
| UNIFIED_QA | (default — no specific keywords matched) |

### Universal Quality Assurance Pipeline

#### Phase 1: Quality Standards Analysis
1. Content asset analysis and quality requirement identification
2. Brand guideline review and consistency standard establishment
3. Platform-specific quality criteria and technical constraint evaluation
4. Performance metrics definition and quality benchmark setting

#### Phase 2: Mode-Specific Quality Assessment

| Mode | Assessment Focus |
|------|-----------------|
| VISUAL_QA | Visual design quality, brand identity compliance, color/typography accuracy, cross-platform visual quality |
| TEXT_QA | Text quality, readability, grammar/style consistency, audience-appropriate language, localization |
| INTERACTIVE_QA | UX quality, usability, accessibility compliance, cross-platform interactive quality, user testing |
| VIDEO_QA | Video quality, technical spec compliance, audio-visual sync, cross-platform streaming, brand alignment |
| UNIFIED_QA | Comprehensive cross-media assessment, integrated consistency, holistic brand experience quality |

#### Phase 3: Quality Testing & Validation
1. Cross-media quality testing and consistency verification
2. Platform-specific quality validation and compliance checking
3. Brand guideline enforcement and identity consistency assessment
4. User experience testing and quality feedback collection

#### Phase 4: Quality Optimization & Improvement
1. Quality issue identification and root cause analysis
2. Cross-media quality optimization strategies and implementation
3. Performance improvement recommendations and action planning
4. Continuous quality monitoring and enhancement programs

### Level-Specific Execution

| Level | Capabilities |
|-------|-------------|
| L1 (Junior) | Basic quality assessment, template-based checking, cross-media monitoring, quality reporting |
| L2 (Senior) | Advanced assessment methodologies, custom evaluation frameworks, quality standard development, excellence leadership |
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Quality assurance platforms and testing frameworks
- Cross-media quality monitoring and analytics tools
- Brand management and consistency verification systems
- Performance testing and optimization platforms
- User testing and feedback collection systems
- Quality reporting and documentation tools
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### OUT Scope (Universal)
- Primary content creation and production
- Technical platform development and implementation
- Original media asset creation and design
- Software engineering and system architecture
- Platform infrastructure and technical operations

### Quality Assurance Constraints
- Quality assessment and evaluation only
- Cross-media consistency verification and optimization
- Performance monitoring and improvement recommendations
- Quality standard development and compliance enforcement
- Modern quality assurance best practices

### Mode-Specific Constraints

| Mode | Constraint |
|------|-----------|
| VISUAL_QA | Visual quality assessment only, no design creation |
| TEXT_QA | Text quality evaluation only, no content writing |
| INTERACTIVE_QA | Interactive quality testing only, no UX design |
| VIDEO_QA | Video quality assessment only, no production |
| UNIFIED_QA | Combined constraints with enhanced scope protection |

### Quality & Standards Constraints
- Quality standards compliance and best practices
- Cross-media consistency and brand alignment
- User experience and accessibility standards
- Ethical quality assessment and cultural sensitivity
- Continuous improvement and excellence standards
<!-- END_BLOCK -->
