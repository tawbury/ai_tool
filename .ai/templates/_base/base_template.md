# Base Template Framework

## Purpose
모든 템플릿의 기본 구조를 정의하는 최상위 템플릿. 이 파일은 모든 문서 템플릿의 단일 진실 공급원(Single Source of Truth) 역할을 합니다.

## Template Hierarchy

```
base_template.md (Level 1: 공통 기반)
├── planning_base.md (Level 2: 기획 문서 기반)
│   ├── anchor_template.md
│   ├── prd_template.md
│   └── architecture_template.md
├── execution_base.md (Level 2: 실행 문서 기반)
│   ├── task_template.md
│   ├── run_record_template.md
│   └── decision_template.md
└── management_base.md (Level 2: 관리 문서 기반)
    ├── roadmap_template.md
    ├── workflow_template.md
    └── report_template.md
```

## Standard Metadata Structure

### 필수 메타데이터 필드 (Required Fields)
```yaml
# Meta
- **Document Type** : [문서 유형]
- **Document ID** : [TYPE]-[CATEGORY]-[NUMBER]
- **Title** : [문서 제목]
- **Status** : [Draft | Under Review | Approved | Active | Deprecated]
- **Created** : {{CURRENT_DATE}}
- **Updated** : {{CURRENT_DATE}}
- **Author** : {{USER}}
- **Reviewer** : {{REVIEWER}}
- **Parent Document** : [[parent_document.md]]
- **Related Reference** : [[related_doc1.md]], [[related_doc2.md]]
- **Version** : [Major].[Minor].[Patch]
- **Tags** : [tag1], [tag2], [tag3]
```

### Document ID 표준 형식
- **ANCHOR**: `ANCHOR-[PROJECT]-[NUMBER]` (예: ANCHOR-AI_TOOL-001)
- **DECISION**: `DECISION-[TOPIC]-[NUMBER]` (예: DECISION-ARCHITECTURE-001)
- **TASK**: `TASK-[CATEGORY]-[YYYYMMDD]-[HHMM]` (예: TASK-BACKEND-20260126-1917)
- **WORKFLOW**: `WF-[CATEGORY]-[NUMBER]` (예: WF-TRADING-001)
- **ROADMAP**: `ROADMAP-[PROJECT]-[NUMBER]` (예: ROADMAP-AI_TOOL-001)
- **RUN_RECORD**: `RUN-[PROJECT]-[YYYYMMDD]-[SEQUENCE]` (예: RUN-AI_TOOL-20260126-1)

## Template Variables

### 시스템 변수 (System Variables)
- `{{CURRENT_DATE}}`: 현재 날짜 (YYYY-MM-DD HH:MM 형식)
- `{{USER}}`: 현재 사용자 이름
- `{{REVIEWER}}`: 시니어 에이전트 지정 (L2 검증용)

### 문서 구조 변수 (Document Structure Variables)
- `---`: 메타데이터와 콘텐츠 구분자
- `[[filename.md]]`: Obsidian 링크 형식 (와일드카드 금지)

## Content Structure Standards

### 섹션 헤더 규칙
- `#`: 문서 제목 (Meta 섹션 제외)
- `##`: 주요 섹션
- `###`: 하위 섹션
- `####`: 세부 항목

### 필수 섹션 구조
```markdown
# Meta
[메타데이터 필드]

---

# [문서 제목]

## 1. 개요 (Overview)
### 목적 (Purpose)
### 범위 (Scope)

## 2. 상세 내용 (Details)
[문서 유형별 특정 섹션]

## 3. 연관 정보 (Related Information)
### 참고 문서 (References)
### 태그 (Tags)
```

## Linking Standards

### 링크 규칙
- **Parent Document**: 반드시 지정 (최상위 문서 제외)
- **Related Reference**: 직접 관련 문서만 허용
- **형식**: `[[filename.md]]` 만 허용
- **금지**: 와일드카드 패턴 (`task_*.md` 등)

### 링크 유효성 검사
- 모든 링크는 실제 존재하는 파일을 참조해야 함
- 링크된 문서의 메타데이터 무결성 확인

## Quality Assurance Rules

### 문서 품질 기준
1. **메타데이터 완전성**: 모든 필수 필드 채움
2. **연결 무결성**: 유효한 문서만 링크
3. **버전 관리**: 변경 시 버전과 날짜 업데이트
4. **구조 일관성**: 템플릿 구조 준수

### AI 에이전트 제약조건
- AI 에이전트는 불완전한 메타데이터로 문서 생성 금지
- AI 에이전트는 Document ID 형식 표준 수정 금지
- AI 에이전트는 와일드카드 링크 사용 금지

## Template Usage Guidelines

### 새 문서 생성 프로세스
1. 적절한 템플릿 선택 및 복사
2. 메타데이터 필드 완전히 채우기
3. 문서 콘텐츠 작성
4. 관련 문서와 링크 연결
5. 검토 후 상태 업데이트

### 문서 수정 프로세스
1. Updated 날짜 변경
2. Version 업데이트 (주요 변경 시)
3. 변경 내용 기록
4. 관련 문서 링크 업데이트

## Integration Points

### Workflow Integration
- **Operational Loop**: Roadmap → Task → Run Record
- **Decision Process**: Architecture → Decision → Implementation
- **Planning Cycle**: Anchor → PRD → Architecture → Spec

### Agent Integration
- **Junior Agent**: 문서 생성 및 초기 작성 (Author 역할)
- **Senior Agent**: 검토 및 최종 승인 (Reviewer 역할)

## Document Categories

### 1. Planning Documents (기획 문서)
- **Anchor**: 프로젝트 비전과 목표
- **PRD**: 제품 요구사항 정의
- **Architecture**: 시스템 아키텍처 설계
- **Specification**: 상세 기능 명세

### 2. Execution Documents (실행 문서)
- **Task**: 최소 실행 단위 정의
- **Run Record**: 실행 결과 기록
- **Decision**: 결정 사항 및 근거 기록

### 3. Management Documents (관리 문서)
- **Roadmap**: 단계별 실행 계획
- **Workflow**: 프로세스 정의
- **Report**: 결과 보고서

## Validation Schema

### 메타데이터 유효성 검사
- Document ID 형식 검증
- 필수 필드 존재 확인
- 링크 형식 및 유효성 검사

### 콘텐츠 구조 검사
- 섹션 헤더 레벨 확인
- 필수 섹션 존재 검증
- 링크 무결성 검사

## Related Documents
- [[base_meta.md]]: 문서 식별 및 분류 체계
- [[base_rules.md]]: 템플릿 사용 규칙 및 제약조건
- [[base_mapping.md]]: AI 컨텍스트 라우팅 및 매핑
- [[base_schema.md]]: 템플릿 스키마 정의

## Version History
- **v1.0**: 초기 기본 템플릿 프레임워크
- **v1.1**: 메타데이터 표준화 및 링크 규칙 강화
- **v1.2**: 카테고리별 분류 및 워크플로우 통합
