# Task 04: Sandbox trace rule promotion

## 목적

Task 03 감사가 권장한 경우에만 sandbox trace static validation behavior를 runtime governance rules에 승격한다.

## 선행 조건

- Task 03 완료
- `docs/reports/sandbox_trace_rule_promotion_audit.md`가 promotion을 권장해야 함

## 허용 범위

- `.ai/rules/operations/validation.rules.md` 최소 수정
- 필요 시 `.ai/rules/operations/sync.rules.md`에 짧은 pointer 추가
- promotion report 작성
- docs index 간결한 갱신

## 금지 범위

- runtime code 변경
- tests/fixtures 변경
- sandbox launcher 구현
- subprocess execution 구현
- provider execution 구현
- replay execution 구현
- generated content 생성
- snapshot update
- sync apply/mutation

## 산출물

- 갱신된 `.ai/rules/operations/validation.rules.md`
- 필요 시 갱신된 `.ai/rules/operations/sync.rules.md`
- `docs/reports/sandbox_trace_runtime_rule_promotion_report.md`

## 검증 명령

```powershell
python -m aios inspect
python -m aios validate
python -m aios validate tests/fixtures/providers/sandbox_traces/valid/successful_sandbox_trace.json --json
python -m pytest tests/test_sandbox_trace_validate_output_contract.py
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

## 요청 문구

```text
Promote sandbox trace validation behavior into runtime governance rules and commit the result.

Scope:
- Update validation rules with static-only `aios validate <sandbox-trace.json>` behavior.
- Add a short sync safety pointer only if the audit recommends it.
- Write `docs/reports/sandbox_trace_runtime_rule_promotion_report.md`.

Do not implement runtime behavior or change tests/fixtures unless strictly necessary.
```

## 다음 task

`05-static-validation-surface-completion-audit.md`
