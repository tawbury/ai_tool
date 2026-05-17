# Execution Base Template

## Purpose
실행 문서(Execution Documents)의 공통 기반 구조 정의. Task, Run Record, Decision 템플릿의 상위 템플릿.

## Inheritance
- **Parent**: [[base_template.md]]
- **Children**: [[task_template.md]], [[run_record_template.md]], [[decision_template.md]]

## Common Metadata Structure for Execution Documents

```markdown
# Meta
- Document Type: [TASK|RUN_RECORD|DECISION]
- Document ID: [TYPE]-[CATEGORY]-[IDENTIFIER]
- Title: [문서 제목]
- Status: Draft
- Created: {{CURRENT_DATE}}
- Updated: {{CURRENT_DATE}}
- Author: {{USER}}
- Reviewer: {{REVIEWER}}
- Parent Document: [[parent_document.md]]
- Related Reference: [[related_doc1.md]], [[related_doc2.md]]
- Version: 1.0.0
- Tags: execution, [document-specific-tags]
```

## Common Content Structure

### 기본 섹션 구조
```markdown
# [문서 제목]

---

## 1. 실행 개요 (Execution Overview)
### 목적 (Purpose)
[실행의 목적과 목표]

### 선행 조건 (Prerequisites)
[실행을 위한 필요 조건]

### 기대 결과 (Expected Outcomes)
[실행으로 기대되는 결과]

---

## 2. 상세 내용 (Details)
[문서 유형별 특정 섹션들]

---

## 3. 실행 결과 (Execution Results)
### 성과 (Achievements)
[성공적으로 달성된 항목]

### 이슈 (Issues)
[실행 중 발생한 문제점]

### 개선점 (Improvements)
[향후 개선할 사항]

---

## 4. 연관 정보 (Related Information)
### 참고 문서 (References)
- [[관련_문서1.md]]
- [[관련_문서2.md]]

### 후속 조치 (Next Actions)
[실행 후 필요한 다음 단계]
```

## Document-Specific Section Guidelines

### Task Document 추가 섹션
```markdown
## 2. 역할 정의 (Role Definition)
### 부서 (Department)
[담당 부서]

### 역할명 (Role Name)
[구체적인 역할 이름]

### 기대 수준 (Expected Level)
[기대하는 역할 수준]

### 제공 기준 (Provided Criteria)
- [ ] [구체적인 책임과 필요 역량 1]
- [ ] [구체적인 책임과 필요 역량 2]
- [ ] [구체적인 책임과 필요 역량 3]

## 3. 실행 계획 (Execution Plan)
### 평가 방법 (Evaluation Method)
[역할 수행 능력 평가 방법]

### 일정 (Timeline)
- 시작일: [날짜]
- 종료일: [날짜]
- 평가일: [날짜]
```

### Run Record Document 추가 섹션
```markdown
## 2. 실행 요약 (Execution Summary)
### 실행 Task (Executed Task)
- [[task_document.md]]: [Task 요약]

### 실행 결과 (Execution Results)
- **성공 항목**: [성공적으로 완료된 작업]
- **부분 성공**: [일부 완료된 작업]
- **실패 항목**: [실패한 작업과 원인]

### 실행 시간 (Execution Time)
- 시작 시간: [YYYY-MM-DD HH:MM]
- 종료 시간: [YYYY-MM-DD HH:MM]
- 소요 시간: [총 소요 시간]

## 3. 실행 증거 (Execution Evidence)
### 생성된 산출물 (Generated Artifacts)
- [산출물 1]: [설명과 위치]
- [산출물 2]: [설명과 위치]

### 로그 및 기록 (Logs and Records)
[실행 과정의 주요 로그와 기록]
```

### Decision Document 추가 섹션
```markdown
## 2. 결정 개요 (Decision Overview)
### 결정 내용 (Decision Content)
[구체적인 결정 사항]

### 결정 배경 (Decision Background)
[결정이 필요하게 된 배경]

### 긴급성 (Urgency)
[결정의 시급성과 영향]

## 3. 대안 분석 (Alternative Analysis)
### 대안 1: [대안 제목]
- **장점**: [장점 목록]
- **단점**: [단점 목록]
- **비용**: [예상 비용]
- **리스크**: [잠재적 리스크]

### 대안 2: [대안 제목]
- **장점**: [장점 목록]
- **단점**: [단점 목록]
- **비용**: [예상 비용]
- **리스크**: [잠재적 리스크]

## 4. 결정 근거 (Decision Rationale)
### 선택된 대안 (Selected Alternative)
[최종 선택된 대안과 이유]

### 기대 효과 (Expected Impact)
[결정으로 기대되는 효과]

### 영향 분석 (Impact Analysis)
[다른 시스템/프로세스에 미치는 영향]
```

## Execution Workflow Integration

### Operational Loop
```
Roadmap → Task → Run Record → Decision → (feedback) → Roadmap
```

### 실행 단계별 문서 흐름
1. **Task 생성**: Roadmap 기반으로 구체적인 실행 단위 정의
2. **Run Record**: Task 실행 결과와 증거 기록
3. **Decision**: 실행 중 발생한 문제나 변경 사항 결정
4. **피드백**: Run Record와 Decision이 Roadmap에 피드백

### 상호 연관성 규칙
- **Task**는 **Roadmap**을 Parent Document로 참조
- **Run Record**는 **Task**를 Parent Document로 참조
- **Decision**은 관련 **Architecture**나 **Task**를 Related Reference로 참조

## Quality Standards for Execution Documents

### 실행 품질 기준
1. **구체성**: 모든 실행 내용이 구체적이고 측정 가능
2. **추적성**: 실행 결과가 원인과 결과를 명확히 연결
3. **증거 기반**: 모든 주장은 실제 증거로 뒷받침
4. **시간성**: 실행 시간과 일정이 명확하게 기록

### 검토 체크리스트
- [ ] 실행 목적이 명확하게 정의
- [ ] 선행 조건이 모두 충족
- [ ] 실행 결과가 객관적으로 기록
- [ ] 관련 문서와 올바르게 연결
- [ ] 후속 조치가 구체적으로 정의

## Agent Assignment for Execution Documents

### 주요 담당 에이전트
| 문서 유형 | 주요 에이전트 | 검토 에이전트 | 최종 승인 |
|----------|---------------|---------------|-----------|
| Task | HR Agent | Team Lead | Senior Agent |
| Run Record | Execution Agent | Any Agent | Senior Agent |
| Decision | Decision Agent | Domain Expert | Senior Agent |

### 협업 패턴
```
HR Agent (Task) → Execution Agent (Run Record) → Decision Agent (Decision)
       ↓                    ↓                         ↓
   Senior Agent         Senior Agent              Senior Agent
```

## Performance Metrics

### Task 문서 메트릭
- Task 완료율
- 평가 정확도
- 역할 정의 명확성

### Run Record 문서 메트릭
- 실행 증거 완전성
- 결과 기록 정확성
- 후속 조치 실행율

### Decision 문서 메트릭
- 결정 실행율
- 대안 분석 깊이
- 영향 예측 정확도

## Common Pitfalls and Solutions

### 흔한 실수
1. **모호한 실행 계획**: 구체성 부족으로 실행 실패
2. **증거 부족**: 실행 결과에 대한 객관적 증거 부재
3. **충동적 결정**: 충분한 분석 없는 성급한 결정
4. **피드백 누락**: 실행 결과가 다음 단계에 반영되지 않음

### 해결 방안
1. **SMART 목표** 기반의 Task 정의
2. **증거 수집 체크리스트** 활용
3. **결정 프로세스** 표준화
4. **피드백 루프** 자동화

## Integration Points

### Planning Phase 연계
- **Task**는 Planning 문서들을 기반으로 생성
- **Run Record**는 Planning 문서들의 실행 결과 기록
- **Decision**은 Planning 변경 시 영향 분석에 활용

### Management Phase 연계
- **Roadmap**은 Execution 문서들을 통해 업데이트
- **Report**는 Execution 문서들을 종합 분석
- **Workflow**는 Execution 프로세스 최적화

## Automation Opportunities

### 자동화 가능한 작업
1. **Task 생성**: Roadmap 항목에서 자동 Task 생성
2. **Run Record 생성**: 실행 완료 시 자동 결과 기록
3. **Decision 추천**: 실행 데이터 기반 결정 지원
4. **피드백 루프**: Run Record 결과를 Roadmap에 자동 반영

### 템플릿 기반 자동화
- 메타데이터 자동 채우기
- 링크 관계 자동 설정
- 상태 자동 업데이트
- 버전 관리 자동화

## Version History
- **v1.0**: Execution 문서 공통 기반 구조 정의
- **v1.1**: 문서 유형별 섹션 가이드라인 추가
- **v1.2**: Operational Loop 통합 및 성능 메트릭 추가
- **v1.3**: 자동화 기회 및 통합 포인트 강화
