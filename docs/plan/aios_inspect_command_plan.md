# AIOS Inspect 명령 구현 계획

## 1. 목표

`aios inspect`는 `.ai OS`의 첫 실행형 검증 계층이다.

이 명령은 sync, adapter generation, manifest 구현 전에 저장소의 현재 참조 무결성을 읽기 전용으로 검사한다. 목적은 파일을 고치는 것이 아니라, 어떤 파일이 stale 상태인지, 어떤 참조가 실제 파일과 맞지 않는지, 어떤 검증 규칙이 아직 실행 불가능한지 명확히 보고하는 것이다.

## 2. 비목표

이번 단계에서 하지 않는다.

- sync 구현
- adapter 생성
- manifest 생성
- managed block 삽입
- 자동 수정
- 파일 rename
- stale reference 자동 교체
- project init
- activation 적용

## 3. 명령 형태

초기 명령은 다음 형태를 권장한다.

```bash
aios inspect
aios inspect --json
aios inspect --scope skills
aios inspect --scope workflows
aios inspect --strict
```

v0에서는 `--scope`와 `--strict`를 설계만 해도 된다. 실제 P0 구현은 기본 inspect와 `--json`에 집중한다.

## 4. 출력 모델

`aios inspect --json`은 다음 구조를 출력한다.

```json
{
  "status": "pass|warning|fail",
  "summary": {
    "files_scanned": 0,
    "errors": 0,
    "warnings": 0
  },
  "checks": [
    {
      "id": "skill-reference-exists",
      "status": "pass|warning|fail",
      "source": ".ai/skills/_shared/skill_index.md",
      "message": "reference target missing",
      "references": [
        {
          "raw": "dev_frontend.skill.md",
          "resolved": null,
          "recommendation": ".ai/skills/developer/dev_frontend_stack_unified.skill.md"
        }
      ]
    }
  ]
}
```

사람용 출력은 JSON과 같은 결과를 요약한다.

## 5. P0 검사 범위

### 5.1 Repository Structure

검사 항목:

- `.ai/` 존재
- `.ai/rules/rules.md` 존재
- `.ai/agents/`, `.ai/skills/`, `.ai/workflows/`, `.ai/validators/`, `.ai/commands/`, `.ai/templates/` 존재
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 존재
- `src/` 존재 여부와 비어 있음 여부는 info로 보고

판정:

| 조건 | 등급 |
|---|---|
| `.ai/rules/rules.md` 없음 | fail |
| 주요 디렉터리 없음 | fail |
| root adapter 없음 | warning |
| `src/` 비어 있음 | info |

### 5.2 Skill Reference Integrity

검사 대상:

- `.ai/skills/_shared/skill_index.md`
- `.ai/agents/developer.agent.md`
- `.ai/agents/pm.agent.md`

검사 방식:

1. `.ai/skills/**/*.skill.md` 실제 목록을 만든다.
2. Markdown에서 `.skill.md` 참조를 추출한다.
3. 명시 경로는 그대로 존재 여부를 검사한다.
4. basename만 있는 경우 현재 section의 location hint를 활용해 후보 경로를 찾는다.
5. 후보가 하나면 pass, 없으면 fail, 여러 개면 warning으로 처리한다.

초기 stale mapping:

| stale | 권장 canonical |
|---|---|
| `dev_frontend.skill.md` | `.ai/skills/developer/dev_frontend_stack_unified.skill.md` |
| `product_analytics.skill.md` | `.ai/skills/pm/pm_analytics_unified.skill.md` |
| `pm_planning.skill.md` | `.ai/skills/pm/pm_strategy_unified.skill.md` 또는 `.ai/skills/_shared/execution_planning.skill.md` |
| `market_research.skill.md` | `.ai/skills/_shared/research_framework.skill.md` |
| `pm_roadmap_management.skill.md` | `.ai/skills/_shared/operational_roadmap_management.skill.md` |
| `product_launch.skill.md` | `.ai/skills/pm/product_lifecycle_management.skill.md` |

### 5.3 Workflow Reference Integrity

검사 대상:

- `.ai/workflows/README.md`

검사 방식:

1. `.ai/workflows/*` 실제 파일 목록을 만든다.
2. README 안의 `*.workflow.md`, `workflow_index.md`, `*_workflow.md` 참조를 추출한다.
3. 같은 디렉터리 기준으로 존재 여부를 검사한다.
4. `l2_review_workflow.md`는 `l2_review.workflow.md`로 추천한다.

### 5.4 Stale Rule Entrypoint Detection

검사 대상:

- v0에서는 지정 파일 중심
- v1에서는 전체 `.ai/**/*.md`

검사 문자열:

- `.ai/.cursorrules`
- `[[../.cursorrules]]`

권장 교체:

- 일반 경로: `.ai/rules/rules.md`
- `.ai/workflows` 기준 Obsidian 링크: `[[../rules/rules.md]]`
- `.ai/templates` 또는 `.ai/validators` 기준 Obsidian 링크도 같은 상대 경로를 별도 계산해야 한다.

### 5.5 Agent Routing Block

검사 대상:

- `.ai/rules/operations/agent.rules.md`

검사 항목:

- `<!-- ai-config:start agent-routing v1 -->` 존재
- `<!-- ai-config:end -->` 존재
- fenced `yaml` block 존재
- 각 agent 항목이 다음 필드를 포함
  - `agent`
  - `file`
  - `default_domain_rules`
  - `default_operation_rules`
  - `validators`
  - `primary_use_cases`
- 각 파일 경로 존재

v0에서는 embedded 상태를 유지한다. 분리는 inspect가 안정화된 뒤 별도 작업으로 진행한다.

## 6. Validator Readiness 반영

`aios inspect` v0가 즉시 반영할 수 있는 validator 규칙은 다음이다.

| validator | v0 반영 여부 | 검사 |
|---|---|---|
| `validation.rules.md` | 반영 | validator 파일 존재, 참조 파일 존재 |
| `agent.rules.md` | 반영 | embedded config anchor, routing 참조 존재 |
| `skill_loading_validator.md` | 부분 반영 | skill file existence, missing skill detection |
| `structure_validator.md` | 부분 반영 | header 존재, 빈 header 탐지 |
| `implement-design.command.md` | 부분 반영 | required rules 존재, symlink, BOM |

v0에서 제외할 규칙:

- loading time measurement
- memory usage optimization
- caching validation
- concurrent loading validation
- success rate 99%+
- language detection strict enforcement
- template compliance strict enforcement
- all sections non-empty enforcement

## 7. 모듈 설계

초기 구현은 작은 모듈로 나눈다.

```text
src/aios/
  __init__.py
  cli.py
  inspect.py
  filesystem.py
  markdown_refs.py
  result.py
```

역할:

| 모듈 | 역할 |
|---|---|
| `cli.py` | argparse 기반 진입점 |
| `inspect.py` | 검사 orchestration |
| `filesystem.py` | 파일 목록, symlink, BOM 검사 |
| `markdown_refs.py` | Markdown 참조 추출 |
| `result.py` | pass/warning/fail 결과 모델 |

Python을 권장하는 이유:

- Windows 경로 처리와 텍스트 검사가 쉽다.
- 별도 package 설치 없이 시작할 수 있다.
- 이후 YAML 파서가 필요해질 때 표준 라이브러리 한계를 명확히 분리할 수 있다.

초기에는 외부 dependency 없이 구현한다. YAML full parser가 필요한 단계는 v1로 미룬다.

## 8. P0 구현 순서

1. `src/aios` skeleton과 `python -m aios inspect` 진입점을 만든다.
2. 결과 모델을 만든다.
3. repository root 탐지 로직을 만든다.
4. 필수 디렉터리와 파일 존재 검사를 구현한다.
5. `.ai/skills/**/*.skill.md` inventory를 구현한다.
6. Markdown `.skill.md` reference extractor를 구현한다.
7. `skill_index.md`, `developer.agent.md`, `pm.agent.md` 참조 검사를 구현한다.
8. workflow README 참조 검사를 구현한다.
9. `.ai/.cursorrules` stale detector를 구현한다.
10. symlink detector를 구현한다.
11. UTF-8 BOM detector를 구현한다.
12. JSON 출력과 human summary 출력을 연결한다.
13. 현재 감사 결과를 기준으로 fixture 테스트를 만든다.

## 9. P1 구현 순서

1. agent frontmatter 경로 검사
2. embedded `agent-routing` YAML light parser
3. validator index 참조 검사
4. Obsidian link existence checker
5. context budget 추정
6. `--scope` 옵션
7. `--strict` 옵션

## 10. P2 구현 순서

1. `activation.yaml` 검사
2. `agent-registry.yaml` 도입 여부 결정
3. template-to-validator mapping 검사
4. inspect 결과를 CI에서 사용할 exit code 정책으로 정리
5. sync dry-run 설계로 연결

## 11. Exit Code 정책

v0 권장:

| 상태 | exit code |
|---|---|
| pass | 0 |
| warning만 있음 | 0 |
| fail 있음 | 1 |
| inspect 자체 실행 오류 | 2 |

초기에는 warning을 실패로 취급하지 않는다. 기존 저장소에 stale 참조가 이미 있으므로, 모든 warning을 fail로 올리면 도입 비용이 커진다.

## 12. 이번 계획 이후의 첫 Codex 작업

다음 작업 프롬프트를 권장한다.

```text
Implement read-only `aios inspect` v0.

Scope:
- no sync
- no adapter generation
- no manifest
- no file modification except new CLI source and tests
- inspect `.ai/skills/_shared/skill_index.md`, `.ai/agents/developer.agent.md`, `.ai/agents/pm.agent.md`, `.ai/workflows/README.md`, and `.ai/rules/operations/agent.rules.md`
- report missing skill references, workflow references, stale `.ai/.cursorrules`, symlinks, and UTF-8 BOM
- support human output and `--json`
```

