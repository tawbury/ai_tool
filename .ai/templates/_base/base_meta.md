# Base Metadata Template

## Purpose
Derived from base_template.md - Document identity and classification only.

## Document Identity Fields

### Core Identification
- Document Name: [문서 이름]
- File Name: [파일이름].md
- Document ID: [TYPE]-[CATEGORY]-[NUMBER]
- Status: [Draft | Under Review | Approved | Active | Deprecated]
- Version: [Major].[Minor].[Patch]

### Temporal Information
- Created Date: {{CURRENT_DATE}}
- Last Updated: {{CURRENT_DATE}}

### Ownership
- Author: {{USER}}
- Reviewer: {{REVIEWER}}

### Relationships
- Parent Document: [[부모_문서.md]]
- Related Reference: [[관련_문서1.md]], [[관련_문서2.md]]

## Relationships 상세 규칙

### Parent Document (부모 문서)
- **목적**: 현재 문서의 직계 부모 또는 상위 문서 지정
- **필수여부**: 최상위 문서(Anchor, Roadmap)를 제외한 모든 문서는 필수
- **표준 연결 패턴**:
  - Task → Roadmap 또는 직계 상위 문서
  - Run Record → Task 또는 Roadmap  
  - Decision → Architecture 또는 PRD
  - Architecture → PRD 또는 Anchor
  - Specification → Architecture
  - Report → Task

### Related Reference (관련 참조)
- **목적**: 직접적으로 관련된 동등 레벨 또는 참조 문서들
- **필수여부**: 선택사항이지만 관련 문서가 있을 경우 반드시 기재
- **포함 대상**:
  - 동일 프로젝트 내 다른 문서들
  - 참조한 기술 문서들
  - 관련 Agent/Skill 문서들
  - 의존성 있는 외부 문서들

### 링크 형식 규칙
- **형식**: 반드시 `[[filename.md]]` 형식 사용
- **금지**: 와일드카드 패턴 (`task_*.md` 등) 사용 금지
- **유효성**: 실제 존재하는 파일만 참조
- **검증**: 순환 참조 방지 및 깨진 링크 감지

## Document ID Standard Format

### 문서 유형별 ID 형식:
- **ANCHOR**: ANCHOR-[PROJECT]-[NUMBER]
- **DECISION**: DECISION-[TOPIC]-[NUMBER] 또는 DECISION-[DATE]-[SEQUENCE]
- **TASK**: TASK-[CATEGORY]-[YYYYMMDD]-[HHMM]
- **WORKFLOW**: WF-[CATEGORY]-[NUMBER]
- **ROADMAP**: ROADMAP-[PROJECT]-[NUMBER]
- **RUN_RECORD**: RUN-[PROJECT]-[YYYYMMDD]-[SEQUENCE]

### 예시:
- ANCHOR-TRADING-001
- DECISION-ARCHITECTURE-001
- TASK-BACKEND-20260126-1917
- WF-TRADING-001
- ROADMAP-AI_TOOL-001
- RUN-AI_TOOL-20260126-1

## Document Categories

### 1. Planning Documents
- Anchor: 프로젝트 비전과 목표
- PRD: 제품 요구사항
- Architecture: 시스템 아키텍처
- Specification: 상세 명세

### 2. Execution Documents
- Task: 최소 실행 단위
- Run Record: 실행 결과 기록
- Decision: 결정 사항 기록

### 3. Management Documents
- Roadmap: 단계별 계획
- Workflow: 프로세스 정의
- Report: 결과 보고서
