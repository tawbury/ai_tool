---
name: Requirements Analysis
type: skill
id: SKILL-REQUIREMENTS-ANALYSIS-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [hr, pm, developer, contents-creator]
tools: [claude-code, codex, gemini-cli]
---

# Requirements Analysis Skill

---

## Purpose

This skill enables agents to systematically analyze, document, and validate requirements across various domains. It provides frameworks for gathering stakeholder needs, translating business requirements into technical specifications, and ensuring requirement quality and traceability.

---

## When to Use / When NOT to Use

**When to Use:**
- Creating PRD documents with detailed requirements
- Translating business needs into technical specifications
- Analyzing user stories and functional requirements
- Validating requirement completeness and consistency
- Establishing requirement traceability

**When NOT to Use:**
- For technical implementation details (use architecture skills)
- For project scheduling and planning (use planning skills)
- For user interface design (use design skills)

---

## Inputs (Contract)

### Required Inputs
- **Business Requirements**: High-level business needs and objectives
- **Stakeholder Input**: Requirements from various stakeholders
- **Context Information**: Project context, constraints, and assumptions
- **Domain Knowledge**: Relevant domain-specific information

### Optional Inputs
- **Existing Requirements**: Previous requirement documentation
- **Technical Constraints**: Technical limitations and constraints
- **Regulatory Requirements**: Legal and compliance requirements
- **Market Research**: Market and user research data

### Input Format
```
Business Requirements: [High-level business needs]
Stakeholder Input: [Requirements from different stakeholders]
Context: [Project context and constraints]
Domain Knowledge: [Relevant domain information]
```

### Preconditions
- Clear understanding of business domain and objectives
- Access to stakeholder requirements and feedback
- Defined requirement scope and boundaries
- Authority to influence requirement definition

---

## Outputs (Contract)

### Guaranteed Outputs
- **Functional Requirements**: Detailed functional requirement specifications
- **Non-Functional Requirements**: Performance, security, usability requirements
- **User Stories**: User-centric requirement descriptions
- **Acceptance Criteria**: Clear criteria for requirement fulfillment
- **Requirement Traceability**: Links to business objectives and design elements

### Optional Outputs
- **Requirement Prioritization**: Prioritized requirement list
- **Risk Assessment**: Requirement-related risks and mitigations
- **Validation Plan**: How requirements will be validated
- **Change Management**: Requirement change process

### Output Format
```markdown
## Functional Requirements
- **FR-001**: [Requirement description]
- **FR-002**: [Requirement description]

## Non-Functional Requirements
- **NFR-001**: [Performance requirement]
- **NFR-002**: [Security requirement]

## User Stories
- **US-001**: As a [user], I want [functionality] so that [benefit]
- **US-002**: As a [user], I want [functionality] so that [benefit]

## Acceptance Criteria
- **AC-001**: [Specific acceptance criteria]
- **AC-002**: [Specific acceptance criteria]

## Requirement Traceability
[Matrix linking requirements to business objectives]
```

---

## Core Logic

### Requirements Analysis Process
1. **Requirement Elicitation**: Gather requirements from all stakeholders
2. **Requirement Classification**: Categorize requirements (functional, non-functional)
3. **Requirement Analysis**: Analyze for completeness, consistency, clarity
4. **Requirement Specification**: Document requirements in standard format
5. **Requirement Validation**: Validate requirements with stakeholders
6. **Requirement Prioritization**: Prioritize based on business value and feasibility
7. **Traceability Establishment**: Link requirements to business objectives

### Quality Assurance Framework
- **Completeness Check**: Ensure all requirements are captured
- **Consistency Check**: Ensure no contradictory requirements
- **Clarity Check**: Ensure requirements are unambiguous
- **Feasibility Check**: Ensure requirements are achievable
- **Testability Check**: Ensure requirements can be tested

---

## Quality Standards

### Requirements Quality Criteria
- **Completeness**: All necessary requirements are included
- **Consistency**: No contradictory or conflicting requirements
- **Clarity**: Requirements are unambiguous and understandable
- **Feasibility**: Requirements are technically and economically feasible
- **Testability**: Requirements can be verified through testing

### Validation Checklist
- [ ] All stakeholder requirements are captured
- [ ] Requirements are clearly and unambiguously stated
- [ ] Functional and non-functional requirements are separated
- [ ] Acceptance criteria are defined for each requirement
- [ ] Requirements are traceable to business objectives
- [ ] Requirements are prioritized based on business value
- [ ] Technical feasibility has been assessed

---

## Error Handling

### Common Requirements Analysis Errors
1. **Incomplete Requirements**: Missing stakeholder needs
2. **Ambiguous Requirements**: Unclear or vague requirement statements
3. **Conflicting Requirements**: Contradictory requirement specifications
4. **Unrealistic Requirements**: Technically or economically infeasible
5. **Poor Traceability**: Requirements not linked to business objectives

### Recovery Strategies
- **Stakeholder Review**: Conduct thorough stakeholder review sessions
- **Requirement Refinement**: Clarify and refine ambiguous requirements
- **Conflict Resolution**: Facilitate resolution of conflicting requirements
- **Feasibility Analysis**: Conduct technical and economic feasibility studies
- **Traceability Matrix**: Establish comprehensive requirement traceability

---

## Integration Points

### Framework Reference
This skill extends: `.ai/skills/_shared/research_framework.skill.md` (for stakeholder research)

### Related Skills
- `.ai/skills/pm/stakeholder_management.skill.md`: For stakeholder engagement
- `.ai/skills/_shared/system_design.skill.md`: For translating requirements to technical design

### Template Integration
- **PRD Template** (`.ai/templates/prd_template.md`): Requirements analysis provides core content for PRD documents
- **Specification Template** (`.ai/templates/spec_template.md`): Detailed requirements inform technical specifications

---

## Performance Metrics

### Skill Effectiveness Metrics
- **Requirement Quality Score**: Measured by completeness and consistency
- **Stakeholder Satisfaction**: Stakeholder feedback on requirement quality
- **Implementation Success**: Rate of successful requirement implementation
- **Change Request Rate**: Number of requirement changes after approval

### Continuous Improvement
- **Requirement Review Cycles**: Regular requirement quality assessments
- **Lessons Learned**: Capture and apply lessons from requirement issues
- **Best Practice Documentation**: Document and share successful approaches

---

## Version History
- **v1.0**: Initial requirements analysis framework
- **v1.1**: Enhanced stakeholder management integration
- **v1.2**: Improved requirement traceability and validation
- **v1.3**: Added quality metrics and continuous improvement
