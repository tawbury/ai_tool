# Phase 7 Entry Risk Assessment

## 개요

이 문서는 Roadmap v1.2 Phase 7 `aios sync --dry-run` planning 진입 시점의 위험을 평가한다. Phase 6은 완료되었고 Phase 7 planning은 시작 가능하지만, runtime code implementation은 아직 시작하면 안 된다.

현재 시스템은 read-only이다. 이 문서는 sync execution, manifest persistence, transaction logs, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Entry Assessment

| 영역 | 상태 | 위험 | 판단 |
|---|---|---|---|
| Phase 6 safety contracts | complete | 낮음 | planning 시작 가능 |
| Runtime-facing sync rule | complete | 낮음 | `.ai/rules/operations/sync.rules.md` 기준 사용 가능 |
| Dry-run output concept | partial | 중간 | native schema 후보는 있으나 field precision 필요 |
| Manifest schema precision | incomplete | 높음 | implementation 전 필수 gate |
| Marker parser fixture | incomplete | 높음 | implementation 전 필수 gate |
| Hash normalization | undecided | 높음 | implementation 전 결정 필요 |
| Insertion anchor | incomplete | 중간~높음 | create candidate 구현 전 필요 |
| Manifest validation strategy | incomplete | 높음 | invalid input 처리 기준 필요 |
| Mutation safety | deferred | 낮음 | Phase 7 dry-run only면 직접 위험 낮음 |

## Primary Risks

### Manifest Schema Drift

위험:

- implementation 중 manifest field를 임의로 정하면 Phase 6 설계와 runtime rule이 어긋날 수 있다.
- field optionality와 nullability가 불명확하면 JSON consumer가 안정적으로 처리하기 어렵다.

완화:

- `sync_manifest_schema_and_validation_plan.md`를 먼저 작성한다.
- schema version, required fields, enum, hash field, marker metadata를 고정한다.

### Marker Parser Ambiguity

위험:

- marker parser가 문서 예시나 code fence 내부 marker-looking text를 실제 marker로 오인할 수 있다.
- missing, duplicated, nested, malformed marker를 다르게 분류하면 drift-stop policy와 충돌한다.

완화:

- `managed_block_parser_fixture_plan.md`를 먼저 작성한다.
- acceptance/rejection fixture를 구현 전 고정한다.
- marker structural failure는 hash 비교 전에 conflict로 처리한다.

### Hash Normalization Ambiguity

위험:

- CRLF/LF 처리, trailing newline, byte/text hashing을 구현 중 선택하면 cross-platform 결과가 흔들릴 수 있다.
- managed block hash가 marker line을 포함하면 marker metadata 변경이 content drift로 오판될 수 있다.

완화:

- marker lines excluded policy는 유지한다.
- observed bytes vs normalized text 결정을 별도 gate로 둔다.
- fixture에 line ending case를 포함한다.

### Manifest Validation Boundary

위험:

- `aios sync --dry-run` 내부 validation과 `aios validate`의 책임이 뒤섞일 수 있다.
- invalid manifest가 dry-run result인지 command error인지 불명확해질 수 있다.

완화:

- manifest validation strategy를 구현 전에 문서화한다.
- invalid schema는 blocking command result로 처리할지 usage/config error로 처리할지 결정한다.

### Dry-run Becoming Apply

위험:

- preview generation, marker insertion, manifest writing이 dry-run 구현에 섞일 수 있다.

완화:

- Phase 7 첫 scope는 read-only evaluation only로 제한한다.
- no mutation, no manifest write, no transaction log write를 test expectation에 포함한다.

## Secondary Risks

### Envelope v2 Mapping Loss

위험:

- native dry-run output과 envelope v2 output이 서로 다른 status/message vocabulary를 가질 수 있다.

완화:

- `result.py` 후보 모듈에서 status/message normalization을 중앙화한다.
- blocking result는 반드시 envelope message로 변환한다.

### Exit Code Policy Drift

위험:

- warning-only dry-run이 exit code 1이 되면 automation에서 실패로 오해할 수 있다.
- blocking conflict가 exit code 0이면 future write safety gate가 약해진다.

완화:

- pass/warn은 exit code 0, fail은 exit code 1, usage error는 exit code 2로 고정한다.

### Orphan and Unmanaged Confusion

위험:

- unmanaged target과 orphan marker가 모두 skip처럼 보이면 복구 방식이 혼동된다.

완화:

- unmanaged target은 `skip` warning.
- orphan marker는 `orphan-warning`.
- stop reason은 각각 `unmanaged-target`, `orphaned-managed-block`으로 분리한다.

## Implementation Entry Gates

Phase 7 code implementation 전에 필요한 gate:

1. Manifest schema precision
   - required/optional/nullability/enum/hash/marker fields 확정.

2. Marker parser fixture
   - valid, invalid, duplicate, nested, code fence cases 확정.

3. Hash normalization decision
   - byte/text, CRLF/LF, trailing newline, marker line exclusion 세부 정책 확정.

4. Insertion anchor contract
   - first-create candidate와 marker missing conflict를 구분하는 기준 확정.

5. Manifest validation strategy
   - `aios validate`, sync dry-run internal validation, error/status/exit code 관계 확정.

## Read-only Boundary Check

Phase 7 planning은 다음 작업을 하지 않아야 한다.

- target write
- manifest write
- transaction log write
- rollback execution
- adapter generation
- marker insertion or repair
- force or decommission
- `.ai/registry/` creation
- source mutation

## Recommended Sequence

1. Manifest schema and validation plan
2. Managed block parser fixture plan
3. Hash normalization and insertion anchor plan
4. Phase 7 implementation task breakdown
5. Runtime code implementation only after the above gates pass

## 결론

Phase 7 planning은 시작 가능하다. 그러나 Phase 7 implementation은 아직 시작하면 안 된다.

가장 큰 위험은 dry-run 자체가 아니라 dry-run이 의존하는 manifest schema, marker parser, hash normalization, insertion anchor, validation boundary가 구현 중에 임의 결정되는 것이다. 이 항목들을 먼저 계획 문서로 고정하면 `aios sync --dry-run`은 read-only safety evaluator로 제한된 범위에서 구현할 수 있다.
