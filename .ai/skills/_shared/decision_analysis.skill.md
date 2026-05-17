---
name: Decision Analysis
type: skill
id: SKILL-DECISION-ANALYSIS-v1
version: 2.2.0
updated: 2026-04-14
scope: shared
used_by: [hr, pm, developer, finance]
tools: [claude-code, codex, gemini-cli]
---

# Decision Analysis Skill

---

## Purpose

This skill enables agents to perform systematic decision analysis across various domains. It provides frameworks for evaluating alternatives, assessing impacts, managing risks, and making informed decisions with clear rationale and documentation.

---

## When to Use / When NOT to Use

**When to Use:**
- Creating Decision documents with comprehensive analysis
- Evaluating multiple alternatives for important decisions
- Assessing impacts and consequences of decisions
- Managing decision risks and uncertainties
- Documenting decision rationale and justification

**When NOT to Use:**
- For routine operational decisions (use operational procedures)
- For emergency decisions requiring immediate action
- For personal preference decisions without analysis requirements

---

## Inputs (Contract)

### Required Inputs
- **Decision Context**: Background and context for the decision
- **Decision Criteria**: Criteria for evaluating alternatives
- **Available Alternatives**: List of viable alternatives
- **Constraints and Limitations**: Decision constraints and limitations

### Optional Inputs
- **Stakeholder Input**: Input from relevant stakeholders
- **Risk Assessment**: Identified risks and their impacts
- **Cost-Benefit Analysis**: Financial and non-financial costs and benefits
- **Timeline Requirements**: Decision timeline and urgency

### Input Format
```
Decision Context: [Background and context for the decision]
Decision Criteria: [Criteria for evaluating alternatives]
Available Alternatives: [List of viable alternatives]
Constraints: [Decision constraints and limitations]
```

### Preconditions
- Clear understanding of decision context and requirements
- Defined decision criteria and evaluation framework
- Identified viable alternatives for consideration
- Authority or influence to make or recommend the decision

---

## Outputs (Contract)

### Guaranteed Outputs
- **Alternative Analysis**: Detailed analysis of each alternative
- **Impact Assessment**: Assessment of impacts and consequences
- **Risk Evaluation**: Evaluation of risks and mitigation strategies
- **Recommendation**: Recommended decision with clear rationale
- **Implementation Plan**: Plan for implementing the decision

### Optional Outputs
- **Sensitivity Analysis**: Analysis of how changes affect the decision
- **Stakeholder Analysis**: Analysis of stakeholder impacts and buy-in
- **Monitoring Plan**: Plan for monitoring decision outcomes
- **Contingency Plans**: Alternative approaches if primary decision fails

### Output Format
```markdown
## Alternative Analysis
- **Alternative 1**: [Description, pros, cons, evaluation against criteria]
- **Alternative 2**: [Description, pros, cons, evaluation against criteria]

## Impact Assessment
- **Positive Impacts**: [Expected positive outcomes]
- **Negative Impacts**: [Potential negative consequences]
- **Stakeholder Impacts**: [Impact on different stakeholders]

## Risk Evaluation
- **Risk 1**: [Description, probability, impact, mitigation]
- **Risk 2**: [Description, probability, impact, mitigation]

## Recommendation
- **Selected Alternative**: [Chosen alternative]
- **Rationale**: [Clear justification for the decision]
- **Expected Outcomes**: [Expected results and benefits]

## Implementation Plan
- **Implementation Steps**: [Step-by-step implementation approach]
- **Timeline**: [Implementation timeline and milestones]
- **Resources**: [Required resources and responsibilities]
```

---

## Core Logic

### Decision Analysis Process
1. **Problem Definition**: Clearly define the decision problem
2. **Criteria Establishment**: Define evaluation criteria and weights
3. **Alternative Generation**: Identify and generate viable alternatives
4. **Analysis**: Analyze alternatives against criteria
5. **Impact Assessment**: Assess impacts and consequences
6. **Risk Evaluation**: Evaluate risks and mitigation strategies
7. **Recommendation**: Make recommendation with clear rationale
8. **Implementation Planning**: Plan for decision implementation

### Decision Frameworks
- **Cost-Benefit Analysis**: Compare costs and benefits of alternatives
- **Risk-Reward Analysis**: Evaluate risk vs. potential reward
- **Multi-Criteria Decision Analysis**: Evaluate against multiple criteria
- **Scenario Analysis**: Evaluate alternatives under different scenarios

---

## Quality Standards

### Decision Analysis Quality Criteria
- **Comprehensiveness**: All relevant factors are considered
- **Objectivity**: Analysis is unbiased and evidence-based
- **Clarity**: Analysis is clear and understandable
- **Actionability**: Decision can be implemented effectively
- **Traceability**: Decision rationale is documented and traceable

### Validation Checklist
- [ ] Decision problem is clearly defined
- [ ] Evaluation criteria are appropriate and weighted
- [ ] All viable alternatives are considered
- [ ] Analysis is thorough and evidence-based
- [ ] Impacts and risks are properly assessed
- [ ] Recommendation is well-justified
- [ ] Implementation plan is realistic and actionable

---

## Error Handling

### Common Decision Analysis Errors
1. **Incomplete Alternatives**: Missing viable alternatives
2. **Biased Analysis**: Personal or organizational bias affecting analysis
3. **Poor Criteria**: Inappropriate or incomplete evaluation criteria
4. **Risk Oversights**: Missing or underestimating risks
5. **Implementation Issues**: Poor implementation planning

### Recovery Strategies
- **Alternative Generation**: Conduct systematic alternative generation
- **Bias Mitigation**: Use structured analysis techniques to reduce bias
- **Criteria Review**: Reassess and refine evaluation criteria
- **Risk Assessment**: Conduct comprehensive risk analysis
- **Implementation Planning**: Develop detailed implementation plans

---

## Integration Points

### Framework Reference
This skill extends: `.ai/skills/_shared/research_framework.skill.md` (for information gathering)

### Related Skills
- `.ai/skills/finance/financial_risk_assessment.skill.md`: For comprehensive risk analysis
- `.ai/skills/pm/stakeholder_management.skill.md`: For stakeholder analysis
- `.ai/skills/finance/financial_analysis.skill.md`: For cost-benefit analysis

### Template Integration
- **Decision Template** (`.ai/templates/decision_template.md`): Decision analysis provides core content for Decision documents

---

## Performance Metrics

### Skill Effectiveness Metrics
- **Decision Quality**: Measured by outcomes and stakeholder satisfaction
- **Analysis Accuracy**: Accuracy of impact and risk predictions
- **Implementation Success**: Rate of successful decision implementation
- **Stakeholder Buy-in**: Level of stakeholder support for decisions

### Continuous Improvement
- **Decision Review**: Regular review of decision outcomes and processes
- **Lessons Learned**: Capture and apply lessons from decision outcomes
- **Best Practice Documentation**: Document and share successful decision approaches

---

## Version History
- **v1.0**: Initial decision analysis framework
- **v1.1**: Enhanced risk assessment and stakeholder analysis
- **v1.2**: Improved implementation planning and monitoring
- **v1.3**: Added performance metrics and continuous improvement
