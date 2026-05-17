# Base Mapping Template
 
## Purpose
Derived from base_template.md - AI context routing and mapping reference.
 
## Template Category Mapping
 
### Document Types → Applicable Agents
- **Planning Documents**: Architecture agents, Planning agents, PM agents
- **Execution Documents**: Task agents, Execution agents, Developer agents
- **Management Documents**: Workflow agents, Management agents, Senior agents
 
### Template Categories → Relevant Skills
- **Anchor**: Vision definition, Goal setting, Strategic planning, Business analysis
- **PRD**: Requirements analysis, User story mapping, Market research, Product management
- **Architecture**: System design, Technical specification, Infrastructure planning, Security design
- **Task**: Execution planning, Resource allocation, HR evaluation, Role definition
- **Run Record**: Result tracking, Performance analysis, Evidence documentation, Quality assurance
- **Decision**: Option evaluation, Impact assessment, Risk analysis, Stakeholder management
- **Roadmap**: Timeline planning, Milestone tracking, Progress monitoring, Strategic alignment
- **Workflow**: Process optimization, Automation design, Efficiency improvement, Standardization

## Document Type → Agent Mapping Matrix

| Document Type | Primary Agent | Secondary Agent | Reviewer Agent | Context Source |
|--------------|---------------|-----------------|----------------|----------------|
| **ANCHOR** | PM Agent | Senior PM | Senior PM | Business requirements |
| **PRD** | PM Agent | Product Manager | Senior PM | Anchor document |
| **ARCHITECTURE** | Developer Agent | Architect Agent | Senior Developer | PRD, Anchor |
| **SPECIFICATION** | Developer Agent | Tech Lead | Senior Developer | Architecture |
| **TASK** | HR Agent | Team Lead | Senior Agent | Roadmap, Planning docs |
| **RUN_RECORD** | Execution Agent | Any Agent | Senior Agent | Task document |
| **DECISION** | Decision Agent | Domain Expert | Senior Agent | Architecture, Requirements |
| **ROADMAP** | PM Agent | Planning Agent | Senior PM | Anchor, Business goals |
| **WORKFLOW** | Workflow Agent | Process Owner | Senior Agent | Business requirements |
| **REPORT** | Domain Agent | Analyst | Senior Agent | Source documents |

## Template Category → Skill Mapping Matrix

| Template | Core Skills | Supporting Skills | Validation Skills | Actual Skill Files |
|----------|-------------|-------------------|-------------------|-------------------|
| **Anchor** | strategic_planning, vision_definition, business_analysis | market_research, stakeholder_management | feasibility_analysis, risk_assessment | [[pm_strategy_unified.skill.md]], [[stakeholder_management.skill.md]], [[market_research.skill.md]] |
| **PRD** | requirements_analysis, user_story_mapping, product_management | market_research, competitive_analysis | requirement_validation, acceptance_criteria | [[pm_requirement_definition.skill.md]], [[pm_analytics_unified.skill.md]], [[user_research.skill.md]] |
| **Architecture** | system_design, technical_specification, infrastructure_planning | security_design, scalability_planning, performance_optimization | architecture_review, security_audit | [[dev_system_architecture.skill.md]], [[dev_api_design.skill.md]], [[dev_security.skill.md]] |
| **Task** | execution_planning, resource_allocation, role_definition | hr_evaluation, capability_assessment, timeline_estimation | task_validation, resource_verification | [[operational_roadmap_management.skill.md]], [[hr_level_check.skill.md]] |
| **Run Record** | result_tracking, performance_analysis, evidence_documentation | quality_assurance, metrics_collection, reporting | result_validation, evidence_verification | [[operational_run_record_creation.skill.md]], [[analytics_framework.skill.md]] |
| **Decision** | option_evaluation, impact_assessment, decision_analysis | risk_analysis, stakeholder_consultation, cost_benefit_analysis | decision_validation, consensus_check | [[financial_risk_assessment.skill.md]], [[pm_strategy_unified.skill.md]] |
| **Roadmap** | timeline_planning, milestone_tracking, progress_monitoring | dependency_management, resource_planning, risk_mitigation | roadmap_validation, feasibility_check | [[operational_roadmap_management.skill.md]], [[pm_analytics_unified.skill.md]] |
| **Workflow** | process_optimization, automation_design, efficiency_improvement | standardization, documentation, training_materials | workflow_validation, efficiency_measurement | [[dev_devops_unified.skill.md]], [[optimization_framework.skill.md]] |
| **Report** | data_analysis, synthesis, communication | visualization, presentation, executive_summary | report_validation, accuracy_check | [[analytics_framework.skill.md]], [[financial_reporting.skill.md]] |

## Context Routing Rules

### Primary Context Flow
1. **Anchor** → All project documents (provides vision and business context)
2. **PRD** → Architecture, Specification (provides requirements context)
3. **Architecture** → Specification, Task (provides technical context)
4. **Roadmap** → Task, Run Record (provides planning context)
5. **Task** → Run Record (provides execution context)
6. **Decision** → All affected documents (provides decision context)

### Agent Collaboration Patterns

#### Planning Phase Collaboration
```
PM Agent (Anchor) → PM Agent (PRD) → Developer Agent (Architecture) → Developer Agent (Spec)
     ↓                      ↓                      ↓                      ↓
Senior PM (Review)    Senior PM (Review)    Senior Developer (Review)  Senior Developer (Review)
```

#### Execution Phase Collaboration
```
PM Agent (Roadmap) → HR Agent (Task) → Execution Agent (Run Record) → Decision Agent (Decision)
       ↓                   ↓                    ↓                         ↓
   Senior PM          Senior Agent         Senior Agent              Senior Agent
```

#### Review and Validation Flow
```
Document Author → Peer Review → Senior Review → Final Approval
       ↓               ↓              ↓              ↓
   Self-check     Domain Expert   Senior Agent   System Validation
```

## Skill Priority Matrix

### High Priority Skills (Core Competencies)
- **strategic_planning**: Anchor, Roadmap
- **requirements_analysis**: PRD, Specification
- **system_design**: Architecture, Workflow
- **execution_planning**: Task, Run Record
- **decision_analysis**: Decision, Report

### Medium Priority Skills (Supporting Competencies)
- **risk_assessment**: All documents
- **stakeholder_management**: Anchor, Decision, Roadmap
- **quality_assurance**: Run Record, Report, Specification
- **documentation**: All documents
- **communication**: All documents

### Context-Dependent Skills
- **technical_expertise**: Architecture, Specification
- **business_acumen**: Anchor, PRD, Roadmap
- **hr_management**: Task, Run Record
- **process_optimization**: Workflow, Run Record

## Template Usage Patterns

### Sequential Usage Patterns
1. **Project Initiation**: Anchor → PRD → Architecture → Specification
2. **Execution Planning**: Roadmap → Task → Run Record
3. **Decision Making**: Decision → (updates) → Related documents
4. **Process Improvement**: Workflow → (optimizes) → All templates

### Iterative Usage Patterns
1. **Agile Development**: Task → Run Record → (feedback) → Roadmap → Task
2. **Continuous Improvement**: Run Record → Decision → (updates) → Architecture/Spec
3. **Strategic Alignment**: Anchor → (periodic review) → Roadmap → Task

## Integration Points

### Workflow System Integration
- **Operational Loop**: Roadmap ↔ Task ↔ Run Record ↔ Decision
- **Planning Cycle**: Anchor → PRD → Architecture → Spec → Task
- **Review Cycle**: All documents → Senior Review → Validation → Approval

### Agent System Integration
- **Junior Agents**: Document creation, initial content, self-review
- **Senior Agents**: Review, validation, approval, mentoring
- **Specialized Agents**: Domain-specific content, technical validation

### Quality System Integration
- **Template Validation**: base_schema.md compliance checking
- **Content Validation**: Domain-specific quality standards
- **Link Validation**: Document relationship integrity

## Performance Optimization

### Context Loading Strategy
- **Just-in-Time Loading**: Load only relevant templates for current task
- **Context Caching**: Cache frequently used template combinations
- **Selective Loading**: Load base templates first, then specific templates

### Memory Optimization
- **Template Inheritance**: Share common base structure
- **Lazy Loading**: Load detailed content only when needed
- **Context Pruning**: Remove unused context after task completion

## Monitoring and Metrics

### Template Usage Metrics
- Document creation frequency by type
- Agent collaboration patterns
- Review cycle times
- Error rates and types

### Quality Metrics
- Template compliance rates
- Link integrity scores
- Review approval rates
- Document reuse frequency

## Version History
- **v1.0**: Basic agent-skill mapping matrix
- **v1.1**: Context routing rules and collaboration patterns
- **v1.2**: Performance optimization and monitoring metrics
- **v1.3**: Integration points and usage patterns
