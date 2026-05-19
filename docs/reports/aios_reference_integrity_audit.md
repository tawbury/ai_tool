# AIOS 참조 무결성 감사 보고서

## 1. 요약

이번 감사는 첫 실행형 검증 계층을 만들기 전, 참조 무결성 문제가 검증 결과를 오염시키지 않도록 지정 파일만 대상으로 수행했다.

감사 대상은 다음 파일이다.

- `.ai/skills/_shared/skill_index.md`
- `.ai/workflows/README.md`
- `.ai/agents/developer.agent.md`
- `.ai/agents/pm.agent.md`
- `.ai/rules/operations/agent.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/validators/skill_loading_validator.md`
- `.ai/validators/structure_validator.md`
- `.ai/commands/implement-design.command.md`

핵심 결론은 다음과 같다.

- `developer.agent.md`와 `pm.agent.md`의 명시적 skill 경로는 모두 실제 파일과 일치한다.
- `skill_index.md`는 과거 skill 이름과 현재 unified skill 구조가 섞여 있어 P0 정리가 필요하다.
- `.ai/workflows/README.md`는 `l2_review_workflow.md`를 참조하지만 실제 파일은 `l2_review.workflow.md`이다.
- `.ai/.cursorrules` 참조는 현재 SSoT 정책과 충돌하므로 `.ai/rules/rules.md`로 교체해야 한다.
- `agent.rules.md`의 embedded `agent-routing` YAML은 v0에서는 유지하되, `aios inspect`가 안정화된 뒤 `agent-registry.yaml` 또는 `activation.yaml`로 분리할 후보이다.
- 현재 validator 문서는 실행 가능한 규칙과 개념적 목표가 섞여 있으므로 `aios inspect` v0는 파일 존재, 경로, frontmatter, 간단한 구조 검증부터 시작해야 한다.

## 2. 실제 Skill 파일 기준

실제 `.ai/skills` 아래에는 다음 통합 구조가 존재한다.

| 영역 | 실제 구조 요약 |
|---|---|
| Shared | `_shared/*.skill.md`, `_shared/ai_cli/*/*.skill.md`, `_shared/contents_creator_frameworks/*.skill.md` |
| Developer | `dev_frontend_stack_unified.skill.md`, `dev_backend_stack_unified.skill.md`, `dev_database_optimization_unified.skill.md`, `dev_cloud_architecture_unified.skill.md`, `dev_devops_unified.skill.md` 등 unified 파일 존재 |
| PM | `pm_strategy_unified.skill.md`, `pm_analytics_unified.skill.md`, `pm_requirement_definition.skill.md`, `product_lifecycle_management.skill.md`, `product_retention.skill.md` 등 존재 |
| HR | `hr_analytics_unified.skill.md`, `hr_performance_lifecycle_unified.skill.md` 등 unified 파일 존재 |
| Contents Creator | `text/`, `visual/`, `video/`, `interactive/`, `business/` 하위 폴더에 실제 skill 존재 |
| Finance | 주요 finance skill 파일 존재 |

## 3. Stale References Table

| 파일 | 현재 참조 | 문제 | 권장 처리 |
|---|---|---|---|
| `.ai/skills/_shared/skill_index.md` | `dev_frontend.skill.md` | 실제 파일 없음 | `dev_frontend_stack_unified.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `dev_frontend_react`, `dev_state_management`, `dev_build_tools` | 이전 분리 skill 이름으로 보임 | `dev_frontend_stack_unified.skill.md` 아래 mode 설명으로 흡수 |
| `.ai/skills/_shared/skill_index.md` | `dev_nodejs`, `dev_api_frameworks`, `dev_middleware` | 실제 파일 없음 | `dev_backend_stack_unified.skill.md`로 통합 표기 |
| `.ai/skills/_shared/skill_index.md` | `dev_nosql`, `dev_query_optimization` | 실제 파일 없음 | `dev_database_optimization_unified.skill.md`로 통합 표기 |
| `.ai/skills/_shared/skill_index.md` | `dev_microservices`, `dev_cloud_infrastructure`, `dev_containerization`, `dev_serverless`, `dev_autoscaling` | 실제 파일 없음 | `dev_cloud_architecture_unified.skill.md` 또는 `dev_devops_unified.skill.md`로 통합 표기 |
| `.ai/skills/_shared/skill_index.md` | `dev_monitoring` | 실제 파일 없음 | `dev_devops_unified.skill.md`로 통합 표기 |
| `.ai/skills/_shared/skill_index.md` | `pm_planning.skill.md` | 실제 파일 없음 | `pm_strategy_unified.skill.md` 또는 `_shared/execution_planning.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `product_analytics.skill.md` | 실제 파일 없음 | `pm_analytics_unified.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `market_research.skill.md` | 실제 파일 없음 | `_shared/research_framework.skill.md` 또는 `pm_strategy_unified.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `pm_roadmap_management.skill.md` | 실제 파일 없음 | `_shared/operational_roadmap_management.skill.md` 또는 `pm_strategy_unified.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `product_growth.skill.md` | 실제 파일 없음 | `product_retention.skill.md`와 `pm_strategy_unified.skill.md`로 개념 분리 |
| `.ai/skills/_shared/skill_index.md` | `product_launch.skill.md` | 실제 파일 없음 | `product_lifecycle_management.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `global_product_strategy.skill.md` | 실제 파일 없음 | `pm_strategy_unified.skill.md` 또는 `product_lifecycle_management.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `data_driven_decision_making.skill.md` | 실제 파일 없음 | `_shared/decision_analysis.skill.md` 또는 `pm_analytics_unified.skill.md`로 교체 |
| `.ai/skills/_shared/skill_index.md` | `user_research.skill.md` | 실제 파일 없음 | `_shared/research_framework.skill.md`로 교체 |
| `.ai/workflows/README.md` | `l2_review_workflow.md` | 실제 파일명과 불일치 | `l2_review.workflow.md`로 교체 |
| `.ai/workflows/README.md` | `backup/software_development.workflow.md.backup_20260120` | 현재 `backup/` 디렉터리 없음 | 삭제하거나 archive 후보로 명시 |
| `.ai/workflows/README.md` | `[[../.cursorrules]]` | 현재 SSoT 정책과 불일치 | `[[../rules/rules.md]]` 또는 `.ai/rules/rules.md`로 교체 |

## 4. Missing File References Table

| 참조 파일명 | 참조 위치 | 실제 상태 | 권장 대체 |
|---|---|---|---|
| `dev_frontend.skill.md` | `skill_index.md` | 없음 | `.ai/skills/developer/dev_frontend_stack_unified.skill.md` |
| `pm_planning.skill.md` | `skill_index.md`, `pm_requirement_definition.skill.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/pm/pm_strategy_unified.skill.md` 또는 `.ai/skills/_shared/execution_planning.skill.md` |
| `product_analytics.skill.md` | `skill_index.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/pm/pm_analytics_unified.skill.md` |
| `market_research.skill.md` | `skill_index.md`, `base_mapping.md` | 없음 | `.ai/skills/_shared/research_framework.skill.md` |
| `pm_roadmap_management.skill.md` | `skill_index.md`, `pm_requirement_definition.skill.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/_shared/operational_roadmap_management.skill.md` |
| `product_growth.skill.md` | `skill_index.md`, `product_retention.skill.md`, `product_monetization.skill.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/pm/product_retention.skill.md` 또는 `.ai/skills/pm/pm_strategy_unified.skill.md` |
| `product_launch.skill.md` | `skill_index.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/pm/product_lifecycle_management.skill.md` |
| `global_product_strategy.skill.md` | `skill_index.md` | 없음 | `.ai/skills/pm/pm_strategy_unified.skill.md` |
| `data_driven_decision_making.skill.md` | `skill_index.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/_shared/decision_analysis.skill.md` |
| `user_research.skill.md` | `skill_index.md`, `base_mapping.md`, `pm_skill_validator.md` | 없음 | `.ai/skills/_shared/research_framework.skill.md` |
| `l2_review_workflow.md` | `.ai/workflows/README.md` | 없음 | `.ai/workflows/l2_review.workflow.md` |
| `.ai/.cursorrules` | workflow/template/validator 계열 다수 | 없음 | `.ai/rules/rules.md` |

## 5. Recommended Rename/Update Table

| 현재 개념 | 권장 canonical 참조 | 이유 |
|---|---|---|
| Frontend Development | `.ai/skills/developer/dev_frontend_stack_unified.skill.md` | frontend 관련 분리 skill이 unified 파일로 통합됨 |
| PM Planning | `.ai/skills/pm/pm_strategy_unified.skill.md` + `.ai/skills/_shared/execution_planning.skill.md` | 전략/실행 계획의 책임이 분리되어 있음 |
| Product Analytics | `.ai/skills/pm/pm_analytics_unified.skill.md` | 실제 PM 분석 skill은 unified 파일임 |
| Market/User Research | `.ai/skills/_shared/research_framework.skill.md` | domain 공통 research framework가 존재함 |
| Product Growth | `.ai/skills/pm/product_retention.skill.md` + `.ai/skills/pm/pm_strategy_unified.skill.md` | growth가 독립 파일이 아니라 retention/strategy로 분산됨 |
| Product Launch | `.ai/skills/pm/product_lifecycle_management.skill.md` | launch는 lifecycle 단계로 다루는 것이 현재 구조와 맞음 |
| Data-Driven Decision | `.ai/skills/_shared/decision_analysis.skill.md` + `.ai/skills/pm/pm_analytics_unified.skill.md` | 의사결정과 분석을 분리해야 함 |
| L2 Review workflow | `.ai/workflows/l2_review.workflow.md` | 실제 파일명과 일치 |
| System rules | `.ai/rules/rules.md` | 현재 SSoT 경로 |

## 6. Developer / PM Agent 참조 결과

| 파일 | 결과 | 비고 |
|---|---|---|
| `.ai/agents/developer.agent.md` | 명시적 `.skill.md` 경로 모두 존재 | `code_quality_analysis`라는 과거 축약명이 dependency order에 남아 있어 `code_quality_and_technical_debt_analysis`로 정리 권장 |
| `.ai/agents/pm.agent.md` | 명시적 `.skill.md` 경로 모두 존재 | L1/L2 표에서 같은 파일을 중복 사용하지만 의도적 level-mode 재사용으로 볼 수 있음 |

## 7. Workflow README 참조 결과

| 참조 | 실제 파일 | 결과 |
|---|---|---|
| `workflow_index.md` | 존재 | 정상 |
| `hr_evaluation.workflow.md` | 존재 | 정상 |
| `stock_trading_system.workflow.md` | 존재 | 정상 |
| `contents_creation.workflow.md` | 존재 | 정상 |
| `financial_management.workflow.md` | 존재 | 정상 |
| `project_management.workflow.md` | 존재 | 정상 |
| `integrated_development.workflow.md` | 존재 | 정상 |
| `l2_review_workflow.md` | `l2_review.workflow.md` 존재 | stale |
| `backup/` | 없음 | stale 또는 미구현 archive 구조 |
| `[[../.cursorrules]]` | 없음 | stale |

## 8. `.ai/.cursorrules` 교체 방침

현재 `.ai/.cursorrules` 참조는 다음 경로로 교체하는 것이 맞다.

| 기존 참조 | 권장 교체 | 적용 대상 |
|---|---|---|
| `.ai/.cursorrules` | `.ai/rules/rules.md` | 일반 텍스트 경로 |
| `[[../.cursorrules]]` | `[[../rules/rules.md]]` | `.ai/workflows/README.md`, `.ai/templates/README.md` 같은 Obsidian 링크 |

단, 이번 작업에서는 감사 문서만 작성하고 원본 파일은 수정하지 않았다.

## 9. `agent-routing` YAML 위치 판단

`agent.rules.md`의 embedded `agent-routing` YAML은 현재 단계에서는 유지하는 것이 적절하다.

판단 근거:

- `.ai/rules/rules.md`가 embedded configuration block 형식을 허용한다.
- 아직 `activation.yaml`, `agent-registry.yaml`, inspect CLI가 없으므로 별도 파일로 빼면 검증 대상만 늘어난다.
- 현재 routing YAML은 agent 파일, 기본 rule, validator 존재 여부를 검사하기 좋은 sentinel 데이터 역할을 한다.

향후 분리 기준:

| 후보 | 목적 | 도입 시점 |
|---|---|---|
| `agent-registry.yaml` | 전체 agent 목록과 canonical metadata | `aios inspect`가 YAML 파싱과 파일 존재 검증을 안정적으로 수행한 뒤 |
| `activation.yaml` | 프로젝트별 agent/skill/workflow 선택 | project init 또는 selective activation 구현 직전 |

권장 방향:

- v0: embedded 유지, `aios inspect`가 embedded YAML을 읽어 검증한다.
- v1: `agent-registry.yaml`을 canonical registry로 분리하고 `agent.rules.md`는 설명과 load policy만 유지한다.
- v2: `activation.yaml`은 registry 전체가 아니라 프로젝트별 선택 상태만 담는다.

## 10. Validator Readiness Table

| 파일 | 규칙 | 분류 | 이유 |
|---|---|---|---|
| `validation.rules.md` | validator index 파일 존재 확인 | 즉시 실행 가능 | 단순 경로 검사 |
| `validation.rules.md` | document-specific validator 존재 확인 | 즉시 실행 가능 | 정적 파일 존재 검사 |
| `validation.rules.md` | 구조, metadata, 언어, 링크 검사 순서 | inspect 이후 실행 가능 | 파서와 링크 추출기가 필요 |
| `validation.rules.md` | executable validation scripts 실행 | 개념적 | 현재 프로젝트 실행 스크립트가 없음 |
| `agent.rules.md` | `agent-routing` anchor 쌍 확인 | 즉시 실행 가능 | 문자열 기반 검사 가능 |
| `agent.rules.md` | embedded YAML 필수 필드 확인 | inspect 이후 실행 가능 | YAML 파서 또는 제한 파서 필요 |
| `agent.rules.md` | routing 내 파일 존재 확인 | inspect 이후 실행 가능 | YAML 추출 후 경로 검사 필요 |
| `agent.rules.md` | agent frontmatter 유효성 확인 | inspect 이후 실행 가능 | frontmatter 파서 필요 |
| `skill_loading_validator.md` | skill file existence verification | 즉시 실행 가능 | 파일 목록과 참조 대조 가능 |
| `skill_loading_validator.md` | skill metadata completeness | inspect 이후 실행 가능 | frontmatter 파싱 필요 |
| `skill_loading_validator.md` | circular dependency detection | inspect 이후 실행 가능 | dependency 그래프 추출 필요 |
| `skill_loading_validator.md` | loading time measurement | 개념적 | 실제 loader가 없음 |
| `skill_loading_validator.md` | memory usage optimization | 개념적 | runtime loader가 없음 |
| `skill_loading_validator.md` | caching mechanism validation | 개념적 | cache 계층이 없음 |
| `skill_loading_validator.md` | concurrent loading validation | 개념적 | 병렬 loader가 없음 |
| `skill_loading_validator.md` | loading success rate 99%+ | 너무 엄격 / 오탐 가능 | 현재 실행 정의가 없어 측정 불가 |
| `skill_loading_validator.md` | loading time optimization 50%+ | 너무 엄격 / 오탐 가능 | baseline 없음 |
| `skill_loading_validator.md` | memory usage efficiency 80%+ | 너무 엄격 / 오탐 가능 | 측정 모델 없음 |
| `structure_validator.md` | header 존재 확인 | 즉시 실행 가능 | Markdown 정적 검사 가능 |
| `structure_validator.md` | 빈 header 금지 | 즉시 실행 가능 | 정적 검사 가능 |
| `structure_validator.md` | `---` separator 확인 | inspect 이후 실행 가능 | 문서 유형별 적용 예외가 필요 |
| `structure_validator.md` | `# Meta`가 첫 섹션이어야 함 | 너무 엄격 / 오탐 가능 | `.ai` rule/agent/skill 파일은 YAML frontmatter 또는 일반 Markdown을 사용함 |
| `structure_validator.md` | 모든 section은 비어 있으면 안 됨 | 너무 엄격 / 오탐 가능 | template placeholder와 intentionally empty 섹션에서 오탐 가능 |
| `structure_validator.md` | 중복 section name 금지 | inspect 이후 실행 가능 | 긴 template에서는 의도적 반복 가능하므로 warning부터 시작 |
| `structure_validator.md` | docs는 Korean, .ai는 English | inspect 이후 실행 가능 | 언어 감지 휴리스틱 필요, code block 예외 필요 |
| `structure_validator.md` | template compliance | 개념적 | template-to-document 매핑 규칙이 아직 없음 |
| `implement-design.command.md` | required rule 파일 존재 | 즉시 실행 가능 | 정적 경로 검사 |
| `implement-design.command.md` | no symbolic links under rules/commands/agents | 즉시 실행 가능 | filesystem 속성 검사 |
| `implement-design.command.md` | referenced file existence check | inspect 이후 실행 가능 | Markdown 참조 추출기 필요 |
| `implement-design.command.md` | UTF-8 without BOM check | 즉시 실행 가능 | byte 검사 가능 |
| `implement-design.command.md` | no unintended standalone manifest/schema/log files | inspect 이후 실행 가능 | allowlist 정책 필요 |
| `implement-design.command.md` | `git diff --check` | 즉시 실행 가능 | git command 실행 가능 |

## 11. First `aios inspect` Checklist

`aios inspect` v0는 쓰기 없는 read-only 명령이어야 한다.

필수 검사:

- `.ai/` 필수 디렉터리 존재 확인
- root adapter 파일 존재 확인: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- `.ai/rules/rules.md` 존재 확인
- `.ai/rules/domains`, `.ai/rules/operations` 존재 확인
- `.ai/agents/*.agent.md` frontmatter 존재 확인
- agent frontmatter의 `domain_rules`, `operation_rules`, `validators` 경로 존재 확인
- `agent.rules.md`의 `agent-routing` block anchor 쌍 확인
- embedded routing YAML의 파일 참조 존재 확인
- `.ai/skills/**/*.skill.md` 실제 목록 생성
- `skill_index.md`, `developer.agent.md`, `pm.agent.md`의 skill 참조 대조
- `.ai/workflows/README.md`의 workflow 참조 대조
- `.ai/.cursorrules` stale 참조 탐지
- rule/agent/command 디렉터리 아래 symlink 탐지
- UTF-8 BOM 탐지
- 결과를 사람이 읽는 summary와 machine-readable JSON으로 출력

초기에는 fail과 warning을 분리해야 한다.

| 등급 | 예 |
|---|---|
| fail | 명시 경로가 존재하지 않음, SSoT rule 파일 없음, symlink 존재 |
| warning | basename만 있고 하위 디렉터리가 불명확함, concept-only skill 이름, 너무 큰 파일 |
| info | 파일 수, skill 수, workflow 수, context budget 추정 |

## 12. Exact P0 Implementation Order

1. `src/` 아래 최소 CLI skeleton을 만든다.
2. `aios inspect --json` 출력 모델을 먼저 정의한다.
3. filesystem scanner를 구현한다.
4. Markdown reference extractor를 구현한다.
5. skill reference checker를 구현한다.
6. workflow reference checker를 구현한다.
7. stale `.ai/.cursorrules` detector를 구현한다.
8. agent frontmatter path checker를 구현한다.
9. `agent-routing` embedded YAML checker를 구현한다.
10. UTF-8 BOM checker와 symlink checker를 추가한다.
11. 사람이 읽는 summary formatter를 붙인다.
12. 현재 감사에서 발견된 stale reference를 fixture로 삼아 테스트를 작성한다.

## 13. 이번 감사에서 수정하지 않은 항목

사용자 제약에 따라 원본 `.ai` 파일은 수정하지 않았다.

수정하지 않은 항목:

- `skill_index.md`의 stale skill 이름
- `.ai/workflows/README.md`의 `l2_review_workflow.md`
- `.ai/workflows/README.md`의 `.ai/.cursorrules` 참조
- 기타 `.ai/templates`, `.ai/validators`에 남아 있는 `.ai/.cursorrules` 참조

