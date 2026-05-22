# aios validate v0 구현 보고서

## 1. 구현 요약

`aios validate` v0를 읽기 전용 실행 검증 계층으로 추가했다.

- 동기화, 매니페스트, 어댑터 생성, 자동 수정은 구현하지 않았다.
- 외부 의존성 없이 표준 라이브러리만 사용했다.
- YAML 전체 파싱은 하지 않고, 에이전트 frontmatter는 단순 구조 파서로만 확인한다.
- 의미 품질 평가, L2/시니어/멘토링/비즈니스 임팩트 점수화는 제외했다.

## 2. 구현 파일

새로 추가한 파일:

- `src/aios/validate/__init__.py`
- `src/aios/validate/result.py`
- `src/aios/validate/targets.py`
- `src/aios/validate/registry.py`
- `src/aios/validate/engine.py`
- `src/aios/validate/validators/__init__.py`
- `src/aios/validate/validators/agent.py`
- `src/aios/validate/validators/skill.py`
- `src/aios/validate/validators/workflow.py`
- `src/aios/validate/validators/references.py`

수정한 파일:

- `src/aios/cli.py`

## 3. 지원 명령

구현된 명령:

```bash
python -m aios validate
python -m aios validate --json
python -m aios validate <path>
python -m aios validate --agent developer
python -m aios validate --workflow l2_review
```

## 4. 구현된 검증

### Agent 검증

- `.ai/agents/*.agent.md` frontmatter 존재 여부
- 필수 frontmatter 필드 확인
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
- `domain_rules`, `operation_rules`, `validators`의 `.ai/...md` 참조 파일 존재 여부

### Skill 검증

- `.skill.md` 파일명 규칙
- frontmatter 존재 여부
- `name` 필드 존재 여부
- 최상위 제목 존재 여부
- v0에서 인식 가능한 목적/사용/실행 섹션 존재 여부

### Workflow 검증

- `.workflow.md` 파일명 규칙
- 최상위 제목 존재 여부
- 목적 계열 섹션 존재 여부
  - `Purpose`
  - `Workflow Overview`
  - `Overview`
  - `Objective`
- 실행 단계 계열 섹션 존재 여부
  - `Workflow Stages`
  - `Process Stages`
  - `Workflow`
  - `Process`
  - `Execution Flow`
- `Review Criteria`, `Quality Gates`, `Performance Metrics`는 human-review-only 영역으로 보고 점수화하지 않음

### Validator Index 검증

- `.ai/validators/validator_index.md`의 Markdown/Obsidian 파일 링크 존재 여부
- 링크 대상 파일 존재 여부

## 5. 결과 스키마

JSON 출력은 다음 스키마 버전을 사용한다.

```json
{
  "schema_version": "aios.validate.result.v0",
  "status": "pass|warn|fail",
  "target": {},
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 0,
    "results": 0
  },
  "results": []
}
```

## 6. 종료 코드

- `0`: pass 또는 warn
- `1`: fail
- `2`: CLI 오류, 루트 탐지 실패, crash

## 7. 검증 결과

### `python -m aios validate`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 error, 0 warning, 3 info`

주요 출력:

```text
AIOS Validate v0
Status: pass
Summary: 0 error, 0 warning, 3 info, 3 results
```

### `python -m aios validate --json`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 스키마: `aios.validate.result.v0`
- 저장소 대상 수: `117`

### `python -m aios validate --agent developer`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 error, 0 warning, 1 info`

### `python -m aios validate --workflow l2_review`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 error, 0 warning, 2 info`

### `python -m aios validate .ai/skills/_shared/context_engineering.skill.md`

결과:

- 종료 코드: `1`
- 상태: `fail`
- 사유: 대상 파일이 존재하지 않음

이 동작은 v0 정책의 `missing target = error`와 일치한다.

### `python -m aios inspect`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 fail, 0 warning, 2 info, 308 pass`

### `python -m compileall -q src/aios aios`

결과:

- 종료 코드: `0`
- 컴파일 성공
- 생성된 `__pycache__` 디렉터리는 검증 후 제거했다.

### `git diff --check`

결과:

- 종료 코드: `0`
- 공백 오류 없음
- 기존 작업 트리의 LF/CRLF 경고는 출력되었으나 diff check 실패는 아님

## 8. 알려진 제한

- YAML 전체 파싱은 아직 하지 않는다.
- Markdown 링크 검증은 validator index에 한정한다.
- Skill 구조 검증은 보수적인 기본 구조 확인만 수행한다.
- Human-review-only 품질 기준은 info로만 표시하고 점수화하지 않는다.
- `--summary-only` 또는 validate 전용 JSON 축약 옵션은 v0 범위에 포함하지 않았다.

## 9. 권장 v1 작업

- validator registry를 실제 설정 파일 또는 명시적 Python registry로 확장
- validate 결과에 pass 항목 포함 여부를 제어하는 옵션 추가
- agent frontmatter 날짜/버전 형식 검증 추가
- validator markdown 파일 자체의 계약/가이드 계층 분리 검증 추가
- workflow별 필수 섹션을 전역 규칙이 아니라 workflow type별 contract로 분리
- `aios validate --validator-index` 같은 명시적 대상 단축 옵션 검토
