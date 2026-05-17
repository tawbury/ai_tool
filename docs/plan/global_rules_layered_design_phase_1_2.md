# 글로벌 룰 레이어드 전환 설계 1: 기반 안정화와 디렉터리 골격

**작성일**: 2026-05-17  
**문서 상태**: 설계  
**대상 페이즈**: Phase 1, Phase 2  
**관련 계획 문서**: `docs/plan/global_rules_split_proposal_plan.md`  
**구현 범위**: 현재 구조 검증, 루트 어댑터 안정화 확인, `.ai/rules/domains/`, `.ai/rules/operations/` 골격 도입, `.ai/rules/README.md` 갱신

---

## 1. 설계 목적

이 설계 문서는 레이어드 룰 아키텍처 전환의 준비 단계를 정의한다. Phase 1-2는 실제 룰 본문을 이동하거나 에이전트 동작을 바꾸는 단계가 아니다. 현재 코드베이스가 안전하게 전환 가능한 상태인지 확인하고, Phase 3-5의 룰 본문 분리와 Phase 6-7의 어댑터/검증 정리를 위한 탐색 구조를 먼저 마련하는 단계다.

이 단계에서 `.ai/rules/rules.md`는 계속 모든 AI CLI의 글로벌 SSoT이자 첫 번째 룰 진입점이다. 이후 섹션에서는 이 파일을 `rules.md`로 표기한다.

---

## 2. 현재 코드베이스 상태

현재 확인된 주요 구조는 다음과 같다.

```text
.
  AGENTS.md
  CLAUDE.md
  GEMINI.md
  README.md

  .ai/
    README.md
    agents/
    rules/
      README.md
      rules.md
    skills/
    templates/
    validators/
    workflows/

  docs/
    plan/
```

루트 어댑터 상태:

| 파일 | 현재 역할 | 평가 |
|---|---|---|
| `AGENTS.md` | Codex 및 범용 AI CLI 어댑터 | 이미 얇은 어댑터 형태 |
| `CLAUDE.md` | Claude Code 어댑터 | 이미 얇은 어댑터 형태 |
| `GEMINI.md` | Gemini CLI 어댑터 | 이미 얇은 어댑터 형태 |

`.ai/rules/` 상태:

| 경로 | 상태 | 평가 |
|---|---|---|
| `.ai/rules/rules.md` | 단일 글로벌 룰 파일 | SSoT 역할은 유지하되 내용이 과도하게 혼합됨 |
| `.ai/rules/README.md` | 룰 디렉터리 설명 | 현재는 단일 룰 파일과 확장 정책 중심 |
| `.ai/rules/domains/` | 없음 | Phase 2에서 생성 필요 |
| `.ai/rules/operations/` | 없음 | Phase 2에서 생성 필요 |

심볼릭 링크 상태:

- 현재 `Get-ChildItem -Recurse -Force -Attributes ReparsePoint` 기준 출력 없음.
- 룰 파일과 룰 디렉터리에 심볼릭 링크는 없는 상태로 간주한다.

---

## 3. Phase 1-2의 책임 경계

Phase 1-2의 책임은 "안전한 증분 마이그레이션을 가능하게 만드는 것"이다. 이 단계는 다음 후속 단계와 직접 연결된다.

| 후속 단계 | Phase 1-2가 준비하는 것 |
|---|---|
| Phase 3 | `rules.md`를 글로벌 계약으로 축소할 때 참조할 레이어 구조와 README 인덱스 |
| Phase 4 | `domains/` 아래 도메인 룰을 생성하고 이동할 수 있는 디렉터리 기준 |
| Phase 5 | `operations/` 아래 운영 룰을 생성하고 이동할 수 있는 디렉터리 기준 |
| Phase 6 | 루트 어댑터가 계속 `rules.md`만 참조해도 새 구조를 발견할 수 있는 안내 경로 |
| Phase 7 | 구조, 심볼릭 링크, 인코딩, 선택 로딩 안내를 검증할 수 있는 기준 |

따라서 이 단계에서는 다음을 하지 않는다.

- `rules.md`의 상세 규칙 본문을 제거하지 않는다.
- 도메인/운영 룰 파일을 대량으로 미리 만들지 않는다.
- 루트 어댑터에 공유 규칙 본문을 추가하지 않는다.
- 선택 로딩 정책을 실제 동작 변경으로 강제하지 않는다.

---

## 4. 설계 원칙

1. 기존 동작을 깨지 않는다.
2. `rules.md`는 계속 글로벌 룰의 단일 진입점이다.
3. 새 디렉터리는 일반 디렉터리로 만든다. 심볼릭 링크를 사용하지 않는다.
4. 공유 규칙 본문은 루트 어댑터나 README에 복제하지 않는다.
5. 빈 룰 파일을 과도하게 선점하지 않는다.
6. 필요한 최소 룰 세트만 로드한다.
7. `.ai/` 하위 문서는 영어로 작성한다.
8. `docs/` 하위 설계 문서는 한국어로 작성한다.
9. 모든 파일은 UTF-8 without BOM으로 유지한다.

---

## 5. 목표 구조

Phase 1-2 완료 후 목표 구조는 다음과 같다.

```text
.ai/
  rules/
    README.md
    rules.md

    domains/
      README.md

    operations/
      README.md
```

Phase 3-5에서 실제 본문 이동이 시작되면 다음 파일들이 추가된다.

```text
.ai/
  rules/
    domains/
      documentation.rules.md
      development.rules.md
      hr.rules.md

    operations/
      workflow.rules.md
      validation.rules.md
      agent.rules.md
```

Phase 1-2에서는 기본적으로 디렉터리와 README만 만든다. 실제 룰 파일은 이동할 본문과 책임 범위가 확정되는 Phase 3-5에서 만든다.

---

## 6. README의 위치와 책임

`.ai/rules/README.md`는 규칙 원본이 아니라 룰 시스템의 탐색 문서다. 이 파일은 다음 네 가지 역할을 가진다.

- 아키텍처 인덱스: `rules.md`, `domains/`, `operations/`의 관계를 설명한다.
- 룰 발견 가이드: 에이전트가 어떤 위치에서 추가 룰을 찾을지 안내한다.
- 선택 로딩 참조: 현재 작업에 필요한 최소 룰 세트를 고르는 기준을 제공한다.
- 마이그레이션 내비게이션: Phase 3-7에서 세부 규칙이 어디로 이동되는지 추적할 수 있게 한다.

README에 넣지 않을 내용:

- 도메인 룰 본문
- 운영 룰 본문
- 템플릿 목록 전체
- HR 평가 절차
- Docker/build/runtime 세부 지침
- L1/L2 협업 상세 규칙
- 검증 체크리스트

권장 구조:

```markdown
# Rules Directory

## Source of Truth
## Rule Layers
## Selective Loading
## Migration Navigation
## Adding Domain Rules
## Adding Operational Rules
## Adapter Policy
## Symlink Policy
```

README는 중복 규칙 저장소가 되면 안 된다. 실제 우선순위와 글로벌 계약은 `rules.md`에 두고, README는 탐색과 전환 안내만 담당한다.

---

## 7. 선택 로딩 원칙

선택 로딩의 기준 문장은 다음과 같다.

> 현재 작업에 충분한 최소 룰 세트를 로드한다.

이 원칙이 중요한 이유는 세 가지다.

- 컨텍스트 효율: 모든 작업에서 HR, 개발, 문서화, 검증, 에이전트 규칙을 한꺼번에 읽지 않는다.
- 다중 CLI 확장성: Codex CLI, Claude Code, Gemini CLI가 같은 진입점을 쓰되 각 작업에 필요한 하위 룰만 참조할 수 있다.
- 미래 도메인 확장: 마케팅, 리서치, 세일즈, 재무 같은 도메인이 추가되어도 모든 작업의 기본 컨텍스트가 계속 커지지 않는다.

Phase 1-2에서는 이 원칙을 README와 디렉터리 구조에 반영한다. 실제 선택 로딩 대상 파일과 세부 `Load When` 기준은 Phase 3-5에서 각 룰 파일을 만들 때 정의한다.

---

## 8. 빈 파일 정책

Phase 1-2에서는 룰 파일을 과도하게 미리 만들지 않는다. 빈 파일을 많이 만들면 구조가 완성된 것처럼 보이지만, 실제로는 다음 문제가 생긴다.

- 유지보수 책임이 없는 파일이 늘어난다.
- 아직 경계가 확정되지 않은 규칙을 조기에 분류하게 된다.
- 향후 도메인이 늘어날 때 룰 파일 난립을 정당화하는 선례가 된다.
- 선택 로딩 기준이 실제 규칙이 아니라 파일 이름 중심으로 흐려진다.

따라서 이 단계의 기본 산출물은 `domains/README.md`와 `operations/README.md`까지다. `documentation.rules.md`, `development.rules.md`, `hr.rules.md`, `workflow.rules.md`, `validation.rules.md`, `agent.rules.md`는 Phase 3-5에서 실제 본문 이동과 함께 생성한다.

예외적으로 같은 작업 세션에서 Phase 3-5 구현까지 연속 진행하기로 확정된 경우에만 초기 룰 파일을 함께 생성할 수 있다.

---

## 9. 계층별 README 설계

### 9.1 `domains/README.md`

`domains/README.md`는 도메인 룰의 의미와 추가 기준을 설명한다.

포함할 내용:

- 도메인 룰은 "무엇을 만들고 어떤 업무 기준을 따르는가"를 정의한다.
- 초기 후보는 `documentation`, `development`, `hr`이다.
- 향후 후보는 `marketing`, `research`, `sales`, `finance`이다.
- 단일 작업이나 일회성 지침만으로 새 도메인 파일을 만들지 않는다.
- 도메인 룰은 운영 룰을 복제하지 않는다.

구현 시 이 파일은 영어로 작성한다.

### 9.2 `operations/README.md`

`operations/README.md`는 운영 룰의 의미와 추가 기준을 설명한다.

포함할 내용:

- 운영 룰은 "어떻게 실행하고 통제할 것인가"를 정의한다.
- 초기 후보는 `workflow`, `validation`, `agent`이다.
- 운영 룰은 특정 업무 도메인에 종속되지 않는다.
- 여러 도메인에 공통 적용되는 실행 규칙만 운영 룰로 둔다.
- 업무 산출물의 세부 기준은 `domains/`에 둔다.

구현 시 이 파일도 영어로 작성한다.

---

## 10. 구현 작업 목록

### 10.1 현 상태 확인

실행할 확인:

```powershell
git status --short
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
Test-Path .ai/rules/rules.md
Test-Path AGENTS.md
Test-Path CLAUDE.md
Test-Path GEMINI.md
```

판정 기준:

- `rules.md`가 존재한다.
- 루트 어댑터 3개가 존재한다.
- 심볼릭 링크가 없다.
- 작업 전 변경 상태를 기록한다.

### 10.2 디렉터리 생성

생성 대상:

```text
.ai/rules/domains/
.ai/rules/operations/
```

주의:

- 일반 디렉터리로 생성한다.
- 심볼릭 링크를 만들지 않는다.
- 기존 `rules.md` 위치를 변경하지 않는다.

### 10.3 README 갱신

갱신 대상:

```text
.ai/rules/README.md
.ai/rules/domains/README.md
.ai/rules/operations/README.md
```

언어:

- `.ai/` 하위 문서이므로 영어로 작성한다.

책임 경계:

- README는 탐색과 마이그레이션 안내를 담당한다.
- 운영 정책의 상세 본문은 Phase 3-5의 `operations/*.rules.md`에서 다룬다.
- 도메인별 업무 기준은 Phase 3-5의 `domains/*.rules.md`에서 다룬다.

### 10.4 루트 어댑터 검토

현재 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`는 이미 얇은 어댑터로 구성되어 있다. Phase 1-2에서는 원칙적으로 수정하지 않는다.

수정이 필요한 경우:

- `rules.md` 참조가 빠져 있을 때
- 공유 규칙 본문이 어댑터에 복제되어 있을 때
- 심볼릭 링크 사용을 안내할 때

현재 상태에서는 수정 불필요로 판단한다.

---

## 11. 구현 후 검증

필수 검증:

```powershell
Test-Path .ai/rules/domains
Test-Path .ai/rules/operations
Test-Path .ai/rules/domains/README.md
Test-Path .ai/rules/operations/README.md
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
git status --short
```

인코딩 검증:

```powershell
$paths = @(
  '.ai/rules/README.md',
  '.ai/rules/domains/README.md',
  '.ai/rules/operations/README.md'
)

$paths | ForEach-Object {
  $bytes = [System.IO.File]::ReadAllBytes($_)
  "$_ $($bytes[0].ToString('X2')) $($bytes[1].ToString('X2')) $($bytes[2].ToString('X2'))"
}
```

첫 3바이트가 `EF BB BF`이면 BOM이 있으므로 실패다.

---

## 12. 완료 기준

- `.ai/rules/domains/`가 일반 디렉터리로 존재한다.
- `.ai/rules/operations/`가 일반 디렉터리로 존재한다.
- `.ai/rules/README.md`가 아키텍처 인덱스, 룰 발견 가이드, 선택 로딩 참조, 마이그레이션 내비게이션 역할을 설명한다.
- `domains/README.md`와 `operations/README.md`가 각 계층의 추가 기준을 설명한다.
- `rules.md` 경로와 기존 본문은 Phase 1-2에서 대규모 변경되지 않았다.
- 루트 어댑터는 계속 얇은 상태다.
- 심볼릭 링크는 없다.
- 새 `.ai/` 문서는 영어이며 UTF-8 without BOM이다.

