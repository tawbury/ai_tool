# Sandbox Policy Validate Output Contract Report

## 목적

이 보고서는 `aios validate <sandbox-policy.json>` static validation의 native JSON과 envelope v2 출력 계약 안정화 결과를 기록한다.

이번 작업은 기존 runtime semantics를 확장하지 않는다. Sandbox launcher, subprocess execution, provider execution, replay execution, dynamic loading, generated content, snapshot update, sync apply, mutation은 계속 차단된다.

## 안정화 범위

강화된 테스트 파일:

- `tests/test_sandbox_policy_validate_output_contract.py`
- `tests/test_validate_sandbox_policy.py`

검토한 구현 파일:

- `src/aios/validate/validators/sandbox_policy.py`
- `src/aios/providers/sandbox_policy.py`

## 고정된 Native JSON 계약

Valid sandbox policy:

- `schema_version: aios.validate.result.v0`
- `target.kind: sandbox-policy`
- `status: pass`
- success code: `sandbox_policy_checked`
- `validator: sandbox-policy`
- `sandbox_mode` preserved
- `network_disabled` preserved
- `deterministic_execution` preserved
- `no_write_required` preserved
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `mutation_performed: false`

Invalid sandbox policy:

- `status: fail`
- helper issue code preserved
- helper issue message preserved
- helper issue field preserved in `details.field`
- policy context fields preserved where available
- non-execution metadata preserved
- success code is not emitted after validation errors

## 고정된 Envelope v2 계약

Valid and invalid envelope v2 output now asserts:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: sandbox-policy`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `meta.sandbox_execution: false`
- `meta.subprocess_execution: false`
- `meta.provider_execution: false`
- `meta.mutation_performed: false`
- `meta.sandbox_mode` preserved where available
- `payload.results` preserves native validation results
- `messages` preserves helper issue details and non-execution metadata

## Target Detection 안정화

테스트는 다음 detection behavior를 고정한다.

- schema-valid sandbox policy is `sandbox-policy`
- sandbox-policy-shaped invalid schema is `sandbox-policy`
- sandbox-policy-shaped missing schema is `sandbox-policy`
- unrelated JSON is not `sandbox-policy`
- provider capability remains `provider-capability`
- provider execution trace remains `provider-execution-trace`
- replay manifest remains `replay-manifest`
- sync manifest remains `sync-manifest`
- `--envelope-v2` without `--json` remains exit code `2`

## Runtime Boundary

이번 안정화는 serialization과 regression tests만 강화한다.

계속 금지:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply
- mutation

## 병렬화 메모

Output contract stabilization, docs index update, report 작성은 이번 task에서 안전하게 묶었다. 모두 static validation 결과의 출력 계약을 고정하는 작업이며 sandbox execution을 도입하지 않는다.

Rule promotion audit는 이 안정화 이후의 다음 순차 작업이어야 한다. Sandbox trace fixture contract와 sandbox execution result fixture contract는 별도 design-only parallel track으로 진행할 수 있다.

Sandbox execution implementation은 계속 차단되며, sandbox policy validation rule promotion만으로도 실행이 승인되지 않는다.

## 다음 권장 방향

다음 안전한 단계는 sandbox policy validation rule promotion audit다. Audit가 rule promotion을 권장하더라도 promotion task는 별도 작업이어야 하며, sandbox execution implementation과 결합하면 안 된다.
