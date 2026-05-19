# AIOS Inspect v0 구현 보고서

## 1. 개요

`aios inspect` v0를 읽기 전용 검증 명령으로 구현했다.

이번 구현은 `.ai OS`의 첫 실행형 validation layer이며, sync, adapter generation, manifest, auto-fix 기능은 포함하지 않는다. 기존 `.ai` 콘텐츠 파일은 수정하지 않았다.

## 2. 구현 파일

| 파일 | 역할 |
|---|---|
| `src/aios/__init__.py` | package version 및 package marker |
| `src/aios/__main__.py` | `src` package 기준 module entrypoint |
| `src/aios/cli.py` | argparse 기반 CLI, human/json 출력, exit code 처리 |
| `src/aios/inspect.py` | inspect orchestration 및 개별 check 구현 |
| `src/aios/filesystem.py` | repo root 탐지, 파일 inventory, symlink, BOM 검사 |
| `src/aios/markdown_refs.py` | Markdown skill/workflow/path reference 추출 |
| `src/aios/result.py` | 검사 결과 dataclass와 JSON 변환 |
| `aios/__init__.py` | 설치 없이 `python -m aios` 실행을 위한 얇은 shim |
| `aios/__main__.py` | root shim entrypoint |
| `scripts/aios_inspect_smoke.ps1` | 수동 smoke test script |

루트 `aios/` shim은 실제 구현을 담지 않고 `src/aios`를 module path에 연결한다. 현재 저장소에 `pyproject.toml`이나 editable install 구성이 없기 때문에, 요구된 `python -m aios inspect` 실행을 만족시키기 위한 최소 호환 계층이다.

## 3. 구현된 검사

| 검사 | 상태 | 설명 |
|---|---|---|
| required repository structure | 구현 | `.ai` 주요 디렉터리와 `.ai/rules/rules.md` 확인 |
| root adapter existence | 구현 | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 확인 |
| skill inventory | 구현 | `.ai/skills/**/*.skill.md` 목록 생성 |
| skill references | 구현 | `skill_index.md`, `developer.agent.md`, `pm.agent.md`의 `.skill.md` 참조 대조 |
| workflow references | 구현 | `.ai/workflows/README.md`의 workflow 참조 대조 |
| stale `.ai/.cursorrules` references | 구현 | 지정 파일 범위에서 stale rule entrypoint 탐지 |
| symlink detection | 구현 | `.ai/rules`, `.ai/agents`, `.ai/commands` 아래 symlink 탐지 |
| UTF-8 BOM detection | 구현 | markdown/json/yaml/toml 파일 BOM 탐지 |
| agent-routing anchors | 구현 | `agent-routing` start/end anchor 확인 |
| agent-routing fenced yaml | 구현 | block 내부 fenced yaml 존재 확인 |
| agent-routing raw path references | 구현 | block 내부 `.ai/...` 경로 존재 확인 |

## 4. 출력 형식

기본 명령:

```bash
python -m aios inspect
```

JSON 명령:

```bash
python -m aios inspect --json
```

Exit code 정책:

| 조건 | exit code |
|---|---|
| pass 또는 warning만 있음 | 0 |
| fail 있음 | 1 |
| inspect crash 또는 root 탐지 실패 | 2 |

## 5. Sample Output Summary

현재 저장소 기준 human 출력 요약은 다음과 같다.

```text
AIOS Inspect v0
Root: D:\development\_templates\ai_tool
Status: fail
Summary: 13 fail, 1 warning, 2 info, 171 pass
Inventory: 307 files scanned, 101 skills, 13 workflow files
```

현재 fail은 구현 오류가 아니라 기존 감사에서 확인된 stale reference 때문이다.

대표 fail:

- `dev_frontend.skill.md` 누락
- `pm_planning.skill.md` 누락
- `product_analytics.skill.md` 누락
- `market_research.skill.md` 누락
- `pm_roadmap_management.skill.md` 누락
- `product_growth.skill.md` 누락
- `product_launch.skill.md` 누락
- `global_product_strategy.skill.md` 누락
- `data_driven_decision_making.skill.md` 누락
- `user_research.skill.md` 누락
- `l2_review_workflow.md` 누락
- `software_development.workflow.md.backup_20260120` 누락

대표 warning:

- `.ai/workflows/README.md:131`의 `[[../.cursorrules]]` stale reference

## 6. Validation Results

실행한 검증:

| 명령 | 결과 |
|---|---|
| `python -m aios inspect` | 실행 성공, 현재 stale reference 때문에 exit code 1 |
| `python -m aios inspect --json` | 실행 성공, 현재 stale reference 때문에 exit code 1 |
| `python -m compileall src/aios aios` | 통과 |
| `powershell -ExecutionPolicy Bypass -File scripts/aios_inspect_smoke.ps1` | 통과. inspect exit code 1을 현재 expected fail로 허용 |
| `git diff --name-only -- .ai` | 출력 없음. 기존 `.ai` 콘텐츠 파일 수정 없음 |
| `git diff --check` | 통과 |

검증 중 생성된 Python `__pycache__` 디렉터리는 제거했다.

## 7. Known Limitations

v0 제한:

- 외부 dependency를 사용하지 않는다.
- YAML full parsing을 수행하지 않는다.
- `agent-routing`은 anchor, fenced yaml, raw `.ai/...` path existence만 검사한다.
- agent frontmatter field validation은 아직 없다.
- Obsidian link 전체 검사는 아직 없다.
- concept-only skill 이름은 `.skill.md` suffix가 없으면 검사하지 않는다.
- stale `.ai/.cursorrules` 탐지는 지정 파일 중심이다. 전체 `.ai/**/*.md` 스캔은 v1 후보이다.
- JSON 출력은 상세 pass 항목까지 포함하므로 현재 다소 길다.
- 현재 저장소 상태에서는 stale reference가 남아 있어 inspect status가 `fail`이다.

## 8. Recommended v1 Tasks

권장 v1 작업:

1. agent frontmatter path validation 추가
2. embedded `agent-routing` light parser 개선
3. `validator_index.md` 참조 무결성 검사 추가
4. Obsidian link existence checker 추가
5. 전체 `.ai/**/*.md` stale `.ai/.cursorrules` 스캔 추가
6. concept-only skill alias 검사 추가
7. JSON 출력에 `--summary-only` 또는 pass 항목 생략 옵션 추가
8. `--scope skills`, `--scope workflows`, `--scope agents` 옵션 추가
9. `--strict` 옵션 추가
10. 현재 stale reference를 정리한 뒤 CI용 baseline 확정

## 9. 다음 작업 제안

다음 단계는 기존 `.ai` 콘텐츠를 수정하는 별도 작업으로 분리하는 것이 좋다.

권장 순서:

1. `skill_index.md`의 stale skill 참조를 unified skill 기준으로 수정
2. `.ai/workflows/README.md`의 `l2_review_workflow.md`를 `l2_review.workflow.md`로 수정
3. `.ai/workflows/README.md`의 `[[../.cursorrules]]`를 `[[../rules/rules.md]]`로 수정
4. inspect 결과가 warning 이하로 내려가는지 재검증

