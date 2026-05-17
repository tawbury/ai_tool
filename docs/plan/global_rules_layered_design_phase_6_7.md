# 글로벌 룰 레이어드 전환 설계 3: 어댑터 정합성, 검증, 운영 안정화

**작성일**: 2026-05-17  
**문서 상태**: 설계  
**대상 페이즈**: Phase 6, Phase 7  
**관련 계획 문서**: `docs/plan/global_rules_split_proposal_plan.md`  
**구현 범위**: 루트 어댑터 및 README 정합성 확인, 선택 로딩 안내 검증, 중복 규칙 제거, 최종 운영 검증, 안정화 후 유지보수 기준 정의

---

## 1. 설계 목적

이 설계 문서는 레이어드 룰 구조를 실제 운영 가능한 상태로 안정화하는 마무리 단계를 정의한다. Phase 3-5에서 룰 본문이 이동되더라도, 어댑터와 README, 검증 절차가 정리되지 않으면 Codex CLI, Claude Code, Gemini CLI가 새 구조를 일관되게 사용하기 어렵다.

Phase 6-7의 목표는 다음과 같다.

- 루트 어댑터가 계속 얇은 상태인지 확인한다.
- `rules.md`, `.ai/rules/README.md`, 루트 어댑터의 책임을 분리한다.
- README가 룰 원본이 아니라 탐색과 선택 로딩 안내 역할만 하도록 정리한다.
- 구조, 중복, 어댑터, 심볼릭 링크, 인코딩 검증을 수행한다.
- 전환 후 새 룰 파일 추가와 변경 기준을 문서화한다.
- 문제가 생기면 공격적인 정리보다 작동 가능한 룰 발견 복구를 우선한다.

---

## 2. 안정화 후 목표 상태

마이그레이션이 안정화된 뒤 저장소의 룰 구조는 다음 상태를 목표로 한다.

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

AGENTS.md
CLAUDE.md
GEMINI.md
```

전환 중 동작:

- `rules.md`에 짧은 `Migration Map`을 둘 수 있다.
- 기존 섹션명과 새 파일 위치를 연결하는 안내를 유지할 수 있다.
- 필요하면 일시적으로 일부 요약을 남겨 룰 발견 실패를 막는다.

안정화 후 동작:

- `rules.md`는 글로벌 계약만 포함한다.
- `.ai/rules/README.md`는 구조 탐색과 선택 로딩 안내만 제공한다.
- 루트 어댑터는 `rules.md` 발견과 도구 런타임 호환성만 돕는다.
- 도메인 규칙은 `domains/`, 운영 규칙은 `operations/`에만 본문으로 존재한다.
- 장기적인 본문 중복은 허용하지 않는다.

---

## 3. 계층별 책임 경계

### 3.1 `rules.md`

역할:

- 글로벌 SSoT
- 규칙 우선순위
- 루트 어댑터 정책
- 레이어 구조의 최소 설명
- 선택 로딩 원칙
- 심볼릭 링크 금지
- 최상위 언어 및 인코딩 원칙

금지:

- 도메인 룰 본문
- 운영 룰 본문
- 도구별 상세 지침
- 템플릿 전체 목록
- validator 또는 workflow 세부 절차

### 3.2 `.ai/rules/README.md`

역할:

- 룰 구조의 내비게이션 레이어
- 아키텍처 발견 레이어
- 선택 로딩 가이드
- 현재 존재하는 룰 파일 목록
- 새 룰 추가 기준 요약

금지:

- 규칙 우선순위 원본 역할
- 도메인/운영 룰 본문 복제
- `rules.md`를 대체하는 보조 SSoT 역할

### 3.3 루트 어댑터

대상:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
```

역할:

- 각 AI CLI가 `rules.md`를 발견하도록 돕는다.
- 도구별 런타임 지침과 프로젝트 룰의 우선순위 관계를 짧게 안내한다.
- 심볼릭 링크 금지 같은 발견 안정성 원칙을 짧게 안내한다.

금지:

- 공유 규칙 본문 복제
- 도메인/운영 룰 인덱스 역할
- `rules.md`와 경쟁하는 2차 룰 원본 역할

---

## 4. 현재 어댑터 상태와 처리 방침

현재 루트 어댑터는 목표 방향에 가깝다.

| 파일 | 현재 평가 | Phase 6-7 방침 |
|---|---|---|
| `AGENTS.md` | Codex 및 범용 AI CLI용 얇은 어댑터 | 원칙적으로 수정하지 않음 |
| `CLAUDE.md` | Claude Code용 얇은 어댑터 | Claude 전용 상세 규칙을 추가하지 않음 |
| `GEMINI.md` | Gemini CLI용 얇은 어댑터 | 구조 설명을 길게 추가하지 않음 |

선택적으로 한 문장만 추가할 수 있다.

```markdown
For task-specific rules, follow the domain and operational rule references listed in `.ai/rules/rules.md`.
```

이 문구도 `rules.md`가 충분히 안내한다면 생략한다. 어댑터는 발견과 호환성을 위한 파일이지 규칙 탐색 인덱스가 아니다.

---

## 5. README 갱신 기준

### 5.1 `.ai/rules/README.md`

권장 섹션:

```markdown
# Rules Directory

## Source of Truth
## Layers
## Selective Loading
## Current Rule Files
## Adding New Rules
## Adapter Policy
## Symlink Policy
## Encoding Policy
```

`Current Rule Files`에는 실제 존재하는 파일만 나열한다. 아직 만들지 않은 향후 도메인 파일을 실제 파일처럼 표시하지 않는다. README는 탐색 문서이므로 규칙 본문을 길게 포함하지 않는다.

### 5.2 `domains/README.md`

포함할 내용:

- 도메인 룰의 정의
- 현재 도메인 룰 목록
- 새 도메인 추가 조건
- 운영 룰과의 경계
- 관련 운영 룰을 참조하는 방식

### 5.3 `operations/README.md`

포함할 내용:

- 운영 룰의 정의
- 현재 운영 룰 목록
- 새 운영 룰 추가 조건
- 도메인 룰과의 경계
- 여러 도메인에 공통 적용된다는 원칙

---

## 6. 최종 검증 설계

Phase 7 검증은 운영 무결성 확인이다. 단순히 파일이 존재하는지만 보는 것이 아니라 다음을 함께 확인한다.

1. 구조 검증
2. 중복 검증
3. 어댑터 검증
4. 심볼릭 링크 검증
5. 인코딩 검증

### 6.1 구조 검증

```powershell
Test-Path .ai/rules/rules.md
Test-Path .ai/rules/domains
Test-Path .ai/rules/operations
Test-Path .ai/rules/domains/documentation.rules.md
Test-Path .ai/rules/domains/development.rules.md
Test-Path .ai/rules/domains/hr.rules.md
Test-Path .ai/rules/operations/workflow.rules.md
Test-Path .ai/rules/operations/validation.rules.md
Test-Path .ai/rules/operations/agent.rules.md
```

판정:

- 필수 파일과 디렉터리가 존재해야 한다.
- 루트 `.ai/rules/`에는 `rules.md`, `README.md`, `domains/`, `operations/`만 두는 것을 권장한다.

### 6.2 중복 검증

```powershell
rg -n "HR Evaluation|Development Documentation Workflow|Workflow System v2|Validation System|L1/L2 Agent System|Project Guidelines" .ai/rules
```

판정:

- `rules.md`에 상세 본문이 남아 있으면 실패다.
- `rules.md`의 짧은 위치 안내나 전환용 `Migration Map`은 허용한다.
- 각 키워드는 책임 있는 하위 룰 파일에 위치해야 한다.

### 6.3 어댑터 검증

```powershell
Get-Content -Raw AGENTS.md
Get-Content -Raw CLAUDE.md
Get-Content -Raw GEMINI.md
```

검토 기준:

- 세 파일 모두 `.ai/rules/rules.md`를 참조한다.
- 공유 규칙 본문을 복제하지 않는다.
- 도구별 특수 내용은 최소한으로 유지한다.
- 어댑터가 도메인/운영 룰의 상세 인덱스가 되지 않는다.

### 6.4 심볼릭 링크 검증

```powershell
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
```

판정:

- 출력이 없어야 한다.
- 출력이 있다면 룰 파일이나 룰 디렉터리와 관련된 항목인지 확인한다.
- 룰 관련 심볼릭 링크는 제거하고 일반 파일 또는 일반 디렉터리로 대체한다.

### 6.5 인코딩 검증

검증 대상:

```text
.ai/rules/rules.md
.ai/rules/README.md
.ai/rules/domains/README.md
.ai/rules/domains/documentation.rules.md
.ai/rules/domains/development.rules.md
.ai/rules/domains/hr.rules.md
.ai/rules/operations/README.md
.ai/rules/operations/workflow.rules.md
.ai/rules/operations/validation.rules.md
.ai/rules/operations/agent.rules.md
AGENTS.md
CLAUDE.md
GEMINI.md
```

확인 방식:

```powershell
$paths = @(
  '.ai/rules/rules.md',
  '.ai/rules/README.md',
  '.ai/rules/domains/README.md',
  '.ai/rules/domains/documentation.rules.md',
  '.ai/rules/domains/development.rules.md',
  '.ai/rules/domains/hr.rules.md',
  '.ai/rules/operations/README.md',
  '.ai/rules/operations/workflow.rules.md',
  '.ai/rules/operations/validation.rules.md',
  '.ai/rules/operations/agent.rules.md',
  'AGENTS.md',
  'CLAUDE.md',
  'GEMINI.md'
)

$paths | ForEach-Object {
  if (Test-Path $_) {
    $bytes = [System.IO.File]::ReadAllBytes($_)
    "$_ $($bytes[0].ToString('X2')) $($bytes[1].ToString('X2')) $($bytes[2].ToString('X2'))"
  }
}
```

판정:

- 첫 3바이트가 `EF BB BF`이면 실패다.
- 모든 대상 파일은 UTF-8 without BOM이어야 한다.

---

## 7. 안정화 후 운영 정책

### 7.1 룰 변경 검토 기준

- 글로벌 계약 변경은 가장 보수적으로 검토한다.
- 도메인 룰 변경은 해당 도메인의 산출물, 관련 템플릿, 관련 validator 참조를 함께 확인한다.
- 운영 룰 변경은 여러 도메인에 영향을 줄 수 있으므로 영향 범위를 명시한다.
- README 변경은 탐색과 안내 정확성을 확인한다. README에 새 규칙 본문을 넣지 않는다.
- 어댑터 변경은 각 CLI의 발견 가능성과 런타임 호환성만 확인한다.

### 7.2 새 도메인 추가 기준

새 도메인 파일은 다음 조건을 만족할 때만 추가한다.

- 반복적으로 사용되는 업무 규칙이 있다.
- 기존 도메인 파일에 넣으면 책임 경계가 흐려진다.
- 산출물, 검증 기준, 승인 흐름이 도메인 특수성을 가진다.
- 선택 로딩으로 컨텍스트 절감 효과가 있다.

향후 후보:

```text
.ai/rules/domains/marketing.rules.md
.ai/rules/domains/research.rules.md
.ai/rules/domains/sales.rules.md
.ai/rules/domains/finance.rules.md
```

이 파일들은 실제 필요가 생기기 전에는 만들지 않는다.

### 7.3 새 운영 룰 추가 기준

새 운영 룰은 여러 도메인에 공통 적용되는 실행 통제 기준일 때만 추가한다.

가능한 향후 후보:

```text
.ai/rules/operations/audit.rules.md
.ai/rules/operations/security.rules.md
.ai/rules/operations/tooling.rules.md
```

단, 보안이나 도구 규칙이 특정 도메인에만 적용된다면 `domains/`에 두는 것이 맞다.

---

## 8. 구현 후 문서 정리

정리 대상:

```text
README.md
.ai/README.md
.ai/rules/README.md
docs/plan/global_rules_split_proposal_plan.md
```

정리 원칙:

- `README.md`에는 최상위 구조 요약만 둔다.
- `.ai/README.md`에는 AI 시스템 구조를 설명한다.
- `.ai/rules/README.md`에는 룰 계층, 선택 로딩, 현재 룰 파일 목록을 설명한다.
- 계획 문서는 의사결정과 배경을 보존한다.
- 설계 문서는 실제 구현 단위와 검증 기준을 보존한다.

현재 `README.md`와 일부 기존 `docs/plan` 문서는 콘솔 출력 기준 한글이 깨져 보인다. 이 문제는 레이어드 룰 구현과 직접 연결된 파일부터 우선 처리하고, 과거 문서의 인코딩 정비는 별도 작업으로 분리하는 것이 안전하다.

---

## 9. 롤백 철학

롤백의 우선순위는 깔끔한 구조 복원이 아니라 룰 발견과 에이전트 작동성 복구다. 전환 중 문제가 생기면 공격적으로 정리하기보다, AI CLI가 다시 `rules.md`를 통해 필요한 규칙 위치를 찾을 수 있게 만드는 것을 먼저 처리한다.

롤백 대상:

- 신규 생성한 `domains/`, `operations/` 파일
- 축소한 `rules.md`
- 갱신한 `.ai/rules/README.md`

롤백 원칙:

- 작동 불능 상태라면 임시 중복이 깨진 룰 발견보다 낫다.
- `rules.md`의 `Migration Map`은 하위 룰 파일 로딩 실패 시 위치를 파악하기 위한 안전장치로 유지할 수 있다.
- 완전 롤백보다 필요한 본문만 일시 복원하는 부분 롤백을 우선 고려한다.
- 안정화 후에는 임시 중복을 다시 제거한다.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 얇은 어댑터 상태를 유지하므로 롤백 대상이 되지 않도록 한다.

---

## 10. 완료 기준

- 안정화 후 목표 구조가 실제 저장소에 반영되어 있다.
- 루트 어댑터 3개가 얇은 상태로 유지된다.
- 어댑터는 2차 룰 원본이나 상세 인덱스가 아니다.
- `rules.md`는 글로벌 계약만 포함한다.
- `.ai/rules/README.md`는 내비게이션, 아키텍처 발견, 선택 로딩 안내만 담당한다.
- 각 하위 룰 파일의 `Load When` 기준이 명확하다.
- Docker/build/runtime은 개발 도메인 룰에 있다.
- 워크플로우, 검증, 에이전트 협업은 운영 룰에 있다.
- 공유 규칙 본문은 어댑터나 README에 복제되지 않는다.
- 심볼릭 링크가 없다.
- 모든 대상 파일은 UTF-8 without BOM이다.
- `git status --short`로 변경 범위를 명확히 확인할 수 있다.

