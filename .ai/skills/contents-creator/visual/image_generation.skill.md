---
name: Image Generation
type: skill
id: SKILL-CC-IMAGE-GEN-v1
version: 2.2.0
updated: 2026-04-14
scope: contents-creator
used_by: [contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Image Generation Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Visual images/graphics creation from concepts/requirements/specs with shared framework integration
- Ideas/visual concepts → actual image assets transformation
- Visual creation, concept interpretation, image production
- **Integration**: Leverages contents_creation_framework for universal visual principles and quality_assurance_framework for image quality standards
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
- Image generation requirements & creative briefs
- Visual concepts & ideas & brand specifications
- Style & atmosphere specifications & technical constraints
- Target platform requirements & format specifications

### Output
- Generated image assets with quality validation
- Image formats & resolutions with optimization
- Generation logs & metadata with version control
- Revision suggestions & improvement recommendations
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Framework Integration

This skill integrates with the following shared frameworks:

| Framework | Path |
|-----------|------|
| Contents Creation | `.ai/skills/_shared/contents_creator_frameworks/contents_creation_framework.skill.md` |
| Quality Assurance | `.ai/skills/_shared/contents_creator_frameworks/quality_assurance_framework.skill.md` |
| Media Integration | `.ai/skills/_shared/contents_creator_frameworks/media_integration_framework.skill.md` |

### Enhanced Image Generation Pipeline
1. Analyze requirements & interpret visual concepts
2. Specify style & atmosphere requirements
3. Integrate shared framework principles for consistency
4. Implement quality assurance standards for image excellence
5. Apply cross-media integration strategies for visual coherence
6. Generate image deliverables with quality validation
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Image generation platforms & AI tools (Midjourney, DALL-E, Stable Diffusion)
- Image editing software & design tools (Adobe Photoshop, Figma)
- Quality assurance platforms & image testing tools
- Cross-media integration & collaboration platforms
- Asset management systems & version control
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints
### Image Generation Scope
- Image generation & visual creation only
- Concept interpretation & visual asset production
- Cross-platform image adaptation & optimization
- Quality assurance integration for image excellence

### Framework Integration Constraints
- Leverage _shared/contents_creation_framework for universal principles
- Apply _shared/quality_assurance_framework for image quality standards
- Utilize _shared/media_integration_framework for cross-media consistency
- Maintain image generation specialization while benefiting from shared frameworks
<!-- END_BLOCK -->
