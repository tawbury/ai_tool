# Sandbox trace validate 출력 계약 안정화 보고서

> 이 보고서는 human context이다. 런타임 계약은 `.ai/rules/`에 있으며, 본 작업은 `.ai/rules`를 수정하지 않았다.

## 목적

`aios validate <sandbox-trace.json>` 정적 검증의 native JSON 및 envelope v2 출력 계약을 안정화했다. 이 작업은 output contract test 강화와 보고서 작성만 수행했으며, 런타임 의미를 변경하지 않았다.

## 안정화 범위

고정한 출력 계약은 다음과 같다.

- native JSON schema version은 `aios.validate.result.v0`이다.
- target kind는 `sandbox-trace`이다.
- 성공 code는 `sandbox_trace_checked`이다.
- helper issue code, severity, status, message, field가 validate result에 보존된다.
- success/failure details는 가능한 경우 다음 evidence identifier를 보존한다.
  - `trace_id`
  - `request_id`
  - `sandbox_mode`
  - `provider_mode`
  - `status`
  - `failure_code`
- native JSON과 envelope v2는 다음 non-execution metadata를 보존한다.
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `replay_execution: false`
  - `mutation_performed: false`

## 강화한 테스트

`tests/test_sandbox_trace_validate_output_contract.py`에서 다음 계약을 확인한다.

- valid sandbox trace native JSON pass
- invalid sandbox trace native JSON fail
- valid sandbox trace envelope v2 pass
- invalid sandbox trace envelope v2 fail
- shaped invalid schema detection
- shaped missing schema detection
- unrelated JSON non-misclassification
- sandbox result/policy/provider trace/provider capability/replay/sync target detection regression
- `--envelope-v2` without `--json` usage error
- helper issue code/message/field/details preservation

## 명시적 비목표

이번 작업은 다음을 구현하지 않았다.

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply/mutation
- `.ai/rules` promotion

## 검증 상태

후속 커밋 전에 task 검증 명령을 실행한다.

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

## 다음 단계

다음 순차 task는 sandbox trace rule promotion audit이다. Audit 전에는 `.ai/rules`를 수정하지 않는다.
