# AI Tool Template Project

이 저장소는 Codex, Claude Code, Gemini CLI를 공통 규칙 체계로 운영하기 위한 AI 도구 템플릿입니다.

## 핵심 원칙

- 공통 rules 원본은 `.ai/rules/rules.md`입니다.
- Codex는 `AGENTS.md`를 루트 어댑터로 사용합니다.
- Claude Code는 `CLAUDE.md`를 루트 어댑터로 사용합니다.
- Gemini CLI는 `GEMINI.md`를 루트 어댑터로 사용합니다.
- rules 파일과 rules 디렉터리는 심볼릭 링크로 연결하지 않습니다.

## 주요 구조

| 경로 | 역할 |
|---|---|
| `.ai/` | 공통 rules, agents, skills, workflows, validators 원본 |
| `.claude/` | Claude Code 관련 로컬 설정과 Claude 전용 자산 |
| `.gemini/` | Gemini CLI 관련 로컬 설정 |
| `AGENTS.md` | Codex 및 범용 AI CLI용 루트 어댑터 |
| `CLAUDE.md` | Claude Code용 루트 어댑터 |
| `GEMINI.md` | Gemini CLI용 루트 어댑터 |
| `docs/` | 계획, 보고서, 로드맵 문서 |
| `prompt/` | 프롬프트 관련 자료 |

## 현재 지원 대상

- Codex
- Claude Code
- Gemini CLI
