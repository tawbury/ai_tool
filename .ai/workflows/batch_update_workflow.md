# Batch Update Workflow

**Purpose**: Systematic batch updates for rule changes across multiple skills

---

## Batch Update Process

### 1. Rule Change Impact Analysis
```python
def analyze_rule_change(rule_change_description):
    """Analyze impact of rule change and create update plan"""
    
    # Parse rule change
    rule_type = extract_rule_type(rule_change_description)
    affected_skills = identify_affected_skills(rule_type)
    
    # Create impact report
    impact_report = {
        'rule_change': rule_change_description,
        'rule_type': rule_type,
        'affected_skills': affected_skills,
        'update_priority': calculate_priority(rule_type),
        'estimated_effort': estimate_update_effort(affected_skills)
    }
    
    return impact_report
```

### 2. User Approval Process
```yaml
rule_change_proposal:
  description: "Add hard coding prevention to all developer skills"
  affected_skills:
    - code_quality_and_technical_debt_analysis.skill.md
    - dev_code_review.skill.md
    - dev_backend.skill.md
    - dev_frontend_stack_unified.skill.md
  estimated_time: "15 minutes"
  impact_level: "HIGH"
  
user_approval_required: true
approval_options:
  - "APPROVE_ALL" # Update all affected skills
  - "APPROVE_SELECTIVE" # Choose specific skills
  - "REJECT" # Cancel update
```

### 3. Batch Update Execution
```python
def execute_batch_update(approved_skills, rule_change):
    """Execute approved batch updates"""
    
    update_results = []
    
    for skill_file in approved_skills:
        try:
            # Load current skill
            skill = load_skill(skill_file)
            
            # Apply rule change
            updated_skill = apply_rule_change(skill, rule_change)
            
            # Validate updated skill
            validation = validate_skill(updated_skill)
            
            if validation['status'] == 'PASS':
                # Save updated skill
                save_skill(updated_skill)
                update_results.append({
                    'skill': skill_file,
                    'status': 'SUCCESS',
                    'validation': validation
                })
            else:
                update_results.append({
                    'skill': skill_file,
                    'status': 'FAILED_VALIDATION',
                    'errors': validation['errors']
                })
                
        except Exception as e:
            update_results.append({
                'skill': skill_file,
                'status': 'ERROR',
                'error': str(e)
            })
    
    return update_results
```

### 4. Rollback Capability
```python
def create_rollback_backup(skills_to_update):
    """Create backup before batch update"""
    
    backup = {
        'timestamp': datetime.now().isoformat(),
        'rule_change': current_rule_change,
        'backups': {}
    }
    
    for skill_file in skills_to_update:
        backup['backups'][skill_file] = {
            'content': read_file(skill_file),
            'checksum': calculate_checksum(read_file(skill_file))
        }
    
    # Save backup
    backup_file = f"backups/batch_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_backup(backup_file, backup)
    
    return backup_file

def rollback_update(backup_file):
    """Rollback batch update from backup"""
    
    backup = load_backup(backup_file)
    
    for skill_file, skill_backup in backup['backups'].items():
        # Verify checksum
        current_content = read_file(skill_file)
        if calculate_checksum(current_content) != skill_backup['checksum']:
            # Restore from backup
            write_file(skill_file, skill_backup['content'])
    
    return f"Rolled back {len(backup['backups'])} skills"
```

## Integration with Base Validator

### Base-First Update Strategy
```python
def base_first_update_strategy(rule_change):
    """Update base validator first, then propagate to skills"""
    
    # Step 1: Update base validator
    base_validator = load_base_validator()
    updated_base = apply_rule_to_base(base_validator, rule_change)
    
    # Validate base validator
    if validate_base_validator(updated_base)['status'] != 'PASS':
        return {'status': 'FAILED', 'reason': 'Base validator validation failed'}
    
    # Step 2: Save base validator
    save_base_validator(updated_base)
    
    # Step 3: Update all dependent skills
    dependent_skills = get_dependent_skills(updated_base)
    update_results = execute_batch_update(dependent_skills, rule_change)
    
    return {
        'status': 'COMPLETED',
        'base_updated': True,
        'skills_updated': len([r for r in update_results if r['status'] == 'SUCCESS']),
        'results': update_results
    }
```

## Quality Assurance

### Validation Gates
```yaml
batch_update_gates:
  pre_update:
    - validate_base_validator
    - create_rollback_backup
    - get_user_approval
  
  during_update:
    - validate_each_skill
    - check_dependencies
    - maintain_consistency
  
  post_update:
    - run_integration_tests
    - validate_workflow_compatibility
    - generate_update_report
```

### Success Criteria
- All base validator updates pass validation
- 95%+ of dependent skills update successfully
- No workflow integration failures
- Rollback capability maintained

## Usage Example

### Hard Coding Rule Update
```python
# User requests: "Add hard coding prevention to all developer skills"

# Step 1: Impact Analysis
impact = analyze_rule_change("Add hard coding prevention")
print(f"Will update {len(impact['affected_skills'])} skills")

# Step 2: User Approval
approval = get_user_approval(impact)
if approval['decision'] != 'APPROVE_ALL':
    return "Update cancelled by user"

# Step 3: Execute Update
results = base_first_update_strategy("hard_coding_prevention")
print(f"Updated {results['skills_updated']} skills successfully")

# Step 4: Validation
if results['status'] == 'COMPLETED':
    print("Batch update completed successfully")
else:
    print("Update failed, initiating rollback")
    rollback_update(last_backup_file)
```

## Benefits

1. **Single Source of Truth**: Base validator updates propagate automatically
2. **Consistency**: All skills follow same standards
3. **Safety**: Rollback capability for failed updates
4. **Efficiency**: Batch updates instead of individual modifications
5. **Transparency**: Impact analysis and user approval required
