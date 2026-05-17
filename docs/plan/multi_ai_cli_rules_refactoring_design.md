# 멀티 AI CLI Rules 리팩토링 설계 문서

**작성일**: 2026-05-17  
**문서 상태**: 설계  
**관련 계획 문서**: `docs/plan/multi_ai_cli_rules_refactoring_plan.md`  
**대상 저장소**: `D:\development\_templates\ai_tool`

---

## 1. 설계 목적

Codex, Claude Code, Gemini CLI를 동시에 사용하는 환경에서 `.ai/rules/rules.md`를 공통 메인 글로벌 rules로 사용하도록 구조를 정리한다. 루트의 AI CLI별 지침 파일은 독립 규칙 원본이 아니라 공통 rules를 참조하는 얇은 어댑터로 만든다.

추가로 현재 프로젝트 안에 남아 있는 모든 심볼릭 링크를 제거한다. Windows 환경, Git clone 환경, AI CLI의 파일 인덱싱 방식에서 심볼릭 링크는 깨지거나 무시될 수 있으므로, 앞으로는 일반 파일과 일반 디렉터리만 사용한다.

---

## 2. 코드베이스 스캔 결과

현재 발견된 심볼릭 링크는 다음 4개다.

| 경로 | 유형 | 현재 대상 | 문제 |
|---|---|---|---|
| `CLAUDE.md` | 파일 심볼릭 링크 | `.ai/rules/rules.mdc` | 대상 파일이 현재 존재하지 않음. 실제 rules는 `.ai/rules/rules.md`임 |
| `.cursor/rules` | 디렉터리 심볼릭 링크 | `.ai/rules` | Cursor가 링크 디렉터리를 안정적으로 인덱싱한다는 보장이 낮음 |
| `.windsurf/rules` | 디렉터리 심볼릭 링크 | `.ai/rules` | Windsurf 환경에서도 동일한 링크 인식 문제가 생길 수 있음 |
| `.github/copilot-instructions.md` | 파일 심볼릭 링크 | `.ai/rules/rules.mdc` | 대상 파일이 현재 존재하지 않음 |

현재 루트 AI CLI 파일 상태는 다음과 같다.

| 경로 | 현재 상태 | 설계 방향 |
|---|---|---|
| `CLAUDE.md` | 심볼릭 링크, 대상 깨짐 | 일반 Markdown 파일로 교체 |
| `AGENTS.md` | 없음 | 신규 생성 |
| `GEMINI.md` | 일반 파일, 내용 존재 | 공통 rules 참조 어댑터로 정리 |

현재 공통 rules 원본은 다음 파일이다.

```text
.ai/rules/rules.md
```

---

## 3. 목표 구조

리팩토링 후 구조는 다음과 같다.

```text
.ai/
  rules/
    README.md
    rules.md

CLAUDE.md
AGENTS.md
GEMINI.md

.cursor/
  README.md
  rules/
    rules.md

.windsurf/
  README.md
  rules/
    rules.md

.github/
  README.md
  copilot-instructions.md
```

`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`는 공통 rules를 직접 복사하지 않는다. 대신 `.ai/rules/rules.md`를 먼저 읽고 적용하라는 지침만 둔다.

Cursor, Windsurf, GitHub Copilot은 도구 특성상 각자 기대하는 위치에 물리 파일이 필요할 수 있다. 따라서 `.cursor/rules/rules.md`, `.windsurf/rules/rules.md`, `.github/copilot-instructions.md`는 심볼릭 링크가 아닌 일반 파일로 둔다. 이 파일들은 원본 rules가 아니라 도구별 어댑터 파일이며, 공통 rules 위치를 안내한다.

---

## 4. 공통 Rules 기준

`.ai/rules/rules.md`를 유일한 공통 rules 원본으로 둔다.

적용 우선순위는 다음과 같이 설계한다.

1. 사용자의 최신 명시 요청
2. 각 AI CLI 런타임의 시스템 또는 개발자 지침
3. `.ai/rules/rules.md`
4. 현재 작업과 직접 관련된 추가 rules 파일
5. 루트 또는 도구별 어댑터 파일

추가 rules 파일은 지금 만들지 않는다. 향후 규칙이 커지거나 특정 도메인의 세부 규칙이 필요해질 때만 추가한다.

예시는 다음과 같은 수준으로만 문서에 남긴다.

- 검증 규칙이 커지면 validator 관련 rules를 별도 파일로 분리할 수 있다.
- 워크플로우 규칙이 커지면 workflow 관련 rules를 별도 파일로 분리할 수 있다.
- 문서 작성 규칙이나 에이전트 협업 규칙도 필요할 때 같은 방식으로 분리할 수 있다.

파일명은 지금 예약하지 않는다.

---

## 5. 루트 AI CLI 파일 설계

### 5.1 `CLAUDE.md`

`CLAUDE.md`는 Claude Code가 읽는 프로젝트 지침 파일로 둔다. 내용은 짧게 유지하고 `.ai/rules/rules.md`를 공통 rules로 읽도록 안내한다.

권장 내용:

```markdown
# Claude Code Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

Before making changes:

1. Read `.ai/rules/rules.md`.
2. Follow the latest explicit user request first.
3. Apply Claude Code-specific runtime instructions when they are stricter than project rules.
4. Treat this file as an adapter, not as the rule source.
```

### 5.2 `AGENTS.md`

`AGENTS.md`는 새로 생성한다. Codex와 향후 추가될 범용 AI CLI 에이전트가 공통으로 읽을 수 있는 루트 지침 파일로 사용한다.

권장 내용:

```markdown
# Agent Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

All AI CLI agents should:

1. Read `.ai/rules/rules.md` before editing files.
2. Keep tool-specific behavior in adapter files only.
3. Do not create symbolic links for rules files.
4. Add domain-specific rules only when there is a real maintenance need.
```

### 5.3 `GEMINI.md`

`GEMINI.md`는 현재 내용이 길고 일부 텍스트 인코딩이 깨져 보인다. 구현 단계에서는 Gemini CLI용 얇은 어댑터로 정리한다.

권장 내용:

```markdown
# Gemini CLI Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for shared AI agent rules.

Before making changes:

1. Read `.ai/rules/rules.md`.
2. Follow the latest explicit user request first.
3. Apply Gemini CLI-specific runtime instructions when they are stricter than project rules.
4. Treat this file as an adapter, not as the rule source.
```

---

## 6. 도구별 Rules 파일 설계

### 6.1 `.cursor/rules/rules.md`

현재 `.cursor/rules`는 심볼릭 링크다. 구현 시 링크를 제거하고 일반 디렉터리로 만든다.

파일 내용은 Cursor가 읽을 수 있는 안내 파일로 둔다.

```markdown
# Cursor Rules Adapter

The shared project rules are maintained in `.ai/rules/rules.md`.

Cursor agents must read and follow `.ai/rules/rules.md` before making changes.

This file is an adapter for Cursor. Do not treat it as the source of truth.
```

### 6.2 `.windsurf/rules/rules.md`

현재 `.windsurf/rules`도 심볼릭 링크다. 구현 시 링크를 제거하고 일반 디렉터리로 만든다.

```markdown
# Windsurf Rules Adapter

The shared project rules are maintained in `.ai/rules/rules.md`.

Windsurf agents must read and follow `.ai/rules/rules.md` before making changes.

This file is an adapter for Windsurf. Do not treat it as the source of truth.
```

### 6.3 `.github/copilot-instructions.md`

현재 이 파일은 깨진 대상 `.ai/rules/rules.mdc`를 가리키는 심볼릭 링크다. 구현 시 일반 Markdown 파일로 교체한다.

```markdown
# GitHub Copilot Instructions

The shared project rules are maintained in `.ai/rules/rules.md`.

GitHub Copilot and related agents should follow `.ai/rules/rules.md` for project-wide rules.

This file is an adapter for GitHub Copilot. Do not treat it as the source of truth.
```

---

## 7. 심볼릭 링크 제거 설계

구현 단계에서 삭제할 대상은 스캔 결과로 확인된 4개다.

```text
CLAUDE.md
.cursor/rules
.windsurf/rules
.github/copilot-instructions.md
```

삭제 전 확인 조건:

- 대상 경로가 실제로 `ReparsePoint` 속성을 가진다.
- 대상 경로가 프로젝트 루트 내부의 예상 경로다.
- 일반 파일이나 일반 디렉터리를 실수로 삭제하지 않는다.

PowerShell 구현 방향:

```powershell
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
```

위 명령으로 링크 목록을 확인한 뒤, 확인된 경로만 `Remove-Item -LiteralPath`로 제거한다. 재귀 삭제가 필요한 디렉터리 링크는 실제 대상 폴더가 아니라 링크 자체만 제거되도록 `-LiteralPath`를 사용한다.

삭제 후 같은 경로에 일반 파일 또는 일반 디렉터리를 만든다.

---

## 8. 구현 단계 설계

### Step 1. 사전 상태 확인

- `git status --short --branch`로 작업트리 상태 확인
- `Get-ChildItem -Recurse -Force -Attributes ReparsePoint`로 심볼릭 링크 목록 확인
- `Test-Path .ai/rules/rules.md`로 공통 rules 존재 확인

### Step 2. 심볼릭 링크 제거

- `CLAUDE.md` 링크 제거
- `.cursor/rules` 링크 제거
- `.windsurf/rules` 링크 제거
- `.github/copilot-instructions.md` 링크 제거

### Step 3. 일반 파일과 디렉터리 생성

- `CLAUDE.md` 일반 파일 생성
- `AGENTS.md` 신규 생성
- `GEMINI.md` 일반 파일로 정리
- `.cursor/rules/` 일반 디렉터리 생성
- `.cursor/rules/rules.md` 일반 파일 생성
- `.windsurf/rules/` 일반 디렉터리 생성
- `.windsurf/rules/rules.md` 일반 파일 생성
- `.github/copilot-instructions.md` 일반 파일 생성

### Step 4. 공통 rules 문구 보강

`.ai/rules/rules.md` 상단 또는 SSoT 섹션에 다음 내용을 반영한다.

- 이 파일이 Codex, Claude Code, Gemini CLI 및 향후 AI CLI의 공통 rules 원본이라는 점
- 루트 AI CLI 파일은 어댑터이며 rules 원본이 아니라는 점
- 심볼릭 링크를 사용하지 않는다는 점
- 도메인별 서브 rules는 필요할 때만 추가한다는 점

### Step 5. 문서 정합성 갱신

다음 문서의 구형 설명을 필요 시 갱신한다.

- `README.md`
- `.ai/rules/README.md`
- `.claude/README.md`
- `.cursor/README.md`
- `.windsurf/README.md`
- `.github/README.md`
- `docs/plan/symlink_refactoring_plan.md`

이번 구현의 최소 범위는 실제 동작 파일과 핵심 README 갱신으로 제한한다. 과거 분석 보고서나 로드맵 문서는 변경 이력 성격이 강하므로, 반드시 필요한 경우가 아니면 수정하지 않는다.

---

## 9. 검증 설계

구현 후 다음을 확인한다.

```powershell
Get-ChildItem -Recurse -Force -Attributes ReparsePoint
```

기대 결과:

```text
출력 없음
```

추가 확인:

```powershell
Test-Path CLAUDE.md
Test-Path AGENTS.md
Test-Path GEMINI.md
Test-Path .cursor/rules/rules.md
Test-Path .windsurf/rules/rules.md
Test-Path .github/copilot-instructions.md
git status --short --branch
```

Git 검증 기준:

- 심볼릭 링크가 Git에 남아 있지 않아야 한다.
- 새 어댑터 파일은 일반 파일로 추적되어야 한다.
- 작업 결과가 의도한 파일 변경으로만 구성되어야 한다.

---

## 10. 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| AI CLI가 상대 경로 참조를 자동으로 로드하지 않음 | `.ai/rules/rules.md`를 직접 읽지 않을 수 있음 | 루트 어댑터 파일에 명시적으로 “read `.ai/rules/rules.md` first”를 반복 명시 |
| Cursor/Windsurf가 어댑터 파일만 읽고 공통 rules를 로드하지 않음 | 공통 rules 적용 누락 | `.cursor/rules/rules.md`, `.windsurf/rules/rules.md`에도 동일한 참조 지침을 둠 |
| `GEMINI.md` 기존 내용 정리로 일부 과거 지침 손실 | Gemini 전용 작업 흐름 누락 가능 | 기존 내용 중 실제로 필요한 Gemini 전용 지침이 있으면 별도 섹션으로 최소 보존 |
| 서브 rules를 너무 일찍 분리 | 규칙 탐색 비용 증가 | 지금은 파일을 만들지 않고 예시와 확장 원칙만 문서화 |
| 일반 디렉터리 생성 중 링크 대상 삭제 위험 | `.ai/rules` 원본 손실 | 링크 삭제는 확인된 링크 경로에만 `-LiteralPath`로 수행 |

---

## 11. 완료 기준

- 프로젝트 내부 심볼릭 링크가 0개다.
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`가 모두 일반 파일이다.
- 세 루트 AI CLI 파일이 `.ai/rules/rules.md`를 공통 rules 원본으로 참조한다.
- `.cursor/rules`와 `.windsurf/rules`가 일반 디렉터리다.
- `.github/copilot-instructions.md`가 일반 파일이다.
- `.ai/rules/rules.md`에 멀티 AI CLI SSoT 정책이 명시되어 있다.
- 서브 rules는 생성하지 않고, 향후 필요 시 확장한다는 원칙만 남긴다.
