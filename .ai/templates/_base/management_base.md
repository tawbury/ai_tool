# Management Base Template

## Purpose
관리 문서(Management Documents)의 공통 기반 구조 정의. Roadmap, Workflow, Report 템플릿의 상위 템플릿.

## Inheritance
- **Parent**: [[base_template.md]]
- **Children**: [[roadmap_template.md]], [[workflow_template.md]], [[report_template.md]]

## Common Metadata Structure for Management Documents

```markdown
# Meta
- Document Type: [ROADMAP|WORKFLOW|REPORT]
- Document ID: [TYPE]-[CATEGORY]-[NUMBER]
- Title: [문서 제목]
- Status: Draft
- Created: {{CURRENT_DATE}}
- Updated: {{CURRENT_DATE}}
- Author: {{USER}}
- Reviewer: {{REVIEWER}}
- Parent Document: [[parent_document.md]] (ROADMAP 제외)
- Related Reference: [[related_doc1.md]], [[related_doc2.md]]
- Version: 1.0.0
- Tags: management, [document-specific-tags]
```

## Common Content Structure

### 기본 섹션 구조
```markdown
# [문서 제목]

---

## 1. 관리 개요 (Management Overview)
### 목적 (Purpose)
[관리 문서의 목적과 역할]

### 관리 범위 (Management Scope)
[관리 대상과 범위]

### 관리 원칙 (Management Principles)
[관리 활동의 기본 원칙]

---

## 2. 상세 내용 (Details)
[문서 유형별 특정 섹션들]

---

## 3. 관리 결과 (Management Results)
### 성과 지표 (Performance Metrics)
[관리 성과를 측정하는 지표]

### 이슈 관리 (Issue Management)
[관리 중 발생한 이슈와 해결]

### 개선 계획 (Improvement Plan)
[향후 관리 개선 계획]

---

## 4. 연관 정보 (Related Information)
### 참고 문서 (References)
- [[관련_문서1.md]]
- [[관련_문서2.md]]

### 스테이크홀더 (Stakeholders)
[관리 활동 관련 주요 이해관계자]
```

## Document-Specific Section Guidelines

### Roadmap Document 추가 섹션
```markdown
## 2. 목표 및 성공지표 (Goals and Success Metrics)
### 정량 목표 (Quantitative Goals)
- [목표 1]: [측정 가능한 목표값]
- [목표 2]: [측정 가능한 목표값]

### 정성 목표 (Qualitative Goals)
- [목표 1]: [질적 목표 설명]
- [목표 2]: [질적 목표 설명]

### 성공 지표 (Success Indicators)
- [지표 1]: [측정 방법과 목표값]
- [지표 2]: [측정 방법과 목표값]

## 3. 실행 계획 (Execution Plan)
### Phase 목록 (Phase List)
- **Phase 1**: [단계명] ([기간])
  - 목표: [단계 목표]
  - 주요 Task: [[task1.md]], [[task2.md]]
  - 상태: [Work Not Started|In Progress|Done]

- **Phase 2**: [단계명] ([기간])
  - 목표: [단계 목표]
  - 주요 Task: [[task3.md]], [[task4.md]]
  - 상태: [Work Not Started|In Progress|Done]

### 의존성 관계 (Dependencies)
- [의존성 1]: [설명과 영향]
- [의존성 2]: [설명과 영향]

## 4. 위험 관리 (Risk Management)
### 주요 리스크 (Key Risks)
- [리스크 1]: [확률], [영향도], [대응 계획]
- [리스크 2]: [확률], [영향도], [대응 계획]
```

### Workflow Document 추가 섹션
```markdown
## 2. 프로세스 정의 (Process Definition)
### 워크플로우 목적 (Workflow Purpose)
[워크플로우의 목적과 가치]

### 참여자 역할 (Participant Roles)
- [역할 1]: [책임과 권한]
- [역할 2]: [책임과 권한]

### 프로세스 단계 (Process Steps)
1. **[단계 1]**: [설명]
   - 입력: [입력 항목]
   - 출력: [출력 항목]
   - 담당자: [역할]
   - 소요 시간: [예상 시간]

2. **[단계 2]**: [설명]
   - 입력: [입력 항목]
   - 출력: [출력 항목]
   - 담당자: [역할]
   - 소요 시간: [예상 시간]

## 3. 품질 관리 (Quality Management)
### 품질 기준 (Quality Standards)
- [기준 1]: [측정 방법]
- [기준 2]: [측정 방법]

### 검토 체크포인트 (Review Checkpoints)
- [체크포인트 1]: [검토 항목과 기준]
- [체크포인트 2]: [검토 항목과 기준]

## 4. 자동화 및 도구 (Automation and Tools)
### 자동화 대상 (Automation Targets)
- [자동화 1]: [범위와 방법]
- [자동화 2]: [범위와 방법]

### 사용 도구 (Used Tools)
- [도구 1]: [용도와 설정]
- [도구 2]: [용도와 설정]
```

### Report Document 추가 섹션
```markdown
## 2. 평가 개요 (Evaluation Overview)
### 평가 대상 (Evaluation Target)
[평가의 대상과 범위]

### 평가 기간 (Evaluation Period)
- 시작일: [YYYY-MM-DD]
- 종료일: [YYYY-MM-DD]

### 평가 방법 (Evaluation Method)
[평가에 사용된 방법론과 도구]

## 3. 평가 결과 (Evaluation Results)
### 정량적 결과 (Quantitative Results)
- [지표 1]: [측정값], [목표값], [달성률]
- [지표 2]: [측정값], [목표값], [달성률]

### 정성적 결과 (Qualitative Results)
- [결과 1]: [상세 설명]
- [결과 2]: [상세 설명]

### 주요 성과 (Key Achievements)
- [성과 1]: [설명과 증거]
- [성과 2]: [설명과 증거]

## 4. 개선 제언 (Improvement Recommendations)
### 단기 개선안 (Short-term Improvements)
- [개선안 1]: [내용과 우선순위]
- [개선안 2]: [내용과 우선순위]

### 장기 개선안 (Long-term Improvements)
- [개선안 1]: [내용과 우선순위]
- [개선안 2]: [내용과 우선순위]
```

## Management Workflow Integration

### 관리 사이클
```
Planning → Execution → Monitoring → Control → Feedback → Planning
```

### 문서 간 관계
1. **Roadmap**: 전체 프로젝트 관리의 중심
2. **Workflow**: 특정 프로세스의 표준화
3. **Report**: 관리 활동의 결과 평가

### 상호 연관성 규칙
- **Roadmap**은 **Anchor**를 Parent Document로 참조
- **Workflow**는 비즈니스 요구사항을 기반으로 생성
- **Report**는 관련 소스 문서들을 Related Reference로 참조

## Quality Standards for Management Documents

### 관리 품질 기준
1. **측정 가능성**: 모든 관리 항목이 측정 가능
2. **추적성**: 관리 활동이 목표와 연결
3. **지속성**: 지속적인 관리와 개선 가능
4. **투명성**: 모든 관리 활동이 투명하게 기록

### 검토 체크리스트
- [ ] 관리 목적이 명확하게 정의
- [ ] 성과 지표가 구체적이고 측정 가능
- [ ] 이슈 관리 프로세스가 명확
- [ ] 개선 계획이 실행 가능
- [ ] 스테이크홀더가 적절히 식별

## Agent Assignment for Management Documents

### 주요 담당 에이전트
| 문서 유형 | 주요 에이전트 | 검토 에이전트 | 최종 승인 |
|----------|---------------|---------------|-----------|
| Roadmap | PM Agent | Planning Agent | Senior PM |
| Workflow | Workflow Agent | Process Owner | Senior Agent |
| Report | Domain Agent | Analyst | Senior Agent |

### 협업 패턴
```
PM Agent (Roadmap) → Workflow Agent (Process) → Domain Agent (Report)
       ↓                    ↓                        ↓
   Senior PM          Senior Agent              Senior Agent
```

## Performance Metrics

### Roadmap 관리 메트릭
- 마일스톤 달성율
- Task 완료율
- 리스크 관리 효과성

### Workflow 관리 메트릭
- 프로세스 효율성
- 품질 준수율
- 자동화 비율

### Report 관리 메트릭
- 평가 정확성
- 개선안 실행율
- 스테이크홀더 만족도

## Common Pitfalls and Solutions

### 흔한 실수
1. **모호한 목표**: 측정 불가능한 관리 목표 설정
2. **과도한 통제**: 비효율적인 과도한 관리
3. **피드백 부재**: 실행 결과가 관리에 반영되지 않음
4. **일관성 부족**: 관리 기준과 실행 간 불일치

### 해결 방안
1. **SMART 목표** 기반의 관리 목표 설정
2. **리스크 기반**의 관리 수준 조절
3. **피드백 루프** 자동화
4. **표준화된** 관리 프로세스 적용

## Integration Points

### Planning Phase 연계
- **Roadmap**은 Planning 문서들을 관리
- **Workflow**는 Planning 프로세스 표준화
- **Report**는 Planning 결과 평가

### Execution Phase 연계
- **Roadmap**은 Execution 문서들을 통해 업데이트
- **Workflow**는 Execution 프로세스 관리
- **Report**는 Execution 결과 종합 분석

### Continuous Improvement
- **PDCA 사이클**: Plan-Do-Check-Act
- **피드백 루프**: 실행 결과를 계획에 반영
- **학습 조직**: 경험을 통한 지식 축적

## Automation Opportunities

### 자동화 가능한 관리 작업
1. **Roadmap 업데이트**: Run Record 결과 자동 반영
2. **Workflow 모니터링**: 프로세스 상태 자동 추적
3. **Report 생성**: 데이터 자동 수집 및 보고서 작성
4. **성과 측정**: KPI 자동 계산 및 알림

### 관리 대시보드
- 실시간 상태 모니터링
- 성과 지표 시각화
- 이슈 알림 및 추적
- 개선 제언 자동 생성

## Version History
- **v1.0**: Management 문서 공통 기반 구조 정의
- **v1.1**: 문서 유형별 섹션 가이드라인 추가
- **v1.2**: 성과 메트릭 및 자동화 기회 강화
- **v1.3**: 지속적 개선 및 통합 포인트 확장
