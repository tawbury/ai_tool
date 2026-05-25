# Sandbox Policy Fixture Risk Audit

> 이 문서는 design-only 위험 감사 보고서이다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Sandbox policy fixtures를 만들기 전에 fixture 계약 자체가 execution authorization으로 오해되거나, 잘못된 policy가 future sandbox 설계를 느슨하게 만들 위험을 감사한다.

## 주요 위험

### Fixture를 실행 승인으로 오해할 위험

Sandbox policy fixture는 정적 계약 예시일 뿐이다. Valid fixture는 subprocess를 실행해도 된다는 뜻이 아니다.

완화:

- fixture 문서와 테스트 이름에 fixture-only/static-only 경계를 명시한다.
- runtime rule promotion 전까지 sandbox policy는 human context로 남긴다.
- valid fixture success와 sandbox launcher approval을 분리한다.

### Python subprocess containment 과신

Python subprocess와 temporary cwd만으로 network, filesystem, environment isolation이 완전해지지 않는다.

완화:

- policy field에 no-write, network disabled, env allowlist를 요구한다.
- no-write verification evidence를 별도 모델로 둔다.
- OS/container sandbox는 future option으로 남긴다.
- network blocking은 v0에서 evidence와 policy로만 다루고 실제 enforcement는 별도 설계로 남긴다.

### Path policy 누락

Relative path, absolute path, parent traversal, duplicate roots, overlapping roots가 명확하지 않으면 future sandbox가 의도하지 않은 파일을 읽거나 쓸 수 있다.

완화:

- absolute paths reject
- parent traversal reject
- duplicate roots error
- overlapping roots edge/warning candidate
- output roots는 sandbox temp token 중심으로 제한

### Environment leakage

환경 변수를 넓게 허용하면 secret 노출과 nondeterministic output이 발생할 수 있다.

완화:

- env policy는 allowlist만 허용한다.
- wildcard env rule은 invalid fixture로 둔다.
- secret-looking prefixes는 forbidden list로 명시한다.
- environment-derived output-affecting config는 별도 declaration 없이는 금지한다.

### Resource policy ambiguity

Timeout과 byte limit의 단위나 범위가 모호하면 test와 runtime behavior가 달라질 수 있다.

완화:

- `timeout_ms`, `max_input_bytes`, `max_output_bytes`, `stdout_limit_bytes`, `stderr_limit_bytes`를 positive integer로 고정한다.
- zero timeout은 invalid로 둔다.
- oversized limits는 edge fixture로 분리한다.

### No-write evidence 불충분

`no_write_required: true`만으로는 mutation이 없었다는 증거가 되지 않는다.

완화:

- pre/post protected root hashes를 future evidence model에 포함한다.
- temp root cleanup evidence를 요구한다.
- unexpected output detection을 포함한다.
- mutation detection은 blocking failure로 분류한다.

### Failure code 확산

Sandbox failure code가 provider trace failure code와 섞이면 결과 해석이 모호해질 수 있다.

완화:

- sandbox failure code namespace를 `sandbox-*`로 유지한다.
- provider execution trace schema와 mapping은 별도 future plan에서 다룬다.
- envelope v2 metadata는 evidence로만 취급한다.

## Invalid Fixture Risk Cases

필수 invalid cases:

- unsupported sandbox mode
- zero timeout
- absolute read root
- parent traversal output root
- duplicate read root
- network enabled
- wildcard env rule
- malformed filesystem policy
- null policy objects
- output root pointing at repository target

## Edge Case Risk Cases

필수 edge cases:

- empty allowed read roots
- max limit boundary
- overlapping roots
- minimal env allowlist
- sandbox temp token output root

Edge fixture는 future validator가 fail, warn, pass 중 무엇을 선택해야 하는지 명확히 하기 위한 것이다. Edge가 runtime approval을 의미하지 않는다.

## Relationship Risk

Provider capability validation:

- risk: capability valid + sandbox policy valid를 execution 승인으로 오해
- mitigation: execution readiness audit 전까지 실행 금지

Provider execution trace validation:

- risk: trace valid를 sandbox success로 오해
- mitigation: trace는 evidence validation이며 sandbox approval이 아님을 유지

Replay comparison:

- risk: sandbox policy를 replay execution으로 연결
- mitigation: replay comparison remains fixture-backed

Envelope v2:

- risk: sandbox metadata가 execution authorization처럼 보임
- mitigation: `sandbox_execution`과 `provider_execution`은 false until separately approved

## Parallelization Evaluation

병렬 진행 가능:

- sandbox policy fixtures
- sandbox trace fixture contract
- sandbox execution result fixture contract
- envelope metadata design

번들 가능:

- fixture-only JSON creation
- contract tests
- fixture bundle report

순차 유지 필요:

1. fixture contract before fixtures
2. fixtures before validator helper
3. validator helper before validate integration
4. output contract tests before rule promotion
5. rule promotion before execution readiness audit
6. readiness audit before sandbox launcher implementation

## 결론

Sandbox policy fixture contract는 지금 설계해도 안전하다. 다음 작업은 fixture-only bundle이어야 하며, sandbox launcher나 provider execution 구현은 계속 금지해야 한다.
