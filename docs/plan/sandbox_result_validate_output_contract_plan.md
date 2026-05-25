# Sandbox Result Validate Output Contract Plan

## 목적

이 문서는 future `aios validate <sandbox-result.json>` 정적 검증의 native JSON 및 envelope v2 출력 계약을 정의한다. 현재 sandbox result validation은 helper-only 상태이며, 이 문서는 validate integration 전에 필요한 설계 기준이다.

이 문서는 runtime code를 구현하지 않으며 `.ai/rules`를 수정하지 않는다.

## 대상 감지

Validate target detection은 다음 순서를 유지해야 한다.

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy
7. sandbox result

Sandbox result target은 다음 중 하나로 감지한다.

- JSON object with `schema_version: aios.sandbox_execution_result.v0`
- sandbox-result-shaped JSON with missing or invalid schema

Sandbox-result-shaped heuristic은 unrelated JSON을 오분류하지 않도록 보수적으로 적용해야 한다. 권장 조건은 sandbox result 필드 중 충분한 개수와 `request_id`, `status`, `no_write_evidence` 중 하나 이상의 핵심 필드가 함께 존재하는 경우다. 정확한 field count는 구현 시 테스트로 고정하되 runtime rule에는 넣지 않는다.

## Target Kind

Future validate target kind:

```text
sandbox-result
```

## Native JSON Contract

Native validate JSON은 기존 shape를 유지한다.

```json
{
  "schema_version": "aios.validate.result.v0",
  "target": {
    "kind": "sandbox-result"
  }
}
```

성공 result:

- `code: sandbox_result_checked`
- `severity: info`
- `status: pass`
- message는 static validation이 sandbox execution 없이 완료되었음을 명시

성공 result details:

- `sandbox_mode`
- `request_id`
- `status`
- `failure_code`
- `trace_id`
- `network_disabled`
- `mutation_performed`
- `no_write_confirmed`
- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`

`mutation_performed`는 실제 fixture 값과 command-level non-execution metadata 모두에서 false여야 한다. Details에서는 sandbox result evidence 값을 보존하되 valid pass에는 false만 허용된다.

실패 result:

- helper issue code를 그대로 보존
- helper severity/status/message를 보존
- helper `field`가 있으면 보존
- 가능한 경우 `sandbox_mode`, `request_id`, `status`, `failure_code`, `trace_id`를 details에 포함
- non-execution metadata를 항상 포함

실패 result details:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

## Envelope v2 Mapping

Envelope v2는 `--json --envelope-v2`에서만 사용한다.

Expected fields:

- `schema_version: aios.command_result.v2`
- `command: validate`
- `target.kind: sandbox-result`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `meta.sandbox_execution: false`
- `meta.subprocess_execution: false`
- `meta.provider_execution: false`
- `meta.replay_execution: false`
- `meta.mutation_performed: false`
- `meta.sandbox_mode` when available
- `meta.request_id` when available
- `meta.failure_code` when available
- `payload.results` preserves native validate results
- `messages` preserves validation issue details

Envelope metadata is evidence only. It must not authorize sandbox launch, provider execution, replay execution, sync apply, or mutation.

## Exit Semantics

- pass -> exit code `0`
- validation error -> exit code `1`
- usage/config error -> exit code `2`

`--envelope-v2` without `--json` must remain exit code `2`.

## Static-only Boundary

Future sandbox result validate integration must validate parsed JSON structure and result evidence only.

It must not:

- launch a sandbox
- run a subprocess
- execute a provider
- execute replay
- dynamically load providers
- discover or register providers
- execute adapters
- create generated content
- update snapshots
- write files
- authorize sync apply or mutation

## Compatibility Requirements

Existing target detection must remain unchanged:

- sandbox policy remains `sandbox-policy`
- provider execution trace remains `provider-execution-trace`
- provider capability remains `provider-capability`
- replay manifest remains `replay-manifest`
- sync manifest remains `sync-manifest`
- unrelated JSON remains generic file or unsupported target, not `sandbox-result`

The new target must be appended after sandbox policy in detection priority.

## Required Future Tests

Implementation should add tests for:

- valid sandbox result native JSON pass
- invalid sandbox result native JSON fail
- sandbox-result-shaped invalid schema detected and failed
- unrelated JSON not misclassified
- valid sandbox result envelope v2 pass
- invalid sandbox result envelope v2 fail
- non-execution metadata preserved
- helper issue code and field preserved
- existing target detection unchanged
- `--envelope-v2` without `--json` remains exit code `2`

## Parallelization Note

Validate integration must wait for this output contract. Sandbox trace fixture contract may proceed independently as design-only work. Sandbox execution, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, and mutation remain blocked.
