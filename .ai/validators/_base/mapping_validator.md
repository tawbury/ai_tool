# AI System Mapping Validator

## Purpose
Comprehensive mapping validation system for the entire .ai ecosystem. Ensures all references between agents, skills, workflows, templates, and validators are accurate and up-to-date.

---

## Validation Categories

### 1. Skill Reference Validation
Validates that all skill references point to existing files.

#### Check Points
- [ ] All `.skill.md` files referenced in agents exist
- [ ] All `.skill.md` files referenced in workflows exist  
- [ ] All `.skill.md` files referenced in validators exist
- [ ] Skill index includes all actual skill files

### 2. Agent Reference Validation
Validates that all agent references point to existing files.

#### Check Points
- [ ] All `.agent.md` files referenced in workflows exist
- [ ] All `.agent.md` files referenced in validators exist
- [ ] Agent skill references are valid

### 3. Template Reference Validation
Validates that all template references point to existing files.

#### Check Points
- [ ] All `.template.md` files referenced in workflows exist
- [ ] All `.template.md` files referenced in validators exist
- [ ] Template inheritance chains are valid

### 4. Workflow Reference Validation
Validates that all workflow references point to existing files.

#### Check Points
- [ ] All `.workflow.md` files referenced in indexes exist
- [ ] Workflow skill/agent/template references are valid
- [ ] Workflow inheritance chains are valid

### 5. Validator Reference Validation
Validates that all validator references point to existing files.

#### Check Points
- [ ] All `.validator.md` files referenced in indexes exist
- [ ] Validator skill/template references are valid
- [ ] Validator inheritance chains are valid

---

## Current Mapping Status

### ✅ Fixed Issues
1. **Skill Index Updated**: Added 5 new shared skills to skill_index.md
2. **Workflow References Updated**: Fixed skill paths in key workflows
3. **Agent Skills Updated**: Added core skill references to agent files
4. **HR Agent Enhanced**: Updated HR Agent with new shared skills and cross-agent assessment

### ⚠️ Remaining Issues

#### Validator Inconsistencies
- `pm_skill_validator.md`: References non-existent `pm_planning.skill.md`
- `hr_skill_validator.md`: References outdated HR skill structure
- `task_validator.md`: References outdated HR skill paths

#### Workflow Inconsistencies  
- `code_quality_validation.workflow.md`: References outdated skill paths
- `batch_update_workflow.md`: References skills that may have moved
- `validation_result_template.md`: Hardcoded skill references

### HR Integration Status (New)
- **HR Agent**: ✅ Updated with new shared skills and cross-agent assessment
- **Agent Registry**: ✅ Enhanced with skill mapping table
- **Workflow Integration**: ✅ HR evaluation workflow updated with new skills
- **Cross-Agent Assessment**: ✅ New flow for consistent evaluation across all agents

---

## Validation Results Summary

### Skills Mapping Status
| Category | Total | Valid | Invalid | Status |
|----------|-------|-------|---------|--------|
| Shared Skills | 7 | 7 | 0 | ✅ Complete |
| Agent Skills | 50+ | 45+ | 5+ | ⚠️ Needs Review |
| Framework Skills | 3 | 3 | 0 | ✅ Complete |

### Workflow Mapping Status  
| Category | Total | Valid | Invalid | Status |
|----------|-------|-------|---------|--------|
| Core Workflows | 10 | 8 | 2 | ⚠️ Needs Review |
| Domain Workflows | 5 | 5 | 0 | ✅ Complete |

### Validator Mapping Status
| Category | Total | Valid | Invalid | Status |
|----------|-------|-------|---------|--------|
| Document Validators | 12 | 10 | 2 | ⚠️ Needs Review |
| Skill Validators | 5 | 3 | 2 | ⚠️ Needs Review |

---

## Recommended Actions

### High Priority (Fix Immediately)
1. **Update PM Skill Validator**: Fix references to actual PM skills
2. **Update HR Skill Validator**: Align with current HR skill structure  
3. **Fix Code Quality Workflow**: Update skill references to current paths

### Medium Priority (Fix Soon)
1. **Update Task Validator**: Fix HR skill references
2. **Review Batch Update Workflow**: Validate skill references
3. **Update Validation Result Template**: Make skill references dynamic

### Low Priority (Nice to Have)
1. **Create Automated Validation Script**: Automated mapping validation
2. **Implement Link Checking**: Automated broken link detection
3. **Add Version Tracking**: Track mapping changes over time

---

## Validation Scripts

### Manual Validation Checklist
```bash
# Check skill references
find .ai -name "*.md" -exec grep -l "\.skill\.md" {} \; | xargs grep -h "\.skill\.md" | sort | uniq

# Check agent references  
find .ai -name "*.md" -exec grep -l "\.agent\.md" {} \; | xargs grep -h "\.agent\.md" | sort | uniq

# Check template references
find .ai -name "*.md" -exec grep -l "\.template\.md" {} \; | xargs grep -h "\.template\.md" | sort | uniq
```

### Automated Validation (Future)
```python
# mapping_validator.py - Future implementation
def validate_skill_references():
    # Validate all .skill.md references
    pass

def validate_agent_references():
    # Validate all .agent.md references  
    pass

def validate_template_references():
    # Validate all .template.md references
    pass
```

---

## Maintenance Procedures

### Weekly Validation
1. Run manual validation checklist
2. Update mapping status
3. Fix any new inconsistencies
4. Update this validator document

### Monthly Review
1. Comprehensive mapping audit
2. Update validation scripts
3. Review and improve validation procedures
4. Document mapping changes

### Release Validation
1. Full mapping validation before releases
2. Update all documentation
3. Test all critical paths
4. Validate backward compatibility

---

## Version History
- **v1.0**: Initial mapping validation framework
- **v1.1**: Fixed skill index and workflow references
- **v1.2**: Added comprehensive validation categories
- **v1.3**: Implemented status tracking and recommended actions
