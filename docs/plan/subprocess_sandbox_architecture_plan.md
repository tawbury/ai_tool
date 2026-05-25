# Subprocess Sandbox Architecture Plan

> 이 문서는 design-only 계획서이다. Provider execution, sandbox launcher, adapter execution, generated content, replay execution, sync apply, mutation을 구현하지 않는다.

## 목적

Future provider-like execution을 검토하기 전에 subprocess sandbox가 만족해야 할 최소 architecture contract를 정의한다. 이 계획은 execution authorization이 아니라 future readiness gate의 입력이다.

## Sandbox Goals

Subprocess sandbox는 future provider-like path가 다음 목표를 만족하도록 설계되어야 한다.

- source/target/manifest/snapshot mutation 방지
- network access 방지
- environment access 제한
- filesystem access 제한
- timeout/resource limit 강제
- deterministic output evidence 보존
- provider execution trace metadata 생성
- no-write verification evidence 생성
- provider output을 read-only comparison input으로만 취급

## Architecture Baseline

권장 v0 baseline:

- Python subprocess
- temporary working directory
- restricted cwd
- sanitized environment
- explicit input bundle
- explicit output JSON
- stdout/stderr capture
- timeout
- max input/output bytes
- no implicit discovery
- no dynamic plugin loading
- no target writes

OS/container sandbox는 future option으로 남긴다. Python subprocess만으로 network와 filesystem containment가 완전하다고 가정하지 않는다.

## Minimum Subprocess Sandbox Contract

### Input bundle

Sandbox input은 명시적 bundle이어야 한다.

필수 항목:

- provider capability declaration
- provider id/version
- provider mode
- case id 또는 request id
- source hashes
- sync mode
- marker metadata when applicable
- hash policy
- output-affecting config
- allowed read roots
- max input/output bytes
- timeout policy

금지:

- implicit repository scan
- default provider discovery
- dynamic plugin lookup
- activation-driven provider selection without separate design

### Output JSON

Sandbox output은 explicit JSON이어야 한다.

필수 항목:

- schema_version
- provider_id
- provider_version
- provider_mode
- preview_available or output_available
- generated hashes
- provenance
- unavailable_reason
- failure_code
- deterministic_execution
- no_write_confirmed
- network_disabled
- mutation_performed
- trace metadata

Output JSON은 generated content persistence가 아니다. Hash와 metadata 중심이어야 하며 raw generated content는 v0에서 피한다.

### Working directory

Sandbox는 temporary working directory에서 실행한다.

Rules:

- cwd는 sandbox temp root여야 한다.
- source/target repository root를 cwd로 사용하지 않는다.
- output file은 temp root 아래 explicit path에만 허용한다.
- temp root 밖 write 시도는 violation이다.
- symlink는 fail-closed로 다룬다.

### Environment

Environment는 allowlist 방식으로 구성한다.

Allowed examples:

- deterministic locale
- deterministic timezone when needed
- minimal Python path required for sandbox harness

Forbidden:

- inherited secrets
- API keys
- host-specific credentials
- broad PATH mutation
- environment-derived output-affecting config without declaration

### Timeout and resource limits

필수 정책:

- timeout_ms positive integer
- max_input_bytes
- max_output_bytes
- stdout/stderr byte cap
- optional max_memory_bytes if supported

Failure mapping:

- timeout -> `sandbox-timeout`
- output cap exceeded -> `sandbox-resource-limit`
- invalid JSON -> `sandbox-output-invalid`
- nonzero exit -> `sandbox-nonzero-exit`

### Stdout/stderr handling

- stdout may contain output JSON only when explicitly selected.
- stderr is diagnostic only and must be size-capped.
- stderr must not be treated as generated content.
- Large stdout/stderr should fail closed.
- Secret-looking values require future redaction policy before display.

### No-write verification

Minimum strategy:

- pre-run hash/metadata snapshot for protected roots
- post-run comparison for source, target, manifest, snapshot, and fixture roots
- temp root cleanup verification
- output file allowlist check
- mutation detection maps to `sandbox-filesystem-violation`

No-write verification does not authorize sync apply. It only proves the sandbox run did not mutate protected paths.

## Exit Code Mapping

| Subprocess state | Sandbox failure code | Status |
| --- | --- | --- |
| exits 0 with valid output | none | pass |
| exits nonzero | `sandbox-nonzero-exit` | fail |
| timeout | `sandbox-timeout` | fail |
| output JSON invalid | `sandbox-output-invalid` | fail |
| output/resource cap exceeded | `sandbox-resource-limit` | fail |
| network attempt detected | `sandbox-network-attempt` | fail |
| filesystem write violation | `sandbox-filesystem-violation` | fail |
| forbidden env access detected | `sandbox-env-access-violation` | fail |
| replay mismatch | `sandbox-nondeterministic-output` | fail |

## Relationship to Existing Artifacts

### Provider capability validation

Sandbox execution eligibility must depend on a valid provider capability declaration, but capability validation alone is not execution authorization.

### Provider execution trace validation

Sandbox output should produce provider execution trace metadata compatible with `aios.provider_execution_trace.v0` or a future version. Trace validation remains static-only.

### Deterministic mock provider fixtures

Mock fixtures are contract evidence for deterministic behavior. They should inform sandbox input/output fixture design but must not be treated as real execution.

### Replay comparison

Replay comparison currently remains fixture-backed. Future sandbox replay must not bypass static replay validation or snapshot update prohibition.

### Envelope v2

Future envelope metadata may include:

- `provider_execution`
- `sandbox_execution`
- `mutation_performed`
- `provider_mode`
- `sandbox_mode`
- `trace_id`
- `failure_code`

Metadata must not imply write authorization.

## Hard Prohibitions

This plan does not authorize:

- provider execution implementation
- sandbox launcher implementation
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply/mutation
- dynamic provider loading
- provider registry/discovery

## Future Implementation Gates

Before sandbox execution can be considered, complete these gates:

1. Sandbox fixture bundle
2. Sandbox trace fixtures
3. Sandbox policy validator helper
4. Sandbox output contract tests
5. Sandbox rule promotion audit
6. Sandbox launcher architecture review
7. No-write verification design
8. Network isolation decision
9. Provider execution readiness audit

## Parallelization Plan

Can proceed in parallel:

- sandbox policy fixture contract design
- sandbox trace fixture contract design
- sandbox envelope metadata design

Can be bundled:

- fixture-only sandbox policy files
- fixture-only trace examples
- schema/contract tests

Must remain sequential:

- static validator before validate integration
- output contract stabilization before rule promotion
- rule promotion before any execution readiness audit
- execution readiness audit before sandbox launcher implementation

## Next Recommended Slice

다음 안전한 작업은 sandbox policy fixture contract design이다. 이는 fixture/schema only여야 하며 subprocess launcher, provider execution, replay execution, generated content, sync apply, mutation을 계속 금지해야 한다.
