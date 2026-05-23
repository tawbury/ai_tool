# Generated Preview Fixture Readiness Audit

## 개요

이 문서는 Phase 8 generated preview fixture contract가 provider 구현 전에 충분한 준비 상태인지 감사한다. 현재 단계는 fixture layout과 expected behavior를 문서로 고정하는 것이며, 실제 fixture JSON 파일, provider, adapter execution, sync apply는 구현하지 않는다.

검토 기준은 다음 문서다.

- `docs/plan/generated_preview_contract_plan.md`
- `docs/reports/generated_preview_risk_audit.md`
- `docs/plan/generated_preview_fixture_contract.md`

## Readiness Matrix

| 항목 | 상태 | 판단 |
| --- | --- | --- |
| Fixture layout | ready | `inputs/`, `outputs/`, `expected/` 구조가 정의되었다. |
| Minimum input fixtures | ready | whole-file, managed-block, mixed-boundary, source-missing, marker-invalid, adapter-unavailable, activation-unresolved 입력이 정의되었다. |
| Minimum output fixtures | ready | available whole-file, available managed-block, adapter-unavailable, source-missing, marker-invalid, activation-unresolved 출력이 정의되었다. |
| Expected classification hints | ready | update, skip, drift-stop precedence, marker conflict precedence, unavailable no-update가 정의되었다. |
| Required fields | ready | input, output, expected fixture 필수 필드가 분리되어 정의되었다. |
| Hash validation expectation | ready | `sha256:<lowercase-hex>`와 `sha256` only 정책이 유지된다. |
| Deterministic metadata | ready | available output은 deterministic metadata와 adapter identity를 요구한다. |
| Source provenance | ready | source paths와 source hashes 보존이 요구된다. |
| Unavailable enum | ready | six-state unavailable reason enum이 정의되었다. |
| Read-only invariant | ready | `expected_no_mutation: true`와 no write authorization이 요구된다. |
| Provider implementation | deferred | 이번 작업 범위가 아니다. |
| Runtime integration | deferred | dry-run update candidate extension은 provider contract 이후 단계다. |
| Adapter execution | blocked | adapter generation/execution은 여전히 금지된다. |
| Sync apply/mutation | blocked | mutation readiness gate 전까지 금지된다. |

## Coverage Assessment

### Positive Cases

Positive fixture coverage는 다음 최소 경로를 포함한다.

- whole-file clean input
- managed-block clean input
- mixed-boundary clean input
- preview available whole-file output
- preview available managed-block output
- clean target + generated hash differs -> update candidate
- clean target + generated hash matches -> skip

이 범위는 generated preview가 제공하는 핵심 가치인 clean target update candidate 판단을 검증하기에 충분하다.

### Negative and Unavailable Cases

Negative fixture coverage는 다음 경로를 포함한다.

- source missing
- marker invalid
- adapter unavailable
- activation unresolved
- drifted target precedence
- invalid marker precedence
- preview unavailable no-update

이 범위는 preview가 기존 Phase 7 safety behavior를 우회하지 않는다는 것을 검증하기에 충분하다.

### Remaining Optional Cases

다음 fixture는 나중에 추가할 수 있지만, provider 전 계약 고정의 blocker는 아니다.

- `unsupported-sync-mode`
- `generation-disabled`
- unavailable output with warning severity hint
- multi-source `source_paths`
- deterministic false fixture
- hash format invalid fixture
- provenance missing fixture
- envelope v2 preview detail expected fixture

## Fixture Implementation Risks

### Fixture Sprawl

초기부터 너무 많은 fixture를 만들면 provider 구현 전 유지보수 비용이 커질 수 있다.

완화:

- minimum fixture set부터 시작한다.
- optional cases는 schema test가 필요해질 때 추가한다.

### Placeholder Hash Drift

문서나 fixture에 placeholder hash를 남기면 future schema test가 실제 hash인지 placeholder인지 구분하기 어렵다.

완화:

- 실제 JSON fixture를 만들 때는 `sha256:<lowercase-hex>` 형식의 deterministic test hash를 사용한다.
- `<source>` 같은 placeholder는 문서 예시에서만 사용한다.

### Expected Classification Overreach

Expected fixture가 future evaluator behavior를 너무 많이 강제하면 구현 flexibility가 줄어든다.

완화:

- expected fixture는 action, status, severity, stop_reason, mutation flag, required hash/message fields 중심으로 제한한다.
- human output text는 이 단계에서 고정하지 않는다.

### Preview Provider Confusion

Fixture-backed provider를 만들 때 adapter execution으로 오해될 수 있다.

완화:

- fixture-backed provider는 input fixture name을 output fixture name에 매핑하는 read-only test utility로 제한한다.
- provider는 target file을 쓰거나 adapter를 실행하지 않는다.

### Update Candidate Misinterpretation

`update` candidate가 곧 sync apply 가능 상태로 오해될 수 있다.

완화:

- expected fixture는 `expected_no_mutation: true`를 필수로 둔다.
- update candidate severity는 informational로 시작한다.
- mutation gate 전까지 write authorization은 없다.

## Future Test Readiness

Fixture-only bundle이 시작되면 다음 테스트를 추가할 준비가 되어 있다.

1. Fixture schema test
   - input/output/expected fixture JSON parse
   - required fields
   - unavailable reason enum
   - hash format
   - deterministic metadata
   - provenance completeness

2. Fixture-backed provider test
   - input fixture -> output fixture deterministic mapping
   - no target writes
   - unavailable output handling

3. Dry-run update candidate test
   - clean target + generated hash differs -> update
   - clean target + generated hash matches -> skip
   - drifted target + generated hash exists -> drift-stop
   - invalid marker + generated hash exists -> conflict
   - preview unavailable -> no update

4. Envelope v2 preview mapping test
   - generated hashes preserved
   - preview unavailable reason preserved
   - provenance preserved
   - update candidate message behavior preserved

## Non-goal Confirmation

이번 fixture readiness 단계는 다음을 하지 않는다.

- runtime code 구현
- `.ai` rules 수정
- generated preview generation 구현
- adapter generation 또는 execution
- sync apply 구현
- target file mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- default manifest discovery
- repository-wide unmanaged scan
- activation-driven sync selection
- force 또는 decommission

## Decision

Generated preview fixture contract는 provider 구현 전 단계로 충분히 준비되었다.

다음으로 진행하기 좋은 작업은 fixture-only bundle이다.

- 실제 JSON fixture 파일 추가
- fixture schema tests 추가
- runtime provider는 아직 구현하지 않음
- dry-run update candidate extension은 provider contract 이후로 유지

## 결론

Phase 8 generated preview는 contract plan과 risk audit에 이어 fixture contract까지 정의되었다. 이 상태에서 바로 provider 구현으로 들어가기보다는 fixture-only bundle로 schema와 expected behavior를 먼저 고정하는 것이 안전하다.
