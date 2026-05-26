# Sandbox trace validate 통합 보고서

> 이 보고서는 human context이다. 런타임 계약은 `.ai/rules/`에 있으며, 본 작업은 `.ai/rules`를 수정하지 않았다.

## 목적

`aios.sandbox_trace.v0` fixture/helper 계층을 `aios validate <sandbox-trace.json>` 정적 검증 대상으로 통합했다. 이 통합은 sandbox trace JSON 구조와 safety evidence metadata를 검증하기 위한 것이며, sandbox launcher, subprocess execution, provider execution, replay execution을 추가하지 않는다.

## 변경 사항

- `src/aios/validate/validators/sandbox_trace.py`를 추가했다.
- `src/aios/validate/targets.py`에 `sandbox-trace` target detection을 추가했다.
- `src/aios/validate/engine.py`에 `sandbox-trace` validator branch를 추가했다.
- `src/aios/cli.py` envelope v2 metadata에 sandbox trace non-execution fields를 추가했다.
- `tests/test_validate_sandbox_trace.py`를 추가했다.
- `tests/test_sandbox_trace_validate_output_contract.py`를 추가했다.

## Target detection

`aios validate <sandbox-trace.json>`는 다음 경우 `sandbox-trace` target으로 분류된다.

- `schema_version: aios.sandbox_trace.v0`
- 또는 sandbox-trace-shaped JSON이며 schema가 없거나 잘못된 경우

기존 target priority는 보존했다.

- provider execution trace detection은 provider trace 고유 evidence를 요구하도록 좁혔다.
- sandbox result detection은 result 고유 evidence를 요구하도록 좁혔다.
- sandbox trace는 sandbox result 이후에 detection된다.
- unrelated JSON은 `file` target으로 남는다.

## Output behavior

Native JSON:

- schema version은 `aios.validate.result.v0`이다.
- target kind는 `sandbox-trace`이다.
- 성공 result code는 `sandbox_trace_checked`이다.
- helper issue code, severity, message, field를 보존한다.

Envelope v2:

- schema version은 `aios.command_result.v2`이다.
- command는 `validate`이다.
- target kind는 `sandbox-trace`이다.
- metadata는 다음 non-execution boundary를 보존한다.
  - `sandbox_execution: false`
  - `subprocess_execution: false`
  - `provider_execution: false`
  - `replay_execution: false`
  - `mutation_performed: false`
- 가능한 경우 `trace_id`, `request_id`, `failure_code`를 보존한다.

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

직접 실행한 검증:

```powershell
python -m pytest tests/test_validate_sandbox_trace.py
python -m pytest tests/test_sandbox_trace_validate_output_contract.py
```

후속 전체 검증은 task 01 커밋 전에 수행한다.

## 다음 단계

다음 순차 task는 sandbox trace output stabilization이다. 현재 통합 테스트가 기본 output contract를 고정했지만, 다음 task에서 output contract를 더 강화하고 regression surface를 재확인해야 한다.
