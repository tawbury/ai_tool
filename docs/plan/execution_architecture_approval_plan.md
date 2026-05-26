# Execution architecture approval 계획

> 이 문서는 design-only 계획서이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Phase 8 static validation surface completion과 Phase 9 execution readiness audit 이후, future execution prototype planning으로 넘어가기 위한 architecture approval boundary를 정의한다. 이 문서는 실행 구현 승인서가 아니라, 다음 단계의 prototype planning이 다뤄야 할 최소 설계 조건을 승인하는 문서다.

## 승인 범위

승인되는 범위는 다음으로 제한된다.

- execution prototype planning을 시작할 수 있다.
- no-write verification strategy를 prototype planning 입력으로 사용할 수 있다.
- network isolation strategy를 prototype planning 입력으로 사용할 수 있다.
- sandbox/process boundary를 prototype planning 입력으로 사용할 수 있다.
- provider capability preflight와 trace evidence requirement를 prototype planning 입력으로 사용할 수 있다.
- sandbox policy/result/trace evidence model을 prototype planning 입력으로 사용할 수 있다.
- envelope v2 metadata requirement를 prototype planning 입력으로 사용할 수 있다.

승인되지 않는 범위:

- sandbox launcher 구현
- subprocess execution 구현
- provider execution 구현
- replay execution 구현
- generated content 생성
- snapshot update
- sync apply/mutation
- rollback execution
- dynamic loading
- registry/discovery
- adapter execution

## Architecture baseline

향후 prototype planning은 다음 baseline을 따라야 한다.

1. 모든 execution-like path는 explicit opt-in이어야 한다.
2. 기본 runtime은 계속 read-only여야 한다.
3. 실행 대상은 repository root가 아니라 isolated temp root를 사용해야 한다.
4. input bundle은 명시적이어야 하며 implicit discovery를 금지해야 한다.
5. output은 JSON evidence와 hash/provenance 중심이어야 한다.
6. output success는 write authorization이 아니어야 한다.
7. sandbox/provider/replay execution facts는 envelope metadata에 숨지 않고 드러나야 한다.
8. failure는 fail-closed여야 한다.

## No-write verification strategy

Prototype planning은 다음 no-write verification strategy를 포함해야 한다.

- protected roots를 명시한다.
- source, target, manifest, snapshot, fixture roots를 보호 대상으로 취급한다.
- 실행 전 protected roots의 hash/metadata snapshot을 만든다.
- 실행 후 protected roots의 hash/metadata snapshot을 비교한다.
- temp root 밖 unexpected output을 violation으로 분류한다.
- temp root cleanup 여부를 evidence로 남긴다.
- mutation이 감지되면 `sandbox-filesystem-violation` 또는 future equivalent failure code로 fail closed한다.

승인 조건:

- no-write evidence가 없으면 prototype planning은 execution prototype을 허용하면 안 된다.
- no-write evidence validation은 sync apply authorization이 아니다.

## Network isolation strategy

Prototype planning은 network isolation을 다음 기준으로 다뤄야 한다.

- v0 prototype은 network disabled를 기본값으로 한다.
- network policy는 provider capability와 sandbox policy에 명시되어야 한다.
- execution result/trace evidence는 `network_disabled: true`를 보존해야 한다.
- network attempt detection 또는 OS/container-level isolation strategy를 명시해야 한다.
- external model/API provider는 별도 policy 없이는 허용하지 않는다.

승인 조건:

- network isolation을 강제할 수 없는 prototype은 실행 계획으로 승격될 수 없다.

## Sandbox/process boundary

Prototype planning은 subprocess sandbox를 첫 architecture candidate로 다룬다.

최소 boundary:

- temporary working directory
- restricted cwd
- sanitized env
- env allowlist
- stdout/stderr byte caps
- max input/output bytes
- timeout
- explicit input bundle
- explicit output JSON
- no dynamic plugin loading
- no implicit provider discovery
- no target writes

금지:

- repository root를 cwd로 사용
- inherited secrets 전달
- broad PATH mutation
- host environment-derived output-affecting config
- temp root 밖 output write
- symlink traversal 허용

## Provider execution boundary

Prototype planning은 provider execution을 바로 구현하지 않는다. 대신 다음 조건을 execution 후보의 prerequisite으로 둔다.

- provider capability validation pass
- provider id/version explicit match
- deterministic capable true
- network policy disabled
- no-write capable true
- output-affecting config snapshot
- supported sync mode match
- provider execution trace requirement
- sandbox policy requirement
- sandbox result/trace requirement

Provider output은 read-only comparison input일 뿐이며, sync apply나 mutation을 승인하지 않는다.

## Replay boundary

Prototype planning은 replay execution을 바로 구현하지 않는다. 대신 다음 replay 조건을 설계 입력으로 둔다.

- static replay manifest validation must pass
- fixture-backed comparison remains separate from real provider replay
- same provider version must produce deterministic evidence
- mismatch must fail closed
- retry must not mask nondeterminism
- snapshot auto-update remains forbidden

## Input/output bundle contract

향후 prototype planning은 input/output bundle을 별도 문서로 구체화해야 한다.

Input bundle minimum:

- request_id
- provider capability reference
- sandbox policy reference
- replay/case metadata when applicable
- source refs and hashes
- sync mode
- hash policy
- output-affecting config
- timeout/resource policy

Output bundle minimum:

- request_id
- status
- failure_code
- generated hashes when available
- provenance
- provider execution trace reference
- sandbox result reference
- sandbox trace reference
- no-write evidence
- network-disabled evidence
- mutation_performed

## Envelope v2 requirement

Future execution-like outputs must preserve:

- `sandbox_execution`
- `subprocess_execution`
- `provider_execution`
- `replay_execution`
- `mutation_performed`
- `sandbox_mode`
- `provider_mode`
- `trace_id`
- `request_id`
- `failure_code`

Metadata must accurately describe what happened. It must not imply write authorization.

## Abort and fail-closed semantics

Prototype planning must define abort conditions for:

- invalid provider capability
- invalid sandbox policy
- missing input bundle
- unsafe path
- timeout
- output size limit
- invalid output JSON
- network attempt
- filesystem mutation
- nondeterministic output
- missing trace evidence
- mismatch between sandbox result and sandbox trace evidence

Abort must not be retried automatically when retry could mask nondeterminism or isolation failure.

## Required promotions before implementation

Before any execution prototype implementation, the following must be promoted into the smallest relevant runtime authority:

- execution command boundary
- sandbox launcher boundary
- no-write verification boundary
- network isolation boundary
- provider execution boundary
- replay execution boundary
- output/envelope metadata boundary
- hard prohibitions and fail-closed semantics

Promotion target may be `.ai/rules/operations/validation.rules.md`, `.ai/rules/operations/sync.rules.md`, a future provider/sandbox operation rule, or an active normative spec. This approval plan alone is not enough.

## Hard prohibitions

Until a later explicit implementation task is approved, the following remain forbidden:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation
- rollback execution
- dynamic loading
- registry/discovery
- adapter execution
- manifest persistence
- transaction log persistence
- marker insertion, repair, delete
- source mutation
- target mutation

## Next allowed task

The next allowed task is design-only execution prototype planning.

That task must still not implement sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply, mutation, dynamic loading, or registry/discovery.
