# AI Tool Template Project

이 저장소는 Codex CLI, Claude Code, Gemini CLI를 공통 룰 체계로 운영하기 위한 AI 도구 템플릿입니다.

## 핵심 구조

- 글로벌 룰 진입점은 `.ai/rules/rules.md`입니다.
- Codex 및 범용 AI CLI는 `AGENTS.md`를 루트 어댑터로 사용합니다.
- Claude Code는 `CLAUDE.md`를 루트 어댑터로 사용합니다.
- Gemini CLI는 `GEMINI.md`를 루트 어댑터로 사용합니다.
- 룰 파일과 룰 디렉터리는 심볼릭 링크로 연결하지 않습니다.

## 룰 레이어

| 경로 | 역할 |
|---|---|
| `.ai/rules/rules.md` | 모든 AI CLI가 먼저 읽는 글로벌 룰 계약 |
| `.ai/rules/domains/` | 문서화, 개발, HR 등 업무 도메인별 룰 |
| `.ai/rules/operations/` | 워크플로우, 검증, 에이전트 운영 룰 |

## 주요 경로

| 경로 | 역할 |
|---|---|
| `.ai/` | 공통 rules, agents, skills, workflows, validators, templates |
| `.claude/` | Claude Code 관련 로컬 설정과 Claude 전용 자산 |
| `.gemini/` | Gemini CLI 관련 로컬 설정 |
| `AGENTS.md` | Codex 및 범용 AI CLI 루트 어댑터 |
| `CLAUDE.md` | Claude Code 루트 어댑터 |
| `GEMINI.md` | Gemini CLI 루트 어댑터 |
| `docs/` | 계획, 설계, 보고서, 로드맵 문서 |
| `prompt/` | 프롬프트 관련 자료 |

## 현재 지원 도구

- Codex CLI
- Claude Code
- Gemini CLI
