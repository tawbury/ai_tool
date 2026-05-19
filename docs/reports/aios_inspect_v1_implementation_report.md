# AIOS Inspect v1 구현 보고서

## 1. 개요

`aios inspect` v1을 구현했다.

이번 버전은 v0의 read-only 검사를 유지하면서 agent frontmatter, validator index, 전체 `.ai/**/*.md` stale rule entrypoint, 명확한 상대 파일 링크 검사를 추가했다. sync, manifest, adapter generation, auto-fix 기능은 구현하지 않았다.

## 2. 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `src/aios/cli.py` | `--json --summary-only` 옵션 추가, human 출력 버전 v1로 갱신 |
| `src/aios/inspect.py` | v1 검사 추가: agent frontmatter, full stale scan, validator index, obvious relative links |
| `src/aios/markdown_refs.py` | Markdown inline link와 Obsidian file link 추출기 추가 |
| `src/aios/result.py` | summary-only JSON 출력을 위한 pass check 생략 옵션 추가 |
| `docs/reports/aios_inspect_v1_implementation_report.md` | 구현 보고서 추가 |

## 3. 구현된 v1 검사

### Agent Frontmatter Validation

대상:

- `.ai/agents/*.agent.md`

검사 항목:

- frontmatter 존재 여부
- 필수 field 존재 여부
  - `name`
  - `type`
  - `version`
  - `updated`
  - `role`
  - `level`
  - `tools`
  - `domain_rules`
  - `operation_rules`
  - `validators`
- `domain_rules`, `operation_rules`, `validators`에 있는 파일 경로 존재 여부

외부 YAML dependency는 추가하지 않았다. v1에서는 현재 agent frontmatter 형식에 맞춘 보수적인 light parser만 사용한다.

### Full `.ai/**/*.md` Stale `.cursorrules` Scan

v0에서는 지정 파일만 검사했다. v1에서는 `.ai` 아래 모든 Markdown 파일에서 다음 stale 참조를 찾는다.

- `.ai/.cursorrules`
- `../.cursorrules`

이 검사는 warning으로 보고한다. 자동 수정은 하지 않는다.

### `validator_index.md` Reference Integrity

대상:

- `.ai/validators/validator_index.md`

검사 항목:

- Markdown inline link 중 `.md` 파일 링크 추출
- 링크 대상 파일 존재 여부 확인

현재 validator index의 명시적 Markdown 링크는 모두 존재한다.

### Obsidian-style Link Existence Check

전체 `.ai/**/*.md`에서 명확한 상대 파일 링크만 검사한다.

검사 대상 예:

- `[[../rules/rules.md]]`
- `[[../templates/README.md]]`
- `[name](_base/document_base_validator.md)`

오탐을 줄이기 위해 다음 링크는 v1에서 제외한다.

- `[[filename.md]]`처럼 디렉터리 정보가 없는 Obsidian 링크
- placeholder가 포함된 링크
- wildcard 링크
- URL
- anchor-only 링크

## 4. Summary-only JSON

추가 명령:

```bash
python -m aios inspect --json --summary-only
```

동작:

- summary는 그대로 출력한다.
- `pass` check는 생략한다.
- `info`, `warning`, `fail` check만 출력한다.

목적:

- 기본 `--json` 출력이 너무 커지는 문제 완화
- CI 또는 수동 점검에서 조치가 필요한 항목만 빠르게 확인

## 5. Validation Results

| 명령 | 결과 |
|---|---|
| `python -m aios inspect` | 실행 성공, exit code 0 |
| `python -m aios inspect --json` | 실행 성공, exit code 0 |
| `python -m aios inspect --json --summary-only` | 실행 성공, exit code 0 |
| `python -m compileall src/aios aios` | 통과 |
| `git diff --check` | 통과 |

`git diff --check`는 기존 `.ai/skills/_shared/skill_index.md`, `.ai/workflows/README.md`에 대해 LF/CRLF 변환 경고를 출력했지만 whitespace error는 없었다.

## 6. 현재 Inspect 결과

현재 `python -m aios inspect` 요약:

```text
AIOS Inspect v1
Status: warning
Summary: 0 fail, 2 warning, 2 info, 306 pass
Inventory: 309 files scanned, 101 skills, 13 workflow files
```

failure는 없다.

남은 warning:

| warning | 내용 |
|---|---|
| `stale-cursorrules-reference` | v1 full scan에서 `.ai/templates`, `.ai/validators`, `.ai/workflows/hr_evaluation.workflow.md`에 남아 있는 `.ai/.cursorrules` 참조 발견 |
| `obvious-relative-link` | 명확한 상대 링크 중 일부 대상 누락 발견 |

대표 relative link warning:

- `.ai/skills/_shared/README.md`의 `../templates/roadmap_template.md`
- `.ai/skills/_shared/README.md`의 `../templates/run_record_template.md`
- `.ai/workflows/deploy_automation.workflow.md`의 `../docs/reports/...` 링크들

## 7. Known Limitations

- full YAML parsing은 아직 하지 않는다.
- agent frontmatter parser는 현재 repo의 단순 YAML 구조만 지원한다.
- Obsidian link 검사는 명확한 상대 파일 링크만 다룬다.
- 디렉터리 없는 `[[filename.md]]` 링크는 아직 검사하지 않는다.
- template placeholder 링크는 검사하지 않는다.
- stale reference와 relative link 문제는 자동 수정하지 않는다.

## 8. Recommended Next Tasks

1. 남은 `.ai/.cursorrules` 참조를 `.ai/rules/rules.md` 또는 올바른 상대 Obsidian 링크로 정리한다.
2. `.ai/skills/_shared/README.md`의 template 상대 경로를 검토한다.
3. `.ai/workflows/deploy_automation.workflow.md`의 과거 E2E report 링크가 필요한지 결정한다.
4. agent frontmatter 검사에 `type: agent`, `level: L1|L2` 같은 값 검증을 추가한다.
5. Obsidian basename link resolver를 설계하되, placeholder 링크와 실제 링크를 구분하는 정책을 먼저 정한다.

