# Skill Self-Validator

**Purpose**: Built-in self-validation logic for all skills, eliminating external file dependencies

---

## Universal Self-Validation Framework

### 1. Built-in Hard Coding Detection
```python
def self_validate_hard_coding(skill_content):
    """Built-in validation - no external files required"""
    violations = []
    
    # Pattern definitions (embedded)
    patterns = {
        'absolute_path_windows': r'[A-Za-z]:\\[^"\'\s]+',
        'absolute_path_unix': r'/[^"\'\s]+',
        'hardcoded_url': r'https?://[^"\'\s]+',
        'hardcoded_password': r'password\s*=\s*["\'][^"\']+["\']',
        'magic_number': r'timeout\s*=\s*\d{4,}',
        'magic_string': r'status\s*=\s*["\'][A-Z_]+["\']'
    }
    
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, skill_content, re.IGNORECASE):
            violations.append({
                'type': pattern_name,
                'severity': 'HIGH' if 'password' in pattern_name else 'MEDIUM',
                'pattern': pattern
            })
    
    return violations
```

### 2. Configuration Validation
```python
def self_validate_configuration(skill_content):
    """Validate configuration externalization"""
    checks = {
        'env_var_usage': r'os\.getenv\(|process\.env\.|@Value\(|@ConfigurationProperties',
        'config_file': r'\.json|\.yaml|\.yml|\.env|\.properties',
        'relative_path': r'\./|\.\.\/|path\.join\(|Path\('
    }
    
    results = {}
    for check_name, pattern in checks.items():
        results[check_name] = bool(re.search(pattern, skill_content))
    
    return results
```

### 3. Quality Metrics Calculation
```python
def calculate_quality_metrics(skill_content):
    """Calculate quality metrics without external dependencies"""
    metrics = {
        'hard_coding_score': 0,
        'configuration_score': 0,
        'path_management_score': 0,
        'overall_score': 0
    }
    
    # Hard coding score (inverse of violations)
    violations = self_validate_hard_coding(skill_content)
    metrics['hard_coding_score'] = max(0, 100 - (len(violations) * 20))
    
    # Configuration score
    config_results = self_validate_configuration(skill_content)
    metrics['configuration_score'] = sum(config_results.values()) / len(config_results) * 100
    
    # Overall score
    metrics['overall_score'] = (
        metrics['hard_coding_score'] * 0.4 +
        metrics['configuration_score'] * 0.6
    )
    
    return metrics
```

### 4. Validation Result Format
```yaml
skill_self_validation:
  skill_name: "dev_backend.skill.md"
  timestamp: "2026-01-25T14:41:00Z"
  hard_coding_violations:
    - type: "absolute_path_windows"
      line: 15
      severity: "HIGH"
      suggestion: "Use environment variable or config file"
  configuration_compliance:
    env_var_usage: true
    config_file: true
    relative_path: false
  quality_metrics:
    hard_coding_score: 80
    configuration_score: 66
    overall_score: 72
  status: "PASS" # if overall_score >= 70
```

### 5. Integration with Skill Execution
```python
def execute_skill_with_validation(skill_function, *args, **kwargs):
    """Execute skill with built-in validation"""
    
    # Execute skill
    result = skill_function(*args, **kwargs)
    
    # Self-validate
    if hasattr(result, 'code_content'):
        validation = self_validate_hard_coding(result.code_content)
        metrics = calculate_quality_metrics(result.code_content)
        
        # Add validation to result
        result.validation = {
            'violations': validation,
            'metrics': metrics,
            'status': 'PASS' if metrics['overall_score'] >= 70 else 'FAIL'
        }
    
    return result
```

## Usage Integration

### Skill Template Integration
```markdown
<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic
### Self-Validation Step
1. Execute primary skill logic
2. Apply built-in hard coding detection
3. Calculate quality metrics
4. Generate validation report
5. Return results with validation status
<!-- END_BLOCK -->
```

### Workflow Integration
```yaml
validation_step:
  type: "self_validation"
  executor: "skill_self_validator.md"
  threshold: 70
  auto_fix: true
```

## Benefits

1. **Zero External Dependencies**: All validation logic embedded
2. **Immediate Feedback**: Validation during skill execution
3. **Consistent Standards**: Universal metrics across all skills
4. **Reduced Complexity**: No separate test files needed
5. **Real-time Monitoring**: Continuous quality assessment
