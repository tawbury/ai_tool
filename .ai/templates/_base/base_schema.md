# Template Schema Definition

## Purpose
템플릿 구조의 JSON 스키마 정의. 자동화된 유효성 검사 및 템플릿 일관성 보장을 위한 스키마 명세.

## Metadata Schema

### 기본 메타데이터 스키마
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Template Metadata Schema",
  "type": "object",
  "required": [
    "Document Type",
    "Document ID", 
    "Title",
    "Status",
    "Created",
    "Updated",
    "Author",
    "Parent Document"
  ],
  "properties": {
    "Document Type": {
      "type": "string",
      "enum": [
        "ANCHOR", "PRD", "ARCHITECTURE", "SPECIFICATION",
        "TASK", "RUN_RECORD", "DECISION",
        "ROADMAP", "WORKFLOW", "REPORT"
      ]
    },
    "Document ID": {
      "type": "string",
      "pattern": "^[A-Z_]+-[A-Z0-9_]+-[0-9]+$"
    },
    "Title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "Status": {
      "type": "string",
      "enum": ["Draft", "Under Review", "Approved", "Active", "Deprecated"]
    },
    "Created": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}$"
    },
    "Updated": {
      "type": "string", 
      "pattern": "^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}$"
    },
    "Author": {
      "type": "string",
      "minLength": 1
    },
    "Reviewer": {
      "type": "string",
      "minLength": 1
    },
    "Parent Document": {
      "type": "string",
      "pattern": "^\\[\\[.+\\.md\\]\\]$"
    },
    "Related Reference": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^\\[\\[.+\\.md\\]\\]$"
      }
    },
    "Version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "Tags": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9_-]+$"
      }
    }
  }
}
```

### Document ID 패턴 상세 정의

#### ANCHOR 문서 ID
```json
{
  "type": "string",
  "pattern": "^ANCHOR-[A-Z0-9_]+-[0-9]{3}$",
  "examples": [
    "ANCHOR-AI_TOOL-001",
    "ANCHOR-TRADING-001"
  ]
}
```

#### DECISION 문서 ID
```json
{
  "type": "string", 
  "pattern": "^DECISION-[A-Z0-9_]+-[0-9]{3}$",
  "examples": [
    "DECISION-ARCHITECTURE-001",
    "DECISION-SECURITY-001"
  ]
}
```

#### TASK 문서 ID
```json
{
  "type": "string",
  "pattern": "^TASK-[A-Z0-9_]+-[0-9]{8}-[0-9]{4}$",
  "examples": [
    "TASK-BACKEND-20260126-1917",
    "TASK-FRONTEND-20260127-1430"
  ]
}
```

#### WORKFLOW 문서 ID
```json
{
  "type": "string",
  "pattern": "^WF-[A-Z0-9_]+-[0-9]{3}$",
  "examples": [
    "WF-TRADING-001",
    "WF-DEVELOPMENT-001"
  ]
}
```

#### ROADMAP 문서 ID
```json
{
  "type": "string",
  "pattern": "^ROADMAP-[A-Z0-9_]+-[0-9]{3}$",
  "examples": [
    "ROADMAP-AI_TOOL-001",
    "ROADMAP-TRADING-001"
  ]
}
```

#### RUN_RECORD 문서 ID
```json
{
  "type": "string",
  "pattern": "^RUN-[A-Z0-9_]+-[0-9]{8}-[0-9]+$",
  "examples": [
    "RUN-AI_TOOL-20260126-1",
    "RUN-TRADING-20260126-2"
  ]
}
```

## Content Structure Schema

### 섹션 헤더 스키마
```json
{
  "title": "Content Section Schema",
  "type": "object",
  "properties": {
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "level": {
            "type": "integer",
            "minimum": 1,
            "maximum": 6
          },
          "title": {
            "type": "string",
            "minLength": 1
          },
          "required": {
            "type": "boolean"
          }
        }
      }
    }
  }
}
```

### 필수 섹션 정의

#### 모든 문서 공통 필수 섹션
```json
{
  "common_required_sections": [
    {
      "level": 1,
      "title": "Meta",
      "required": true
    },
    {
      "level": 2,
      "title": "개요",
      "required": true
    },
    {
      "level": 3,
      "title": "목적",
      "required": true
    },
    {
      "level": 3,
      "title": "범위", 
      "required": true
    }
  ]
}
```

#### 문서 유형별 필수 섹션
```json
{
  "document_specific_sections": {
    "ANCHOR": [
      {"level": 2, "title": "목표 설정", "required": true},
      {"level": 3, "title": "비즈니스 목표", "required": true},
      {"level": 2, "title": "실행 계획", "required": true}
    ],
    "ROADMAP": [
      {"level": 2, "title": "목표 및 성공지표", "required": true},
      {"level": 3, "title": "정량 목표", "required": true},
      {"level": 2, "title": "실행 계획", "required": true},
      {"level": 3, "title": "Phase 목록", "required": true}
    ],
    "TASK": [
      {"level": 2, "title": "Department", "required": true},
      {"level": 2, "title": "Role Name", "required": true},
      {"level": 2, "title": "Expected Level", "required": true},
      {"level": 2, "title": "Provided Criteria", "required": true}
    ],
    "RUN_RECORD": [
      {"level": 2, "title": "실행 요약", "required": true},
      {"level": 3, "title": "실행 Task", "required": true},
      {"level": 3, "title": "실행 결과", "required": true},
      {"level": 2, "title": "실행 증거", "required": true}
    ],
    "DECISION": [
      {"level": 2, "title": "결정 개요", "required": true},
      {"level": 3, "title": "결정 내용", "required": true},
      {"level": 2, "title": "대안 분석", "required": true},
      {"level": 2, "title": "결정 근거", "required": true}
    ]
  }
}
```

## Link Validation Schema

### Obsidian 링크 스키마
```json
{
  "title": "Link Validation Schema",
  "type": "object",
  "properties": {
    "link_format": {
      "type": "string",
      "pattern": "^\\[\\[.+\\.md\\]\\]$",
      "description": "Obsidian 링크 형식만 허용"
    },
    "forbidden_patterns": [
      "\\[\\[.*\\*.*\\.md\\]\\]",
      "\\[\\[.*\\?.*\\.md\\]\\]"
    ],
    "required_links": {
      "Parent Document": {
        "required_except": ["ANCHOR"],
        "description": "최상위 문서를 제외한 모든 문서에 필수"
      }
    }
  }
}
```

## Template Validation Rules

### 유효성 검사 규칙
```json
{
  "validation_rules": {
    "metadata_completeness": {
      "description": "모든 필수 메타데이터 필드 존재 확인",
      "required_fields": [
        "Document Type", "Document ID", "Title", "Status", 
        "Created", "Updated", "Author", "Parent Document"
      ]
    },
    "link_integrity": {
      "description": "링크 형식 및 대상 파일 존재 확인",
      "rules": [
        "모든 링크는 [[filename.md]] 형식",
        "와일드카드 패턴 금지",
        "링크된 파일 실제 존재 확인"
      ]
    },
    "content_structure": {
      "description": "섹션 구조 및 헤더 레벨 확인",
      "rules": [
        "필수 섹션 모두 존재",
        "헤더 레벨 적절성",
        "섹션 순서 준수"
      ]
    },
    "version_consistency": {
      "description": "버전 정보 및 날짜 일관성",
      "rules": [
        "Updated ≥ Created",
        "버전 형식 준수 (Major.Minor.Patch)",
        "상태 변경 시 버전 업데이트"
      ]
    }
  }
}
```

## Error Definitions

### 유효성 검사 오류 유형
```json
{
  "error_types": {
    "METADATA_MISSING": {
      "code": "E001",
      "message": "필수 메타데이터 필드 누락",
      "severity": "error"
    },
    "INVALID_DOCUMENT_ID": {
      "code": "E002", 
      "message": "Document ID 형식 오류",
      "severity": "error"
    },
    "INVALID_LINK_FORMAT": {
      "code": "E003",
      "message": "링크 형식 오류",
      "severity": "warning"
    },
    "MISSING_REQUIRED_SECTION": {
      "code": "E004",
      "message": "필수 섹션 누락",
      "severity": "error"
    },
    "BROKEN_LINK": {
      "code": "E005",
      "message": "존재하지 않는 파일 링크",
      "severity": "warning"
    },
    "VERSION_INCONSISTENCY": {
      "code": "E006",
      "message": "버전 정보 불일치",
      "severity": "warning"
    }
  }
}
```

## Validation Implementation

### 자동 검사 프로세스
1. **문서 생성 시**: 메타데이터 완전성 검사
2. **문서 저장 시**: 링크 무결성 검사  
3. **문서 수정 시**: 버전 일관성 검사
4. **주기적 검사**: 전체 문서 구조 검사

### 검증 도구 통합
- **AI Agent**: 문서 생성 시 자동 검증
- **Validator Scripts**: 일괄 검증 실행
- **CI/CD Pipeline**: 커밋 시 자동 검증

## Usage Examples

### 템플릿 유효성 검사 예시
```bash
# 단일 문서 검증
validate-template.py --file roadmap_project_v1.md

# 디렉토리 전체 검증
validate-template.py --directory docs/

# 특정 문서 유형 검증
validate-template.py --type ROADMAP --directory docs/
```

### 스키마 업데이트 절차
1. 스키마 변경 제안
2. 하위 호환성 검토
3. 테스트 케이스 업데이트
4. 스키마 버전 업그레이드
5. 관련 템플릿 업데이트

## Version History
- **v1.0**: 기본 메타데이터 및 콘텐츠 스키마 정의
- **v1.1**: Document ID 패턴 상세화 및 링크 검증 강화
- **v1.2**: 문서 유형별 필수 섹션 정의 및 오류 처리 체계화
