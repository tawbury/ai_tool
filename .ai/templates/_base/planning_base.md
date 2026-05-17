# Planning Base Template

## Purpose
기획 문서(Planning Documents)의 공통 기반 구조 정의. Anchor, PRD, Architecture, Specification 템플릿의 상위 템플릿.

## Inheritance
- **Parent**: [[base_template.md]]
- **Children**: [[anchor_template.md]], [[prd_template.md]], [[architecture_template.md]], [[spec_template.md]]

## Common Metadata Structure for Planning Documents

```markdown
# Meta
- Document Type: [ANCHOR|PRD|ARCHITECTURE|SPECIFICATION]
- Document ID: [TYPE]-[PROJECT]-[NUMBER]
- Title: [문서 제목]
- Status: Draft
- Created: {{CURRENT_DATE}}
- Updated: {{CURRENT_DATE}}
- Author: {{USER}}
- Reviewer: {{REVIEWER}}
- Parent Document: [[parent_document.md]] (ANCHOR 제외)
- Related Reference: [[related_doc1.md]], [[related_doc2.md]]
- Version: 1.0.0
- Tags: planning, [document-specific-tags]
```

## Common Content Structure

### 기본 섹션 구조
```markdown
# [문서 제목]

---

## 1. 개요 (Overview)
### 목적 (Purpose)
[이 문서의 목적과 달성 목표]

### 범위 (Scope)
[문서가 다루는 범위와 경계]

### 배경 (Background)
[문서 작성의 배경과 필요성]

---

## 2. 상세 내용 (Details)
[문서 유형별 특정 섹션들]

---

## 3. 연관 정보 (Related Information)
### 참고 문서 (References)
- [[관련_문서1.md]]
- [[관련_문서2.md]]

### 영향 관계 (Impact Analysis)
[다른 문서/시스템에 미치는 영향]

### 검토 기록 (Review History)
- **v1.0**: 초기 작성 ({{USER}}, {{CURRENT_DATE}})
```

## Document-Specific Section Guidelines

### Anchor Document 추가 섹션
```markdown
## 2. 목표 설정 (Goal Setting)
### 비즈니스 목표 (Business Goals)
- 수익 모델 및 목표 수익
- 시장 점유율 목표
- 성공 측정 지표 (KPI)

## 3. 실행 계획 (Execution Plan)
### 단계별 계획 (Phased Plan)
- Phase 1: [단계 내용]
- Phase 2: [단계 내용]
```

### PRD Document 추가 섹션
```markdown
## 2. 요구사항 정의 (Requirements Definition)
### 기능 요구사항 (Functional Requirements)
- [FR-001] [요구사항 내용]
- [FR-002] [요구사항 내용]

### 비기능 요구사항 (Non-Functional Requirements)
- [NFR-001] [요구사항 내용]
- [NFR-002] [요구사항 내용]

## 3. 사용자 시나리오 (User Scenarios)
### 주요 사용자 유형 (User Personas)
- [페르소나 1]: [설명]
- [페르소나 2]: [설명]
```

### Architecture Document 추가 섹션
```markdown
## 2. 시스템 아키텍처 (System Architecture)
### 전체 구조 (Overall Structure)
[시스템 전체 아키텍처 다이어그램과 설명]

### 주요 컴포넌트 (Key Components)
- [컴포넌트 1]: [역할과 책임]
- [컴포넌트 2]: [역할과 책임]

## 3. 기술 스택 (Technology Stack)
### 프레임워크 및 라이브러리 (Frameworks & Libraries)
- [프레임워크 1]: [버전], [사용 이유]
- [프레임워크 2]: [버전], [사용 이유]
```

### Specification Document 추가 섹션
```markdown
## 2. 상세 명세 (Detailed Specifications)
### API 명세 (API Specifications)
- [API-001] [엔드포인트]: [메소드], [설명]
- [API-002] [엔드포인트]: [메소드], [설명]

### 데이터 모델 (Data Models)
- [모델 1]: [필드 정의]
- [모델 2]: [필드 정의]

## 3. 구현 가이드 (Implementation Guide)
### 개발 환경 (Development Environment)
- [환경 설정 요구사항]
- [의존성 관리]
```

## Planning Workflow Integration

### 문서 생성 순서
1. **Anchor** → 프로젝트 비전과 목표 정의
2. **PRD** → Anchor 기반 요구사항 정의
3. **Architecture** → PRD 기반 시스템 설계
4. **Specification** → Architecture 기반 상세 명세

### 승인 워크플로우
```
작성자(Author) → 동료 검토(Peer Review) → 시니어 검토(Senior Review) → 최종 승인(Final Approval)
```

### 상호 연관성 규칙
- **PRD**는 **Anchor**를 Parent Document로 참조
- **Architecture**는 **PRD**와 **Anchor**를 Related Reference로 참조
- **Specification**은 **Architecture**와 **PRD**를 Related Reference로 참조

## Quality Standards for Planning Documents

### 콘텐츠 품질 기준
1. **명확성**: 모든 요구사항과 설계가 명확하게 기술
2. **완전성**: 필요한 모든 정보 포함
3. **일관성**: 문서 간 모순 없는 일관된 내용
4. **추적성**: 요구사항과 설계의 추적 관계 명확

### 검토 체크리스트
- [ ] 모든 필수 메타데이터 필드 완료
- [ ] 목적과 범위가 명확하게 정의
- [ ] 관련 문서와 올바르게 연결
- [ ] 버전 관리 규칙 준수
- [ ] 링크 무결성 확인

## Agent Assignment for Planning Documents

### 주요 담당 에이전트
| 문서 유형 | 주요 에이전트 | 검토 에이전트 | 최종 승인 |
|----------|---------------|---------------|-----------|
| Anchor | PM Agent | Senior PM | Senior PM |
| PRD | PM Agent | Product Manager | Senior PM |
| Architecture | Developer Agent | Architect Agent | Senior Developer |
| Specification | Developer Agent | Tech Lead | Senior Developer |

### 협업 패턴
```
PM Agent (Anchor) → PM Agent (PRD) → Developer Agent (Architecture) → Developer Agent (Specification)
        ↓                      ↓                        ↓                            ↓
   Senior PM (Review)    Senior PM (Review)      Senior Developer (Review)    Senior Developer (Review)
```

## Common Pitfalls and Solutions

### 흔한 실수
1. **불완전한 요구사항**: 요구사항 누락이나 모호한 표현
2. **과도한 설계**: 필요 이상의 복잡한 아키텍처
3. **일관성 부족**: 문서 간 모순되는 내용
4. **링크 누락**: 관련 문서와의 연결 부재

### 해결 방안
1. **요구사항 검토 체크리스트** 사용
2. **아키텍처 리뷰** 프로세스 도입
3. **문서 간 일관성 검증** 자동화
4. **링크 무결성 검사** 정기 실행

## Integration Points

### Execution Phase 연계
- Planning 문서들은 **Task** 생성의 기준 제공
- **Architecture**와 **Specification**은 개발 가이드 역할
- **Decision** 문서는 Planning 변경 시 영향 분석에 활용

### Management Phase 연계
- **Roadmap**은 Planning 문서들을 기반으로 작성
- **Report**는 Planning 문서들의 실행 결과 평가
- **Workflow**는 Planning 프로세스 표준화

## Version History
- **v1.0**: Planning 문서 공통 기반 구조 정의
- **v1.1**: 문서 유형별 섹션 가이드라인 추가
- **v1.2**: 워크플로우 통합 및 품질 기준 강화
