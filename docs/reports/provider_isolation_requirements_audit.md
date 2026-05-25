# 제공자 격리 요구사항 감사

> 이 문서는 human context용 감사 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 향후 실제 preview/replay provider 실행을 설계하기 전 필요한 격리 요구사항과 위험 경계를 정리한다.

## 목적

현재 `.ai OS`는 fixture 기반 replay 비교까지만 지원한다. `aios validate <replay-manifest.json> --replay-compare fixture`는 정적 JSON fixture를 서로 비교할 뿐 provider 코드, adapter, 생성 로직, 네트워크, 파일 쓰기를 실행하지 않는다.

실제 provider 실행은 이 범위를 넘어서는 새 위험 계층이다. 따라서 provider 실행을 설계하거나 구현하기 전에 실행 격리, 결정성, 관측성, 금지 동작, 실패 의미를 별도 게이트로 정의해야 한다.

## 현재 기준선

| 항목 | 현재 상태 |
| --- | --- |
| Replay manifest static validation | 구현 및 runtime rule 승격 완료 |
| Fixture-backed replay comparison | opt-in 구현 및 output contract 안정화 완료 |
| Real provider execution | 미구현, 금지 |
| Adapter execution | 미구현, 금지 |
| Generated content creation | 미구현, 금지 |
| Snapshot update | 미구현, 금지 |
| Replay CLI | 미구현 |
| Sync apply / mutation | 차단 |

## 새 위험 계층인 이유

Fixture 기반 비교는 이미 존재하는 JSON 파일을 읽고 정적 필드를 비교한다. 반면 실제 provider 실행은 다음 위험을 추가한다.

- 실행 가능한 코드가 입력을 해석하고 출력을 생성한다.
- provider 의존성, 환경 변수, 시간, 랜덤 값, 플랫폼 차이가 결과에 영향을 줄 수 있다.
- provider가 의도하지 않게 source, target, manifest, snapshot, transaction 파일을 쓸 수 있다.
- provider가 네트워크나 외부 모델/API를 호출하면 재현성과 보안 경계가 약해진다.
- 생성 출력이 preview와 apply의 경계를 혼동하게 만들 수 있다.
- provider failure가 update candidate로 오인되면 false update candidate 위험이 생긴다.
- adapter 실행과 provider 실행의 권한 경계가 섞이면 아직 승인되지 않은 adapter runtime이 우회될 수 있다.

따라서 실제 provider 실행은 fixture 비교의 자연스러운 확장이 아니라 별도 격리 아키텍처가 필요한 단계다.

## Provider Isolation Goals

Provider 실행 설계는 최소한 다음 목표를 만족해야 한다.

- target/source 파일을 변경하지 않는다.
- snapshot을 자동 갱신하지 않는다.
- manifest를 쓰거나 persist하지 않는다.
- transaction log를 쓰지 않는다.
- managed marker를 삽입, 수정, 삭제하지 않는다.
- sync apply를 직접 또는 간접적으로 승인하지 않는다.
- 동일 입력과 동일 provider version에서 결정적 출력을 만든다.
- 시간, 메모리, 출력 크기, 입력 크기에 제한을 둔다.
- provenance를 보존한다.
- provider identity와 output-affecting config를 결과에 남긴다.
- 네트워크 접근은 향후 정책이 명시적으로 허용하기 전까지 금지한다.
- provider unavailable/failure는 update authorization이 아니라 비교 불가 상태로 분류한다.

## 실행 경계 옵션 평가

| 옵션 | 결정성 위험 | IO 위험 | 네트워크 위험 | 의존성 위험 | 관측성 | 테스트성 | 복잡도 | 평가 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| In-process pure provider | 중간 | 중간 | 중간 | 중간 | 중간 | 높음 | 낮음 | 순수 함수형 mock이나 제한된 provider에는 유용하지만, Python process 권한을 공유하므로 첫 real execution 기본값으로는 약하다. |
| Subprocess sandbox | 중간 | 낮음-중간 | 낮음-중간 | 중간 | 높음 | 중간-높음 | 중간 | 명시적 cwd, env, timeout, read roots, output capture를 줄 수 있어 첫 실제 실행 아키텍처 후보로 가장 현실적이다. |
| Container sandbox | 낮음-중간 | 낮음 | 낮음 | 낮음-중간 | 중간-높음 | 중간 | 높음 | 강한 격리가 필요할 때 적합하지만 개발/CI 복잡도가 높다. v0보다 후속 단계에 적합하다. |
| External model/API provider | 높음 | 낮음 | 높음 | 높음 | 낮음-중간 | 낮음 | 높음 | 네트워크, 모델 버전, nondeterminism 위험이 크므로 별도 정책 전까지 부적합하다. |
| Mock/deterministic provider | 낮음 | 낮음 | 낮음 | 낮음 | 높음 | 높음 | 낮음 | 실제 provider 실행으로 가기 전 첫 executable slice로 가장 안전하다. 단, real provider 안전성을 대체하지는 않는다. |

## 최소 Provider Capability Contract

Provider 실행을 허용하기 전에 다음 capability 정보가 정적으로 검증되어야 한다.

| 필드 | 요구사항 |
| --- | --- |
| `provider_id` | 안정적인 provider 식별자 |
| `provider_version` | output-affecting 변경을 구분하는 version |
| `deterministic_capable` | 결정적 replay 가능 여부 |
| `supported_sync_modes` | `whole-file`, `managed-block`, `mixed-boundary` 중 명시 |
| `hash_policy` | Phase 7 v0 observed UTF-8 bytes 정책과의 호환성 |
| `output_affecting_config` | 출력에 영향을 주는 설정의 고정된 snapshot |
| `no_write_capable` | write 없이 실행 가능한 provider임을 선언 |
| `network_policy` | 기본값 `disabled` |
| `timeout_policy` | 최대 실행 시간 |
| `resource_policy` | 입력/출력/메모리 제한 |
| `allowed_read_roots` | 명시적으로 허용된 read-only path 범위 |
| `provenance_required` | 출력 provenance 필수 여부 |

Capability 선언은 실행 허가가 아니다. 실행 전 validate gate와 sandbox policy가 함께 통과해야 한다.

## Hard Prohibitions

향후 provider 실행 설계에서도 다음은 기본 금지다.

- 파일 쓰기
- manifest mutation 또는 persistence
- snapshot 자동 업데이트
- transaction log 작성
- marker 삽입, 복구, 삭제
- sync apply 실행 또는 apply authorization 생성
- line ending의 조용한 정규화
- hash policy 우회
- 명시적으로 허용되지 않은 네트워크 접근
- 명시된 input/source root 밖의 파일 읽기
- wall-clock, random, ambient environment를 output-affecting input으로 숨기는 행위
- nondeterminism을 숨기기 위한 자동 retry

## Failure and Unavailable Semantics

실제 provider 실행에서 실패는 update candidate가 아니라 unavailable 또는 validation failure로 표현되어야 한다.

| Code | 의미 |
| --- | --- |
| `provider-timeout` | timeout policy를 초과했다. |
| `nondeterministic-output` | 동일 입력 replay에서 출력이 일치하지 않았다. |
| `provider-execution-disabled` | 현재 정책상 provider 실행이 비활성화되어 있다. |
| `provider-isolation-violation` | write, network, path boundary 등 격리 위반이 감지되었다. |
| `provider-capability-missing` | capability contract 필수 필드가 없거나 불충분하다. |
| `provider-output-invalid` | provider output schema, hash, provenance, metadata가 유효하지 않다. |
| `provider-network-disabled` | provider가 금지된 네트워크 접근을 요구하거나 시도했다. |
| `provider-resource-limit` | 입력, 출력, 메모리 등 resource policy를 초과했다. |

## Observability Requirements

Provider 실행을 도입하려면 최소 관측 정보가 결과와 future event model에 남아야 한다.

- provider execution trace identifier
- provider_id와 provider_version
- isolation mode
- network_policy
- timeout_policy와 duration
- input hash 또는 input fixture hash
- output hash
- unavailable reason
- provenance
- output-affecting config summary
- no mutation confirmation
- resource limit result

관측 정보는 provider output을 신뢰하기 위한 증거이며, provider가 write를 하지 않았다는 주장도 결과 metadata에 명시되어야 한다.

## Readiness Gates

실제 provider 실행 구현 전 다음 게이트가 필요하다.

1. Provider capability schema 설계
2. Provider capability fixture contract와 schema tests
3. Sandbox policy 설계
4. Deterministic mock provider boundary 설계
5. Deterministic replay tests
6. Provider output contract tests
7. No-write verification strategy
8. Failure/unavailable output contract
9. Observability/event mapping
10. Runtime governance rule promotion

## 권장 다음 방향

다음 단계는 provider 실행 구현이 아니라 provider isolation architecture와 capability schema를 구체화하는 것이다.

권장 순서:

1. Provider capability schema fixture contract 설계
2. Deterministic mock provider boundary 설계
3. Subprocess sandbox architecture plan 작성

외부 model/API provider와 adapter-backed provider는 이 세 단계와 rule promotion이 끝날 때까지 계속 보류해야 한다.

## 결론

Phase 8 replay comparison runtime v0는 fixture-backed 검증으로 닫을 수 있지만, 실제 provider 실행은 아직 승인할 수 없다. Provider 실행은 새로운 권한, IO, 네트워크, 결정성 위험을 도입하므로 capability schema, sandbox policy, deterministic replay, no-write verification, observability가 먼저 설계되어야 한다.

Mutation/apply는 계속 차단해야 하며, provider preview output은 향후에도 write authorization이 아니라 read-only comparison input으로만 취급해야 한다.
