# 멀티 AI CLI 공통 Rules 리팩토링 계획

**작성일**: 2026-05-17  
**문서 상태**: 계획  
**대상 경로**: `D:\development\_templates\ai_tool`

---

## 1. 배경

현재 프로젝트는 Codex, Claude Code, Gemini CLI를 함께 사용하는 방향으로 확장되고 있다. 향후 다른 AI CLI 도구가 추가될 가능성도 있으므로, 특정 도구 중심의 규칙 파일을 각각 독립적으로 관리하면 규칙 불일치와 유지보수 비용이 커질 수 있다.

따라서 `.ai/rules/rules.md`를 공통 메인 글로벌 rules의 단일 원천(SSoT, Single Source of Truth)으로 지정하고, 루트의 각 AI CLI 엔트리 파일은 이 공통 rules를 참조하는 얇은 어댑터 역할로 정리하는 것이 적절하다.

현재 사용 또는 예정인 루트 엔트리 파일은 다음과 같다.

- `CLAUDE.md`: Claude Code용 프로젝트 지침
- `AGENTS.md`: Codex 및 범용 에이전트 지침
- `GEMINI.md`: Gemini CLI용 프로젝트 지침

사용자가 언급한 `root/claude.md`, `agent.md`, `gemini.md`는 실제 파일명 기준으로 각각 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`에 매핑하는 것을 기본안으로 한다.

---

## 2. 목표

1. `.ai/rules/rules.md`를 모든 AI CLI가 공유하는 메인 글로벌 rules로 확정한다.
2. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`는 공통 rules 파일을 참조하도록 단순화한다.
3. AI CLI별 특수 지침은 루트 엔트리 파일에 최소한만 둔다.
4. 향후 `validator.rules.md`, `workflow.rules.md` 같은 서브 rules 파일을 추가할 수 있는 확장 구조를 마련한다.
5. 새로운 AI CLI 도구가 추가되어도 공통 rules와 도구별 어댑터 파일만 연결하면 되도록 구조를 표준화한다.

---

## 3. 제안 구조

권장 디렉터리 구조는 다음과 같다.

```text
.ai/
  rules/
    rules.md                    # 공통 메인 글로벌 rules, SSoT
    validator.rules.md           # 선택: 검증 규칙 확장
    workflow.rules.md            # 선택: 워크플로우 규칙 확장
    document.rules.md            # 선택: 문서 작성 규칙 확장
    agent.rules.md               # 선택: 에이전트 공통 동작 규칙 확장

CLAUDE.md                        # Claude Code용 얇은 참조 파일
AGENTS.md                        # Codex 및 범용 에이전트용 얇은 참조 파일
GEMINI.md                        # Gemini CLI용 얇은 참조 파일
```

### 역할 분리

- `.ai/rules/rules.md`: 모든 AI CLI가 반드시 따라야 하는 최상위 공통 규칙
- `.ai/rules/*.rules.md`: 특정 영역별 확장 규칙
- 루트 엔트리 파일: 각 AI CLI가 읽기 쉬운 형식으로 공통 rules 위치와 우선순위를 안내

---

## 4. 루트 엔트리 파일 표준안

각 루트 엔트리 파일은 자체적으로 긴 규칙을 중복 보관하지 않고, 아래 내용을 공통 패턴으로 가진다.

```markdown
# Project Instructions

This project uses `.ai/rules/rules.md` as the single source of truth for global AI agent rules.

Before making changes, read and follow:

1. `.ai/rules/rules.md`
2. Any relevant `.ai/rules/*.rules.md` extension files
3. Tool-specific notes in this file

If instructions conflict, follow this priority:

1. User's latest explicit request
2. Tool-specific system/developer instructions
3. `.ai/rules/rules.md`
4. Relevant `.ai/rules/*.rules.md`
5. This adapter file
```

CLI별 파일에는 다음 정도의 차이만 허용한다.

- `CLAUDE.md`: Claude Code가 프로젝트 컨텍스트로 읽는 형식에 맞춘 짧은 안내
- `AGENTS.md`: Codex와 범용 CLI 에이전트가 인식하기 쉬운 표준 안내
- `GEMINI.md`: Gemini CLI의 프로젝트 지침 관례에 맞춘 짧은 안내

---

## 5. 서브 Rules 확장 방식

초기에는 `.ai/rules/rules.md` 하나만 유지한다. 규칙이 커져서 탐색성과 유지보수성이 떨어지는 시점에만 서브 rules 파일을 분리한다.

분리 후보는 다음과 같다.

- `.ai/rules/validator.rules.md`: 문서, 템플릿, 실행 결과 검증 규칙
- `.ai/rules/workflow.rules.md`: 로드맵, 태스크, 실행 기록, 보고 흐름 규칙
- `.ai/rules/document.rules.md`: `docs/`와 `.ai/`의 언어, 템플릿, 메타데이터 규칙
- `.ai/rules/agent.rules.md`: L1/L2 에이전트 역할, 권한, 협업 규칙

서브 rules 파일을 만들 경우, `.ai/rules/rules.md`에는 다음과 같은 인덱스 섹션을 둔다.

```markdown
## Rule Extensions

Additional rule files:

- `.ai/rules/validator.rules.md`
- `.ai/rules/workflow.rules.md`
- `.ai/rules/document.rules.md`
- `.ai/rules/agent.rules.md`

Agents must load relevant extension files when the task touches that domain.
```

---

## 6. 리팩토링 단계

### Phase 1. 현재 상태 정리

- 루트의 `CLAUDE.md`, `GEMINI.md` 상태를 확인한다.
- `AGENTS.md`가 없으면 신규 생성 여부를 결정한다.
- `.ai/rules/rules.md`의 현재 내용을 유지하되, 오탈자와 깨진 문자 여부를 점검한다.
- 기존 문서에 남아 있는 symlink 기반 설명이나 구형 CLI 목록을 최신 구조에 맞게 갱신한다.

### Phase 2. 공통 rules 선언 강화

- `.ai/rules/rules.md` 상단에 이 파일이 모든 AI CLI의 SSoT라는 내용을 명시한다.
- 지원 대상 CLI 목록을 특정 도구에 고정하지 않고 “Codex, Claude Code, Gemini CLI, and future AI CLI tools”처럼 확장 가능한 표현으로 변경한다.
- 루트 엔트리 파일은 규칙 원본이 아니며, 공통 rules를 참조하는 어댑터라고 명시한다.

### Phase 3. 루트 엔트리 파일 정비

- `CLAUDE.md`를 Claude Code용 참조 파일로 작성한다.
- `AGENTS.md`를 Codex 및 범용 AI CLI용 참조 파일로 생성한다.
- `GEMINI.md`를 Gemini CLI용 참조 파일로 단순화하거나, 기존 내용 중 필요한 도구별 설명만 남긴다.
- 세 파일 모두 `.ai/rules/rules.md`를 먼저 읽도록 안내한다.

### Phase 4. 서브 rules 확장 준비

- 당장 필요한 서브 rules가 있으면 `.ai/rules/validator.rules.md`, `.ai/rules/workflow.rules.md`부터 분리한다.
- 아직 분리 필요성이 낮으면 파일은 만들지 않고, `.ai/rules/rules.md`에 확장 규칙 파일 네이밍만 예약한다.
- 서브 rules는 공통 rules를 대체하지 않고, 특정 도메인의 세부 규칙만 보강한다.

### Phase 5. 검증 및 운영 규칙

- 각 AI CLI가 루트 엔트리 파일을 읽었을 때 `.ai/rules/rules.md` 위치를 명확히 알 수 있는지 확인한다.
- Git에서 symlink가 아닌 일반 파일로 관리되는지 확인한다.
- 새 AI CLI를 추가할 때는 루트 또는 도구별 설정 파일에 동일한 참조 패턴을 적용한다.
- 변경 후 `git status`로 추적 대상과 무시 대상이 의도대로 정리되었는지 확인한다.

---

## 7. 우선순위 규칙

여러 규칙이 충돌할 경우 다음 우선순위를 적용한다.

1. 사용자의 최신 명시 요청
2. 각 AI CLI 런타임의 시스템 또는 개발자 지침
3. `.ai/rules/rules.md`
4. 관련 `.ai/rules/*.rules.md`
5. 루트 엔트리 파일의 도구별 보조 지침

이 우선순위는 모든 루트 엔트리 파일에 동일하게 반영한다.

---

## 8. 기대 효과

- 공통 규칙 중복을 줄이고 변경 지점을 `.ai/rules/rules.md`로 집중할 수 있다.
- Codex, Claude Code, Gemini CLI가 동일한 프로젝트 운영 규칙을 공유한다.
- AI CLI가 추가되어도 새 어댑터 파일만 작성하면 기존 rules 체계를 재사용할 수 있다.
- rules 파일이 커질 경우 도메인별 서브 rules로 자연스럽게 확장할 수 있다.
- symlink 의존 없이 일반 Markdown 파일 참조 방식으로 운영할 수 있어 Windows 환경과 Git 관리가 안정적이다.

---

## 9. 추천 실행 순서

1. `AGENTS.md`를 신규 생성한다.
2. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`를 공통 rules 참조용 얇은 어댑터로 정리한다.
3. `.ai/rules/rules.md` 상단에 멀티 AI CLI SSoT 선언과 확장 rules 인덱스 정책을 추가한다.
4. 현재 rules 내용 중 도구별로 오래된 항목을 “현재 지원 CLI”와 “향후 추가 CLI” 구조로 갱신한다.
5. 서브 rules 분리는 즉시 진행하지 않고, 첫 후보로 `validator.rules.md`와 `workflow.rules.md`를 예약한다.
6. 변경 후 각 CLI에서 루트 엔트리 파일을 정상 인식하는지 확인한다.

---

## 10. 산출물 체크리스트

- [ ] `.ai/rules/rules.md` SSoT 선언 갱신
- [ ] `CLAUDE.md` 참조 파일 정비
- [ ] `AGENTS.md` 참조 파일 생성
- [ ] `GEMINI.md` 참조 파일 정비
- [ ] 서브 rules 네이밍 정책 추가
- [ ] 구형 symlink 또는 특정 CLI 전용 설명 제거
- [ ] Git 상태 확인
- [ ] 필요 시 커밋 및 원격 푸시
