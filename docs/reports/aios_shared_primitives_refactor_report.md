# AIOS 공유 Primitive P0 리팩터 보고서

## 1. 작업 요약

AIOS 런타임 명령의 public CLI 동작과 JSON shape를 유지하면서, 중복되던 내부 primitive를 공통 모듈로 분리했다.

대상 명령:

- `python -m aios inspect`
- `python -m aios load-context`
- `python -m aios validate`

범위 밖으로 유지한 항목:

- sync
- manifest
- adapter generation
- orchestration
- worker execution
- auto-fix
- public schema migration

## 2. 추가한 공유 모듈

### `src/aios/frontmatter.py`

가벼운 frontmatter 추출/파싱 모듈을 추가했다.

지원 범위:

- `---`로 시작하고 종료되는 단순 frontmatter
- 단순 scalar 필드
- 단순 list 필드
- inline list 필드
- raw body 보존
- start/end line 정보 제공

주요 API:

- `FrontmatterBlock`
- `extract_frontmatter`
- `parse_simple_frontmatter`
- `as_list`
- `is_empty`

### `src/aios/references.py`

참조 추출과 경로 resolve primitive를 추가했다.

지원 범위:

- Markdown inline file link 추출
- Obsidian file link 추출
- `.ai/...` 경로 resolve
- 상대 경로 resolve
- obvious relative Markdown link 판별
- external/anchor link 제외 판별
- canonical `.ai/...md` path 판별

주요 API:

- `extract_file_links`
- `is_external_or_anchor`
- `is_obvious_relative_file_link`
- `clean_file_reference`
- `resolve_reference`
- `resolve_ai_path`
- `is_canonical_ai_markdown_path`

### `src/aios/status.py`

상태, 심각도, exit code 상수를 추가했다.

주의:

- public schema migration은 하지 않았다.
- `inspect`의 public status `warning`은 유지했다.
- `validate`의 public status `warn`은 유지했다.

주요 상수:

- `STATUS_PASS`
- `STATUS_WARN`
- `STATUS_WARNING`
- `STATUS_FAIL`
- `SEVERITY_INFO`
- `SEVERITY_WARNING`
- `SEVERITY_ERROR`
- `EXIT_PASS`
- `EXIT_FAIL`
- `EXIT_CRASH`
- `VALIDATE_SEVERITY_STATUS`
- `INSPECT_STATUS_ORDER`

### `src/aios/contracts.py`

agent contract 관련 공통 상수를 추가했다.

주요 상수:

- `AGENT_REQUIRED_FIELDS`
- `AGENT_REFERENCE_FIELDS`

## 3. 수정한 기존 모듈

### `src/aios/inspect.py`

변경 사항:

- agent frontmatter 추출/파싱을 `frontmatter.py`로 대체
- agent required field 목록을 `contracts.py`로 대체
- agent reference field 목록을 `contracts.py`로 대체
- Markdown/Obsidian file link 추출을 `references.py`의 `extract_file_links`로 일부 대체
- obvious relative link 판별과 상대 경로 resolve를 `references.py`로 대체

유지한 사항:

- inspect JSON shape 유지
- inspect public status `pass|warning|fail` 유지
- inspect check id 유지
- inspect CLI 옵션 유지

### `src/aios/validate/validators/agent.py`

변경 사항:

- 자체 frontmatter parser 제거
- 자체 list/scalar helper 제거
- agent required/reference field 상수를 공유 모듈로 대체
- `.ai/...md` 참조 판별과 resolve를 `references.py`로 대체

유지한 사항:

- validate result schema 유지
- error/warning/info 정책 유지
- agent validator code/message 유지

### `src/aios/validate/validators/skill.py`

변경 사항:

- agent validator에서 parser를 import하던 구조 제거
- `frontmatter.py`의 `extract_frontmatter`를 직접 사용

유지한 사항:

- skill 구조 검증 정책 유지
- warning/error 기준 유지

### `src/aios/validate/validators/references.py`

변경 사항:

- Markdown/Obsidian file link 추출을 `references.py`로 대체
- external/anchor 판별을 `references.py`로 대체
- relative path resolve를 `references.py`로 대체

유지한 사항:

- validator index reference integrity 정책 유지
- result code/message 유지

### `src/aios/result.py`

변경 사항:

- inspect status order를 `status.py` 상수로 대체

유지한 사항:

- inspect public JSON shape 유지
- inspect public status `warning` 유지

### `src/aios/validate/result.py`

변경 사항:

- validate severity/status mapping을 `status.py` 상수로 대체

유지한 사항:

- validate public JSON shape 유지
- validate public status `warn` 유지

### `src/aios/cli.py`

변경 사항:

- exit code literal을 `status.py` 상수로 일부 대체

유지한 사항:

- CLI command names 유지
- CLI option names 유지
- human output shape 유지
- JSON output shape 유지

## 4. 중복 제거 결과

| 중복 영역 | 이전 위치 | 변경 후 |
|---|---|---|
| frontmatter extraction | `inspect.py`, `validate/validators/agent.py` | `frontmatter.py` |
| simple frontmatter parser | `inspect.py`, `validate/validators/agent.py` | `frontmatter.py` |
| list/scalar helper | `inspect.py`, `validate/validators/agent.py` | `frontmatter.py` |
| agent required fields | `inspect.py`, `validate/validators/agent.py` | `contracts.py` |
| agent reference fields | `validate/validators/agent.py` 내부 상수 | `contracts.py` |
| relative Markdown link resolve | `inspect.py`, `validate/validators/references.py` | `references.py` |
| Markdown/Obsidian combined extraction | 여러 호출부에서 직접 조합 | `references.py` |
| validate severity/status mapping | `validate/result.py` | `status.py` |
| inspect status order | `result.py` | `status.py` |

## 5. 동작 보존 확인

이번 리팩터는 내부 구현 정리이며 public behavior 변경을 의도하지 않았다.

보존한 사항:

- `aios inspect` 출력 형식
- `aios validate` 출력 형식
- `aios load-context` 출력 형식
- inspect JSON schema
- validate JSON schema
- semantic loader bundle schema
- exit code 정책

주의:

- 새 Python 모듈 4개가 추가되어 `inspect`의 `files_scanned` 수는 증가했다.
- fail/warning 기준선은 유지되었다.

## 6. 검증 결과

### `python -m aios inspect`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 fail, 0 warning, 2 info, 308 pass`

### `python -m aios validate`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 error, 0 warning, 3 info`

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

### `python -m aios load-context .ai/rules/rules.md --json --summary-only`

결과:

- 종료 코드: `0`
- 상태: `warning`
- 기존과 동일하게 `rules_file_fallback` warning 1개 출력

### `python -m compileall -q src/aios aios`

결과:

- 종료 코드: `0`
- 컴파일 성공
- 생성된 `__pycache__` 디렉터리는 제거했다.

### `git diff --check`

결과:

- 종료 코드: `0`
- 공백 오류 없음
- 기존 `.bkit/state/*` 작업 트리 파일의 LF/CRLF 경고는 출력되었으나 이번 리팩터 실패는 아님

## 7. 남은 제한

- `markdown_refs.py`와 `references.py`가 아직 완전히 통합된 것은 아니다.
- `references.py`는 policy-free primitive만 제공하며, command별 fail/warning 정책은 기존 위치에 남아 있다.
- public status 통합은 아직 하지 않았다.
- command envelope 통합은 아직 하지 않았다.
- validate registry는 아직 dispatch에 적극적으로 사용하지 않는다.

## 8. 다음 권장 작업

P1 후보:

- `inventory.py` 추가로 agent/skill/workflow inventory 공통화
- `targets.py` 공통화 검토
- `markdown_refs.py`와 `references.py` 역할 정리
- validate 전용 `--summary-only` 추가
- command JSON envelope v1/v2 전환 계획 작성

P2 후보:

- human summary 출력 helper 공통화
- validate registry를 실제 dispatch 테이블로 사용
- status `warning`/`warn` public migration 계획 수립
