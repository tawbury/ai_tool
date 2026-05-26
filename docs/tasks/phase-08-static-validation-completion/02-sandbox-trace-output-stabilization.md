# Task 02: Sandbox trace output stabilization

## 목적

`aios validate <sandbox-trace.json>`의 native JSON 및 envelope v2 output contract를 안정화한다. 런타임 의미 변경은 피하고, 명백한 contract bug만 수정한다.

## 선행 조건

- Task 01 완료
- sandbox trace validate integration report 존재
- `tests/test_sandbox_trace_validate_output_contract.py` 존재

## 허용 범위

- output contract tests 강화
- pass/fail native JSON contract 고정
- pass/fail envelope v2 contract 고정
- shaped invalid/missing schema detection 테스트
- unrelated JSON non-misclassification 테스트
- existing target detection regression 테스트
- stabilization report 작성
- 필요한 docs index의 간결한 갱신

## 금지 범위

- 새 execution behavior 추가
- sandbox launcher, subprocess execution, provider execution, replay execution
- generated content, snapshot update, sync apply/mutation
- `.ai/rules` 수정

## 산출물

- 강화된 `tests/test_sandbox_trace_validate_output_contract.py`
- 필요 시 contract bug fix
- `docs/reports/sandbox_trace_validate_output_contract_report.md`

## 검증 명령

```powershell
python -m pytest tests/test_sandbox_trace_validate_output_contract.py
python -m pytest tests/test_validate_sandbox_trace.py
python -m pytest tests/test_sandbox_trace_validator.py
python -m aios validate tests/fixtures/providers/sandbox_traces/valid/successful_sandbox_trace.json --json
python -m aios validate tests/fixtures/providers/sandbox_traces/valid/successful_sandbox_trace.json --json --envelope-v2
python -m aios validate
python -m aios inspect
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

## 요청 문구

```text
Stabilize sandbox trace validate output contracts for `.ai OS` and commit the result.

Scope:
- Strengthen native JSON and envelope v2 output contract tests.
- Preserve non-execution metadata.
- Preserve existing target detection behavior.
- Write `docs/reports/sandbox_trace_validate_output_contract_report.md`.

Do not add sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation, dynamic loading, or registry/discovery.
```

## 다음 task

`03-sandbox-trace-rule-promotion-audit.md`
