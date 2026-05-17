# 글로벌 룰 레이어드 전환 설계 2: 글로벌 계약 축소와 룰 본문 분리

**작성일**: 2026-05-17  
**문서 상태**: 설계  
**대상 페이즈**: Phase 3, Phase 4, Phase 5  
**관련 계획 문서**: `docs/plan/global_rules_split_proposal_plan.md`  
**구현 범위**: `.ai/rules/rules.md` 축소, 도메인 룰 분리, 운영 룰 분리

---

## 1. 설계 목적

이 설계 문서는 실제 룰 본문을 레이어드 구조로 이동하는 구현 방안을 정의한다. Phase 1-2가 구조를 준비하는 단계라면, Phase 3-5는 현재 비대해진 `.ai/rules/rules.md`를 글로벌 계약 중심으로 줄이고, 세부 규칙을 `domains/`와 `operations/`로 분리하는 핵심 구현 단계다.

이 단계의 핵심 기준은 단순하다. 도메인 룰은 업무 또는 작업 산출물의 기준을 정의하고, 운영 룰은 작업을 실행하고 통제하는 방식을 정의한다. 이 기준을 모든 이동 판단에 일관되게 적용한다.

---

## 2. 현재 `rules.md`의 주요 문제

현재 `.ai/rules/rules.md`는 다음 성격의 규칙을 한 파일에 포함한다.

- 글로벌 SSoT 선언
- 규칙 우선순위
- 언어 및 인코딩 정책
- 문서 생성 규칙
- HR 평가 경로와 제약
- 개발 문서 경로와 템플릿
- Roadmap, Task, Run Record 운영 흐름
- 에이전트 목록과 L1/L2 협업
- 검증 절차
- 오류 처리와 복구
- 성능 및 컨텍스트 관리
- Claude 관련 잔여 프로젝트 지침
- Docker, Makefile, 컨테이너 실행 지침

문제의 핵심은 규칙의 양이 아니라 변경 이유가 다른 규칙이 같은 위치에 있다는 점이다. 글로벌 계약, 업무 도메인 기준, 실행 거버넌스를 분리해야 선택 로딩과 장기 유지보수가 가능하다.

---

## 3. 목표 파일 구성

Phase 3-5 완료 후 목표 파일은 다음과 같다.

```text
.ai/
  rules/
    README.md
    rules.md

    domains/
      README.md
      documentation.rules.md
      development.rules.md
      hr.rules.md

    operations/
      README.md
      workflow.rules.md
      validation.rules.md
      agent.rules.md
```

각 룰 파일은 영어로 작성한다. 이 설계 문서만 `docs/` 하위에 있으므로 한국어로 유지한다.

향후 `marketing.rules.md`, `research.rules.md`, `sales.rules.md`, `finance.rules.md` 같은 도메인이 추가되어도 `operations/` 구조는 변경하지 않는다. 새 업무 기준은 `domains/`에 추가하고, 실행 흐름과 검증, 에이전트 거버넌스는 기존 운영 룰을 재사용한다.

---

## 4. `rules.md` 축소 기준

`rules.md`는 모든 AI CLI가 항상 읽어야 하는 글로벌 계약만 포함해야 한다.

반드시 남길 내용:

- `.ai/rules/rules.md`가 글로벌 SSoT라는 선언
- Codex CLI, Claude Code, Gemini CLI 및 향후 AI CLI의 공통 진입점
- 규칙 우선순위
- 루트 어댑터 정책
- 공유 규칙 중복 금지
- 심볼릭 링크 금지
- `domains/`와 `operations/`의 역할 요약
- 선택 로딩 원칙
- `docs/`는 한국어, `.ai/`는 영어라는 최상위 언어 원칙
- UTF-8 without BOM 원칙
- 변경 시 검증과 변경 기록이 필요하다는 최소 거버넌스

반드시 제거할 내용:

- HR 평가 상세 절차
- 개발 문서 세부 경로
- 템플릿 목록 전체
- L1/L2 상세 협업 프로토콜
- 검증 단계별 체크리스트
- Docker/build/runtime 세부 지침
- Claude 전용 프로젝트 지침
- 특정 validator나 workflow의 세부 사용 절차

권장 섹션:

```markdown
---
description: "Global rule contract for multi-AI CLI orchestration"
globs: "**/*"
alwaysApply: true
---

# Global Rules

## Purpose
## Source of Truth
## Rule Priority
## Root Adapter Policy
## Rule Layers
## Selective Loading
## Global File and Encoding Requirements
## Symlink Policy
## Change Governance
## Migration Map
```

`Migration Map`은 영구 아키텍처가 아니라 전환 기간용 안내다. 하위 룰 파일이 안정화되면 상세 매핑은 `.ai/rules/README.md`나 변경 기록으로 이동하고, `rules.md`에는 짧은 레이어 안내만 남긴다.

---

## 5. 도메인 룰 설계

도메인 룰은 "무엇을 만들고 어떤 업무 기준을 따르는가"를 정의한다. 운영 흐름, 검증 방식, 에이전트 협업 규칙을 복제하지 않고 필요 시 관련 운영 룰을 참조한다.

### 5.1 `documentation.rules.md`

책임:

- 문서가 어떤 언어로 작성되어야 하는지
- 문서가 어떤 구조와 메타데이터를 가져야 하는지
- 템플릿을 어떻게 적용해야 하는지
- Obsidian 링크와 문서 관계를 어떻게 표현해야 하는지
- 문서 산출물의 형식 일관성을 어떻게 유지할지

책임이 아닌 것:

- HR 산출물의 구체 저장 위치
- 개발 산출물의 구체 저장 위치
- 특정 도메인의 승인 흐름
- 특정 validator 실행 순서

현재 `rules.md`에서 이동할 대상:

- `Language & Content Rules`
- `Content Creation Rules`
- `Language Validation`
- `Template Processing Rules`
- 문서 구조 관련 `Directory & Path Mapping`
- `Document Templates` 중 공통 템플릿 사용 원칙
- `Additional Rules` 중 Metadata Integrity
- 문서 관련 `Template Compliance`

실제 코드베이스 참조:

```text
.ai/templates/
  task_template.md
  report_template.md
  architecture_template.md
  spec_template.md
  prd_template.md
  decision_template.md
  roadmap_template.md
  run_record_template.md

docs/
  plan/
  reports/
  roadmap/
```

주의:

- `documentation.rules.md`는 문서가 어떻게 작성되고 구조화되는지를 정의한다.
- 도메인별 산출물이 어디에 위치하는지는 각 도메인 룰이 정의한다.
- 예를 들어 HR 평가 보고서 위치는 `hr.rules.md`, 개발 아키텍처 문서 위치는 `development.rules.md`가 소유한다.

### 5.2 `development.rules.md`

책임:

- 개발 관련 산출물 경로
- 개발 문서 작성 기준
- 코드 변경 전후 확인 원칙
- Docker, Makefile, build, runtime 지침
- 개발 워크플로우와 관련된 도메인 특수 규칙

현재 `rules.md`에서 이동할 대상:

- `Development Documentation`
- `Development Documentation Constraints`
- `Development Documentation Workflow`
- `Project Guidelines (CLAUDE.md)` 중 Docker, Makefile, container execution 관련 내용
- 개발 문서 템플릿 경로

실제 코드베이스 참조:

```text
.ai/agents/developer.agent.md
.ai/skills/developer/
.ai/workflows/integrated_development.workflow.md
.ai/workflows/code_quality_validation.workflow.md
.ai/workflows/deploy_automation.workflow.md
.ai/templates/architecture_template.md
.ai/templates/spec_template.md
.ai/templates/prd_template.md
.ai/templates/decision_template.md
```

주의:

- Docker/build/runtime은 개발 실행 환경 지침이므로 이 파일에 둔다.
- 검증이라는 공통 행위는 `validation.rules.md`가 소유한다.
- 개발 작업에서 어떤 검증을 우선 참조할지는 `development.rules.md`에서 관련 운영 룰로 연결한다.

### 5.3 `hr.rules.md`

책임:

- HR 평가 입력과 출력 경로
- 역할 정의 문서 생성 규칙
- 평가 리포트 생성 규칙
- Meta Isolation
- Pending Protocol
- HR 관련 skill과 validator 참조

현재 `rules.md`에서 이동할 대상:

- `HR Evaluation`
- `HR Evaluation Constraints`
- `HR Evaluation Workflow`
- HR 관련 Task Template 및 Report Template 사용 규칙

실제 코드베이스 참조:

```text
.ai/agents/hr.agent.md
.ai/skills/hr/
  hr_onboarding.skill.md
  hr_level_check.skill.md
  hr_report_emit.skill.md
.ai/workflows/hr_evaluation.workflow.md
.ai/validators/hr_skill_validator.md
.ai/validators/report_validator.md
.ai/validators/task_validator.md
```

주의:

- HR 평가의 업무 절차와 산출물 위치는 `hr.rules.md`가 소유한다.
- Roadmap, Task, Run Record 같은 실행 증거 체계는 `workflow.rules.md`가 소유한다.
- HR 룰은 필요한 workflow와 validator를 참조하되 그 내용을 복제하지 않는다.

---

## 6. 운영 룰 설계

운영 룰은 "어떻게 실행하고 통제할 것인가"를 정의한다. 운영 룰은 도메인 독립이며, 개발, HR, 향후 마케팅/리서치/세일즈/재무 도메인에서 재사용된다.

### 6.1 `workflow.rules.md`

책임:

- Roadmap -> Task -> Run Record -> Roadmap update 루프
- Metadata-first linking
- 실행 증거 기록
- 세션 중단 후 복구
- 오류 발생 시 운영 복구 흐름

현재 `rules.md`에서 이동할 대상:

- `Workflow System v2 Rules`
- `Metadata-First Linking`
- `Operational Loop Rules`
- `Operational Loop Templates`
- `System Recovery Protocol` 중 세션, 문서, 워크플로우 복구
- `Error Reporting` 중 운영 기록 관련 내용

실제 코드베이스 참조:

```text
.ai/templates/roadmap_template.md
.ai/templates/task_template.md
.ai/templates/run_record_template.md
.ai/workflows/
  workflow_index.md
  project_management.workflow.md
  batch_update_workflow.md
  l2_review.workflow.md
docs/roadmap/
```

주의:

- `workflow.rules.md`는 실행 흐름을 정의한다.
- HR 평가나 개발 문서 작성의 업무 절차는 각 도메인 룰에 둔다.
- 도메인 룰은 workflow 룰을 참조할 수 있지만 실행 루프 본문을 복제하지 않는다.

### 6.2 `validation.rules.md`

책임:

- 검증 대상 식별
- 템플릿 검증
- 메타데이터 검증
- 링크 검증
- 실행 가능한 검증 스크립트 또는 validator 문서 참조
- 검증 실패 시 처리 원칙

현재 `rules.md`에서 이동할 대상:

- `Validation System`
- `Validation Process`
- `Document Creation Errors`
- `Validation Failures`
- `Link Validation`
- `Template Compliance`

실제 코드베이스 참조:

```text
.ai/validators/
  validator_index.md
  task_validator.md
  report_validator.md
  architecture_validator.md
  spec_validator.md
  prd_validator.md
  decision_validator.md
  meta_validator.md
  structure_validator.md
  skill_loading_validator.md
  skill_execution_validator.md
```

주의:

- 검증 규칙은 도메인 독립이다.
- 도메인 룰은 어떤 validator를 우선 참조할지 안내할 수 있다.
- 도메인 룰은 검증 절차의 공통 본문을 복제하지 않는다.

### 6.3 `agent.rules.md`

책임:

- 에이전트 목록과 역할
- L1/L2 협업 모델
- 승인, 리뷰, 에스컬레이션
- 컨텍스트 관리
- 병렬 처리와 배치 처리 원칙
- 에이전트 실패 시 대응

현재 `rules.md`에서 이동할 대상:

- `Agent System`
- `L1/L2 Agent System`
- `Agent Boundaries`
- `Agent Failure`
- `Performance & Optimization`

실제 코드베이스 참조:

```text
.ai/agents/
  hr.agent.md
  developer.agent.md
  contents-creator.agent.md
  finance.agent.md
  pm.agent.md

.ai/skills/
  hr/
  developer/
  contents-creator/
  finance/
  pm/
  _shared/
```

주의:

- 에이전트의 업무 전문성은 각 agent/skill 파일에 둔다.
- `agent.rules.md`는 공통 운영, 협업, 권한 경계만 정의한다.

---

## 7. 룰 파일 공통 템플릿

각 신규 룰 파일은 다음 구조를 사용한다.

```markdown
# [Rule Name]

## Scope

## Load When

## Responsibilities

## Rules

## Validation

## Related Rules
```

각 파일의 상단에는 반드시 `Load When`을 둔다. 선택 로딩이 작동하려면 에이전트가 언제 파일을 읽어야 하는지 명확해야 한다.

---

## 8. 마이그레이션 안전 정책

이 단계에서는 중복과 표류를 엄격히 관리한다.

허용되는 임시 중복:

- `rules.md`의 짧은 위치 안내
- 기존 섹션명과 새 파일 위치를 연결하는 `Migration Map`
- 전환 중임을 알리는 한두 문장의 설명

허용되지 않는 중복:

- 같은 규칙 본문이 `rules.md`와 하위 룰 파일에 장기간 공존하는 것
- 도메인 룰이 운영 룰의 실행 절차를 복제하는 것
- 운영 룰이 특정 도메인의 산출물 기준을 복제하는 것
- 어댑터가 공유 규칙 본문을 복제하는 것

부분 마이그레이션 표류를 막기 위해, 본문을 이동한 섹션은 같은 작업 단위 안에서 `rules.md`의 상세 본문을 제거하거나 전환 안내로 축소한다. 이동 대상만 만들고 기존 위치를 방치하지 않는다.

---

## 9. 구현 순서

### Step 1. 신규 룰 파일 생성

먼저 신규 파일을 생성하되, 기존 `rules.md` 본문은 바로 삭제하지 않는다.

생성 대상:

```text
.ai/rules/domains/documentation.rules.md
.ai/rules/domains/development.rules.md
.ai/rules/domains/hr.rules.md
.ai/rules/operations/workflow.rules.md
.ai/rules/operations/validation.rules.md
.ai/rules/operations/agent.rules.md
```

### Step 2. 본문 이동

현재 `rules.md`의 섹션을 위 설계에 따라 새 파일로 이동한다. 이동할 때 다음을 정리한다.

- 깨진 문자로 보이는 화살표나 제목은 정상 ASCII 또는 영어 문구로 교체한다.
- 중복된 SSoT 선언은 제거한다.
- Claude 전용 지침은 글로벌 룰에 남기지 않는다.
- Docker/build/runtime은 `development.rules.md`로 이동한다.
- workflow, validation, agent 실행 절차는 `operations/`로 이동한다.
- 도메인 산출물 기준은 `domains/`로 이동한다.

### Step 3. `rules.md` 축소

새 파일에 본문이 들어간 뒤 `rules.md`를 글로벌 계약 중심으로 축소한다.

전환 기간 동안 포함할 매핑:

```markdown
## Migration Map

This map is transitional and should not become the permanent rule index.

- Language and content rules -> `.ai/rules/domains/documentation.rules.md`
- Development rules -> `.ai/rules/domains/development.rules.md`
- HR evaluation rules -> `.ai/rules/domains/hr.rules.md`
- Workflow rules -> `.ai/rules/operations/workflow.rules.md`
- Validation rules -> `.ai/rules/operations/validation.rules.md`
- Agent rules -> `.ai/rules/operations/agent.rules.md`
```

### Step 4. 중복 제거

새 룰 파일과 `rules.md`에 같은 규칙 본문이 길게 중복되지 않도록 정리한다. 한 번의 전환 기간 동안 짧은 요약과 위치 안내는 허용하지만, 본문 중복은 남기지 않는다.

---

## 10. 구현 후 검증

구조 검증:

```powershell
Test-Path .ai/rules/domains/documentation.rules.md
Test-Path .ai/rules/domains/development.rules.md
Test-Path .ai/rules/domains/hr.rules.md
Test-Path .ai/rules/operations/workflow.rules.md
Test-Path .ai/rules/operations/validation.rules.md
Test-Path .ai/rules/operations/agent.rules.md
```

중복 검증 후보:

```powershell
rg -n "Project Guidelines|Docker|Makefile|L1/L2|HR Evaluation|Validation System|Workflow System" .ai/rules
```

판정:

- `rules.md`에는 위 키워드의 상세 본문이 남아 있으면 안 된다.
- `rules.md`의 짧은 `Migration Map`이나 위치 안내는 허용한다.
- 각 키워드는 책임 있는 하위 룰 파일에 위치해야 한다.

심볼릭 링크 검증:

```powershell
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
```

인코딩 검증:

```powershell
$paths = @(
  '.ai/rules/rules.md',
  '.ai/rules/domains/documentation.rules.md',
  '.ai/rules/domains/development.rules.md',
  '.ai/rules/domains/hr.rules.md',
  '.ai/rules/operations/workflow.rules.md',
  '.ai/rules/operations/validation.rules.md',
  '.ai/rules/operations/agent.rules.md'
)
$paths | ForEach-Object {
  $bytes = [System.IO.File]::ReadAllBytes($_)
  "$_ $($bytes[0].ToString('X2')) $($bytes[1].ToString('X2')) $($bytes[2].ToString('X2'))"
}
```

첫 3바이트가 `EF BB BF`이면 실패다.

---

## 11. 완료 기준

- `rules.md`는 글로벌 계약 중심으로 축소되었다.
- `Migration Map`은 전환 안내로만 남아 있고 영구 인덱스로 취급되지 않는다.
- 도메인 규칙은 `domains/`에 위치한다.
- 운영 규칙은 `operations/`에 위치한다.
- `documentation.rules.md`는 문서 구조와 작성 방식만 소유한다.
- 도메인별 산출물 위치는 해당 도메인 룰이 소유한다.
- Docker/build/runtime 지침은 `development.rules.md`에 위치한다.
- workflow, validation, agent 규칙은 `operations/`에 위치한다.
- 도메인 룰은 운영 룰을 참조할 수 있지만 복제하지 않는다.
- 각 신규 룰 파일에는 `Scope`, `Load When`, `Responsibilities`, `Rules`, `Validation`, `Related Rules`가 있다.
- `.ai/` 하위 신규 문서는 영어로 작성되었다.
- 모든 신규 파일은 UTF-8 without BOM이다.
- 심볼릭 링크는 없다.

