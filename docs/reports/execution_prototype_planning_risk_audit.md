# Execution prototype planning 위험 감사

> 이 보고서는 human context이다. 본 작업은 design-only prototype planning 위험을 감사하며 런타임 코드, `.ai/rules`, 실행 구현을 변경하지 않는다.

## 목적

`docs/plan/execution_prototype_planning.md`가 실행 구현으로 오해되지 않도록 위험을 식별하고, 후속 implementation readiness gate를 명확히 한다.

## 핵심 판단

판단: **execution prototype planning은 완료되었지만 implementation readiness는 아직 아니다.**

다음 단계는 prototype request/output fixture contract, no-write harness design, network isolation decision 같은 design-only 작업이어야 한다. Sandbox launcher, subprocess execution, provider execution, replay execution 구현은 여전히 금지된다.

## 주요 위험

### Prototype planning을 implementation approval로 오해

위험:

- planning 문서가 생겼다는 이유로 `sandbox-prototype` 같은 명령 구현을 바로 시작할 수 있다.

완화:

- planning 문서에 command boundary 후보가 구현 승인된 명령이 아님을 명시했다.
- implementation 전 rule/spec promotion과 implementation readiness audit를 요구했다.

### No-write harness 미구현 상태

위험:

- no-write evidence model만으로 실제 filesystem safety를 보장한다고 오해할 수 있다.

완화:

- protected roots pre/post snapshot, unexpected output detection, temp cleanup verification을 별도 harness requirement로 남겼다.
- no-write harness design을 후속 design-only 작업으로 분리했다.

### Network isolation 미구현 상태

위험:

- `network_disabled: true` metadata만으로 network access가 차단되었다고 믿을 수 있다.

완화:

- OS/container isolation 또는 network attempt detection strategy를 후속 decision으로 요구했다.
- external model/API provider를 별도 policy 전까지 금지했다.

### Trace evidence와 execution evidence 혼동

위험:

- provider trace, sandbox result, sandbox trace validation이 실제 실행 안전성을 증명한다고 오해할 수 있다.

완화:

- trace/evidence harness는 static validators로 재검증 가능한 output evidence requirement로만 정의했다.
- evidence validation success는 execution safety proof가 아니라고 경계를 유지했다.

### Replay determinism masking

위험:

- nondeterministic output을 retry로 숨길 수 있다.

완화:

- abort condition에서 nondeterministic output을 fail-closed로 정의했다.
- 자동 retry 금지와 별도 nondeterminism masking risk audit 필요성을 명시했다.

### Generated content persistence 유입

위험:

- prototype output bundle이 raw generated content를 저장하거나 target write로 이어질 수 있다.

완화:

- output bundle은 hash/provenance/evidence 중심으로 제한했다.
- raw generated content는 v0 prototype planning에서 제외했다.
- generated hashes는 write authorization이 아니라고 명시했다.

### Dynamic loading 및 discovery 유입

위험:

- provider discovery나 plugin loading이 prototype 편의를 위해 추가될 수 있다.

완화:

- input bundle은 explicit refs만 허용한다.
- dynamic plugin loading, provider registry/discovery, activation-driven execution selection을 금지했다.

## 남은 design-only 작업

다음 작업은 implementation 전 design-only로 진행할 수 있다.

- sandbox prototype request fixture contract design
- prototype output bundle fixture contract design
- no-write verification harness design
- network isolation enforcement decision audit
- timeout/resource harness design
- execution boundary rule/spec promotion audit
- provider/sandbox-specific operation rule 필요성 감사

## 반드시 순차로 남겨야 할 작업

다음 순서는 건너뛰면 안 된다.

1. Prototype request/output fixture contract design
2. Harness design and risk audits
3. Execution boundary rule/spec promotion audit
4. Runtime authority promotion if approved
5. Implementation readiness audit
6. Only then possible prototype implementation task

## 계속 차단되는 작업

다음은 계속 차단된다.

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

## 결론

Execution prototype planning은 future implementation을 위한 경계와 gate를 충분히 정리했다. 그러나 no-write harness, network isolation, command boundary, request/output schema, runtime authority promotion, implementation readiness audit가 아직 없으므로 코드 구현은 시작하면 안 된다.
