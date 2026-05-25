# 결정론적 목 제공자 fixture bundle 보고서

> 이 문서는 human context 구현 보고서이다. 런타임 계약의 정본은 `.ai/rules/`이며, 이번 작업은 deterministic mock provider의 fixture-only 계약을 추가했을 뿐 provider execution을 구현하지 않았다.

## 목적

결정론적 목 제공자 경계 계획에 따라 future provider execution 또는 sandbox architecture 이전에 사용할 fixture-only 검증 자산을 추가했다. 이 bundle은 실행 런타임이 아니라 JSON fixture와 구조 검증 테스트만 제공한다.

## 추가한 fixture layout

추가 경로:

```text
tests/fixtures/providers/mock/
  mock_provider_index.json
  inputs/
  outputs/
  snapshots/
  expected/
```

추가한 주요 fixture:

- valid input/output cases
  - deterministic available output
  - deterministic unavailable output
  - managed-block output
  - whole-file output
- invalid output cases
  - missing provenance
  - hash mismatch
  - nondeterministic duplicate output
  - invalid provider version
  - unavailable output with generated hash
  - missing no_write_confirmed
- provider snapshot
  - `aios.mock_provider_snapshot.v0`

## 계약 테스트

추가 테스트:

- `tests/test_deterministic_mock_provider_fixtures.py`

검증 내용:

- fixture inventory consistency
- valid fixtures structural assertions
- invalid fixtures expected issue assertions
- deterministic metadata required
- unavailable output semantics
- generated hash consistency
- provenance presence and source order preservation
- no normalization assumptions
- `no_write_confirmed` requirement
- non-execution contract flags in fixture index

## 유지한 경계

이번 작업은 다음을 구현하지 않았다.

- provider execution
- sandbox execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content creation
- snapshot update
- replay execution
- sync apply
- mutation
- `.ai/rules` 변경

Fixture index의 contract flags는 다음을 명시한다.

- `provider_execution: false`
- `sandbox_execution: false`
- `dynamic_loading: false`
- `network_access: false`
- `generated_content_creation: false`
- `mutation_performed: false`

## 검증

수행한 검증:

- `python -m pytest tests/test_deterministic_mock_provider_fixtures.py`

나머지 회귀 검증은 최종 validation 단계에서 수행한다.

## 다음 권장 작업

다음 안전한 작업은 execution trace schema design이다. 목 제공자 helper나 sandbox execution을 구현하기 전, trace id, provider identity, input/output hash, duration, no-write confirmation, failure code가 어떤 출력 모델에 보존될지 먼저 고정해야 한다.

Provider execution, sandbox execution, adapter execution, generated content creation, replay execution, snapshot update, sync apply, mutation은 계속 차단한다.
