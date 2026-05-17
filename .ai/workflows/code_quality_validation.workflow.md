# Meta
- Workflow Name: Code Quality Validation Workflow
- File Name: code_quality_validation.workflow.md
- Document ID: WF-CODEQUALITY-001
- Status: Active
- Created Date: 2026-01-25
- Last Updated: 2026-01-25
- Author: AI System
- Parent Document: .ai/workflows/README.md
- Related Reference: .ai/templates/anchor_template.md
- Version: 1.0.0

---

# Code Quality Validation Workflow

## Purpose
Workflow for systematic validation of code quality, hard coding prevention, and path management standards using modified developer skills

## Workflow Overview
Integrated code quality validation pipeline from commit through deployment, focusing on hard coding detection and configuration management

## Workflow Stages

### 1. Pre-Commit Validation
- **Trigger**: Git pre-commit hook
- **Lead**: Developer Agent
- **Input**: Staged code changes
- **Output**: Pre-commit validation report
- **Tools**: `test_hard_coding_examples.py`
- **Deliverable**: `reports/quality/pre_commit_<timestamp>.md`

#### Validation Steps:
1. **Hard Coding Pattern Detection**
   - Scan for absolute paths (Windows/Unix)
   - Detect hardcoded URLs and credentials
   - Identify magic numbers and strings
   - Check for environment-specific values

2. **Path Configuration Analysis**
   - Verify relative path usage
   - Check cross-platform compatibility
   - Validate configuration externalization

### 2. Automated Quality Analysis
- **Lead**: Code Quality Analysis Skill
- **Input**: Pre-commit validation results
- **Output**: Comprehensive quality assessment
- **Skills**: `code_quality_and_technical_debt_analysis.skill.md`
- **Deliverable**: `reports/quality/quality_analysis_<timestamp>.md`

#### Analysis Components:
1. **Code Quality Metrics**
   - Hard coding violations count
   - Absolute path usage metrics
   - Configuration externalization score
   - Technical debt quantification

2. **Technical Debt Assessment**
   - Hard coding technical debt impact
   - Configuration management debt
   - Path dependency analysis

### 3. Code Review Integration
- **Lead**: Code Review Skill
- **Input**: Quality analysis results
- **Output**: Review recommendations
- **Skills**: `dev_code_review.skill.md`
- **Deliverable**: `reports/quality/code_review_<timestamp>.md`

#### Review Focus:
1. **Hard Coding Prevention Enforcement**
   - Verify configuration externalization
   - Check path handling best practices
   - Validate environment-specific separation

2. **Configuration Management Verification**
   - Environment variable usage
   - Config file implementation
   - Fallback mechanism presence

### 4. Backend/Frontend Specialized Validation
- **Lead**: Backend/Frontend Skills
- **Input**: Review recommendations
- **Output**: Specialized validation results
- **Skills**: `dev_backend.skill.md`, `dev_frontend_stack_unified.skill.md`
- **Deliverable**: `reports/quality/specialized_validation_<timestamp>.md`

#### Backend Validation:
- Configuration externalization enforcement
- Path management best practices
- Environment-specific configuration separation
- Cross-platform path handling

#### Frontend Validation:
- Asset path management (relative paths only)
- Environment-specific configuration (API endpoints)
- Build variables usage
- Hard coding prevention (URLs, API keys)

### 5. Improvement Recommendations
- **Lead**: Developer Agent
- **Input**: All validation results
- **Output**: Actionable improvement plan
- **Template**: `.ai/templates/improvement_template.md`
- **Deliverable**: `reports/quality/improvement_plan_<timestamp>.md`

#### Recommendation Categories:
1. **Critical Issues** (Immediate Fix Required)
   - Security vulnerabilities (hardcoded passwords/keys)
   - System-breaking absolute paths
   - Environment-specific hardcoded values

2. **High Priority** (Next Sprint)
   - Magic numbers/strings without constants
   - Missing configuration externalization
   - Cross-platform compatibility issues

3. **Medium Priority** (Technical Debt)
   - Code duplication
   - Complex path handling
   - Configuration optimization opportunities

### 6. Re-validation and Approval
- **Lead**: Senior Developer Agent
- **Input**: Implemented improvements
- **Output**: Final validation and approval
- **Deliverable**: `reports/quality/final_approval_<timestamp>.md`

#### Approval Criteria:
- Zero critical hard coding violations
- 95%+ configuration externalization
- Cross-platform path compatibility
- Documentation completeness

## Agent Roles

### Developer Agent (Primary)
- Code quality validation execution
- Hard coding pattern detection
- Improvement implementation
- **L1 Role**: Primary validation executor
- **L2 Role**: Senior quality assurance reviewer

### Senior Developer Agent (Validator)
- Final validation and approval
- Technical excellence assessment
- Quality standards compliance verification
- **Meta Role**: Reviewer field in validation reports

### Quality Assurance Agent (Support)
- Automated test execution
- Validation metrics collection
- Quality trend analysis
- Continuous improvement monitoring

## Integration Points

### Development Tools Integration
```bash
# Git Hook Integration
#!/bin/bash
python test_hard_coding_examples.py
if [ $? -ne 0 ]; then
    echo "Hard coding detected! Commit blocked."
    exit 1
fi
```

### CI/CD Pipeline Integration
```yaml
# GitHub Actions
- name: Code Quality Validation
  run: |
    python test_hard_coding_examples.py
    python -m pytest tests/hard_coding_test.py
    # Apply code_quality_and_technical_debt_analysis skill
    # Apply dev_code_review skill
    # Apply specialized validation skills
```

### IDE Integration
- Real-time hard coding detection
- Inline configuration suggestions
- Automated refactoring recommendations

## Related Documents

### Skills
- `.ai/skills/developer/code_quality_and_technical_debt_analysis.skill.md` - Primary quality analysis
- `.ai/skills/developer/dev_code_review.skill.md` - Code review validation
- `.ai/skills/developer/dev_backend.skill.md` - Backend specialized validation
- `.ai/skills/developer/dev_frontend_stack_unified.skill.md` - Frontend specialized validation

### Test Files
- `test_hard_coding_examples.py` - Automated detection script
- `skill_validation_test.md` - Validation test scenarios

### Templates
- `.ai/templates/improvement_template.md` - Improvement recommendations
- `.ai/templates/quality_report_template.md` - Quality reporting

## Constraint Conditions

### Validation Standards
- All code changes must pass pre-commit validation
- Critical issues block deployment
- Quality metrics must meet minimum thresholds
- Documentation required for all exceptions

### Quality Requirements
- Hard coding detection accuracy: 95%+
- False positive rate: <5%
- Configuration externalization: 95%+
- Cross-platform compatibility: 100%

### Integration Requirements
- Seamless Git workflow integration
- IDE real-time feedback
- CI/CD pipeline automation
- Developer-friendly error messages

## Success Indicators

### Validation Effectiveness
- Hard coding detection rate: 95%+
- False positive rate: <5%
- Issue resolution time: <24 hours
- Developer satisfaction: 4.5/5+

### Quality Improvement
- Technical debt reduction: 20% per quarter
- Configuration externalization: 95%+
- Code review efficiency: 30% improvement
- Deployment success rate: 99%+

### Adoption Metrics
- Workflow usage rate: 100%
- Developer compliance: 95%+
- Automated validation coverage: 100%
- Quality trend improvement: Positive

## Quality Gates

### Pre-Commit Gates
- ✅ No critical hard coding violations
- ✅ Basic configuration externalization
- ✅ Relative path usage
- ✅ Cross-platform compatibility

### Deployment Gates
- ✅ Zero critical issues
- ✅ 95%+ configuration externalization
- ✅ Complete documentation
- ✅ Senior developer approval

### Production Gates
- ✅ All quality metrics met
- ✅ Security validation passed
- ✅ Performance benchmarks achieved
- ✅ Monitoring integration complete

## Continuous Improvement

### Metrics Collection
- Hard coding violation trends
- Configuration quality scores
- Developer feedback analysis
- Tool effectiveness measurement

### Workflow Optimization
- Detection pattern refinement
- Validation speed optimization
- User experience improvements
- Integration expansion

### Knowledge Base Development
- Best practices documentation
- Common patterns library
- Training materials creation
- Community contribution guidelines
