# 제공자 격리 요구사항 계획

> 이 문서는 human context용 계획 문서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 계획은 future real preview/replay provider execution을 설계하기 전 필요한 격리 게이트를 정의한다.

## 목적

실제 preview/replay provider는 fixture-backed comparison과 달리 코드를 실행한다. 이 계획은 provider 실행을 바로 구현하지 않고, 실행을 허용하기 전에 필요한 capability schema, sandbox policy, deterministic replay, no-write verification, observability 요구사항을 정리한다.

## 범위

포함:

- provider capability contract 후보
- 실행 경계 후보
- sandbox 요구사항
- 결정성 검증 요구사항
- no-mutation 검증 요구사항
- failure/unavailable semantics
- future validation/readiness gates

제외:

- provider runtime 구현
- adapter execution
- generated content creation
- replay CLI
- snapshot update
- sync apply
- 파일 mutation
- `.ai` runtime rule 변경

## 기본 정책

실제 provider 실행은 기본 비활성화 상태여야 한다. 향후 실행이 추가되더라도 다음 조건을 만족해야 한다.

- 명시적 opt-in이어야 한다.
- provider capability가 정적으로 검증되어야 한다.
- sandbox policy가 통과해야 한다.
- 동일 input과 provider version에 대한 deterministic replay가 통과해야 한다.
- provider output은 read-only comparison input으로만 사용되어야 한다.
- drift-stop, marker conflict, source-missing 같은 기존 차단 조건을 우회할 수 없어야 한다.

## Provider Capability Schema Candidate

향후 capability fixture는 다음 형태를 기준으로 설계한다.

```json
{
  "schema_version": "aios.provider_capability.v0",
  "provider_id": "aios.preview.example",
  "provider_version": "0.1.0",
  "deterministic_capable": true,
  "supported_sync_modes": ["whole-file", "managed-block", "mixed-boundary"],
  "hash_policy": "aios.hash_policy.v0",
  "output_affecting_config": {},
  "no_write_capable": true,
  "network_policy": "disabled",
  "timeout_policy": {
    "timeout_ms": 5000
  },
  "resource_policy": {
    "max_input_bytes": 262144,
    "max_output_bytes": 262144
  },
  "allowed_read_roots": [],
  "provenance_required": true
}
```

필수 검증:

- `schema_version`은 지원 버전이어야 한다.
- `provider_id`와 `provider_version`은 replay manifest/provider snapshot과 일치해야 한다.
- `deterministic_capable`이 false이면 real replay comparison에는 사용할 수 없다.
- `network_policy`는 v0에서 `disabled`만 허용한다.
- `no_write_capable`은 true여야 한다.
- `hash_policy`는 Phase 7 v0 observed UTF-8 bytes policy와 호환되어야 한다.
- `output_affecting_config`는 replay snapshot에 포함되어야 한다.

## 실행 경계 계획

### 1단계: Capability fixture only

Provider 실행 없이 capability schema와 fixture tests를 먼저 만든다. 이 단계는 현재 replay fixture/static validation 흐름과 가장 잘 맞는다.

목표:

- provider capability fixture layout 확정
- schema validation tests
- unsafe capability rejection tests
- docs/index 갱신

### 2단계: Deterministic mock provider boundary

실제 adapter나 생성 로직이 아니라 고정 입력을 결정적으로 변환하는 mock provider boundary를 설계한다.

목표:

- provider execution request/response model 확정
- no-write interface 확인
- deterministic replay harness 설계
- failure/unavailable output mapping 확인

### 3단계: Subprocess sandbox architecture

첫 real execution 후보는 subprocess sandbox다. in-process provider는 권한 공유 위험이 크고, container는 초기 복잡도가 높다.

목표:

- explicit cwd
- read-only roots
- temp scratch policy
- env whitelist
- network disabled by default
- timeout
- output size cap
- stdout/stderr capture
- no inherited secrets

### 4단계: Real provider implementation gate

위 세 단계와 runtime rule promotion이 끝난 뒤에만 real provider 구현 여부를 다시 판단한다.

## Sandbox Requirements

향후 sandbox 정책은 다음 요구사항을 포함해야 한다.

- provider는 명시된 input만 읽어야 한다.
- source root는 read-only로만 접근해야 한다.
- target root는 기본적으로 read 금지 또는 read-only로 제한해야 한다.
- manifest, snapshot, transaction path는 write 금지다.
- network는 기본 금지다.
- environment variable은 allowlist 방식으로 전달한다.
- provider output은 stdout 또는 explicit result file 중 하나로 제한한다.
- result file을 허용하더라도 temp scratch 내부에서만 쓰고 runtime target에는 쓰지 않는다.
- timeout과 output size limit 초과는 unavailable/failure로 처리한다.
- sandbox 종료 후 pre/post mutation check를 수행한다.

## Determinism Gates

Provider는 다음 replay gate를 통과해야 한다.

- 동일 input fixture와 동일 provider version에서 generated hash가 동일하다.
- provenance가 동일하다.
- provider metadata가 동일하다.
- unavailable reason이 동일하다.
- LF/CRLF 차이를 조용히 정규화하지 않는다.
- trailing newline 차이를 보존한다.
- BOM byte policy를 hash policy와 일치시킨다.
- wall-clock, random, host path, environment drift가 output에 숨어 들어가지 않는다.

Replay mismatch는 retry로 덮지 않고 `nondeterministic-output`으로 분류한다.

## No-Mutation Verification

Provider 실행 설계에는 no-mutation 검증이 포함되어야 한다.

- 실행 전후 source, target, manifest, snapshot 후보 path의 hash를 비교한다.
- marker content가 변경되지 않았는지 확인한다.
- transaction log가 생성되지 않았는지 확인한다.
- snapshot file mtime/hash가 바뀌지 않았는지 확인한다.
- temp scratch 외부에 새 파일이 생기면 `provider-isolation-violation`으로 처리한다.

No-mutation verification은 sync apply safety를 대체하지 않는다. 이는 provider preview/replay 실행이 read-only였는지 확인하는 별도 증거다.

## Output and Failure Contract

Provider output은 기존 `aios.real_preview.output.v0` 계열과 호환되어야 한다.

필수 원칙:

- generated hash가 있더라도 write authorization이 아니다.
- preview unavailable은 update candidate를 만들지 않는다.
- provider failure는 drift-stop, marker conflict, source-missing을 우회하지 않는다.
- provider output이 invalid하면 `provider-output-invalid`로 처리한다.
- isolation violation은 blocking failure로 처리한다.

권장 unavailable/failure code:

- `provider-timeout`
- `nondeterministic-output`
- `provider-execution-disabled`
- `provider-isolation-violation`
- `provider-capability-missing`
- `provider-output-invalid`
- `provider-network-disabled`
- `provider-resource-limit`

## Observability Mapping

향후 native output, envelope v2, future event model에는 다음 정보를 보존해야 한다.

- provider_id
- provider_version
- isolation_mode
- network_policy
- timeout_ms
- duration_ms
- input hashes
- generated output hashes
- unavailable_reason
- provider_output_schema_version
- output_affecting_config summary
- mutation_performed: false
- no_write_verified: true 또는 false

## Readiness Checklist

Provider 실행 구현 전에 다음 항목이 완료되어야 한다.

| Gate | Required before execution |
| --- | --- |
| Provider capability schema | Yes |
| Capability fixture tests | Yes |
| Sandbox policy | Yes |
| Deterministic mock provider boundary | Yes |
| Replay determinism tests | Yes |
| Provider output contract tests | Yes |
| No-mutation verification plan | Yes |
| Failure/unavailable contract | Yes |
| Observability mapping | Yes |
| Runtime rule promotion | Yes |

## 다음 작업 제안

권장 다음 작업은 provider 실행 구현이 아니다.

1. Provider capability schema fixture contract 작성
2. Deterministic mock provider boundary 설계
3. Subprocess sandbox architecture plan 작성

이 세 작업이 끝나기 전까지 real provider execution, adapter execution, generated content creation, snapshot update, sync apply, mutation은 계속 차단한다.
