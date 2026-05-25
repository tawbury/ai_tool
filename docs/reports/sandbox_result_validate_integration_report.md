# Sandbox Result Validate Integration Report

## 목적

이 보고서는 `aios validate <sandbox-result.json>` 정적 검증 통합 결과를 기록한다. 통합은 `aios.sandbox_execution_result.v0` JSON 구조와 sandbox result evidence만 검증하며 sandbox launcher, subprocess execution, provider execution, replay execution을 도입하지 않는다.

## 구현 범위

변경된 runtime 파일:

- `src/aios/validate/targets.py`
- `src/aios/validate/engine.py`
- `src/aios/validate/validators/sandbox_result.py`
- `src/aios/cli.py`

추가된 테스트:

- `tests/test_validate_sandbox_result.py`
- `tests/test_sandbox_result_validate_output_contract.py`

## 지원 동작

새 validate target:

- `target.kind: sandbox-result`
- schema: `aios.sandbox_execution_result.v0`
- success code: `sandbox_result_checked`

Native JSON은 기존 `aios.validate.result.v0` shape를 유지한다. Envelope v2는 `command: validate`, `target.kind: sandbox-result`, non-execution metadata를 보존한다.

## Target Detection

Sandbox result detection은 다음 우선순위 뒤에 배치했다.

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy
7. sandbox result

`schema_version: aios.sandbox_execution_result.v0`를 우선 인식하고, schema가 누락되거나 잘못된 sandbox-result-shaped JSON은 보수적 heuristic으로 감지해 schema validation error를 반환한다. Unrelated JSON은 `sandbox-result`로 오분류하지 않는다.

## Output Metadata

성공 및 실패 result details는 다음 non-execution metadata를 보존한다.

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

Envelope v2 meta에는 가능한 경우 다음 evidence identifiers를 추가한다.

- `sandbox_mode`
- `request_id`
- `failure_code`

## 비목표

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
- sync apply 또는 mutation
- `.ai/rules` 변경

## 문서 인덱스

`docs/index/document_status_registry.md`는 output contract plan을 historical/superseded로 전환하고 이 integration report를 completed implementation report로 추가했다. `docs/index/current_runtime_context.md`와 `docs/index/phase_6_8_summary.md`는 sandbox result static validation 지원을 반영했다.

## 병렬화 메모

Validate integration과 output contract tests는 같은 static validation 범위라 안전하게 묶어 진행했다. Sandbox trace fixture contract는 독립적인 design-only track으로 계속 진행할 수 있다. Sandbox launcher와 execution implementation은 여전히 순차적으로 차단된다.

## 검증

실행 대상:

- `python -m pytest tests/test_validate_sandbox_result.py`
- `python -m pytest tests/test_sandbox_result_validate_output_contract.py`
- `python -m pytest tests/test_sandbox_execution_result_validator.py`
- `python -m aios validate tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json --json`
- `python -m aios validate tests/fixtures/providers/sandbox_results/invalid/network_disabled_false.json --json`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
