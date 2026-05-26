# Execution prototype planning

> 이 문서는 design-only 계획서이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation, dynamic loading, registry/discovery를 구현하거나 승인하지 않는다.

## 목적

Execution architecture approval 이후 가능한 future execution prototype의 계획 범위를 정의한다. 이 문서는 실제 prototype 구현 작업을 시작하기 위한 문서가 아니라, prototype 구현 전에 충족해야 할 test harness, no-write, network-disabled, trace/evidence, abort 조건을 정리하는 planning artifact다.

## Prototype 목표

향후 prototype은 다음 질문에 답하기 위한 실험이어야 한다.

- sandbox-like boundary에서 명시적 input bundle을 받을 수 있는가
- repository source/target/manifest/snapshot mutation 없이 evidence를 생성할 수 있는가
- network disabled policy를 강제하거나 검출할 수 있는가
- timeout/resource/stdout/stderr limit을 fail-closed로 처리할 수 있는가
- provider capability, sandbox policy, sandbox result, sandbox trace, provider trace evidence를 연결할 수 있는가
- envelope v2가 execution facts를 숨기지 않고 보존할 수 있는가
- failure/abort condition이 sync apply나 mutation authorization으로 오해되지 않는가

## Prototype non-goals

다음은 prototype planning의 비목표다.

- 실제 sandbox launcher 구현
- 실제 subprocess execution 구현
- 실제 provider execution 구현
- 실제 replay execution 구현
- generated content 생성
- generated content persistence
- snapshot update
- sync apply/mutation
- rollback execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- repository-wide scan
- activation-driven execution selection
- force/decommission

## 허용 가능한 prototype planning 범위

다음 항목은 planning 범위에서 다룰 수 있다.

- future command boundary 후보
- explicit input bundle 후보
- explicit output bundle 후보
- no-write verification harness 요구사항
- network-disabled verification harness 요구사항
- timeout/resource limit harness 요구사항
- stdout/stderr capture policy
- sandbox result evidence 생성 조건
- sandbox trace evidence 생성 조건
- provider execution trace evidence 생성 조건
- envelope v2 metadata requirements
- fail-closed/abort semantics
- implementation readiness audit checklist

## Future command boundary 후보

실제 명령은 아직 승인되지 않는다. 다만 prototype planning은 다음과 같은 command boundary 후보를 검토할 수 있다.

```text
python -m aios sandbox-prototype --request <sandbox-request.json> --json
```

이 후보는 다음 조건이 충족되기 전까지 구현하지 않는다.

- command boundary가 runtime authority에 승격됨
- sandbox request/result/trace schemas가 명확함
- no-write verification runtime design이 승인됨
- network isolation runtime design이 승인됨
- implementation readiness audit가 통과함

## Input bundle 후보

Prototype input bundle은 implicit discovery 없이 명시적 JSON이어야 한다.

필수 후보 필드:

- `schema_version`
- `request_id`
- `sandbox_mode`
- `provider_mode`
- `provider_capability_ref`
- `sandbox_policy_ref`
- `replay_manifest_ref` 또는 `case_ref` when applicable
- `source_refs`
- `source_hashes`
- `sync_mode`
- `hash_policy`
- `output_affecting_config`
- `timeout_policy`
- `resource_policy`
- `expected_output_contract`

경계:

- repository-wide scan 금지
- default provider discovery 금지
- dynamic plugin loading 금지
- activation-driven execution selection 금지
- host env에서 output-affecting config를 암묵적으로 읽는 것 금지

## Output bundle 후보

Prototype output bundle은 generated content persistence가 아니라 evidence bundle이어야 한다.

필수 후보 필드:

- `schema_version`
- `request_id`
- `status`
- `failure_code`
- `failure_message`
- `sandbox_mode`
- `provider_mode`
- `duration_ms`
- `generated_hashes`
- `provenance`
- `provider_trace`
- `sandbox_result`
- `sandbox_trace`
- `no_write_evidence`
- `network_disabled`
- `mutation_performed`
- `stdout_bytes`
- `stderr_bytes`
- `output_json_valid`

경계:

- raw generated content는 v0 prototype planning에서 제외한다.
- generated hashes는 write authorization이 아니다.
- output success는 sync apply authorization이 아니다.
- output evidence는 static validators로 재검증 가능해야 한다.

## Test harness 요구사항

Prototype implementation readiness 전에는 다음 test harness 요구사항이 정의되어야 한다.

### No-write harness

요구사항:

- protected roots 목록을 명시한다.
- protected roots의 pre/post hash 또는 metadata snapshot을 만든다.
- temp root 밖 unexpected output을 검출한다.
- source, target, manifest, snapshot, fixture roots mutation을 fail closed로 처리한다.
- mutation이 감지되면 `sandbox-filesystem-violation`으로 분류한다.

필수 테스트 후보:

- protected root unchanged pass
- target mutation detected fail
- manifest mutation detected fail
- snapshot mutation detected fail
- temp root cleanup evidence pass/fail
- unexpected output outside temp root fail

### Network-disabled harness

요구사항:

- network disabled policy를 input에 명시한다.
- network disabled evidence를 output에 남긴다.
- network attempt detection 또는 OS/container isolation strategy를 명시한다.
- network attempt는 `sandbox-network-attempt`로 fail closed 처리한다.

필수 테스트 후보:

- network disabled metadata pass
- network attempt detected fail
- external API/model access forbidden
- missing network evidence fail

### Timeout/resource harness

요구사항:

- timeout_ms를 명시한다.
- max input/output bytes를 명시한다.
- stdout/stderr caps를 명시한다.
- timeout, nonzero exit, output invalid, resource limit을 distinct failure code로 매핑한다.

필수 테스트 후보:

- timeout maps to `sandbox-timeout`
- nonzero exit maps to `sandbox-nonzero-exit`
- invalid output maps to `sandbox-output-invalid`
- stdout/stderr cap maps to `sandbox-resource-limit`

### Trace/evidence harness

요구사항:

- provider execution trace evidence를 생성하거나 명시적으로 unavailable 처리한다.
- sandbox result evidence를 생성한다.
- sandbox trace evidence가 sandbox result와 provider trace relationship을 보존한다.
- trace_id/request_id consistency를 확인한다.
- static validators로 output evidence를 재검증한다.

필수 테스트 후보:

- provider trace valid
- sandbox result valid
- sandbox trace valid
- trace_id mismatch fail
- request_id mismatch fail
- missing trace evidence fail

## Abort conditions

Prototype planning은 다음 abort condition을 fail-closed로 정의해야 한다.

- invalid provider capability
- invalid sandbox policy
- missing input bundle
- malformed input bundle
- unsafe path
- parent traversal
- absolute protected path where not allowed
- timeout
- nonzero exit
- stdout/stderr/resource limit exceeded
- output JSON invalid
- network attempt
- filesystem mutation
- nondeterministic output
- missing provider trace
- missing sandbox result
- missing sandbox trace
- sandbox result/trace mismatch
- provider id/version mismatch
- unsupported sync mode
- hash policy mismatch

Abort 결과는 retry로 자동 복구하지 않는다. Retry가 필요한 경우는 별도 설계와 nondeterminism masking risk audit가 필요하다.

## Required static validators before implementation

Prototype implementation 전에는 다음 static validators 또는 equivalent contract가 준비되어 있어야 한다.

- provider capability validation
- sandbox policy validation
- sandbox result validation
- sandbox trace validation
- provider execution trace validation
- replay manifest validation when replay is involved
- future sandbox request validation
- future prototype output bundle validation

현재 앞의 다섯 항목은 구현되어 있다. sandbox request와 prototype output bundle은 아직 별도 schema/validator가 없다.

## Required rule/spec promotion before implementation

Prototype implementation 전에는 다음 boundary가 runtime authority에 승격되어야 한다.

- prototype command boundary
- sandbox launcher boundary
- subprocess execution boundary
- no-write verification boundary
- network isolation boundary
- provider execution boundary
- replay execution boundary
- output bundle schema boundary
- trace/evidence requirement
- fail-closed failure code mapping
- explicit non-goals

승격 대상은 `.ai/rules/operations/validation.rules.md`, `.ai/rules/operations/sync.rules.md`, future provider/sandbox operation rule, 또는 active normative spec 중 가장 작은 적절한 위치여야 한다.

## Implementation readiness checklist

Prototype implementation task가 생성되기 전에 다음 checklist를 통과해야 한다.

| Gate | Required |
| --- | --- |
| Prototype command boundary approved | yes |
| Sandbox request schema designed | yes |
| Prototype output bundle schema designed | yes |
| No-write harness designed | yes |
| Network-disabled harness designed | yes |
| Timeout/resource harness designed | yes |
| Trace/evidence harness designed | yes |
| Rule/spec promotion audit completed | yes |
| Runtime authority promotion completed | yes |
| Implementation readiness audit completed | yes |

## 권장 다음 design-only 작업

Prototype planning 이후에도 바로 구현하지 않는다. 권장 후속 작업은 다음 순서다.

1. Sandbox prototype request fixture contract design
2. Prototype output bundle fixture contract design
3. No-write verification harness design
4. Network isolation enforcement decision audit
5. Execution boundary rule/spec promotion audit
6. Implementation readiness audit

## 최종 경계

이 계획은 future execution prototype planning을 정리하지만 실행 구현을 승인하지 않는다. 실제 code implementation은 별도 implementation readiness audit와 runtime authority promotion 이후에만 검토한다.
