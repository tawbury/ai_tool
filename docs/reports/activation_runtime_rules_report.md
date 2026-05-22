# Activation Runtime Rules 승격 보고서

## 1. 작업 요약

`aios activation` v0 구현을 `.ai OS` runtime-facing 운영 규칙으로 승격했다.

추가한 파일:

- `.ai/rules/operations/activation.rules.md`
- `docs/reports/activation_runtime_rules_report.md`

수정한 파일:

- `.ai/rules/rules.md`
- `.ai/rules/operations/README.md`

코드 변경은 하지 않았다.

## 2. Activation Rule 내용

`.ai/rules/operations/activation.rules.md`에 다음 내용을 짧은 runtime-facing rule로 정리했다.

- activation purpose
- supported schema fields
- inventory relationship
- semantic loader profile relationship
- future sync selection과의 차이
- read-only boundary
- deferred items

## 3. Global Rules 반영

`.ai/rules/rules.md`에 다음을 반영했다.

- Rule Layers 예시에 `activation.rules.md` 추가
- operations 설명에 activation governance 포함
- Selective Loading 예시에 activation contract task 추가
- Migration Map에 activation contract 관련 entry 추가

## 4. Operations README 반영

`.ai/rules/operations/README.md`의 Current Operational Rules 목록에 `activation.rules.md`를 추가했다.

## 5. Runtime Boundary

activation rule은 activation이 runtime selection contract임을 명시한다.

activation은 다음을 수행하지 않는다.

- file copy
- manifest write
- adapter generation
- managed block insertion
- drift detection
- worker dispatch
- workflow execution
- auto-fix

future sync가 activation을 입력으로 사용할 수는 있지만, activation 자체는 sync selection이 아니다.

## 6. 검증 결과

### `python -m aios activation .ai/templates/activation.template.yaml`

결과:

- 종료 코드: `0`
- 상태: `pass`
- references: `6/6 resolved`

### `python -m aios inventory --summary-only`

결과:

- 종료 코드: `0`
- 상태: `pass`
- total: `157`
- rule count: `12`

새 activation rule이 inventory에 포함되어 rule count가 증가했다.

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

### `python -m compileall -q src/aios aios`

결과:

- 종료 코드: `0`
- 컴파일 성공
- 생성된 `__pycache__` 디렉터리는 제거했다.

### `git diff --check`

결과:

- 종료 코드: `0`
- 공백 오류 없음
- 변경된 `.ai/rules` 파일의 LF/CRLF 경고는 출력되었으나 diff check 실패는 아님

## 7. 커밋

검증 통과 후 다음 메시지로 커밋한다.

```text
docs(aios): promote activation contract rules
```
