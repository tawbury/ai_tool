# 글로벌 룰 레이어드 아키텍처 전환 계획

**작성일**: 2026-05-17  
**문서 상태**: 제안  
**대상 파일**: `.ai/rules/rules.md`  
**대상 시스템**: Codex CLI, Claude Code, Gemini CLI  
**문서 목적**: 기존의 단일 글로벌 룰 파일을 유지하면서, 장기적으로 확장 가능한 레이어드 룰 시스템으로 전환하기 위한 아키텍처와 단계별 마이그레이션 계획을 정의한다.

---

## 1. 배경

현재 `.ai/rules/rules.md`는 Codex CLI, Claude Code, Gemini CLI가 공유하는 글로벌 룰의 단일 진입점이다. 이 원칙은 유지되어야 한다. 루트 어댑터인 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 각 도구가 프로젝트 룰을 발견하도록 돕는 얇은 안내 파일이며, 공통 규칙의 원본이 되어서는 안 된다.

다만 현재 `rules.md`는 글로벌 계약, 문서 작성 규칙, HR 평가 규칙, 개발 문서 규칙, 워크플로우, 검증, 에이전트 운영, Claude 관련 잔여 지침까지 한 파일 안에 함께 포함하고 있다. 이 구조는 초기에는 단순하지만, AI CLI 도구와 프로젝트 유형이 늘어날수록 다음 문제가 커진다.

- 모든 작업에서 불필요한 도메인 규칙까지 함께 로드된다.
- 개발, HR, 문서화, 검증, 에이전트 운영의 책임 경계가 흐려진다.
- 특정 도메인 규칙을 수정할 때 글로벌 계약 전체를 함께 건드리게 된다.
- 새 도메인을 추가할 때 파일 단위 기준이 없어 규칙 파일이 평면적으로 늘어날 수 있다.
- 운영 규칙과 업무 도메인 규칙이 섞여 선택 로딩 기준이 불명확해진다.
- 마케팅, 리서치, 세일즈, 재무 등 비개발 업무로 확장할 때 기존 개발 중심 분류가 한계가 된다.

따라서 이번 리팩터링은 `.ai/rules/rules.md`를 폐기하거나 대체하는 작업이 아니다. 기존 의도와 운영 철학을 보존하되, 글로벌 진입점은 더 작고 안정적인 계약으로 만들고, 세부 규칙은 목적에 따라 계층화해 선택적으로 로드할 수 있게 만드는 작업이다.

---

## 2. 핵심 원칙

1. `.ai/rules/rules.md`는 계속 글로벌 SSoT이자 첫 번째 프로젝트 룰 진입점이다.
2. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 얇은 루트 어댑터로 유지한다.
3. 심볼릭 링크는 룰 파일과 룰 디렉터리에 사용하지 않는다.
4. 공유 규칙 본문은 루트 어댑터에 복제하지 않는다.
5. 도메인 룰은 해당 도메인 작업에 진입할 때만 로드한다.
6. 운영 룰은 도메인 룰과 분리한다.
7. 아키텍처는 소프트웨어 개발을 넘어 마케팅, 리서치, 세일즈, 재무, 향후 비즈니스 워크플로우를 수용해야 한다.
8. 구조 설계의 우선순위는 유지보수성, 컨텍스트 효율, 선택 로딩, 확장성, AI CLI 간 일관성이다.

---

## 3. 목표 아키텍처

권장 구조는 다음과 같다.

```text
.ai/
  rules/
    README.md
    rules.md

    domains/
      documentation.rules.md
      development.rules.md
      hr.rules.md

    operations/
      workflow.rules.md
      validation.rules.md
      agent.rules.md
```

이 구조의 핵심 구분은 다음과 같다.

| 레이어 | 역할 | 예시 |
|---|---|---|
| `rules.md` | 모든 AI CLI가 항상 읽는 글로벌 계약 | SSoT, 우선순위, 어댑터 정책, 심볼릭 링크 금지, 선택 로딩 원칙 |
| `domains/` | 업무 또는 작업 도메인별 세부 규칙 | 문서화, 개발, HR, 마케팅, 리서치, 세일즈, 재무 |
| `operations/` | 도메인과 무관하게 작업을 실행하고 통제하는 운영 규칙 | 워크플로우, 검증, 에이전트 협업, 복구, 실행 증거 |

이 구분은 단순한 폴더 정리가 아니다. 규칙의 변경 이유를 기준으로 파일을 분리하는 설계다. 도메인 룰은 업무 내용이 바뀔 때 변경되고, 운영 룰은 실행 방식이나 품질 게이트가 바뀔 때 변경된다. 글로벌 룰은 시스템 전체의 계약이 바뀔 때만 변경된다.

---

## 4. 레이어드 구조가 평면 분리보다 나은 이유

기존 제안은 `document.rules.md`, `workflow.rules.md`, `agent.rules.md`, `validation.rules.md`, `hr.rules.md`를 같은 디렉터리에 두는 평면 분리 구조였다. 이 방식은 단일 파일 비대화 문제는 줄이지만, 장기적으로는 다음 한계가 있다.

- 업무 도메인 규칙과 운영 규칙이 같은 레벨에 있어 로딩 기준이 흐려진다.
- `marketing.rules.md`, `sales.rules.md`, `research.rules.md`, `finance.rules.md`가 추가되면 `.ai/rules/` 루트가 빠르게 비대해진다.
- 새 사용자가 어떤 파일이 업무 규칙이고 어떤 파일이 프로세스 규칙인지 이름만으로 판단하기 어렵다.
- 워크플로우, 검증, 에이전트 규칙이 특정 도메인에 속한다는 오해가 생길 수 있다.
- 향후 도구별 어댑터와 도메인 룰, 운영 룰의 변경 책임을 분리하기 어렵다.

반면 `domains/`와 `operations/`를 분리하면 다음 장점이 있다.

- 선택 로딩 기준이 단순해진다. 작업 주제에 따라 `domains/`를 고르고, 실행 방식에 따라 `operations/`를 고른다.
- 새 비즈니스 도메인을 추가해도 운영 규칙과 섞이지 않는다.
- 개발 중심 템플릿에서 범용 비즈니스 워크플로우 시스템으로 자연스럽게 확장된다.
- 파일 수가 늘어나도 디렉터리의 의미가 유지되어 탐색 비용이 낮다.
- 글로벌 계약은 더 안정적으로 유지되고, 변경 영향 범위가 좁아진다.

---

## 5. 용어 정의

| 용어 | 정의 |
|---|---|
| 글로벌 룰 | 모든 AI CLI가 항상 따라야 하는 최상위 계약 |
| 루트 어댑터 | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`처럼 도구가 글로벌 룰을 찾도록 안내하는 얇은 파일 |
| 도메인 룰 | 특정 업무 영역이나 작업 유형에 적용되는 규칙 |
| 운영 룰 | 작업 선택, 검증, 에이전트 협업, 실행 기록, 복구처럼 도메인과 무관하게 적용되는 실행 거버넌스 |
| 선택 로딩 | 현재 작업과 관련 있는 룰 파일만 추가로 읽는 방식 |
| 글로벌 계약 | SSoT, 우선순위, 파일 배치 원칙, 충돌 해결 방식처럼 전체 시스템에 적용되는 최소 규칙 |

이 문서에서는 `서브 룰`이라는 포괄적 표현보다 `도메인 룰`과 `운영 룰`을 우선 사용한다. `서브 룰`은 두 범주를 함께 부르는 일반 표현으로만 사용한다.

---

## 6. 현재 파일 스캔 결과와 이동 방향

| 현재 섹션 | 현재 성격 | 목표 위치 | 이동 근거 |
|---|---|---|---|
| `0. Multi AI CLI Rule Source` | 글로벌 계약 | `.ai/rules/rules.md` | 모든 CLI가 항상 알아야 하는 SSoT 선언 |
| `Rule Priority` | 글로벌 계약 | `.ai/rules/rules.md` | 충돌 해결 기준은 전역이어야 함 |
| `1. Language & Content Rules` | 문서화 도메인 | `.ai/rules/domains/documentation.rules.md` | 문서 작성과 언어 정책은 문서화 작업에 특화됨 |
| `2. Directory & Path Mapping` | 도메인별 경로 규칙 | `documentation.rules.md`, `development.rules.md`, `hr.rules.md` | 경로는 업무 도메인별로 달라짐 |
| `3. Workflow System v2 Rules` | 운영 거버넌스 | `.ai/rules/operations/workflow.rules.md` | Roadmap, Task, Run Record는 도메인 독립 실행 흐름 |
| `4. Agent System` | 운영 거버넌스 | `.ai/rules/operations/agent.rules.md` | 에이전트 역할과 협업 방식은 도메인보다 실행 체계에 가까움 |
| `5. L1/L2 Agent System` | 운영 거버넌스 | `.ai/rules/operations/agent.rules.md` | 리뷰, 승인, 에스컬레이션은 공통 작업 운영 규칙 |
| `6. Constraint Enforcement` | 혼합 | 글로벌, 도메인, 운영으로 분할 | 파일 무결성은 글로벌, HR/개발 제약은 도메인, 검증 제약은 운영 |
| `7. Validation System` | 운영 거버넌스 | `.ai/rules/operations/validation.rules.md` | 검증은 모든 도메인의 품질 게이트로 사용됨 |
| `8. Document Templates` | 문서화 및 도메인 규칙 | `documentation.rules.md` 중심, 일부 도메인으로 분산 | 템플릿 사용은 문서화 규칙이지만 HR/개발별 특수성이 있음 |
| `9. Workflow Systems` | 도메인 워크플로우와 운영 흐름 혼합 | 공통 흐름은 `workflow.rules.md`, HR/개발 특수 흐름은 각 도메인 | 실행 패턴과 업무 절차를 분리해야 함 |
| `10. Error Handling & Recovery` | 운영 거버넌스 | `workflow.rules.md`, `validation.rules.md`, `agent.rules.md` | 복구와 오류 처리는 실행 통제 규칙 |
| `11. Performance & Optimization` | 운영 거버넌스 | `agent.rules.md` | 컨텍스트 관리와 병렬 처리는 에이전트 운영 문제 |
| `12. Additional Rules` | 문서 무결성 반복 | `documentation.rules.md`, `validation.rules.md` | 메타데이터는 문서 규칙, 링크 검증은 검증 규칙 |
| `13. Enforcement & Compliance` | 거버넌스 혼합 | 글로벌, 운영으로 분할 | 버전 정책은 글로벌, 집행 절차와 지표는 운영 |
| `Project Guidelines (CLAUDE.md)` | 도구별/개발 도메인 혼합 | `CLAUDE.md`, `development.rules.md` | Claude 전용은 어댑터, Docker/build/runtime은 개발 도메인 |

---

## 7. 책임 경계

### 7.1 `rules.md`: 글로벌 계약

`rules.md`는 모든 AI CLI가 항상 읽는 가장 작은 안정 계층이어야 한다. 이 파일은 세부 업무 절차를 담지 않고, 어떤 규칙을 어디에서 찾고 어떤 우선순위로 적용할지 정의한다.

포함할 내용:

- `.ai/rules/rules.md`가 글로벌 SSoT라는 선언
- Codex CLI, Claude Code, Gemini CLI와 향후 AI CLI가 따를 공통 진입점
- 루트 어댑터는 얇은 안내 파일이라는 원칙
- 심볼릭 링크 금지
- 공유 규칙 중복 금지
- 규칙 우선순위
- `domains/`와 `operations/`의 역할
- 선택 로딩 원칙
- `docs/`는 한국어, `.ai/`는 영어라는 요약 원칙
- UTF-8 without BOM 저장 원칙
- 변경 시 검증과 변경 기록이 필요하다는 최소 거버넌스

포함하지 않을 내용:

- HR 평가 세부 절차
- 개발 문서 템플릿 세부 경로
- Docker, Makefile, 컨테이너 실행 절차
- L1/L2 상세 협업 프로토콜
- 검증 단계별 체크리스트
- 도구별 프롬프트 또는 어댑터 전용 문구

### 7.2 `domains/`: 업무 도메인 규칙

`domains/`는 작업 주제나 비즈니스 영역에 따라 달라지는 규칙을 보관한다. 도메인 룰은 "무엇을 만들고 어떤 업무 기준을 따라야 하는가"에 답한다.

초기 도메인:

- `documentation.rules.md`: 문서 작성, 언어 정책, 템플릿, 메타데이터, 링크 형식
- `development.rules.md`: 개발 문서, 코드 작업 전후 절차, Docker/Makefile/build/runtime 지침, 개발 산출물 경로
- `hr.rules.md`: HR 평가, 역할 정의, 평가 리포트, Meta Isolation, Pending Protocol

향후 추가 가능한 도메인:

- `marketing.rules.md`: 캠페인 문서, 메시지 톤, 채널별 산출물, 승인 흐름
- `research.rules.md`: 리서치 질문, 근거 수집, 출처 품질, 요약 형식
- `sales.rules.md`: 세일즈 자료, 고객 세그먼트, 제안서, CRM 업데이트 규칙
- `finance.rules.md`: 재무 분석, 예산 문서, 리스크 표시, 숫자 검증

도메인 룰은 서로 독립적으로 발전해야 한다. 예를 들어 HR 평가 기준을 바꿔도 개발 빌드 규칙이나 마케팅 캠페인 규칙에는 영향을 주지 않아야 한다.

### 7.3 `operations/`: 실행 및 거버넌스 규칙

`operations/`는 작업 도메인과 무관하게 "어떻게 실행하고 통제할 것인가"에 답한다. 이 계층은 모든 도메인 위에서 재사용되는 운영 체계다.

초기 운영 룰:

- `workflow.rules.md`: Roadmap, Task, Run Record, 실행 증거, 복구, 진행 상태 갱신
- `validation.rules.md`: 템플릿 검증, 메타데이터 검증, 링크 검증, 실행 가능한 검증 스크립트 처리
- `agent.rules.md`: 에이전트 역할, L1/L2 협업, 에스컬레이션, 컨텍스트 관리, 병렬 처리

워크플로우, 검증, 에이전트 규칙이 `domains/`가 아니라 `operations/`에 속해야 하는 이유는 명확하다. 이들은 HR, 개발, 마케팅, 리서치 같은 업무 주제의 내용이 아니라 작업을 실행하고 품질을 통제하는 방식이다. 같은 검증 절차는 개발 문서에도, HR 평가 리포트에도, 마케팅 캠페인 문서에도 적용될 수 있다. 같은 에이전트 협업 원칙도 도메인이 바뀌어도 유지된다.

---

## 8. Docker, Build, Runtime 지침의 위치

현재 `rules.md` 말미에는 Claude 관련 프로젝트 지침과 함께 Docker, Makefile, 컨테이너 실행 지침이 포함되어 있다. 이 내용은 글로벌 계약이나 운영 공통 규칙이 아니라 개발 도메인 규칙으로 보는 것이 맞다.

이유:

- Docker, Makefile, build, runtime은 소프트웨어 개발 작업에 특화된 실행 환경이다.
- HR 평가, 마케팅 캠페인, 리서치 요약, 재무 분석 작업에는 일반적으로 적용되지 않는다.
- 모든 작업에서 이 규칙을 로드하면 컨텍스트 비용이 증가한다.
- 개발 도메인으로 분리하면 개발 작업에서만 정확히 로드할 수 있다.

따라서 Docker/build/runtime 지침은 `.ai/rules/domains/development.rules.md`에 둔다. 단, "검증 가능한 변경 후 적절한 확인을 수행한다" 같은 일반 품질 원칙은 `rules.md` 또는 `operations/validation.rules.md`에 둘 수 있다.

---

## 9. 선택 로딩 전략

선택 로딩은 이번 아키텍처의 핵심이다. 모든 AI CLI는 먼저 `rules.md`를 읽고, 작업의 성격에 따라 필요한 도메인 룰과 운영 룰만 추가로 읽는다.

기본 흐름:

1. 루트 어댑터가 `.ai/rules/rules.md`를 읽도록 안내한다.
2. 에이전트는 사용자 요청을 분석해 작업 도메인을 식별한다.
3. 해당 도메인 파일을 `domains/`에서 로드한다.
4. 실행 방식에 필요한 운영 파일을 `operations/`에서 로드한다.
5. 도메인과 운영 규칙이 충돌하면 `rules.md`의 우선순위에 따라 해결한다.

예시:

| 사용자 요청 | 로드할 도메인 룰 | 로드할 운영 룰 |
|---|---|---|
| 개발 아키텍처 문서 작성 | `documentation.rules.md`, `development.rules.md` | `workflow.rules.md`, `validation.rules.md` |
| Docker 빌드 오류 분석 | `development.rules.md` | `validation.rules.md` |
| HR 직무 평가 리포트 작성 | `documentation.rules.md`, `hr.rules.md` | `workflow.rules.md`, `validation.rules.md` |
| 마케팅 캠페인 계획 작성 | `documentation.rules.md`, 향후 `marketing.rules.md` | `workflow.rules.md` |
| 재무 분석 보고서 검토 | `documentation.rules.md`, 향후 `finance.rules.md` | `validation.rules.md` |
| 에이전트 협업 프로세스 조정 | 필요 시 없음 | `agent.rules.md`, `workflow.rules.md` |

선택 로딩 기준은 `.ai/rules/README.md`와 `rules.md`에 짧게 명시하고, 각 룰 파일의 상단에도 "언제 로드하는가"를 포함한다.

---

## 10. 네이밍 규칙

룰 파일 이름은 다음 규칙을 따른다.

- 파일명은 소문자와 하이픈 또는 단어형 소문자를 사용한다.
- 룰 파일은 `.rules.md` 접미사를 사용한다.
- `domains/`에는 업무 또는 작업 도메인 이름을 사용한다.
- `operations/`에는 실행 통제 기능 이름을 사용한다.
- 루트에는 `rules.md`와 `README.md`만 둔다.

초기 파일명은 다음과 같이 고정한다.

```text
.ai/rules/domains/documentation.rules.md
.ai/rules/domains/development.rules.md
.ai/rules/domains/hr.rules.md
.ai/rules/operations/workflow.rules.md
.ai/rules/operations/validation.rules.md
.ai/rules/operations/agent.rules.md
```

`document.rules.md` 대신 `documentation.rules.md`를 권장한다. `documentation`은 업무 도메인 이름으로 더 명확하며, 문서 파일 자체가 아니라 문서화 활동 전체를 의미한다.

---

## 11. 하위 룰 파일 권장 구조

각 도메인 룰과 운영 룰은 같은 기본 골격을 갖는다.

```markdown
# [Rule Name]

## Scope
- 이 파일이 적용되는 작업 범위

## Load When
- 이 파일을 로드해야 하는 조건

## Responsibilities
- 이 파일이 관리하는 규칙

## Rules
- 실제 규칙 본문

## Validation
- 적용 후 확인해야 하는 항목

## Related Rules
- 함께 로드될 수 있는 관련 룰 파일
```

이 구조는 장기 유지보수에 중요하다. 새 도메인이 추가될 때 작성자가 기존 파일 형식을 복사해 일관된 품질로 확장할 수 있고, 에이전트도 각 파일의 적용 범위를 빠르게 판단할 수 있다.

---

## 12. 마이그레이션 전략

마이그레이션은 한 번에 모든 규칙을 이동하는 방식보다 증분 방식이 안전하다. 기존 AI CLI가 계속 `.ai/rules/rules.md`를 글로벌 진입점으로 인식해야 하며, 루트 어댑터의 동작도 유지되어야 한다.

### Phase 1. 현 상태 안정화

- `.ai/rules/rules.md`를 현재 글로벌 SSoT로 유지한다.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`가 모두 `.ai/rules/rules.md`를 먼저 읽도록 안내하는지 확인한다.
- 심볼릭 링크가 없는지 확인한다.
- 기존 문서 중 인코딩이 깨진 파일은 이번 구조 전환과 분리해 별도 정비 항목으로 둔다.

### Phase 2. 디렉터리 골격 생성

- `.ai/rules/domains/`를 생성한다.
- `.ai/rules/operations/`를 생성한다.
- 아직 내용을 이동하지 않더라도 `README.md`에 목표 구조와 로딩 원칙을 먼저 기록한다.
- 단, 빈 룰 파일을 무분별하게 선점하지 않는다. 실제 이동할 규칙이 있을 때 파일을 만든다.

### Phase 3. `rules.md`를 글로벌 계약으로 축소

- SSoT, 우선순위, 어댑터 정책, 심볼릭 링크 금지, 선택 로딩 원칙을 유지한다.
- 세부 도메인 절차와 운영 절차는 이동 대상으로 표시한다.
- 전환 기간에는 `rules.md`에서 새 파일 위치를 안내해 기존 에이전트가 길을 잃지 않게 한다.

### Phase 4. 1차 도메인 룰 분리

- `documentation.rules.md`를 먼저 만든다.
- 언어 정책, 문서 경로, 템플릿, 메타데이터, 링크 규칙을 이동한다.
- `development.rules.md`를 만든다.
- 개발 문서 경로, Docker/Makefile/build/runtime, 개발 산출물 규칙을 이동한다.
- `hr.rules.md`를 만든다.
- HR 평가 입력/출력, 평가 제약, 보고서 규칙을 이동한다.

### Phase 5. 운영 룰 분리

- `workflow.rules.md`를 만든다.
- Roadmap, Task, Run Record, 실행 증거, 복구 흐름을 이동한다.
- `validation.rules.md`를 만든다.
- 템플릿 검증, 메타데이터 검증, 링크 검증, 실행 검증 원칙을 이동한다.
- `agent.rules.md`를 만든다.
- 에이전트 목록, L1/L2 협업, 에스컬레이션, 컨텍스트 관리, 병렬 처리 규칙을 이동한다.

### Phase 6. 어댑터 및 문서 갱신

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 계속 얇게 유지한다.
- 도구별 특수 지침은 해당 어댑터에만 둔다.
- 공유 규칙 본문을 어댑터에 복제하지 않는다.
- `.ai/rules/README.md`에 레이어 설명, 선택 로딩 규칙, 파일 추가 기준을 기록한다.

### Phase 7. 검증 및 정리

- 중복 규칙이 남아 있는지 확인한다.
- `rules.md`가 글로벌 계약만 포함하는지 확인한다.
- 새 룰 파일이 UTF-8 without BOM인지 확인한다.
- `.ai/` 하위 룰 문서는 영어로 작성되었는지 확인한다.
- 이 제안 문서처럼 `docs/` 하위 문서는 한국어로 유지되는지 확인한다.
- 기존 루트 어댑터가 여전히 정상적으로 글로벌 룰을 안내하는지 확인한다.

---

## 13. 하위 호환성 전략

전환 중에도 `.ai/rules/rules.md`는 계속 유효해야 한다. 기존 에이전트가 새 디렉터리를 즉시 인식하지 못하더라도 최소 글로벌 규칙은 계속 적용되어야 한다.

하위 호환성 원칙:

- `rules.md` 경로는 변경하지 않는다.
- 루트 어댑터의 기본 문구는 유지한다.
- `rules.md`에 새 룰 위치를 안내하는 인덱스 섹션을 둔다.
- 최소 한 번의 전환 기간 동안 이전 섹션 제목과 새 위치의 매핑을 제공한다.
- 중복 본문은 장기간 유지하지 않는다. 전환 기간이 끝나면 원문은 하위 파일로만 유지한다.
- 새 도메인 룰이 없더라도 기존 작업은 `rules.md`만으로 최소 동작해야 한다.

권장 전환 문구:

```markdown
## Rule Layers

This file is the global rule contract. Load additional rules only when relevant:

- Domain rules: `.ai/rules/domains/*.rules.md`
- Operational rules: `.ai/rules/operations/*.rules.md`
```

---

## 14. 장기 유지보수 전략

### 14.1 새 도메인 추가 기준

새 도메인 룰은 다음 조건을 만족할 때만 추가한다.

- 기존 도메인 룰에 넣으면 책임이 흐려진다.
- 반복적으로 사용되는 업무 규칙이 있다.
- 특정 산출물, 검증 기준, 승인 흐름이 존재한다.
- 선택 로딩으로 컨텍스트 절감 효과가 있다.

단일 작업을 위해 새 도메인 파일을 만들지 않는다. 예외적이거나 일회성인 지침은 작업 문서나 사용자 요청 안에서 처리한다.

### 14.2 운영 룰 추가 기준

새 운영 룰은 여러 도메인에 걸쳐 재사용되는 실행 규칙일 때만 추가한다. 예를 들어 권한 관리, 감사 로그, 외부 도구 사용 정책이 여러 도메인에 공통으로 필요해지면 `operations/`에 별도 파일을 둘 수 있다.

### 14.3 변경 관리

- 글로벌 계약 변경은 가장 보수적으로 처리한다.
- 도메인 룰 변경은 해당 도메인 산출물과 검증 절차를 함께 확인한다.
- 운영 룰 변경은 여러 도메인에 영향을 줄 수 있으므로 변경 이유와 영향 범위를 명시한다.
- 버전과 변경 기록은 `rules.md` 또는 `.ai/rules/README.md`에서 추적한다.

---

## 15. 위험과 대응

| 위험 | 영향 | 대응 |
|---|---|---|
| 룰 파일이 너무 많이 늘어남 | 선택 로딩 기준이 흐려짐 | `domains/`와 `operations/` 추가 기준을 엄격히 적용 |
| 에이전트가 필요한 하위 룰을 로드하지 않음 | 도메인 규칙 누락 | `rules.md`와 각 룰 파일 상단에 `Load When` 명시 |
| 운영 룰과 도메인 룰이 중복됨 | 충돌과 유지보수 비용 증가 | 실행 방식은 `operations/`, 업무 기준은 `domains/`로 분리 |
| 개발 중심 규칙이 글로벌에 남음 | 비개발 도메인 확장 방해 | Docker/build/runtime은 `development.rules.md`로 이동 |
| 전환 중 기존 CLI 동작이 깨짐 | 자동 룰 로딩 실패 | `rules.md` 경로 유지, 어댑터 경량화 유지, 인덱스 섹션 제공 |
| 인코딩 문제 재발 | 한국어 문서 손상 | UTF-8 without BOM 원칙과 검증 단계 유지 |

---

## 16. 완료 기준

- `.ai/rules/rules.md`가 글로벌 계약만 포함한다.
- `.ai/rules/domains/`와 `.ai/rules/operations/`의 책임 경계가 명확하다.
- 루트 어댑터는 얇은 안내 파일로 유지된다.
- 공유 규칙 본문이 어댑터에 복제되지 않는다.
- 심볼릭 링크가 생성되지 않는다.
- Docker/build/runtime 지침은 `development.rules.md`로 이동한다.
- 워크플로우, 검증, 에이전트 규칙은 `operations/`에 위치한다.
- 문서화, 개발, HR 규칙은 `domains/`에 위치한다.
- 새 비즈니스 도메인을 추가할 수 있는 기준과 위치가 문서화되어 있다.
- 모든 룰 파일은 UTF-8 without BOM으로 저장된다.
- `.ai/` 하위 룰 문서는 영어로 작성되고, `docs/` 하위 계획 문서는 한국어로 유지된다.

---

## 17. 권장 실행 순서

1. `.ai/rules/README.md`에 레이어드 아키텍처 원칙을 먼저 반영한다.
2. `.ai/rules/domains/`와 `.ai/rules/operations/` 디렉터리를 만든다.
3. `rules.md`에 선택 로딩 인덱스와 레이어 설명을 추가한다.
4. `documentation.rules.md`를 분리한다.
5. `development.rules.md`를 분리하고 Docker/build/runtime 지침을 이동한다.
6. `workflow.rules.md`와 `validation.rules.md`를 분리한다.
7. `agent.rules.md`를 분리한다.
8. `hr.rules.md`를 분리한다.
9. `rules.md`에서 이동 완료된 세부 본문을 제거한다.
10. 루트 어댑터가 여전히 얇은 상태인지 확인한다.
11. 심볼릭 링크, 인코딩, 중복 규칙, 선택 로딩 안내를 검증한다.

이 순서는 안전한 전환을 우선한다. 가장 먼저 구조와 인덱스를 만들고, 그 다음 변경 영향이 큰 문서화와 개발 도메인을 분리한다. 운영 룰은 여러 도메인에 영향을 주므로 도메인 분리 후 이동하는 것이 검토하기 쉽다.

---

## 18. 후속 결정 필요 항목

- 전환 기간 동안 `rules.md`에 기존 섹션 본문을 얼마나 오래 유지할지 결정해야 한다.
- `development.rules.md`에 코드 작업 규칙까지 포함할지, 개발 문서와 런타임 지침만 포함할지 결정해야 한다.
- HR 평가가 핵심 도메인인지 예제 도메인인지 결정해야 한다.
- 마케팅, 리서치, 세일즈, 재무 도메인을 언제 실제 파일로 생성할지 기준을 정해야 한다.
- 운영 룰 변경 시 검토자를 별도로 지정할지 결정해야 한다.
- 기존 `docs/plan` 문서 일부에서 보이는 한글 인코딩 깨짐을 별도 정비 작업으로 처리할지 결정해야 한다.

