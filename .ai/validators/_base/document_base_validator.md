# Document Base Validator

**Purpose**: Unified base validation framework for all document types. All document validators inherit from this base.

---

## Inherited Validators

This base validator consolidates common validation rules from:
- `meta_validator.md` - Meta section validation
- `structure_validator.md` - Document structure validation

All document-specific validators (task, anchor, architecture, spec, prd, decision, report) should reference this base instead of duplicating rules.

---

## Section 1: Meta Validation (from meta_validator.md)

### 1.1 Required Fields
| Field | Required | Format |
|-------|----------|--------|
| Project Name | Yes | String |
| File Name | Yes | String |
| Document ID | Yes | Category-based prefix |
| Status | Yes | Draft/Active/Completed/Deprecated |
| Created Date | Yes | YYYY-MM-DD HH:MM |
| Last Updated | Yes | YYYY-MM-DD HH:MM |
| Author | Yes | Valid agent name (L1 level) |
| Reviewer | L2 only | Valid senior agent name |
| Parent Document | Optional | Valid reference |
| Related Reference | Optional | Valid references |
| Version | Yes | X.Y.Z semantic versioning |

### 1.2 Field Validation Rules
```python
def validate_meta_fields(document):
    """Validate all meta fields"""
    errors = []

    # Required fields check
    required_fields = ['Project Name', 'File Name', 'Document ID',
                       'Status', 'Created Date', 'Last Updated',
                       'Author', 'Version']
    for field in required_fields:
        if field not in document.meta or not document.meta[field]:
            errors.append(f"Missing or empty required field: {field}")

    # Date format validation
    date_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
    if not re.match(date_pattern, document.meta.get('Created Date', '')):
        errors.append("Invalid Created Date format (expected: YYYY-MM-DD HH:MM)")
    if not re.match(date_pattern, document.meta.get('Last Updated', '')):
        errors.append("Invalid Last Updated format (expected: YYYY-MM-DD HH:MM)")

    # Document ID format validation
    doc_id = document.meta.get('Document ID', '')
    if not re.match(r'^[A-Z]+-\w+-\d+$', doc_id):
        errors.append(f"Invalid Document ID format (expected: CATEGORY-TYPE-001)")

    # Parent Document validation (if present)
    parent_doc = document.meta.get('Parent Document', '')
    if parent_doc and not validate_document_reference(parent_doc):
        errors.append(f"Invalid Parent Document reference: {parent_doc}")

    # Author/Reviewer validation
    author = document.meta.get('Author', '')
    if not validate_agent_name(author):
        errors.append(f"Invalid Author name: {author}")

    return errors

def validate_document_reference(reference):
    """Validate document reference exists and is accessible"""
    try:
        # Check if reference follows valid pattern
        if not re.match(r'^\.ai/[\w/]+\.md$', reference):
            return False
        
        # Check if file exists (in real implementation)
        # return os.path.exists(reference)
        return True
    except:
        return False

def validate_agent_name(agent_name):
    """Validate agent name matches known agents"""
    valid_agents = ['AI System', 'PM Agent', 'Developer Agent', 
                   'Finance Agent', 'HR Agent', 'Contents-Creator Agent']
    return agent_name in valid_agents
```

### 1.3 Document Consistency Validation
```python
def validate_document_consistency(document):
    """Validate internal consistency and external references"""
    errors = []
    
    # Meta consistency
    if document.meta.get('Created Date') > document.meta.get('Last Updated'):
        errors.append("Created Date cannot be after Last Updated")
    
    # Version consistency
    version = document.meta.get('Version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        errors.append("Version must follow semantic versioning (X.Y.Z)")
    
    # Content-Meta alignment
    doc_type = extract_document_type(document.meta.get('Document ID', ''))
    if not validate_content_matches_type(document.content, doc_type):
        errors.append(f"Content does not match document type: {doc_type}")
    
    return errors
```

### 1.4 Impact Analysis for Rule Changes
```python
def analyze_rule_change_impact(rule_change, all_documents):
    """Analyze impact of rule changes across document ecosystem"""
    
    impact_report = {
        'rule_change': rule_change,
        'affected_documents': [],
        'required_updates': [],
        'priority': 'MEDIUM'
    }
    
    # Example: Hard coding rule change
    if 'hard_coding' in rule_change.lower():
        affected_types = ['skill', 'workflow', 'validator']
        
        for doc in all_documents:
            doc_type = extract_document_type(doc.meta.get('Document ID', ''))
            if doc_type in affected_types:
                impact_report['affected_documents'].append({
                    'file': doc.meta.get('File Name'),
                    'type': doc_type,
                    'impact_level': 'HIGH'
                })
    
    # Sort by priority
    impact_report['affected_documents'].sort(
        key=lambda x: x['impact_level'], reverse=True
    )
    
    return impact_report
```
        errors.append("Invalid Created Date format (expected: YYYY-MM-DD HH:MM)")

    # Version format validation
    version_pattern = r'^\d+\.\d+(\.\d+)?$'
    if not re.match(version_pattern, document.meta.get('Version', '')):
        errors.append("Invalid Version format (expected: X.Y or X.Y.Z)")

    # L2 reviewer validation
    if document.requires_l2_review and not document.meta.get('Reviewer'):
        errors.append("Reviewer field required for L2 validation")

    return errors
```

### 1.3 Status Values
| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| Draft | Initial creation | → Active |
| Active | In use | → Completed, Deprecated |
| Completed | Finished | → Deprecated |
| Deprecated | No longer used | (terminal) |

---

## Section 2: Structure Validation (from structure_validator.md)

### 2.1 Document Structure Requirements
```
# Document Title
# Meta
[Meta fields...]
---
## Section 1
[Content...]
## Section 2
[Content...]
```

### 2.2 Structure Validation Rules
```python
def validate_structure(document):
    """Validate document structure"""
    errors = []

    # Meta section must be first
    if not document.starts_with_meta_section():
        errors.append("Document must start with # Meta section")

    # Contents separator must exist
    if '---' not in document.content:
        errors.append("Contents separator '---' required after Meta section")

    # Section headers must use ## format
    for section in document.sections:
        if not section.header.startswith('## '):
            errors.append(f"Section header must use ## format: {section.header}")

    # No empty sections
    for section in document.sections:
        if not section.content.strip():
            errors.append(f"Empty section not allowed: {section.header}")

    return errors
```

### 2.3 Header Hierarchy
| Level | Format | Usage |
|-------|--------|-------|
| 1 | # | Document title only |
| 2 | ## | Main sections |
| 3 | ### | Subsections |
| 4 | #### | Detail items |

### 2.4 Language Compliance
| Location | Language | Note |
|----------|----------|------|
| docs/ | Korean | User-facing documents |
| .ai/ | English | System documents |

---

## Section 3: Validation Execution

### 3.1 Validation Order
1. Meta field existence check
2. Meta field format validation
3. Structure validation
4. Document-specific validation (delegated to specific validator)

### 3.2 Result Format
```yaml
validation_result:
  document_id: "DOC-001"
  status: PASS | FAIL
  meta_validation:
    status: PASS | FAIL
    errors: []
  structure_validation:
    status: PASS | FAIL
    errors: []
  specific_validation:
    status: PASS | FAIL
    errors: []
  total_errors: 0
```

### 3.3 Error Severity
| Severity | Description | Action |
|----------|-------------|--------|
| CRITICAL | Document invalid | Block processing |
| ERROR | Missing required element | Require fix |
| WARNING | Best practice violation | Recommend fix |
| INFO | Suggestion | Optional |

---

## Section 4: Integration Points

### 4.1 Document-Specific Validators
All these validators extend this base:
- `task_validator.md` - Task documents
- `anchor_validator.md` - Anchor documents
- `architecture_validator.md` - Architecture documents
- `spec_validator.md` - Specification documents
- `prd_validator.md` - PRD documents
- `decision_validator.md` - Decision documents
- `report_validator.md` - Report documents

### 4.2 Usage Pattern
```markdown
<!-- In document-specific validator -->
## Base Validation
This validator extends: `_base/document_base_validator.md`
Inherits: Meta validation, Structure validation

## Document-Specific Validation
[Only document-specific rules here]
```

---

## Section 5: Quality Standards

### 5.1 Validation Thresholds
| Check | Threshold | Required |
|-------|-----------|----------|
| Meta completeness | 100% | Yes |
| Structure compliance | 100% | Yes |
| Header format | 100% | Yes |
| Content completeness | 95%+ | Yes |

### 5.2 Performance Requirements
- Validation time: < 100ms per document
- Memory usage: < 10MB per validation
- Batch validation: Support 100+ documents
