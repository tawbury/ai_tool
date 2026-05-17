---
name: Strategic Planning
type: skill
id: SKILL-STRATEGIC-PLANNING-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [hr, pm, contents-creator, finance]
tools: [claude-code, codex, gemini-cli]
---

# Strategic Planning Skill

---

## Purpose

This skill enables agents to perform comprehensive strategic planning across business domains. It provides frameworks for vision definition, goal setting, market analysis, and long-term planning with measurable outcomes and clear execution pathways.

---

## When to Use / When NOT to Use

**When to Use:**
- Creating Anchor documents with strategic vision
- Developing long-term business strategies
- Setting organizational goals and objectives
- Market positioning and competitive strategy development
- Strategic roadmap creation and alignment

**When NOT to Use:**
- For tactical execution planning (use operational skills instead)
- For detailed technical implementation (use architecture skills)
- For day-to-day task management (use task management skills)

---

## Inputs (Contract)

### Required Inputs
- **Business Context**: Current business situation, challenges, opportunities
- **Stakeholder Requirements**: Key stakeholder needs and expectations
- **Resource Constraints**: Available resources, budget, timeline limitations
- **Market Analysis**: Market trends, competitive landscape, customer insights

### Optional Inputs
- **Historical Data**: Past performance, lessons learned
- **Regulatory Environment**: Legal and compliance requirements
- **Technology Trends**: Emerging technologies and their impact
- **Risk Assessment**: Identified risks and mitigation strategies

### Input Format
```
Business Context: [Current situation description]
Stakeholder Requirements: [Key stakeholder needs]
Resource Constraints: [Budget, timeline, resource limitations]
Market Analysis: [Market trends and competitive landscape]
```

### Preconditions
- Clear understanding of business domain and context
- Access to relevant market and stakeholder information
- Defined planning horizon (short-term, mid-term, long-term)
- Authority to influence strategic direction

---

## Outputs (Contract)

### Guaranteed Outputs
- **Strategic Vision**: Clear, inspiring vision statement
- **Strategic Goals**: SMART goals aligned with vision
- **Strategic Initiatives**: Key initiatives to achieve goals
- **Success Metrics**: Measurable indicators of success
- **Implementation Roadmap**: High-level implementation timeline

### Optional Outputs
- **Risk Mitigation Plan**: Strategies to address identified risks
- **Resource Allocation Plan**: How resources will be allocated
- **Stakeholder Communication Plan**: How to engage stakeholders
- **Performance Monitoring Framework**: How to track progress

### Output Format
```markdown
## Strategic Vision
[Clear, compelling vision statement]

## Strategic Goals
- **Goal 1**: [SMART goal description]
- **Goal 2**: [SMART goal description]

## Strategic Initiatives
- **Initiative 1**: [Description, timeline, responsible party]
- **Initiative 2**: [Description, timeline, responsible party]

## Success Metrics
- **Metric 1**: [KPI, target, measurement method]
- **Metric 2**: [KPI, target, measurement method]

## Implementation Roadmap
[High-level timeline with key milestones]
```

---

## Core Logic

### Strategic Planning Process
1. **Situation Analysis**: Assess current state and context
2. **Vision Definition**: Create compelling future vision
3. **Goal Setting**: Define SMART strategic goals
4. **Initiative Identification**: Identify key strategic initiatives
5. **Resource Planning**: Allocate resources to initiatives
6. **Risk Assessment**: Identify and mitigate strategic risks
7. **Implementation Planning**: Create high-level implementation roadmap

### Decision Framework
- **Vision-Goal Alignment**: Ensure all goals support the vision
- **Resource-Initiative Fit**: Match resources to initiative requirements
- **Risk-Reward Balance**: Evaluate risk vs. potential reward
- **Stakeholder Value**: Ensure stakeholder needs are addressed

---

## Quality Standards

### Strategic Planning Quality Criteria
- **Vision Clarity**: Vision is clear, inspiring, and actionable
- **Goal Specificity**: Goals are specific, measurable, and time-bound
- **Initiative Feasibility**: Initiatives are realistic and achievable
- **Resource Adequacy**: Resources are sufficient for implementation
- **Risk Coverage**: Major risks are identified and addressed

### Validation Checklist
- [ ] Vision statement is clear and inspiring
- [ ] Goals follow SMART criteria
- [ ] Initiatives are directly linked to goals
- [ ] Success metrics are defined and measurable
- [ ] Implementation timeline is realistic
- [ ] Resource requirements are clearly defined
- [ ] Major risks are identified with mitigation plans

---

## Error Handling

### Common Strategic Planning Errors
1. **Vague Vision**: Vision too general or uninspiring
2. **Unrealistic Goals**: Goals not achievable with available resources
3. **Poor Initiative Selection**: Initiatives don't align with goals
4. **Inadequate Risk Assessment**: Missing critical risks
5. **Insufficient Stakeholder Consideration**: Ignoring key stakeholder needs

### Recovery Strategies
- **Vision Refinement**: Use stakeholder feedback to clarify vision
- **Goal Adjustment**: Revise goals based on resource constraints
- **Initiative Re-prioritization**: Reorder initiatives based on impact and feasibility
- **Risk Mitigation**: Develop contingency plans for critical risks

---

## Integration Points

### Framework Reference
This skill extends: `.ai/skills/_shared/research_framework.skill.md` (for market analysis)

### Related Skills
- `.ai/skills/pm/stakeholder_management.skill.md`: For stakeholder engagement
- `.ai/skills/finance/financial_risk_assessment.skill.md`: For comprehensive risk analysis

### Template Integration
- **Anchor Template** (`.ai/templates/anchor_template.md`): Strategic planning provides core content for Anchor documents
- **Roadmap Template** (`.ai/templates/roadmap_template.md`): Strategic initiatives inform roadmap development
- **Decision Template** (`.ai/templates/decision_template.md`): Strategic decisions use this skill's framework

---

## Performance Metrics

### Skill Effectiveness Metrics
- **Strategic Clarity Score**: Measured by stakeholder understanding
- **Goal Achievement Rate**: Percentage of strategic goals achieved
- **Implementation Success**: Rate of successful initiative execution
- **Stakeholder Satisfaction**: Stakeholder feedback on strategic direction

### Continuous Improvement
- **Strategy Review Cycles**: Regular strategy assessment and adjustment
- **Learning Integration**: Incorporate lessons learned into future planning
- **Best Practice Documentation**: Capture and share successful approaches

---

## Version History
- **v1.0**: Initial strategic planning framework
- **v1.1**: Added stakeholder management integration
- **v1.2**: Enhanced risk assessment and mitigation planning
- **v1.3**: Improved quality standards and validation checklist
