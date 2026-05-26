# Sandbox Result Validate Output Contract Report

## 목적

이 보고서는 `aios validate <sandbox-result.json>` static validation 출력 계약 안정화 결과를 기록한다. 이번 작업은 기존 runtime semantics를 변경하지 않고 output contract tests를 보강했다.

## 안정화 범위

보강된 테스트:

- `tests/test_sandbox_result_validate_output_contract.py`
- `tests/test_validate_sandbox_result.py`

고정된 계약:

- valid sandbox result native JSON pass
- invalid sandbox result native JSON fail
- valid sandbox result envelope v2 pass
- invalid sandbox result envelope v2 fail
- sandbox-result-shaped invalid schema detection
- sandbox-result-shaped missing schema detection
- unrelated JSON non-misclassification
- sandbox policy target detection 유지
- provider execution trace target detection 유지
- provider capability target detection 유지
- replay manifest target detection 유지
- sync manifest target detection 유지
- `--envelope-v2` without `--json` exit code `2`

## Metadata Invariants

Native JSON result details와 envelope v2 meta/messages/payload에서 다음 invariant를 고정했다.

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`
- `sandbox_mode` preserved where available
- `request_id` preserved where available
- `failure_code` preserved where available

Helper issue code/message/field/details는 validate output에 보존된다.

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

`docs/index/document_status_registry.md`에 이 보고서를 completed implementation report로 추가했다. `docs/index/phase_6_8_summary.md`와 `docs/index/current_runtime_context.md`는 다음 순차 작업을 sandbox result validation rule promotion audit로 갱신했다.

## 병렬화 메모

Output contract stabilization, docs index update, report update는 같은 static validation 안정화 범위라 안전하게 묶어 진행했다. Rule promotion audit는 이 안정화 완료 이후의 다음 순차 작업이다. Sandbox trace fixture contract는 별도 design-only parallel track으로 계속 진행할 수 있다. Sandbox execution은 계속 차단된다.

## 검증

실행 대상:

- `python -m pytest tests/test_sandbox_result_validate_output_contract.py`
- `python -m pytest tests/test_validate_sandbox_result.py`
- `python -m pytest tests/test_sandbox_execution_result_validator.py`
- `python -m aios validate tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json --json`
- `python -m aios validate tests/fixtures/providers/sandbox_results/valid/successful_subprocess_result.json --json --envelope-v2`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`
