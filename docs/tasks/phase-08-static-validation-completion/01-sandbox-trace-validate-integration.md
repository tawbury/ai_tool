# Task 01: Sandbox trace validate integration

## 목적

`aios validate <sandbox-trace.json>` static validation을 통합한다. 이 task는 sandbox trace validator helper를 validate target으로 연결하는 작업이며, sandbox launcher나 execution behavior를 구현하지 않는다.

## 선행 조건

- `docs/roadmap/static_validation_and_execution_readiness_roadmap.md`
- `docs/plan/sandbox_trace_validate_output_contract_plan.md`
- `src/aios/providers/sandbox_trace.py`
- `tests/test_sandbox_trace_validator.py`
- `tests/test_sandbox_trace_fixtures.py`

## 허용 범위

- sandbox trace target detection 추가
- target kind `sandbox-trace` 추가
- `validate_sandbox_trace_data(data)` 통합
- native JSON success/error result 추가
- envelope v2 metadata 추가
- target detection regression tests 추가
- integration report 작성
- 필요한 docs index의 간결한 갱신

## 금지 범위

- sandbox launcher 구현
- subprocess execution 구현
- provider execution 구현
- replay execution 구현
- dynamic loading 구현
- provider registry/discovery 구현
- generated content 생성
- snapshot update
- sync apply/mutation
- `.ai/rules` 수정

## 산출물

- `src/aios/validate/validators/sandbox_trace.py`
- validate target detection/engine integration 변경
- `tests/test_validate_sandbox_trace.py`
- `tests/test_sandbox_trace_validate_output_contract.py`
- `docs/reports/sandbox_trace_validate_integration_report.md`

## 검증 명령

```powershell
python -m pytest tests/test_validate_sandbox_trace.py
python -m pytest tests/test_sandbox_trace_validate_output_contract.py
python -m pytest tests/test_sandbox_trace_validator.py
python -m aios validate tests/fixtures/providers/sandbox_traces/valid/successful_sandbox_trace.json --json
python -m aios validate
python -m aios inspect
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

## 요청 문구

```text
Implement sandbox trace validate integration for `.ai OS` and commit the result.

Scope:
- Integrate `validate_sandbox_trace_data(data)` into `aios validate <sandbox-trace.json>`.
- Add target kind `sandbox-trace`.
- Preserve existing target detection behavior.
- Add native JSON and envelope v2 static-only output.
- Add integration/output contract tests.
- Write `docs/reports/sandbox_trace_validate_integration_report.md`.

Do not implement sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation, dynamic loading, or registry/discovery.
```

## 다음 task

`02-sandbox-trace-output-stabilization.md`
