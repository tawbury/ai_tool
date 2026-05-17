# Meta
- Document Type: Design
- Document ID: DESIGN-AGENT-RULES-CONFIGURATION-20260517
- Title: 에이전트 규칙 설정 연결 설계
- Status: Draft
- Created: 2026-05-17
- Updated: 2026-05-17
- Author: Codex
- Reviewer: TBD
- Parent Document: [[agent_rules_connection_enhancement_plan.md]]
- Related Reference: [[rules.md]], [[agent.rules.md]], [[documentation.rules.md]], [[workflow.rules.md]], [[validation.rules.md]]
- Version: 0.1.0
- Tags: design, ai-agents, rules, markdown-config, metadata

---

# 에이전트 규칙 설정 연결 설계

## 1. 목적

이 문서는 `.ai/rules/rules.md`, `.ai/rules/operations/agent.rules.md`, `.ai/agents/*.agent.md`, 향후 `docs/plan/*.md`가 Markdown 내부 YAML/JSON 설정 블록을 활용하는 방식을 정의한다.

핵심 목표는 별도 설정 파일을 기본값으로 만들지 않고, 사람이 읽는 Markdown 설명과 기계가 읽는 연결 메타데이터를 같은 문서 안에서 유지하는 것이다.

## 2. 설계 결정

### 2.1 기본값은 Markdown 내부 YAML 블록

구조화 설정이 필요하면 Markdown 내부 fenced `yaml` 블록을 기본으로 사용한다.

YAML을 기본값으로 두는 이유는 다음과 같다.

- Markdown 문서 안에서 사람이 읽기 쉽다.
- frontmatter와 문법적 친화성이 높다.
- 라우팅, 검증, 연결 메타데이터처럼 계층형 목록이 많은 설정에 적합하다.

### 2.2 JSON 블록 사용 조건

JSON 블록은 다음 상황에만 사용한다.

- JSON Schema 예시를 문서 안에 포함한다.
- 외부 도구가 JSON만 입력으로 받는다.
- 엄격한 데이터 구조, 타입 예시, API payload 예시가 필요하다.

일반 라우팅 매트릭스나 문서 실행 계획 구조화 데이터에는 YAML을 우선한다.

### 2.3 JSONL 사용 조건

JSONL은 실행 이벤트 로그처럼 append-only 데이터가 실제로 필요할 때만 사용한다.

일반 계획 문서, 규칙 문서, agent 연결 메타데이터에는 JSONL을 사용하지 않는다.

### 2.4 standalone YAML/JSON 파일은 v1 범위 밖

`manifest.yml`, `manifest.schema.json`, `*.json`, `*.jsonl` 파일은 v1 기본 구현 범위에 포함하지 않는다.

별도 파일은 다음 필요성이 검증된 뒤 후속 phase에서 추가한다.

- 여러 Markdown 문서가 동일 설정을 공유해야 한다.
- 자동 validator가 Markdown 내부 설정 블록을 안정적으로 읽기 어렵다.
- CLI adapter가 중앙 설정 파일을 직접 읽어야 한다.
- schema 검증과 버전 관리가 Markdown 내부 블록보다 명확히 단순하다.

## 3. 공통 설정 블록 형식

설정 블록은 HTML 주석 앵커와 fenced code block을 함께 사용한다.

````markdown
<!-- ai-config:start agent-routing v1 -->
```yaml
source_of_truth: .ai/rules/rules.md
```
<!-- ai-config:end -->
````

규칙:

- 시작 앵커 형식은 `<!-- ai-config:start <name> <version> -->`을 사용한다.
- 종료 앵커는 `<!-- ai-config:end -->`를 사용한다.
- `<name>`은 `agent-routing`, `plan-structure`, `validation-map`처럼 kebab-case로 작성한다.
- `<version>`은 `v1`, `v2`처럼 짧은 버전 식별자를 사용한다.
- 설정 블록은 가까운 본문 설명과 의미가 일치해야 한다.
- 설정 블록은 규칙 본문이나 역할 설명을 대체하지 않는다.

## 4. 파일별 설계

### 4.1 `.ai/rules/rules.md`

`rules.md`는 전역 계약만 정의한다.

추가할 원칙:

- Markdown 문서 내부에 fenced YAML 또는 JSON 설정 블록을 둘 수 있다.
- 설정 블록은 라우팅, 검증, 연결 메타데이터를 기계 판독 가능하게 보조한다.
- 설정 블록은 규칙 본문을 대체하지 않는다.
- 설정 블록은 HTML 주석 앵커로 식별한다.
- 상세 에이전트 라우팅은 `rules.md`가 아니라 `.ai/rules/operations/agent.rules.md`가 소유한다.

`rules.md`에는 에이전트별 스킬, validator 상세 목록, domain별 매트릭스를 넣지 않는다.

### 4.2 `.ai/rules/operations/agent.rules.md`

`agent.rules.md`는 공통 에이전트 라우팅 인덱스를 소유한다.

설정 블록 필드:

- `agent`: 에이전트 식별자
- `file`: `.ai/agents/*.agent.md` 경로
- `default_domain_rules`: 기본 도메인 규칙 목록
- `default_operation_rules`: 기본 운영 규칙 목록
- `validators`: 기본 validator 목록
- `primary_use_cases`: 주요 사용 사례 목록

예시:

````markdown
<!-- ai-config:start agent-routing v1 -->
```yaml
source_of_truth: .ai/rules/rules.md
agents:
  - agent: developer
    file: .ai/agents/developer.agent.md
    default_domain_rules:
      - .ai/rules/domains/development.rules.md
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/developer_skill_validator.md
    primary_use_cases:
      - software architecture
      - implementation
      - code review
  - agent: hr
    file: .ai/agents/hr.agent.md
    default_domain_rules:
      - .ai/rules/domains/hr.rules.md
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/hr_skill_validator.md
    primary_use_cases:
      - HR evaluation
      - role management
      - performance review
```
<!-- ai-config:end -->
````

이 블록은 `.ai/agents/*.agent.md`의 세부 정의를 대체하지 않는다. 공통 라우팅 인덱스로만 사용한다.

### 4.3 `.ai/agents/*.agent.md`

각 agent 파일은 frontmatter에 연결 메타데이터를 둔다.

권장 필드:

```yaml
domain_rules:
  - .ai/rules/domains/development.rules.md
  - .ai/rules/domains/documentation.rules.md
operation_rules:
  - .ai/rules/operations/agent.rules.md
  - .ai/rules/operations/workflow.rules.md
  - .ai/rules/operations/validation.rules.md
validators:
  - .ai/validators/developer_skill_validator.md
```

규칙:

- agent 본문에는 상세 역할, 책임, 스킬 설명을 유지한다.
- 규칙 본문을 agent 파일에 복사하지 않는다.
- frontmatter는 로딩 후보를 알려주는 메타데이터이며 최종 우선순위는 `.ai/rules/rules.md`를 따른다.
- 도메인 규칙이 아직 없는 agent는 `domain_rules: []` 또는 후보 상태를 명시한다.

### 4.4 `docs/plan/*.md`

향후 plan 문서는 필요한 경우 Markdown 내부 YAML/JSON 설정 블록을 둘 수 있다.

용도:

- 실행 계획의 phase 구조화
- 산출물과 validator 매핑
- 후속 자동 검증을 위한 체크리스트 구조화
- 여러 agent가 공유해야 하는 제한된 라우팅 힌트

예시:

````markdown
<!-- ai-config:start plan-structure v1 -->
```yaml
phases:
  - id: phase-1
    title: 현황 정리
    outputs:
      - docs/plan/agent_rules_configuration_design.md
    validators:
      - .ai/validators/structure_validator.md
```
<!-- ai-config:end -->
````

별도 `manifest.yml`, `*.json`, `*.jsonl` 파일은 여러 문서에서 공유되거나 자동 검증 도구가 직접 읽어야 할 때만 추가한다.

## 5. 배치 원칙

공통 정책의 배치는 다음과 같이 고정한다.

| 정책 영역 | 위치 |
|---|---|
| 전역 우선순위, 규칙 레이어, 선택 로딩, 설정 블록 원칙 | `.ai/rules/rules.md` |
| 에이전트 라우팅, L1/L2 협업, 에스컬레이션 | `.ai/rules/operations/agent.rules.md` |
| 문서 작성, metadata, 링크, Markdown 내부 설정 블록 작성 정책 | `.ai/rules/domains/documentation.rules.md` |
| 개별 에이전트 역할과 스킬 연결 | `.ai/agents/*.agent.md` |
| 실제 스킬 수행 절차 | `.ai/skills/**` |
| 검증 기준 | `.ai/validators/**` |

v1에서는 신규 도메인 규칙 파일을 만들지 않는다.

## 6. 구현 지침

`.ai/` 아래 규칙 문서에 들어갈 실제 구현 지침은 영어로 작성한다. `docs/plan/` 아래 설계 및 계획 문서는 한국어로 작성한다.

### 6.1 실사용 개선사항 환류 원칙

이 AI 도구의 목적은 도구 자체 설계에 머무르지 않고 개발 및 기타 프로젝트에서 반복적으로 활용되는 것이다. 따라서 실제 프로젝트 사용 중 반복 가능한 개선사항이 발견되면, 다음 실행부터 별도 사용자 지시 없이 반영될 수 있도록 가장 작은 공유 규칙 레이어에 기록한다.

배치 기준:

- 여러 CLI와 모든 작업에 적용되는 전역 원칙은 `.ai/rules/rules.md`에 기록한다.
- 문서 작성, metadata, 링크, Markdown 내부 설정 블록 작성 방식은 `.ai/rules/domains/documentation.rules.md`에 기록한다.
- 에이전트 라우팅, 협업, context loading, validator 연결은 `.ai/rules/operations/agent.rules.md`에 기록한다.
- 개별 에이전트 역할, 스킬, 기본 로딩 후보는 `.ai/agents/*.agent.md` frontmatter와 본문에 기록한다.
- 특정 CLI만의 동작은 root adapter 또는 해당 도구 adapter에만 기록한다.

운영 규칙:

- 반복 지시가 필요해지는 항목은 규칙화 후보로 본다.
- 규칙화할 때는 기존 규칙 파일을 우선 확장하고, 신규 도메인 규칙 파일은 반복 유지보수 필요가 검증된 뒤 만든다.
- 규칙 변경은 관련 문서, validator, agent frontmatter와 함께 검증한다.
- 큰 변경은 `docs/plan/` 또는 `docs/reports/`에 한국어로 근거와 결과를 남긴다.

### 6.2 적용 순서

적용 순서:

1. `rules.md`에 Markdown 내부 설정 블록 전역 원칙을 추가한다.
2. `documentation.rules.md`에 문서 작성 시 설정 블록 작성 정책을 추가한다.
3. `agent.rules.md`에 공통 에이전트 라우팅 YAML 블록을 추가한다.
4. `.ai/agents/*.agent.md` frontmatter에 연결 메타데이터를 추가한다.
5. 필요성이 검증될 때만 standalone manifest 도입을 별도 phase로 검토한다.

## 7. 검증 기준

문서 검증:

- 이 문서는 한국어로 작성되어야 한다.
- metadata의 `Parent Document`, `Related Reference`는 실제 파일명을 참조해야 한다.
- 모든 fenced YAML/JSON 예시는 닫혀 있어야 한다.

규칙 검증:

- `rules.md`에는 전역 원칙만 있어야 한다.
- `agent.rules.md`에는 공통 라우팅 블록만 있어야 하며 스킬 본문을 복사하지 않아야 한다.
- `.agent.md` frontmatter는 YAML로 파싱 가능해야 한다.

회귀 검증:

- 루트 adapter 파일은 계속 `.ai/rules/rules.md`만 가리킨다.
- 심볼릭 링크를 만들지 않는다.
- 신규 도메인 규칙 파일을 만들지 않는다.

## 8. 비범위

다음 항목은 v1 범위 밖이다.

- Markdown 설정 블록 parser 구현
- 자동 validator 스크립트 구현
- `.ai/agents/manifest.yml` 생성
- `manifest.schema.json` 생성
- JSONL 실행 로그 저장소 생성
- `pm.rules.md`, `finance.rules.md`, `contents.rules.md` 신규 생성
