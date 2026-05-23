# AI Tool Template Project

이 저장소는 여러 AI CLI 도구가 같은 `.ai` 런타임 자산을 읽고 작업하도록 구성한 템플릿 프로젝트입니다.

## 현재 구조

| 경로 | 역할 |
|---|---|
| `.ai/` | 공유 AI 런타임 자산: rules, agents, skills, workflows, validators, templates, commands |
| `.claude/` | Claude Code 전용 설정과 호환 자산 |
| `.gemini/` | Gemini CLI 전용 설정 |
| `aios/` | `python -m aios` 실행을 위한 compatibility shim |
| `src/aios/` | AIOS CLI 런타임 구현 |
| `docs/` | 계획, 감사, 구현 보고서, ADR, 로드맵 문서 |
| `ops/` | 운영 보조 자산 |
| `scripts/` | 프로젝트 보조 스크립트 |

## 진입점

- 공통 규칙의 단일 진입점은 `.ai/rules/rules.md`입니다.
- Codex 및 범용 AI CLI는 `AGENTS.md`를 루트 어댑터로 사용합니다.
- Claude Code는 `CLAUDE.md`를 루트 어댑터로 사용합니다.
- Gemini CLI는 `GEMINI.md`를 루트 어댑터로 사용합니다.

루트 어댑터는 discovery 파일입니다. 공유 규칙 본문은 `.ai/rules/`에 유지합니다.

## AIOS CLI

주요 런타임 명령은 다음과 같습니다.

```powershell
python -m aios inspect
python -m aios inventory
python -m aios validate
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios load-context .ai/rules/rules.md
```

JSON 출력은 각 명령의 기존 스키마를 기본으로 유지합니다. 통합 결과 형식은 `--json --envelope-v2`로 opt-in 합니다.

## 문서 언어

- `.ai/` 아래 런타임 규칙과 정의 파일은 영어로 작성합니다.
- `docs/` 아래 계획 및 보고 문서는 한국어로 작성합니다.
- 모든 텍스트 파일은 UTF-8 without BOM으로 저장합니다.
