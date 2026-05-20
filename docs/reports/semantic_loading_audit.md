# .ai OS 시맨틱 로딩 아키텍처 감사 보고서

## 1. 요약

`.ai OS`는 아직 orchestration/runtime worker가 없지만, 이미 규칙, 스킬, 워크플로우, validator 문서의 양과 의미 밀도가 커져 있다. 현재 상태에서 모든 `.ai` 문서를 항상 로딩하면 context bloat가 빠르게 발생하고, 실행 계약과 사람 검토 기준, 철학, 예시가 섞여 작업 판단을 흐릴 가능성이 높다.

미래 안전한 방향은 `.ai/rules/rules.md`만 항상 로딩하고, 나머지는 작업 유형과 semantic layer에 따라 선택 로딩하는 것이다. `Executable Contract`, `Structural Rules`, `Runtime Policy`는 기계 로딩 후보이고, `Human Review Guidance`, `Review Criteria`, `Philosophy`, `Examples`는 기본적으로 lazy 또는 explicit-load로 제한해야 한다.

이번 감사는 loader를 구현하지 않고, 향후 `activation.yaml`과 runtime worker가 사용할 수 있는 로딩 taxonomy와 worker profile을 설계한다.

## 2. 스캔 범위와 관찰

대상:

- `.ai/rules/**/*.md`
- `.ai/skills/**/*.md`
- `.ai/workflows/**/*.md`
- `.ai/validators/**/*.md`

주요 관찰:

- `.ai/rules/rules.md`는 SSoT, rule priority, adapter policy, selective loading을 담고 있어 always-load 핵심으로 적합하다.
- `.ai/rules/domains/*.rules.md`, `.ai/rules/operations/*.rules.md`는 작업 관련성이 있을 때만 로딩해야 한다.
- `.ai/skills/**/*.skill.md`는 대부분 `Core Logic`, `Input/Output`, `Execution Logic`, `Technical Requirements`, `Constraints`, `Quality Standards`, `Performance Metrics`를 포함한다. 전체 로딩은 비용이 높다.
- `.ai/workflows/_base/workflow_base.md`, `.ai/workflows/workflow_index.md`, `.ai/workflows/README.md`는 역할 철학, workflow inventory, 품질 지표가 길게 섞여 있다.
- `.ai/validators/_base/*.md`와 agent별 validator는 실행 가능한 구조 규칙과 human-review-only quality criteria가 섞여 있다.
- 큰 파일 상위권은 workflow와 shared/unified skill, base validator가 차지한다. 이들은 always-load 금지 대상이다.

## 3. 시맨틱 로딩 Taxonomy

| 로딩 등급 | 의미 | 기본 트리거 | 예시 |
|---|---|---|---|
| `always-load` | 모든 AI CLI 작업 시작 시 최소로 읽는 코어 | 모든 작업 | `.ai/rules/rules.md` |
| `task-load` | 특정 도메인/작업 수행에 필요한 규칙과 스킬 | 작업 intent, agent, command | `development.rules.md`, 관련 `.skill.md` |
| `review-load` | 검토, 승인, L2 판단에 필요한 기준 | review task, `--review`, L2 workflow | `l2_review_validator.md`, review criteria |
| `strategy-load` | 전략, roadmap, architecture, decision 작업 시 필요한 철학/프레임워크 | strategy/plan/design 작업 | `strategic_planning.skill.md`, `decision_analysis.skill.md` |
| `runtime-load` | worker 실행 직전 필요한 runtime policy와 execution contract | runtime worker activation | skill `Executable Contract`, `Runtime Policy` |
| `lazy-load` | 링크를 따라 필요할 때만 읽는 세부 문서 | 참조 탐색, explicit request | examples, reference docs, detailed workflow |
| `never-auto-load` | 자동 로딩하면 noise가 큰 철학/예시/장문 품질 기준 | 명시적 요청만 | 장문 Examples, Philosophy, broad metrics |

## 4. 권장 Always-Load Core

always-load는 극도로 작아야 한다.

| 항목 | 로딩 범위 | 이유 |
|---|---|---|
| `.ai/rules/rules.md` | 전체 | SSoT, 우선순위, selective loading, adapter policy |
| 활성 runtime adapter | 얇은 adapter 본문만 | runtime별 발견 및 호환성 |
| 최신 사용자 요청 | 전체 | 최상위 우선순위 |
| repository root와 `.ai` 경로 정보 | 메타데이터 | 파일 탐색 기준 |

항상 로딩하지 말아야 할 것:

- `.ai/rules/README.md`
- `.ai/rules/domains/*.rules.md` 전체
- `.ai/rules/operations/*.rules.md` 전체
- `.ai/skills/_shared/skill_index.md`
- 모든 `.skill.md` 본문
- 모든 workflow index/base 문서
- 모든 validator 문서
- examples, reference docs, performance metrics, philosophy 섹션

## 5. 파일별 권장 로딩 등급

| 파일/패턴 | 권장 등급 | 설명 |
|---|---|---|
| `.ai/rules/rules.md` | always-load | 글로벌 계약 |
| `.ai/rules/domains/documentation.rules.md` | task-load | 문서 작성/수정 시 |
| `.ai/rules/domains/development.rules.md` | task-load | 코드/아키텍처/개발 작업 시 |
| `.ai/rules/domains/hr.rules.md` | task-load | HR 평가 작업 시 |
| `.ai/rules/operations/validation.rules.md` | task-load/runtime-load | 검증 또는 validate 실행 시 |
| `.ai/rules/operations/workflow.rules.md` | task-load | roadmap/task/run record 작업 시 |
| `.ai/rules/operations/agent.rules.md` | task-load/review-load | agent routing, escalation, collaboration 작업 시 |
| `.ai/skills/**/*.skill.md` | task-load/runtime-load | 해당 skill이 선택된 경우만 |
| `.ai/skills/**/references/*.md` | lazy-load | skill 본문이 직접 요구할 때만 |
| `.ai/skills/**/assets/*.md` | lazy-load | 생성/스캐폴딩 시만 |
| `.ai/skills/_shared/skill_index.md` | lazy-load | skill discovery 또는 audit 시 |
| `.ai/workflows/*.workflow.md` | task-load | 특정 workflow 실행/설계/검토 시 |
| `.ai/workflows/_base/workflow_base.md` | strategy-load/task-load | workflow 설계 시, 항상 로딩 금지 |
| `.ai/workflows/workflow_index.md` | lazy-load | workflow discovery 시 |
| `.ai/validators/meta_validator.md` | runtime-load | validate 대상이 문서/agent/skill일 때 |
| `.ai/validators/structure_validator.md` | runtime-load | 구조 validate 시 |
| `.ai/validators/skill_validator.md` | runtime-load | skill validate 시 |
| `.ai/validators/_base/*.md` | runtime-load/lazy-load | validator 구현 또는 contract 추출 시 |
| `.ai/validators/l2_review_validator.md` | review-load | L2 review 명시 시만 |
| `.ai/validators/*_skill_validator.md` | runtime-load/review-load | agent skill 검증 시만 |

## 6. Context Bloat 위험 파일

| 위험 | 파일 | 이유 | 권장 로딩 |
|---|---|---|---|
| 높음 | `.ai/workflows/deploy_automation.workflow.md` | 장문 workflow, 실행 예시와 정책 혼재 | task-load only |
| 높음 | `.ai/workflows/stock_trading_system.workflow.md` | 도메인 특화 장문 전략/단계 | explicit task-load |
| 높음 | `.ai/workflows/workflow_index.md` | inventory, dependency graph, MUST 규칙, quality target 혼재 | lazy-load |
| 높음 | `.ai/workflows/_base/workflow_base.md` | operational loop와 L1/L2 철학, 성공지표 혼재 | strategy-load only |
| 높음 | `.ai/skills/_shared/operational_run_record_creation.skill.md` | operational loop 상세와 실행 로직 | task-load |
| 높음 | `.ai/skills/_shared/operational_roadmap_management.skill.md` | roadmap 운영 상세 | task-load |
| 높음 | `.ai/skills/_shared/skill_index.md` | 전체 skill discovery 정보 | lazy-load |
| 높음 | `.ai/skills/developer/code_quality_and_technical_debt_analysis.skill.md` | 품질 철학, 지표, guideline 포함 | task/review-load only |
| 높음 | `.ai/validators/_base/document_base_validator.md` | 예시 코드, contract, quality metric 혼재 | runtime-load filtered |
| 높음 | `.ai/validators/_base/agent_skill_base_validator.md` | L1/L2 철학과 contract 혼재 | runtime-load filtered |
| 중간 | `.ai/validators/developer_skill_validator.md` | skill matrix와 quality metric 혼재 | agent-specific runtime-load |
| 중간 | `.ai/validators/README.md` | 설명성 인덱스와 프레임워크 안내 | lazy-load |

## 7. 중복 의미 영역

| 중복 영역 | 반복 위치 | 문제 |
|---|---|---|
| L1/L2 역할 정의 | workflow base, workflow index, agent skill validators, many skills | 항상 로딩 시 같은 개념이 반복되어 token 낭비 |
| quality standards | validators, skills, workflows | 자동 fail 기준과 사람 평가 기준이 혼재 |
| performance metrics | skills, workflows, validators | telemetry 없이 로딩해도 실행 가치 낮음 |
| validation result format | validator base, validation result workflow/template | schema divergence 가능성 |
| metadata-first linking | workflow base, rules, templates, validators | contract와 guidance가 여러 위치에 중복 |
| skill matrices | skill index, agent files, agent skill validators | stale reference와 context bloat 위험 |
| runtime/editor references | workflows, skills references | CLI-first runtime policy와 충돌 가능 |

## 8. High-Noise / Expensive Sections

기본 자동 로딩에서 제외할 섹션:

- `Philosophy`
- `Examples`
- `Performance Metrics`
- `Quality Standards`
- `Special Considerations`
- `Benefits`
- `Version History`
- `Usage Example`
- 장문 `Related Documents`
- validator의 예시 Python 코드 블록
- workflow의 CI/Git hook/IDE 예시
- skill reference 하위 문서

자동 로딩 후보 섹션:

- `Executable Contract`
- `Structural Rules`
- `Runtime Policy`
- `Core Logic`의 첫 단락
- `Input/Output`
- `Execution Logic`의 mode detection 또는 step summary
- `Constraints` 중 OUT scope

## 9. Worker별 로딩 프로필

### Minimal Worker Context

목적: 일반 작업자 또는 CLI agent가 작업을 시작할 때 필요한 최소 문맥.

로드:

- `.ai/rules/rules.md`
- 작업 도메인 rule 1개 이하
- 필요한 operation rule 1개 이하
- 명시된 command 또는 task 파일
- 선택된 skill의 `Executable Contract`, `Input/Output`, `Execution Logic` 요약

제외:

- workflow index
- 전체 skill index
- 모든 validator
- examples와 philosophy

### Reviewer Context

목적: L2 검토, 품질 리뷰, 승인 판단.

로드:

- `.ai/rules/rules.md`
- 관련 domain rule
- `.ai/rules/operations/validation.rules.md`
- 해당 산출물의 validator contract
- 필요한 `Review Criteria`
- 관련 workflow의 review stage

제외:

- unrelated skills
- full workflow base
- examples unless reviewer asks

### Strategist Context

목적: roadmap, architecture, decision, long-term planning.

로드:

- `.ai/rules/rules.md`
- documentation/development/domain rule
- 관련 전략 skill 일부
- workflow base의 operational loop 요약
- decision/roadmap 관련 templates 또는 validator contract

제외:

- agent별 skill matrix 전체
- runtime policy 상세
- execution examples

### Runtime Execution Context

목적: 향후 worker가 실제 skill 또는 workflow를 실행할 때 필요한 context.

로드:

- `.ai/rules/rules.md`에서 우선순위와 runtime policy 관련 섹션
- agent activation profile
- 선택된 skill의 contract, input/output, constraints, runtime policy
- 해당 workflow stage의 input/output/exit criteria
- 필요한 validator의 executable contract

제외:

- human review guidance
- strategic philosophy
- long examples
- unrelated reference docs

### Validation Runtime Context

목적: `aios validate` 또는 향후 validator worker.

로드:

- target file
- target kind registry
- 적용 validator의 `Executable Contract`와 `Structural Rules`
- reference resolver 결과

제외:

- quality metric philosophy
- review guidance
- examples
- performance targets without telemetry

## 10. 미래 Runtime Loading Policy

정책 원칙:

1. Always-load는 글로벌 계약과 명시적 사용자 요청으로 제한한다.
2. Task-load는 intent, path, agent, command, workflow ID 중 하나가 있어야 한다.
3. Review-load는 review intent 또는 reviewer role이 명확할 때만 허용한다.
4. Strategy-load는 planning/architecture/decision/roadmap intent가 있을 때만 허용한다.
5. Runtime-load는 worker activation 직전에 필요한 contract만 로드한다.
6. Lazy-load는 참조를 따라가기 전에 필요성을 기록한다.
7. Never-auto-load 섹션은 명시 요청 없이는 자동 로딩하지 않는다.

로딩 결과에는 최소한 다음 메타데이터를 남기는 것이 좋다.

```yaml
loaded_context:
  path: .ai/skills/developer/dev_backend_stack_unified.skill.md
  semantic_layers:
    - executable_contract
    - runtime_policy
  trigger: task_intent
  reason: backend implementation task
  excluded_layers:
    - examples
    - philosophy
```

## 11. Core Runtime Memory에 둘 것

향후 runtime memory가 생겨도 저장할 내용은 “작고 안정적인 정책”이어야 한다.

포함:

- rule priority
- source of truth policy
- adapter policy
- official runtime list
- symlink 금지
- UTF-8 without BOM
- language policy
- selective loading 원칙
- semantic layer taxonomy
- current agent identity와 task intent

제외:

- skill 본문
- workflow 본문
- validator 본문
- L1/L2 장문 설명
- quality metric tables
- examples
- reference docs

## 12. 명시적 Task Invocation에만 로딩할 것

- 특정 `.skill.md` 전체 본문
- `.ai/skills/**/references/*.md`
- `.ai/workflows/*.workflow.md` 전체
- `.ai/workflows/workflow_index.md`
- `.ai/validators/*_skill_validator.md`
- L2 review validator
- senior decision / mentorship / cross-agent validators
- stock trading, deploy automation 같은 domain-heavy workflow
- code quality/technical debt 분석 skill의 metric/guideline 상세

## 13. `activation.yaml` Semantic Extension 제안

아직 구현하지 않지만, 미래 activation schema는 다음 정보를 담을 수 있다.

```yaml
activation:
  agent: developer
  task_intent: implementation
  runtime: codex-cli

semantic_loading:
  always:
    - path: .ai/rules/rules.md
      layers: [runtime_policy, governance_core]

  task:
    - match:
        domains: [development]
      paths:
        - .ai/rules/domains/development.rules.md
      layers: [runtime_policy, guidance]

  skills:
    selection: explicit-or-agent-routed
    default_layers:
      - executable_contract
      - input_output
      - execution_logic
      - constraints
    excluded_layers:
      - examples
      - philosophy
      - performance_metrics

  review:
    load_only_when:
      - review_intent
      - l2_role
    layers:
      - review_criteria
      - human_review_guidance

  validators:
    default_layers:
      - executable_contract
      - structural_rules
    excluded_layers:
      - examples
      - philosophy
```

이 schema는 manifest/sync가 아니다. runtime activation 시 어떤 semantic layer를 읽을지 선언하는 정책 후보일 뿐이다.

## 14. Semantic Layer Filtering Model

필터링 순서:

1. target intent 판별
2. agent/runtime profile 선택
3. candidate file 목록 생성
4. annotation boundary 우선 추출
5. 표준 섹션명으로 fallback
6. high-noise 섹션 제외
7. token budget에 맞춰 요약 또는 lazy-load
8. 로딩 사유 기록

우선순위:

```text
user request
  > runtime system/developer instruction
  > .ai/rules/rules.md
  > task/domain rule
  > selected skill/workflow contract
  > validator contract
  > review guidance
  > examples/philosophy
```

섹션별 기본 필터:

| 섹션 | worker | reviewer | strategist | validator |
|---|---|---|---|---|
| Executable Contract | include | include | include | include |
| Structural Rules | include when needed | include | include when document work | include |
| Runtime Policy | include | include when relevant | exclude by default | include when policy target |
| Human Review Guidance | exclude | include | include if strategic review | exclude |
| Review Criteria | exclude | include | include when planning review | exclude |
| Philosophy | exclude | exclude by default | lazy-load | exclude |
| Examples | lazy-load | lazy-load | lazy-load | exclude |

## 15. 권장 시맨틱 로딩 정책

P0 정책:

- always-load는 `.ai/rules/rules.md`만 허용한다.
- operation/domain rules는 task intent가 있을 때만 읽는다.
- skill은 명시되거나 agent routing으로 선택된 경우만 읽는다.
- validator는 validate/review 작업에서만 읽는다.
- workflow index/base는 discovery나 workflow 설계 작업에서만 읽는다.

P1 정책:

- governance annotation boundary를 인식하는 loader를 설계한다.
- `Examples`, `Philosophy`, `Performance Metrics`는 기본 제외한다.
- agent별 loading profile을 activation 후보로 문서화한다.
- review task에서만 review criteria를 로딩한다.

P2 정책:

- runtime worker activation에 semantic layer filter를 연결한다.
- token budget 기반으로 lazy-load를 제한한다.
- 로딩된 context와 제외된 context를 run record 또는 runtime trace에 남길지 검토한다.
- `.ai/contracts/` 물리 분리는 annotation adoption 이후에만 검토한다.

## 16. 미래 Runtime 호환성 메모

- Codex CLI, Gemini CLI, Claude Code CLI 모두 동일한 `.ai` SSoT를 참조해야 한다.
- adapter 파일은 semantic loading policy를 복제하지 말고 `.ai/rules/rules.md`와 향후 activation 정책을 가리켜야 한다.
- worker가 생겨도 처음에는 full orchestration이 아니라 read-only context selection부터 시작해야 한다.
- runtime worker는 skill 실행 전 `Executable Contract`와 `Runtime Policy`를 읽고, 실행 후 validator contract를 읽는 흐름으로 충분하다.
- review worker와 execution worker는 기본 로딩 프로필이 달라야 한다.
- strategy worker는 가장 쉽게 context bloat가 발생하므로 philosophy는 opt-in으로 유지해야 한다.

## 17. 결론

현재 `.ai OS`에서 의미 로딩의 핵심 원칙은 “전부 읽지 말고, 작업 의도에 맞는 semantic layer만 읽는다”이다. always-load는 `.ai/rules/rules.md`로 제한하고, skills/workflows/validators는 task, review, strategy, runtime intent가 있을 때만 로딩해야 한다. 특히 workflow index/base, unified skills, base validators, examples, quality metrics, philosophy는 자동 로딩하면 비용 대비 noise가 크다.

향후 구현 순서는 annotation boundary 도입, semantic layer extraction, activation profile 설계, runtime worker 연결 순서가 적절하다. 이번 감사에서는 loader, runtime, orchestration, sync를 구현하지 않았다.
