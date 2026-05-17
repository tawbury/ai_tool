---
name: Execution Planning
type: skill
id: SKILL-EXECUTION-PLANNING-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [hr, pm, developer]
tools: [claude-code, codex, gemini-cli]
---

# Execution Planning Skill

---

## Purpose

This skill enables agents to create detailed execution plans for tasks and projects. It provides frameworks for breaking down work into manageable units, estimating resources, defining timelines, and establishing success criteria with clear accountability and measurement.

---

## When to Use / When NOT to Use

**When to Use:**
- Creating Task documents with detailed execution plans
- Planning project execution phases and milestones
- Defining resource requirements and allocations
- Establishing timelines and dependencies
- Setting success criteria and measurement approaches

**When NOT to Use:**
- For strategic planning (use strategic planning skills)
- For detailed technical implementation (use development skills)
- For high-level roadmap creation (use roadmap management skills)

---

## Inputs (Contract)

### Required Inputs
- **Task Definition**: Clear description of work to be performed
- **Objectives**: Specific objectives and success criteria
- **Constraints**: Time, budget, resource constraints
- **Dependencies**: Task dependencies and prerequisites

### Optional Inputs
- **Resource Availability**: Available resources and skills
- **Risk Assessment**: Identified risks and mitigation strategies
- **Quality Standards**: Quality requirements and standards
- **Stakeholder Requirements**: Stakeholder expectations and requirements

### Input Format
```
Task Definition: [Clear description of work to be performed]
Objectives: [Specific objectives and success criteria]
Constraints: [Time, budget, resource limitations]
Dependencies: [Task dependencies and prerequisites]
```

### Preconditions
- Clear understanding of task scope and objectives
- Knowledge of available resources and constraints
- Understanding of dependencies and prerequisites
- Authority to influence execution planning

---

## Outputs (Contract)

### Guaranteed Outputs
- **Execution Plan**: Detailed step-by-step execution plan
- **Resource Requirements**: Specific resource needs and allocations
- **Timeline**: Detailed timeline with milestones and dependencies
- **Success Criteria**: Measurable criteria for success
- **Risk Mitigation**: Strategies to address identified risks

### Optional Outputs
- **Quality Plan**: Quality assurance and control measures
- **Communication Plan**: Stakeholder communication approach
- **Contingency Plans**: Alternative approaches for potential issues
- **Performance Metrics**: Metrics to track execution progress

### Output Format
```markdown
## Execution Plan
- **Step 1**: [Description, duration, resources, dependencies]
- **Step 2**: [Description, duration, resources, dependencies]

## Resource Requirements
- **Human Resources**: [Skills, roles, time commitment]
- **Technical Resources**: [Tools, equipment, software]
- **Financial Resources**: [Budget allocation and timing]

## Timeline
- **Milestone 1**: [Date, deliverables, dependencies]
- **Milestone 2**: [Date, deliverables, dependencies]

## Success Criteria
- **Criterion 1**: [Measurable success indicator]
- **Criterion 2**: [Measurable success indicator]

## Risk Mitigation
- **Risk 1**: [Description, probability, impact, mitigation]
- **Risk 2**: [Description, probability, impact, mitigation]
```

---

## Core Logic

### Execution Planning Process
1. **Task Decomposition**: Break down task into manageable components
2. **Resource Planning**: Identify and allocate required resources
3. **Timeline Development**: Create detailed timeline with milestones
4. **Dependency Analysis**: Identify and manage task dependencies
5. **Risk Assessment**: Identify risks and develop mitigation strategies
6. **Success Definition**: Define measurable success criteria
7. **Quality Planning**: Establish quality standards and controls

### Planning Principles
- **SMART Goals**: Ensure objectives are Specific, Measurable, Achievable, Relevant, Time-bound
- **Resource Optimization**: Optimize resource allocation and utilization
- **Risk Management**: Proactively identify and mitigate risks
- **Stakeholder Alignment**: Ensure stakeholder requirements are addressed
- **Continuous Monitoring**: Plan for ongoing progress monitoring

---

## Quality Standards

### Execution Plan Quality Criteria
- **Completeness**: All aspects of execution are planned
- **Feasibility**: Plan is realistic and achievable
- **Clarity**: Plan is clear and understandable
- **Measurability**: Success can be measured objectively
- **Flexibility**: Plan can adapt to changes and uncertainties

### Validation Checklist
- [ ] Task is properly decomposed into manageable steps
- [ ] Resource requirements are clearly defined
- [ ] Timeline is realistic and accounts for dependencies
- [ ] Success criteria are measurable and achievable
- [ ] Risks are identified with mitigation strategies
- [ ] Quality standards are defined and measurable
- [ ] Stakeholder requirements are addressed

---

## Error Handling

### Common Execution Planning Errors
1. **Unrealistic Timelines**: Underestimating time requirements
2. **Resource Shortages**: Underestimating resource needs
3. **Dependency Oversights**: Missing critical dependencies
4. **Risk Neglect**: Ignoring potential risks and issues
5. **Poor Success Criteria**: Vague or unmeasurable success criteria

### Recovery Strategies
- **Timeline Adjustment**: Reassess and adjust timelines based on realistic estimates
- **Resource Reallocation**: Reallocate resources based on priority and availability
- **Dependency Analysis**: Conduct thorough dependency analysis and planning
- **Risk Management**: Implement comprehensive risk assessment and mitigation
- **Success Criteria Refinement**: Define clear, measurable success criteria

---

## Integration Points

### Framework Reference
This skill extends: `.ai/skills/_shared/operational_roadmap_management.skill.md` (for task integration)

### Related Skills
- `.ai/skills/finance/financial_risk_assessment.skill.md`: For comprehensive risk analysis
- `.ai/skills/_shared/optimization_framework.skill.md`: For resource optimization

### Template Integration
- **Task Template** (`.ai/templates/task_template.md`): Execution planning provides core content for Task documents
- **Run Record Template** (`.ai/templates/run_record_template.md`): Execution plans inform run record creation

---

## Performance Metrics

### Skill Effectiveness Metrics
- **Plan Accuracy**: Difference between planned and actual execution
- **Resource Utilization**: Efficiency of resource allocation and use
- **Timeline Adherence**: Percentage of milestones completed on time
- **Success Achievement**: Rate of achieving defined success criteria

### Continuous Improvement
- **Plan Review Cycles**: Regular plan assessment and adjustment
- **Lessons Learned**: Capture and apply lessons from execution issues
- **Best Practice Documentation**: Document and share successful planning approaches

---

## Version History
- **v1.0**: Initial execution planning framework
- **v1.1**: Enhanced resource planning and optimization
- **v1.2**: Improved risk assessment and mitigation
- **v1.3**: Added performance metrics and continuous improvement
