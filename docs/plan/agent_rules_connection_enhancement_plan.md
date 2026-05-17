# Meta
- Document Type: Plan
- Document ID: PLAN-AGENT-RULES-CONNECTION-20260517
- Title: 에이전트 규칙 연결 고도화 계획
- Status: Draft
- Created: 2026-05-17
- Updated: 2026-05-17
- Author: Codex
- Reviewer: TBD
- Parent Document: [[global_rules_split_proposal_plan.md]]
- Related Reference: [[agent_rules_configuration_design.md]], [[rules.md]], [[agent.rules.md]], [[documentation.rules.md]], [[workflow.rules.md]], [[validation.rules.md]]
- Version: 0.2.0
- Tags: plan, ai-agents, rules, orchestration, metadata

---

# 에이전트 규칙 연결 고도화 계획

## 1. 목적

`.ai/rules/rules.md`를 단일 진실 공급원으로 유지하면서, `.ai/rules/operations/agent.rules.md`와 `.ai/agents/*.agent.md`가 필요한 규칙, 스킬, 워크플로우, 검증 기준을 일관되게 참조하도록 연결 구조를 정리한다.

이 계획의 v1 범위는 별도 설정 파일을 늘리는 것이 아니라, Markdown 문서 내부의 YAML/JSON 설정 블록과 agent frontmatter를 우선 활용해 사람이 읽는 규칙 설명과 기계가 읽는 연결 메타데이터를 같은 문서 안에서 동기화하는 것이다.

상세 설계는 [[agent_rules_configuration_design.md]]를 따른다.

## 2. 현재 판단

신규 도메인 규칙 파일을 즉시 만들기보다 기존 운영 규칙인 `.ai/rules/operations/agent.rules.md`를 확장하는 방향이 우선이다.

판단 근거는 다음과 같다.

- 에이전트 라우팅, L1/L2 협업, 컨텍스트 로딩은 특정 업무 도메인이 아니라 여러 도메인에 공통 적용되는 운영 규칙이다.
- `.ai/rules/rules.md`는 전역 계약만 보유해야 하며, 상세 에이전트 라우팅을 직접 포함하면 전역 규칙이 비대해진다.
- `.ai/agents/*.agent.md`는 개별 에이전트의 역할과 스킬을 설명하되, 공통 라우팅 인덱스 역할까지 맡으면 중복과 불일치가 생긴다.
- 별도 `manifest.yml`은 자동 검증 도구가 직접 읽어야 할 필요가 검증된 뒤 도입해도 늦지 않다.

## 3. 목표 구조

v1 목표 구조는 다음과 같다.

```text
.ai/
  rules/
    rules.md
    operations/
      agent.rules.md
      workflow.rules.md
      validation.rules.md
    domains/
      documentation.rules.md
      development.rules.md
      hr.rules.md

  agents/
    README.md
    pm.agent.md
    developer.agent.md
    contents-creator.agent.md
    finance.agent.md
    hr.agent.md
```

`manifest.yml`, `manifest.schema.json`, `*.jsonl` 로그 파일은 v1 기본 구조에 포함하지 않는다. 여러 문서에서 공유되는 중앙 인덱스가 실제로 필요하거나, 자동 검증 도구가 Markdown을 처리하기 어렵다는 근거가 생길 때 Phase 4 이후 선택 사항으로 검토한다.

## 4. 연결 원칙

### 4.1 전역 규칙과 에이전트 파일의 책임 분리

- `.ai/rules/rules.md`: 전역 계약, 우선순위, 규칙 레이어, 선택 로딩 원칙, Markdown 내부 설정 블록 원칙만 정의한다.
- `.ai/rules/operations/agent.rules.md`: 공통 에이전트 목록, 라우팅 매트릭스, L1/L2 협업, 에스컬레이션, 컨텍스트 로딩 원칙을 정의한다.
- `.ai/agents/*.agent.md`: 개별 에이전트의 역할, 범위, 스킬, frontmatter 연결 메타데이터를 정의한다.
- `.ai/rules/domains/documentation.rules.md`: 문서 작성과 문서 내부 설정 블록 작성 정책을 둔다.
- `.ai/skills/**`: 실제 수행 능력과 절차를 정의한다.
- `.ai/validators/**`: 구조, 산출물, 스킬 검증 기준을 둔다.

### 4.2 Markdown 내부 설정 블록 우선

Markdown 문서 안에서 구조화 설정이 필요하면 fenced `yaml` 또는 `json` 블록을 사용한다. 기본값은 YAML이며, JSON은 JSON Schema 예시나 외부 도구 연동처럼 엄격한 구조가 필요한 경우에만 사용한다.

권장 식별 방식은 HTML 주석 앵커다.

````markdown
<!-- ai-config:start agent-routing v1 -->
```yaml
source_of_truth: .ai/rules/rules.md
```
<!-- ai-config:end -->
````

설정 블록은 규칙 본문을 대체하지 않는다. 라우팅, 검증, 연결 메타데이터를 기계 판독 가능하게 보조하는 용도로만 사용한다.

### 4.3 중복 금지

- 에이전트 파일에 전역 규칙 본문을 복사하지 않는다.
- `agent.rules.md`에 개별 에이전트의 상세 스킬 본문을 복사하지 않는다.
- README는 탐색 문서로 유지하고 규칙 본문을 중복하지 않는다.
- 루트 adapter 파일은 `.ai/rules/rules.md`를 가리키는 얇은 진입점으로 유지한다.
- 규칙 파일과 규칙 디렉터리에 심볼릭 링크를 만들지 않는다.

## 5. 구현 단계

### Phase 1: 현황 정리

- `.ai/agents/*.agent.md`의 frontmatter 필드를 조사한다.
- 각 에이전트의 `role`, `level`, `tools`, `skills`, `scope` 필드가 일관적인지 확인한다.
- `.ai/rules/operations/agent.rules.md`의 에이전트 목록이 실제 파일 목록과 일치하는지 확인한다.
- 기존 plan 및 설계 문서의 metadata 링크가 실제 파일을 참조하는지 확인한다.

완료 기준:

- 에이전트 파일 목록과 운영 규칙의 에이전트 목록이 일치한다.
- 깨진 링크나 존재하지 않는 validator 참조가 있으면 후속 수정 항목으로 기록한다.

### Phase 2: `rules.md` 전역 원칙 보강

`.ai/rules/rules.md`에는 다음 전역 원칙만 추가한다.

- Markdown 내부에 fenced YAML/JSON 설정 블록을 둘 수 있다.
- 설정 블록은 규칙 본문을 대체하지 않는다.
- 설정 블록은 라우팅, 검증, 연결 메타데이터를 보조한다.
- HTML 주석 앵커로 설정 블록의 시작과 끝을 식별한다.

완료 기준:

- 전역 원칙만 존재하고 에이전트별 상세 라우팅은 들어가지 않는다.
- `.ai/` 아래 실제 구현 지침은 영어로 작성된다.

### Phase 3: `agent.rules.md` 라우팅 매트릭스 추가

`.ai/rules/operations/agent.rules.md`에 Markdown 내부 YAML 설정 블록으로 공통 라우팅 인덱스를 추가한다.

필드:

- `agent`
- `file`
- `default_domain_rules`
- `default_operation_rules`
- `validators`
- `primary_use_cases`

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
```
<!-- ai-config:end -->
````

완료 기준:

- 공통 에이전트 라우팅 정보가 운영 규칙에 정리된다.
- 개별 에이전트의 상세 역할 또는 스킬 본문은 복사되지 않는다.

### Phase 4: `.agent.md` frontmatter 표준화

각 `.agent.md` 파일의 frontmatter에 연결 메타데이터를 추가하거나 정리한다.

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

주의 사항:

- 이 필드는 규칙 본문이 아니라 연결 메타데이터다.
- 실제 우선순위는 계속 `.ai/rules/rules.md`가 소유한다.
- 도메인 규칙이 아직 없는 에이전트는 빈 배열 또는 후보 상태를 명시한다.

완료 기준:

- 모든 에이전트 파일의 frontmatter가 YAML로 파싱 가능한 구조다.
- CLI나 검증 도구가 frontmatter만으로 기본 로딩 후보를 계산할 수 있다.

### Phase 5: 별도 manifest 도입 여부 검토

Markdown 내부 설정 블록과 agent frontmatter만으로 부족한 경우에만 `.ai/agents/manifest.yml` 또는 schema 파일을 검토한다.

도입 조건:

- 여러 문서에서 동일 라우팅 인덱스를 반복 참조해야 한다.
- 자동 검증 도구가 Markdown 내부 설정 블록을 안정적으로 읽기 어렵다.
- CLI adapter가 중앙 설정 파일을 직접 읽어야 한다.
- 설정 버전 관리나 schema 검증이 별도 파일일 때 명확히 단순해진다.

JSONL은 실행 이벤트 로그처럼 append-only 데이터가 실제로 필요할 때만 검토한다.

## 6. 신규 도메인 규칙 파일 생성 기준

신규 도메인 규칙 파일은 다음 조건 중 2개 이상을 만족할 때만 만든다.

- 특정 도메인의 산출물 형식이 반복적으로 사용된다.
- 해당 도메인 전용 템플릿 또는 validator가 존재한다.
- 기존 `documentation.rules.md` 또는 `development.rules.md`에 넣기에는 책임 경계가 모호하다.
- 에이전트별 스킬이 아니라 도메인 전체에 적용되는 규칙이 필요하다.
- 여러 CLI에서 동일 도메인 규칙을 반복 로드해야 한다.

현재 v1에서는 `pm.rules.md`, `finance.rules.md`, `contents.rules.md`를 만들지 않는다. 필요한 경우 후속 phase에서 근거와 함께 추가한다.

## 7. 검증 계획

### 7.1 문서 검증

- `docs/plan/agent_rules_configuration_design.md`와 이 문서가 한국어로 작성되어 있는지 확인한다.
- metadata의 `Parent Document`, `Related Reference`가 실제 파일명을 참조하는지 확인한다.
- Markdown 내부 YAML/JSON 예시의 fenced block이 닫혀 있는지 확인한다.

### 7.2 규칙 검증

- `rules.md`에는 전역 원칙만 있고 에이전트 상세 라우팅이 들어가지 않는지 확인한다.
- `agent.rules.md`에는 공통 에이전트 라우팅 블록만 있고 스킬 본문이 복사되지 않는지 확인한다.
- `.agent.md` frontmatter가 YAML로 파싱 가능한 구조인지 확인한다.

### 7.3 회귀 확인

- 루트 adapter 파일은 계속 `.ai/rules/rules.md`만 가리키는 얇은 진입점으로 유지한다.
- 심볼릭 링크를 만들지 않는다.
- 신규 도메인 규칙 파일을 만들지 않는다.
- `.ai/` 아래 실제 구현 지침은 영어로 작성하도록 설계한다.

## 8. 완료 기준

- Markdown 내부 YAML/JSON 설정 블록을 우선하는 설계가 문서화된다.
- `manifest.yml`은 v1 기본 목표가 아니라 Phase 4 이후 선택 사항으로 낮아진다.
- `agent.rules.md`와 `.agent.md`의 책임 경계가 명확해진다.
- 별도 신규 도메인 규칙 파일 없이 공통 운영 정책은 `agent.rules.md`, 문서 작성 정책은 `documentation.rules.md`, 전역 원칙은 `rules.md`에 배치하는 방향이 확정된다.
