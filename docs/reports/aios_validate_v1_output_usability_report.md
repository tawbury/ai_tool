# aios validate v1 출력 사용성 개선 보고서

## 1. 작업 요약

`aios validate`의 검증 정책은 변경하지 않고 JSON 출력 사용성만 개선했다.

추가한 옵션:

- `python -m aios validate --json --summary-only`
- `python -m aios validate --json --include-pass`

범위 밖으로 유지한 항목:

- sync
- manifest
- adapter generation
- orchestration
- worker execution
- auto-fix
- public schema migration
- validation rule 변경

## 2. 구현 변경

### `src/aios/cli.py`

`validate` subcommand에 JSON 보조 옵션을 추가했다.

- `--summary-only`
- `--include-pass`

기본 `--json` 동작은 기존과 동일하게 `results` 배열을 포함한다.

### `src/aios/validate/result.py`

`ValidationRun.to_dict()`에 다음 인자를 추가했다.

- `summary_only: bool = False`
- `include_pass: bool = False`

`summary_only=True`일 때 출력 형태:

- `schema_version`
- `status`
- `target`
- `summary`
- `errors` 배열: error가 있을 때만 포함
- `warnings` 배열: warning이 있을 때만 포함
- `info` 배열: info가 있을 때만 포함

`results` 배열은 summary-only 출력에서 생략한다.

## 3. 호환성

기본 JSON 출력은 기존 shape를 유지한다.

유지된 항목:

- `schema_version: aios.validate.result.v0`
- `status`
- `target`
- `summary`
- `results`

변경하지 않은 항목:

- validate status 이름
- validate severity 이름
- exit code 정책
- human output
- 검증 대상 resolve 정책
- agent/skill/workflow/reference 검증 정책

## 4. `--include-pass` 처리

현재 `validate` 내부 result model은 명시적인 pass result를 기록하지 않는다.

현재 기록하는 항목:

- `error`
- `warning`
- `info`

따라서 `--include-pass`는 CLI/API 호환용 옵션으로 추가했지만, 현재는 새 pass 항목을 생성하지 않는다. pass 결과를 가짜로 만들지 않기 위해 기본 `--json`과 동일한 `results` 배열을 출력한다.

향후 pass item이 내부 모델에 추가되면 같은 옵션에서 자연스럽게 노출할 수 있다.

## 5. 검증 결과

### `python -m aios validate --json`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 기존 `results` 배열 포함
- 요약: `0 errors, 0 warnings, 3 info`

### `python -m aios validate --json --summary-only`

결과:

- 종료 코드: `0`
- 상태: `pass`
- `results` 배열 생략
- `info` 배열만 포함
- 요약: `0 errors, 0 warnings, 3 info`

### `python -m aios validate --json --include-pass`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 현재 내부 모델에 explicit pass result가 없어 기본 `--json`과 동일한 결과

### `python -m aios validate --agent developer --json --summary-only`

결과:

- 종료 코드: `0`
- 상태: `pass`
- `results` 배열 생략
- `info` 배열만 포함
- 요약: `0 errors, 0 warnings, 1 info`

### `python -m aios validate --workflow l2_review --json --summary-only`

결과:

- 종료 코드: `0`
- 상태: `pass`
- `results` 배열 생략
- `info` 배열만 포함
- 요약: `0 errors, 0 warnings, 2 info`

### `python -m aios inspect`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 fail, 0 warning, 2 info, 308 pass`

### `python -m compileall -q src/aios aios`

결과:

- 종료 코드: `0`
- 컴파일 성공
- 생성된 `__pycache__` 디렉터리는 제거했다.

### `git diff --check`

결과:

- 종료 코드: `0`
- 공백 오류 없음
- 변경 파일의 LF/CRLF 경고는 출력되었으나 diff check 실패는 아님

## 6. 알려진 제한

- `--include-pass`는 현재 explicit pass result가 없으므로 출력을 늘리지 않는다.
- `summary_only` 출력은 v0 schema_version을 유지하되, `results` 대신 severity group 배열을 사용한다.
- public schema migration은 하지 않았다.

## 7. 권장 다음 작업

- validate result model에 explicit pass item이 필요한지 별도 설계
- `--summary-only`와 `--include-pass` 동작을 향후 schema 문서에 반영
- validate command contract를 `.ai` runtime-facing rule 또는 spec으로 승격 검토
