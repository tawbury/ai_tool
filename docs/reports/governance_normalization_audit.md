# .ai OS 거버넌스 정규화 감사 보고서

## 1. 요약

`.ai OS`는 현재 프롬프트/스킬 저장소에서 CLI-first AI workforce 운영체제로 이동하는 중이다. 이 전환 과정에서 `.ai/validators`, `.ai/workflows`, `.ai/skills` 안에 실행 가능한 계약, 구조 규칙, 런타임 정책, 운영 철학, 품질 가이드, 사람 검토 전용 평가 기준이 함께 섞여 있다.

가장 큰 문제는 “validator”라는 이름의 문서가 실제 실행 가능한 검증 계약과 사람의 판단이 필요한 품질 철학을 동시에 담고 있다는 점이다. `aios inspect`와 향후 `aios validate`가 안정적으로 동작하려면 자동 실행 가능한 contract와 human-review-only guidance를 분리하거나, 최소한 같은 문서 안에서 명확히 주석화해야 한다.

이번 감사는 파일 수정 없이 `.ai/validators/**/*.md`, `.ai/workflows/**/*.md`, `.ai/skills/**/*.md`를 스캔해 혼재 위험과 정규화 방향을 정리했다.

## 2. 콘텐츠 블록 분류 기준

| 분류 | 의미 | 자동 실행 가능성 |
|---|---|---|
| executable contract | 파일 존재, 필수 필드, 필수 섹션, 링크, 형식처럼 코드로 판정 가능한 계약 | 높음 |
| structural rule | 문서 구조, frontmatter, 블록 태그, 헤더 계층 등 구조 규칙 | 높음 |
| runtime policy | 공식 runtime, adapter, symlink 금지, BOM 금지, 경로 정책 등 실행 환경 정책 | 중간 |
| governance guidance | 운영 원칙, 역할 분담, 승인 흐름, 변경 관리 방식 | 낮음 |
| human-review-only quality criteria | 전략성, 리더십, 타당성, 비즈니스 임팩트, 품질 점수 등 사람 판단 기준 | 낮음 |
| strategic philosophy | AI OS 방향성, L1/L2 철학, 지속 개선, 조직 운영 관점 | 매우 낮음 |

## 3. 위험하게 혼재된 파일

| 파일 | 혼재 유형 | 위험 | 권장 조치 |
|---|---|---|---|
| `.ai/validators/_base/document_base_validator.md` | 실행 계약 + 예시 Python + severity 정책 + 품질/성능 목표 | validator runtime이 예시 코드를 실제 계약으로 오해할 수 있음 | split |
| `.ai/validators/_base/agent_skill_base_validator.md` | 스킬 블록 계약 + L1/L2 철학 + 품질 점수 + hard coding 예시 | 스킬 구조 검증과 코드 품질/레벨 평가가 섞임 | split |
| `.ai/validators/_base/skill_self_validator.md` | 실행 중 self-validation + hard coding 정책 + 품질 메트릭 + 통합 철학 | worker execution 없는 v0에서 실행 가능한 것처럼 보임 | annotate |
| `.ai/validators/skill_loading_validator.md` | 로딩 구조 + runtime 성능 + dependency/cache/concurrent loading 기준 | inspect/validate 범위와 runtime telemetry 범위가 혼재 | split |
| `.ai/validators/skill_execution_validator.md` | 스킬 실행 품질 + 산출물 평가 + 성능 기준 | worker execution 없는 상태에서 자동 validator로 오인될 수 있음 | keep-as-guidance |
| `.ai/validators/l2_review_validator.md` | L2 리뷰 흐름 + senior 품질 평가 | 사람 리뷰 기준이 executable validator처럼 명명됨 | rename 또는 annotate |
| `.ai/validators/senior_decision_validator.md` | decision 구조 + 전략적 판단 품질 | 의사결정 타당성은 자동 fail 기준으로 부적합 | keep-as-guidance |
| `.ai/validators/mentorship_validator.md` | 멘토링 효과와 지식 전파 기준 | 실행 로그와 사람 평가 없이는 판정 불가 | keep-as-guidance |
| `.ai/validators/cross_agent_validator.md` | 협업 구조 + synergy/effectiveness 평가 | orchestration 실행 없이 판정 불가 | keep-as-guidance |
| `.ai/workflows/_base/workflow_base.md` | operational loop 계약 + metadata rule + L1/L2 철학 + 성공지표 | workflow contract와 거버넌스 철학이 모두 single source로 선언됨 | split |
| `.ai/workflows/code_quality_validation.workflow.md` | workflow 단계 + shell/CI 예시 + IDE integration + quality gates | CLI-first 정책과 editor/CI 실행 예시가 한 문서에 혼재 | rewrite |
| `.ai/workflows/batch_update_workflow.md` | rule propagation 절차 + pseudo-code + rollback + validation gate | sync/auto-update와 validate 경계가 모호함 | archive 또는 rewrite |
| `.ai/workflows/l2_review.workflow.md` | workflow 단계 + L2 품질 인증 기준 | 실행 가능한 단계와 사람 리뷰 기준이 혼재 | annotate |
| `.ai/workflows/workflow_index.md` | 인덱스 + MUST 규칙 + dependency graph + 품질 목표 | README/index가 정책 원천처럼 작동할 위험 | split |
| `.ai/skills/_shared/skill_performance_management.md` | 스킬 관리 지침 + 성능/품질 기준 | guidance와 executable skill contract가 혼재 | keep-as-guidance |
| `.ai/skills/_shared/strategic_planning.skill.md` | input/output contract + 전략 철학 + 품질 체크리스트 | contract와 전략 품질 기준 분리 필요 | annotate |
| `.ai/skills/_shared/system_design.skill.md` | input/output contract + 설계 원칙 + 리뷰/성능 메트릭 | 실행 기준과 설계 품질 기준이 혼재 | annotate |
| `.ai/skills/developer/code_quality_and_technical_debt_analysis.skill.md` | 실행 로직 + 품질 철학 + 메트릭 | skill 사용법과 평가 기준이 과밀 | rewrite later |
| `.ai/skills/hr/hr_level_check.skill.md` | L1/L2 판정 로직 + 사람 평가 기준 | 일부는 executable decision rule, 일부는 HR 판단 기준 | split later |

## 4. 실행 전용 후보 파일

다음 파일 또는 파일의 일부는 `aios validate` 실행 계약으로 전환하기 좋다.

| 후보 | 실행 가능한 부분 | 권장 위치 |
|---|---|---|
| `.ai/validators/meta_validator.md` | 필수 meta 필드, 날짜/버전 형식, 빈 값 검사 | contract 또는 validator runtime |
| `.ai/validators/structure_validator.md` | 제목, `# Meta`, `---`, 헤더 계층, 빈 섹션 검사 | contract 또는 validator runtime |
| `.ai/validators/skill_validator.md` | `.skill.md` 필수 블록, `END_BLOCK`, 파일명 규칙 | contract 또는 validator runtime |
| `.ai/validators/_base/mapping_validator.md` | skill/agent/template/workflow/validator 참조 존재 검사 | inspect/validate shared reference contract |
| `.ai/validators/_base/document_base_validator.md` 일부 | 공통 문서 필드와 구조 계약 | split 후 contract |
| `.ai/validators/_base/agent_skill_base_validator.md` 일부 | 필수 스킬 블록과 agent skill matrix | split 후 contract |
| `.ai/workflows/_base/workflow_base.md` 일부 | metadata-first linking, artifact location, status values | policy/contract 분리 |
| `.ai/skills/*/*.skill.md` frontmatter와 `Core Logic`, `Input/Output`, `Execution Logic` | 스킬 최소 구조 계약 | skill contract validator |

## 5. 가이드 전용 후보 파일

다음 파일은 실행 validator로 다루기보다 guidance 또는 governance 문서로 유지하는 것이 안전하다.

| 파일 | 이유 | 권장 조치 |
|---|---|---|
| `.ai/validators/l2_review_validator.md` | senior review 품질 판단 필요 | keep-as-guidance |
| `.ai/validators/senior_decision_validator.md` | 전략적 판단과 의사결정 맥락 필요 | keep-as-guidance |
| `.ai/validators/mentorship_validator.md` | 멘토링 효과는 실행 로그와 사람 평가 필요 | keep-as-guidance |
| `.ai/validators/cross_agent_validator.md` | orchestration 결과가 없으면 자동 판정 불가 | keep-as-guidance |
| `.ai/validators/skill_execution_validator.md` | worker/skill 실행 결과가 필요 | keep-as-guidance until runtime exists |
| `.ai/skills/_shared/skill_performance_management.md` | 운영 관리와 성능 개선 지침 | keep-as-guidance |
| `.ai/workflows/_base/README.md` | base workflow 설명과 사용법 | keep-as-guidance |

## 6. 분리가 필요한 하이브리드 파일

| 파일 | 남길 계약 | 분리할 guidance |
|---|---|---|
| `.ai/validators/_base/document_base_validator.md` | required fields, date format, status values, structure rules, result schema | impact analysis, performance targets, content completeness percentage |
| `.ai/validators/_base/agent_skill_base_validator.md` | required blocks, naming convention, I/O section existence, result schema | L1/L2 leadership standards, quality metrics, hard coding examples |
| `.ai/validators/skill_loading_validator.md` | skill file existence, index reference, dependency reference | loading performance, cache behavior, concurrent loading |
| `.ai/workflows/_base/workflow_base.md` | metadata-first linking, artifact roles, status derivation, required metadata fields | L1/L2 philosophy, success indicators, quality metrics, role philosophy |
| `.ai/workflows/code_quality_validation.workflow.md` | workflow stages, input/output, approval gate names | Git hook/CI examples, IDE integration, broad quality philosophy |
| `.ai/workflows/workflow_index.md` | workflow file inventory, dependency links | MUST policy statements, quality targets, role governance |
| `.ai/skills/_shared/strategic_planning.skill.md` | inputs, outputs, preconditions, output format | strategic clarity score, stakeholder understanding, continuous improvement |
| `.ai/skills/_shared/system_design.skill.md` | inputs, outputs, preconditions, output format | design quality philosophy, security review depth, continuous improvement metrics |
| `.ai/skills/hr/hr_level_check.skill.md` | explicit L1/L2/PENDING decision rules | domain judgment nuance and ambiguous human evaluation notes |

## 7. 제안 용어 체계

### 거버넌스 레이어 vocabulary

| 용어 | 정의 | 위치 후보 |
|---|---|---|
| governance | AI OS 운영 원칙, 역할, 승인, 책임 경계 | `.ai/rules/operations/*.rules.md` 또는 `.ai/governance/` |
| policy | 반드시 지켜야 하는 운영 정책. 일부는 inspect/validate 가능 | `.ai/rules/` |
| guidance | 사람이 읽고 적용하는 권고, 판단 기준, 모범 사례 | `.ai/guidance/` 또는 기존 문서의 Guidance 섹션 |
| review criteria | 사람 리뷰 체크리스트와 품질 판단 기준 | `.ai/reviews/` 또는 validator 문서의 Human Review 섹션 |
| philosophy | 장기 방향성, 설계 원칙, 가치 체계 | docs/plan 또는 `.ai/governance/` |

### 계약 레이어 vocabulary

| 용어 | 정의 | 위치 후보 |
|---|---|---|
| contract | 코드로 판정 가능한 입력, 출력, 필드, 구조, 참조 계약 | `.ai/contracts/` 또는 validator 문서의 Contract 섹션 |
| validator | contract를 실행해 pass/warn/fail 결과를 만드는 코드 또는 명세 | `src/aios/validate/`, `.ai/validators/` |
| execution criteria | 런타임 실행 전후에 기계적으로 확인할 수 있는 조건 | validator runtime |
| structural rule | 문서/스킬/워크플로우의 형태 규칙 | contract |
| runtime policy | runtime/adapters/filesystem 관련 운영 제한 | inspect/validate policy checks |

## 8. canonical distinction 제안

| 개념 | 포함해야 할 것 | 포함하지 말아야 할 것 |
|---|---|---|
| contract | 필수 필드, 허용 값, 경로 존재, 파일명 패턴, 링크 규칙, result schema | 품질 철학, 사람의 전문 판단, 전략적 가치 |
| validator | contract를 읽고 결과를 산출하는 실행 로직 | 실제 작업 수행, worker 실행, 자동 수정 |
| policy | 공식 runtime, adapter 얇게 유지, symlink 금지, 언어/인코딩 정책 | domain별 취향, 선택적 best practice |
| guidance | 적용 방법, 예시, 권장 흐름, 리뷰 관점 | fail을 발생시키는 규칙처럼 보이는 MUST |
| workflow | 단계, 입력, 출력, 산출물, 승인 지점 | validator 코드, 포괄적 조직 철학 |
| execution criteria | 실행 전 준비 조건, 실행 후 산출물 존재, 상태 전이 조건 | 산출물의 전략적 탁월성 판단 |

## 9. executable validation에 들어갈 것

`aios validate` v0/v1에 넣을 수 있는 것은 다음처럼 기계 판정 가능한 항목이어야 한다.

- 파일과 디렉터리 존재
- root와 `.ai` SSoT 확인
- frontmatter 필수 필드와 타입
- `.agent.md`, `.skill.md`, `.workflow.md` 파일명 규칙
- `.skill.md` 필수 블록 존재
- validator/rule/skill/workflow/template 참조 존재
- Obsidian 링크의 명백한 상대 경로 확인
- 문서 헤더 계층과 필수 섹션 존재
- status 허용 값
- 공식 runtime 용어와 legacy runtime 금지 정책
- UTF-8 BOM, symlink, adapter 두께 같은 저장소 정책

## 10. human-review-only로 남길 것

다음은 자동 validator가 아니라 사람 리뷰 체크리스트나 guidance로 남겨야 한다.

- strategic depth
- leadership quality
- business impact
- decision validity
- architecture excellence
- mentorship quality
- cross-agent synergy
- stakeholder satisfaction
- content completeness percentage
- skill effectiveness score
- L2 certification quality
- performance target 달성 여부 중 실제 telemetry가 없는 항목

## 11. 미래 저장소 레이어링 제안

v0에서는 구조 변경 없이 문서에 주석을 다는 방식이 안전하다. 이후 실제 분리가 필요해지면 다음 레이어가 적합하다.

```text
.ai/
  contracts/
    agents/
    skills/
    workflows/
    documents/

  validators/
    README.md
    validator_index.md
    guidance/
      l2_review_validator.md
      senior_decision_validator.md

  rules/
    rules.md
    domains/
    operations/

  workflows/
    *.workflow.md

  skills/
    **/*.skill.md

  guidance/
    quality/
    governance/
    reviews/
```

단, 이 구조는 즉시 만들 필요가 없다. 먼저 기존 문서 안에 `Executable Contract`, `Runtime Policy`, `Human Review Guidance`, `Examples` 같은 섹션 경계를 도입하는 것이 더 현실적이다.

## 12. 우선순위별 권장 조치

### P0

| 작업 | 이유 |
|---|---|
| validator 문서에 `Executable Contract`와 `Human Review Guidance` 섹션 표준 도입 | `aios validate`가 무엇을 실행해야 하는지 명확해짐 |
| `_base/document_base_validator.md`의 실행 가능한 필드/구조 계약만 별도 표시 | 문서 validator의 기반 안정화 |
| `_base/agent_skill_base_validator.md`의 스킬 블록 계약만 별도 표시 | 스킬 validator의 기반 안정화 |
| `workflow_base.md`에서 metadata-first/status rule을 contract로 표시 | workflow validate 범위 명확화 |

### P1

| 작업 | 이유 |
|---|---|
| L2/mentorship/cross-agent validator를 guidance-only로 명시 | 자동 fail 오판 방지 |
| skill_loading/execution validator를 runtime-ready와 future-runtime으로 분리 | worker execution 이전의 경계 정리 |
| workflow_index의 policy 문장을 rules 또는 contract로 이동 | index가 정책 원천이 되는 문제 방지 |
| skill 문서의 `Inputs (Contract)`/`Outputs (Contract)` 패턴을 전체 스킬에 점진 적용 | validate target 결정 단순화 |

### P2

| 작업 | 이유 |
|---|---|
| `.ai/contracts/` 도입 검토 | 실행 계약을 마크다운 guidance와 물리적으로 분리 |
| guidance 전용 디렉터리 도입 검토 | 고급 품질/철학 문서의 context bloat 감소 |
| review criteria를 L2 리뷰 전용 문서로 이동 | 사람 리뷰 흐름과 validator runtime 분리 |
| contract coverage 리포트 추가 | validator 문서와 실행 코드 간 추적성 확보 |

## 13. 결론

현재 저장소에서 위험한 혼재는 “validator 문서가 모두 실행 가능한 것처럼 보이는 문제”와 “workflow base가 계약, 정책, 거버넌스 철학을 동시에 single source로 선언하는 문제”다. 즉시 대규모 이동을 하기보다, 먼저 실행 가능한 계약과 사람 검토 가이드를 문서 내부에서 명확히 분리하고 `aios validate`는 그중 기계 판정 가능한 contract만 대상으로 삼는 방향이 가장 실용적이다.

이번 감사에서는 `.ai` 파일을 수정하지 않았다.
