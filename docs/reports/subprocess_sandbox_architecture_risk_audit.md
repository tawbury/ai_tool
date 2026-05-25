# Subprocess Sandbox Architecture Risk Audit

> 이 문서는 design-only 감사 보고서이다. Provider execution, sandbox execution, replay execution, generated content, sync apply, mutation을 구현하거나 승인하지 않는다.

## 목적

Future provider-like execution을 검토하기 전에 subprocess sandbox가 왜 fixture/static validation보다 높은 위험 단계인지 감사하고, 실제 실행을 허용하기 전에 필요한 안전 요구사항을 정리한다.

## 현재 상태

현재 `.ai OS`는 다음까지만 지원한다.

- provider capability static validation
- provider execution trace static validation
- fixture-backed replay comparison
- deterministic mock provider fixtures
- provider execution trace fixtures

다음은 계속 금지되어 있다.

- provider execution
- sandbox execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- replay execution
- sync apply/mutation

## 별도 위험 단계인 이유

Subprocess sandbox는 fixture/mock validation과 다르다. Fixture validation은 이미 존재하는 JSON을 읽고 비교하지만, subprocess sandbox는 별도 process를 시작하고 code path를 실행한다. 이 순간부터 다음 위험이 생긴다.

- 파일 시스템 write 시도
- source/target/manifest/snapshot mutation
- 네트워크 접근
- 환경 변수와 secret 노출
- host-specific path leakage
- dynamic import 또는 plugin loading
- nondeterministic output
- stdout/stderr를 통한 대량 출력 또는 민감 정보 노출
- timeout/resource exhaustion
- 실행 성공을 sync apply authorization으로 오해할 위험

따라서 sandbox design은 가능하지만, sandbox launcher 구현이나 provider execution 구현은 별도 readiness gate 전까지 금지해야 한다.

## Architecture Options 평가

| Option | IO containment | Network containment | Environment leakage | Determinism | Observability | Portability | Complexity | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No sandbox / in-process only | 낮음 | 낮음 | 높음 | 낮음 | 중간 | 높음 | 낮음 | real execution에는 부적합 |
| Python subprocess with restricted cwd/env | 중간 | 낮음-중간 | 중간 | 중간 | 높음 | 높음 | 중간 | v0 설계 기준 후보, 단 network/file write 검증 필요 |
| Subprocess with temporary working directory | 중간-높음 | 낮음-중간 | 중간 | 중간 | 높음 | 높음 | 중간 | v0 후보, explicit input/output bundle과 결합 필요 |
| OS/container sandbox | 높음 | 높음 | 낮음 | 중간 | 중간-높음 | 낮음-중간 | 높음 | future option, 초기 portable v0에는 과함 |

권장 방향은 subprocess with temporary working directory를 기준으로 요구사항을 설계하되, 이것만으로 network 차단과 write 차단이 완전하다고 가정하지 않는 것이다.

## 주요 위험

### Filesystem risk

Subprocess는 cwd를 제한해도 absolute path, parent traversal, symlink, inherited file descriptor, environment path를 통해 의도하지 않은 파일에 접근할 수 있다.

필요한 완화:

- explicit input bundle만 전달
- restricted cwd
- temp working directory
- allowed read roots 명시
- output path allowlist
- pre/post hash scan
- symlink policy
- no-write verification

### Network risk

Python subprocess만으로는 OS-level network 차단이 보장되지 않는다.

필요한 완화:

- v0 subprocess sandbox contract에서 network disabled를 요구
- network access를 금지하는 provider capability flag 확인
- future OS/container sandbox 또는 process policy 필요성 명시
- network attempt failure code 정의

### Environment leakage

기본 environment를 상속하면 credentials, API keys, host path, locale/timezone이 output에 영향을 줄 수 있다.

필요한 완화:

- sanitized env
- allowlist env only
- no secret propagation
- deterministic locale/timezone policy
- output-affecting config snapshot

### Determinism risk

Subprocess는 wall-clock, randomness, dependency version, host path, environment drift의 영향을 받을 수 있다.

필요한 완화:

- deterministic capability validation
- provider version pinning
- output-affecting config
- retry prohibition for nondeterminism
- replay comparison gate

### Observability risk

실패를 단순 nonzero exit로만 처리하면 왜 실패했는지 알 수 없다.

필요한 완화:

- provider execution trace metadata
- duration
- input/output hashes
- provider id/version
- failure/unavailable reason
- no-write/network confirmation

## Failure Codes

Sandbox 관련 failure code 후보:

- `sandbox-timeout`
- `sandbox-nonzero-exit`
- `sandbox-output-invalid`
- `sandbox-resource-limit`
- `sandbox-network-attempt`
- `sandbox-filesystem-violation`
- `sandbox-env-access-violation`
- `sandbox-nondeterministic-output`

이 code들은 provider execution trace failure code와 별도 namespace로 유지하거나, future trace schema 확장 시 명시적으로 mapping해야 한다.

## Existing Artifacts와의 관계

- Provider capability validation은 sandbox execution authorization이 아니다. 다만 deterministic, no-write, network disabled, resource policy의 사전 조건을 검증한다.
- Provider execution trace validation은 실행 결과의 정적 증거 검증이다. Trace success는 sandbox approval이 아니다.
- Deterministic mock provider fixtures는 execution-like contract를 fixture로 검증한다. Real subprocess execution을 대체하지 않는다.
- Replay comparison은 fixture-backed 비교만 수행한다. Provider output replay execution은 아직 없다.
- Envelope v2는 future sandbox metadata를 담을 수 있지만, metadata 존재가 execution authorization은 아니다.

## Parallelization 평가

병렬 설계 가능:

- sandbox fixture bundle design
- sandbox trace fixture design
- sandbox validator helper design
- envelope metadata design

병렬 구현 가능하지만 execution은 아님:

- fixture-only sandbox policy JSON
- static validator helper
- output contract tests for static validation

순차 유지 필요:

1. sandbox policy/schema design
2. fixture bundle
3. static validator helper
4. output contract tests
5. runtime rule promotion audit
6. sandbox launcher design
7. sandbox launcher implementation 여부 재감사

Sandbox launcher, provider execution, replay execution은 위 gate가 끝나기 전까지 구현하면 안 된다.

## 결론

Subprocess sandbox architecture planning은 지금 design-only track으로 진행할 수 있다. 그러나 subprocess sandbox implementation은 아직 이르다. 다음 안전한 단계는 sandbox architecture plan을 바탕으로 sandbox fixture/schema contract를 설계하는 것이다.
