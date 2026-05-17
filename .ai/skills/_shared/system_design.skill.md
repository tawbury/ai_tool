---
name: System Design
type: skill
id: SKILL-SYSTEM-DESIGN-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [developer, pm]
tools: [claude-code, codex, gemini-cli]
---

# System Design Skill

---

## Purpose

This skill enables agents to perform comprehensive system design across various domains. It provides frameworks for architectural design, component specification, interface definition, and system integration with focus on scalability, reliability, and maintainability.

---

## When to Use / When NOT to Use

**When to Use:**
- Creating Architecture documents with system design
- Translating requirements into technical architecture
- Designing system components and their interactions
- Defining interfaces and integration points
- Planning system scalability and performance

**When NOT to Use:**
- For detailed implementation code (use development skills)
- For project scheduling and planning (use planning skills)
- For user interface design (use design skills)

---

## Inputs (Contract)

### Required Inputs
- **Functional Requirements**: Detailed functional requirement specifications
- **Non-Functional Requirements**: Performance, security, scalability requirements
- **Technical Constraints**: Technology stack, platform limitations
- **Integration Requirements**: External system integration needs

### Optional Inputs
- **Existing Architecture**: Current system architecture documentation
- **Business Constraints**: Budget, timeline, resource limitations
- **Regulatory Requirements**: Compliance and security requirements
- **Performance Benchmarks**: Expected performance targets

### Input Format
```
Functional Requirements: [Detailed functional specifications]
Non-Functional Requirements: [Performance, security, scalability needs]
Technical Constraints: [Technology stack and limitations]
Integration Requirements: [External system integration needs]
```

### Preconditions
- Clear understanding of functional and non-functional requirements
- Knowledge of available technology stack and constraints
- Understanding of integration requirements and interfaces
- Authority to influence technical decisions

---

## Outputs (Contract)

### Guaranteed Outputs
- **System Architecture**: High-level system architecture design
- **Component Design**: Detailed component specifications
- **Interface Definitions**: API and interface specifications
- **Data Model**: Database schema and data flow design
- **Integration Plan**: System integration approach and strategy

### Optional Outputs
- **Performance Analysis**: Performance modeling and predictions
- **Security Design**: Security architecture and controls
- **Scalability Plan**: Scalability strategies and approaches
- **Deployment Architecture**: Deployment and infrastructure design

### Output Format
```markdown
## System Architecture
[High-level architecture diagram and description]

## Component Design
- **Component 1**: [Description, responsibilities, interfaces]
- **Component 2**: [Description, responsibilities, interfaces]

## Interface Definitions
- **API-001**: [Endpoint, method, parameters, response]
- **API-002**: [Endpoint, method, parameters, response]

## Data Model
[Database schema and data flow diagrams]

## Integration Plan
[System integration approach and strategy]
```

---

## Core Logic

### System Design Process
1. **Requirement Analysis**: Analyze functional and non-functional requirements
2. **Architecture Design**: Create high-level system architecture
3. **Component Design**: Design system components and their responsibilities
4. **Interface Design**: Define interfaces between components
5. **Data Design**: Design data models and data flows
6. **Integration Design**: Plan system integration approach
7. **Quality Attribute Design**: Address performance, security, scalability

### Design Principles
- **Modularity**: Design components with clear boundaries and responsibilities
- **Scalability**: Design for horizontal and vertical scalability
- **Reliability**: Design for fault tolerance and high availability
- **Security**: Design with security principles and controls
- **Maintainability**: Design for ease of maintenance and evolution

---

## Quality Standards

### System Design Quality Criteria
- **Completeness**: All requirements are addressed in the design
- **Consistency**: Design is consistent across all components
- **Feasibility**: Design is technically and economically feasible
- **Scalability**: Design can handle expected growth and load
- **Maintainability**: Design is easy to understand and modify

### Validation Checklist
- [ ] All functional requirements are addressed
- [ ] Non-functional requirements are satisfied
- [ ] Component responsibilities are clearly defined
- [ ] Interfaces are well-defined and documented
- [ ] Data model supports all requirements
- [ ] Integration points are identified and planned
- [ ] Performance and scalability are considered

---

## Error Handling

### Common System Design Errors
1. **Over-Engineering**: Design that is more complex than needed
2. **Under-Engineering**: Design that doesn't meet requirements
3. **Poor Scalability**: Design that doesn't handle growth
4. **Security Oversights**: Missing security considerations
5. **Integration Issues**: Poor integration planning

### Recovery Strategies
- **Simplification**: Remove unnecessary complexity
- **Requirement Re-evaluation**: Reassess and prioritize requirements
- **Scalability Analysis**: Conduct scalability modeling and testing
- **Security Review**: Perform comprehensive security assessment
- **Integration Testing**: Plan and execute integration testing

---

## Integration Points

### Framework Reference
This skill extends: `.ai/skills/_shared/optimization_framework.skill.md` (for performance optimization)

### Related Skills
- `.ai/skills/developer/dev_api_design.skill.md`: For detailed API design
- `.ai/skills/developer/dev_database_design.skill.md`: For database design
- `.ai/skills/developer/dev_security.skill.md`: For security architecture

### Template Integration
- **Architecture Template** (`.ai/templates/architecture_template.md`): System design provides core content for Architecture documents
- **Specification Template** (`.ai/templates/spec_template.md`): Detailed design informs technical specifications

---

## Performance Metrics

### Skill Effectiveness Metrics
- **Design Quality Score**: Measured by completeness and consistency
- **Implementation Success**: Rate of successful design implementation
- **Performance Achievement**: Meeting performance requirements
- **Maintenance Efficiency**: Ease of system maintenance and updates

### Continuous Improvement
- **Design Review Cycles**: Regular design quality assessments
- **Architecture Evolution**: Continuous architecture improvement
- **Best Practice Documentation**: Document and share successful design patterns

---

## Version History
- **v1.0**: Initial system design framework
- **v1.1**: Enhanced security and scalability considerations
- **v1.2**: Improved integration design and validation
- **v1.3**: Added performance metrics and continuous improvement
