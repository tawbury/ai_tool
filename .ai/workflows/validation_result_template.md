# Validation Result Template

**Purpose**: Minimal validation result recording for run_record.md integration

---

## Validation Result YAML Format

```yaml
validation_result:
  workflow: "code_quality_validation"
  timestamp: "2026-01-25T14:41:00Z"
  session_id: "session_001"
  
  # Skills Validated (minimal info)
  skills_checked:
    - "code_quality_and_technical_debt_analysis.skill.md"
    - "dev_code_review.skill.md"
    - "dev_backend.skill.md"
    - "dev_frontend_stack_unified.skill.md"
  
  # Validation Summary
  summary:
    total_skills: 4
    passed: 4
    failed: 0
    overall_status: "SUCCESS"
  
  # Critical Issues Only
  critical_issues: []
  
  # Quality Metrics (aggregated)
  quality_metrics:
    hard_coding_detection_rate: 98
    configuration_externalization: 96
    path_management: 100
    overall_score: 98
  
  # Action Required (minimal)
  next_actions:
    - status: "COMPLETED"
      description: "All validation checks passed"
  
  # Document References (minimal)
  documents_updated:
    - type: "run_record"
      id: "run_record_001"
      action: "validation_recorded"
```

## Run Record Integration

### Minimal Recording Pattern
```markdown
## Validation Results
- **Workflow**: code_quality_validation
- **Status**: SUCCESS
- **Skills Checked**: 4/4 passed
- **Quality Score**: 98%
- **Critical Issues**: 0
- **Next**: Proceed with development
```

### Success Case (No Detailed Report)
```yaml
validation_complete:
  status: "SUCCESS"
  summary: "All 4 skills passed validation with 98% quality score"
  detailed_report: "SKIPPED" # No document proliferation
```

### Failure Case (Minimal Detail)
```yaml
validation_complete:
  status: "FAILURE"
  summary: "2 skills failed validation"
  critical_issues:
    - skill: "dev_backend.skill.md"
      issue: "Hard coding violations detected"
  detailed_report: "GENERATED" # Only on failure
```

## Operational Loop Compliance

### Context Loading Rules
```python
def load_workflow_context(workflow_name, session_id):
    """Load only relevant context for current session"""
    
    # Load current session run_record
    current_run_record = load_run_record(session_id)
    
    # Load workflow definition (only this workflow)
    workflow_def = load_workflow(workflow_name)
    
    # Load only skills mentioned in current execution
    required_skills = extract_skills_from_run_record(current_run_record)
    skill_files = {skill: load_skill(skill) for skill in required_skills}
    
    return {
        'workflow': workflow_def,
        'run_record': current_run_record,
        'skills': skill_files
        # No other documents loaded
    }
```

### Memory Optimization
- **Session-based loading**: Only current session documents
- **On-demand skill loading**: Load skills only when referenced
- **Minimal result recording**: YAML format in run_record only
- **Success path optimization**: Skip detailed report generation

## Quality Gates

### Pass/Fail Criteria
```yaml
quality_gates:
  pass_criteria:
    overall_score: ">= 70"
    critical_issues: 0
    hard_coding_detection: ">= 95%"
  
  fail_actions:
    - generate_detailed_report
    - create_improvement_plan
    - block_deployment
  
  pass_actions:
    - record_validation_only
    - proceed_with_workflow
    - skip_detailed_reporting
```

## Integration Points

### Workflow Integration
```yaml
workflow_step:
  name: "validation"
  type: "self_validating"
  template: "validation_result_template.md"
  recording: "run_record_only"
  detailed_report: "on_failure_only"
```

### Agent Integration
```python
def agent_validation_step(agent, skills):
    """Agent performs validation with minimal recording"""
    
    results = []
    for skill in skills:
        # Self-validation (built-in)
        validation = skill.self_validate()
        results.append(validation)
    
    # Aggregate results
    summary = aggregate_validation_results(results)
    
    # Record in run_record only
    record_validation_in_run_record(summary)
    
    # Return minimal result
    return {
        'status': summary['overall_status'],
        'score': summary['overall_score'],
        'proceed': summary['overall_status'] == 'SUCCESS'
    }
```

## Benefits

1. **Reduced Document Proliferation**: Only run_record updates on success
2. **Faster Execution**: Minimal context loading
3. **Memory Efficiency**: Session-based document management
4. **Operational Compliance**: Strict adherence to workflow loop
5. **Scalability**: Handles 20+ workflows without document bloat
