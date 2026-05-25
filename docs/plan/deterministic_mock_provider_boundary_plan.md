# 결정론적 목 제공자 경계 계획

> 이 문서는 human context 계획 문서이다. 런타임 계약의 정본은 `.ai/rules/`이며, 이 계획은 future real preview/replay provider execution 이전에 필요한 deterministic mock provider 경계를 정의한다.

## 목적

결정론적 목 제공자는 실제 생성기나 어댑터가 아니다. 목적은 future provider execution과 sandbox architecture를 설계하기 전에, 실행처럼 보이는 경로를 안전한 fixture-backed simulation으로 제한하고 계약 검증만 수행할 수 있는 경계를 정하는 것이다.

목 제공자는 다음을 검증하기 위한 중간 단계다.

- replay-safe deterministic execution simulation
- provider input/output contract 검증
- replay comparison plumbing 검증
- provenance와 hash preservation 검증
- execution trace와 no-write metadata 설계 검증

목 제공자는 real generation, model execution, adapter execution, sync apply authorization을 제공하지 않는다.

## 범위

포함한다.

- deterministic mock provider의 목적과 경계
- 허용/금지 동작
- input/output contract
- deterministic guarantee
- observability requirement
- isolation expectation
- future implementation prerequisite
- 다음 안전 작업 추천

제외한다.

- runtime code 구현
- provider execution 구현
- sandbox execution 구현
- provider registry/discovery
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply 또는 mutation
- `.ai/rules` 변경

## 목 제공자의 정의

결정론적 목 제공자는 명시된 fixture input을 명시된 fixture output으로 매핑하는 read-only simulation provider다. 실행 인터페이스와 trace, replay comparison, capability declaration을 시험하기 위한 도구일 뿐이며 real provider와 동일하게 취급해서는 안 된다.

핵심 정의:

- fixture-backed output만 반환한다.
- 동일 input과 동일 provider version에서 byte-identical output을 반환해야 한다.
- output hash, provenance, provider metadata, unavailable reason을 정확히 보존해야 한다.
- provider capability declaration을 참조할 수 있지만, capability validation이 execution authorization으로 승격되지는 않는다.
- 목 제공자 성공은 sandbox approval이나 real provider approval이 아니다.

## 허용 동작

결정론적 목 제공자에 허용되는 동작은 다음으로 제한한다.

- fixture-backed deterministic output 반환
- in-memory read-only execution simulation
- replayable output metadata 생성
- exact provenance preservation
- exact generated hash preservation
- explicit unavailable reason 반환
- provider id/version과 capability declaration 확인
- deterministic execution metadata 생성
- no-write confirmation metadata 생성

목 제공자는 target/source file을 직접 읽거나 쓰지 않는 것을 기본으로 한다. 필요한 fixture는 테스트 harness나 future caller가 이미 로드해 전달하는 방식이 가장 안전하다.

## 금지 동작

다음 동작은 결정론적 목 제공자 경계 안에서도 금지한다.

- model/API call
- network access
- filesystem write
- snapshot update
- manifest persistence
- transaction log write
- sync apply 또는 mutation
- marker insertion, repair, deletion
- adapter execution
- dynamic plugin loading
- provider registry/discovery
- nondeterministic randomness
- wall-clock time을 output-affecting value로 사용
- environment variable을 output-affecting value로 사용
- line ending 또는 whitespace의 hidden normalization
- retry로 nondeterminism을 숨기는 행위

## 입력 계약

Future deterministic mock provider input은 다음 요소를 명시해야 한다.

| Field | Purpose |
| --- | --- |
| `provider_capability` | provider id/version, deterministic flag, no-write/network/resource policy 확인 |
| `replay_manifest` | case id, input fixture, expected output fixture, replay dimension 확인 |
| `input_fixture` | `aios.real_preview.input.v0` 계열의 fixture-backed input |
| `provider_snapshot` | provider metadata와 output-affecting config의 고정 기준 |
| `deterministic_config` | normalization none, retry disabled, network disabled 등 execution simulation config |
| `case_id` | replay comparison과 trace correlation 기준 |
| `hash_policy` | `aios.hash_policy.v0`와의 호환성 확인 |

입력은 명시적이어야 하며 default discovery에 의존하지 않는다.

## 출력 계약

Future deterministic mock provider output은 기존 real preview output 계열과 호환되어야 한다.

필수 출력 정보:

- `preview_available`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `provenance`
- `unavailable_reason`
- `provider_metadata`
- `replay_metadata`
- `deterministic_execution`
- `no_write_confirmed`
- `input_hash`
- `output_hash`
- `duration_ms`

`preview_available: false`인 경우 generated hash fields는 null이어야 하며, unavailable reason은 명시되어야 한다.

## 결정론 보장

결정론적 목 제공자는 다음 보장을 만족해야 한다.

- 동일 input, 동일 provider id, 동일 provider version, 동일 output-affecting config는 byte-identical output을 만든다.
- hash, provenance, provider metadata, unavailable reason은 exact equality로 비교한다.
- list order는 의미가 있으며 source path order도 보존한다.
- null과 missing field는 같지 않다.
- string `"true"`와 boolean `true`는 같지 않다.
- line ending, trailing newline, BOM은 자동 정규화하지 않는다.
- replay mismatch는 retry하지 않고 mismatch 또는 `nondeterministic-output`으로 분류한다.

목 제공자도 deterministic gate를 통과하지 못하면 future execution boundary의 후보가 될 수 없다.

## Observability 요구사항

목 제공자 simulation은 future event/trace model과 envelope metadata를 검증하기 위해 최소한 다음 정보를 남겨야 한다.

- execution trace id
- provider id/version
- mock provider mode
- deterministic execution flag
- input hash
- output hash
- generated hashes
- duration
- unavailable reason
- no-write confirmation
- network disabled confirmation
- mutation_performed: false

이 정보는 provider execution을 승인하기 위한 증거가 아니라, future execution boundary 설계가 필요한 정보를 빠뜨리지 않았는지 확인하기 위한 것이다.

## 격리 기대사항

초기 목 제공자는 pure in-memory execution을 기본으로 한다.

권장 경계:

- caller가 fixture data를 dict로 전달한다.
- provider는 external file IO를 수행하지 않는다.
- provider는 environment를 읽거나 변경하지 않는다.
- provider는 network를 사용하지 않는다.
- provider는 dynamic import/plugin loading을 하지 않는다.
- provider는 target/source/manifest/snapshot path에 쓰지 않는다.

Subprocess sandbox는 미래 선택지다. 목 제공자 boundary가 안정된 뒤에만 별도 architecture plan에서 다룬다.

## Future compatibility boundary

다음 경계를 명확히 유지한다.

- deterministic mock provider는 real provider가 아니다.
- mock execution success는 real execution authorization이 아니다.
- deterministic replay success는 sync apply authorization이 아니다.
- provider capability validation은 sandbox approval이 아니다.
- fixture-backed output은 generated content creation이 아니다.
- no-write confirmation metadata는 mutation safety 전체를 대체하지 않는다.

## Future implementation prerequisites

목 제공자 helper 또는 execution harness를 구현하기 전에 다음 산출물이 필요하다.

1. deterministic mock provider fixture bundle
2. execution trace schema
3. provider execution envelope metadata contract
4. no-write verification checklist
5. sandbox readiness plan
6. mock provider output contract tests
7. runtime rule promotion decision

## 다음 권장 작업

다음 작업은 real provider execution이 아니라 deterministic mock fixture bundle이 적절하다.

권장 순서:

1. Deterministic mock provider fixture bundle
2. Execution trace schema design
3. Subprocess sandbox architecture plan

Provider execution, sandbox execution, adapter execution, generated content creation, snapshot update, replay execution, sync apply, mutation은 위 경계가 안정될 때까지 계속 차단한다.
