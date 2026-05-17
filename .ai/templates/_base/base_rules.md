# Base Rules Template
 
## Purpose
Derived from base_template.md - Human- and AI-readable rules governing template usage.
 
## Document Rules

### Metadata Constraints
- 모든 문서는 필수 메타데이터 필드를 모두 채워야 함
- Document ID는 표준 형식을 따라야 함
- File Name은 영문, 소문자, 언더스코어만 사용

### Linking Constraints
- Parent Document는 반드시 지정되어야 함 (최상위 제외)
- Related Reference는 직접 관련 문서만 허용
- Obsidian Links는 [[filename.md]] 형식만 허용
- Wildcard Links 금지

### Relationships Rules

#### Parent Document 규칙
- **정의**: 현재 문서의 직계 부모 또는 상위 문서
- **필수여부**: 최상위 문서(Anchor, Roadmap)를 제외한 모든 문서는 필수
- **연결 패턴**:
  - Task → Roadmap 또는 직계 상위 문서
  - Run Record → Task 또는 Roadmap
  - Decision → Architecture 또는 PRD
  - Architecture → PRD 또는 Anchor
  - Specification → Architecture
  - Report → Task

#### Related Reference 규칙
- **정의**: 직접적으로 관련된 동등 레벨 또는 참조 문서들
- **필수여부**: 선택사항이지만 관련 문서가 있을 경우 반드시 기재
- **연결 패턴**:
  - 동일 프로젝트 내 다른 문서들
  - 참조한 기술 문서들
  - 관련 Agent/Skill 문서들
  - 의존성 있는 외부 문서들

#### 링크 유효성 검증
- 모든 링크는 실제 존재하는 파일을 참조해야 함
- 링크된 문서의 메타데이터 무결성 확인
- 순환 참조 방지 (A→B→C→A 금지)
- 깨진 링크 자동 감지 및 보고

#### 자동화 규칙
- AI 에이전트가 문서 생성 시 Parent Document 자동 추천
- Related Reference 후보 문서 자동 제안
- 문서 간 의존성 관계 자동 분석 및 표시
- 링크 일관성 검증 자동 수행

### Structural Constraints
- Base templates must not contain execution-specific content
- Content templates must not redefine metadata structure
- Base templates must not be overwritten by content templates

### AI Agent Constraints
- AI agents must not create documents without complete metadata
- AI agents must not modify Document ID format standards

## Workflow Integration Mapping
 
### Template Dependencies
- [[base_template.md]] → All content templates
- [[workflow_base.md]] → Operational loop integration
- [[roadmap_template.md]] → Phase tracking
- [[run_record_template.md]] → Execution recording
 
### Context Routing Rules
- Anchor documents provide project context for all related documents
- Decision documents reference applicable architecture and requirements
- Task documents link to parent planning documents
- Run records reference originating task documents
 
## Operational Continuity Mapping
 
### Session Continuity Guarantee
- All documents traceable through metadata connections
- Session interruptions do not affect work continuity
- Work can be resumed from repository state at any time
 
### Integration Points
- Metadata-first connection approach
- Artifact relationship tracking
- Cross-session state preservation

## Quality Standards
 
### 모든 문서는 다음 기준 충족:
1. **메타데이터 완전성**: 필수 필드 모두 채움
2. **연결 무결성**: 유효한 문서만 링크
3. **버전 관리**: 변경 시 버전과 날짜 업데이트
4. **일관성**: 템플릿 구조 준수
 
## Operational Rules
 
### 새 문서 생성 시:
1. 이 템플릿을 복사하여 새 파일 생성
2. 메타데이터 필드 채우기
3. 문서 내용 작성
4. 관련 문서와 연결
5. 검토 후 상태 업데이트
 
### 문서 수정 시:
1. Last Updated 날짜 변경
2. Version 업데이트 (주요 변경 시)
3. 변경 내용을 Version History에 기록
4. 관련 문서의 링크 업데이트
 
## Forbidden Actions
- AI agents must not create documents without complete metadata
- AI agents must not use wildcard links in document references
- AI agents must not modify Document ID standard format