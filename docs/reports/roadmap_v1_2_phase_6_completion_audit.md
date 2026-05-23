# Roadmap v1.2 Phase 6 Completion Audit

## 개요

이 문서는 Roadmap v1.2 Phase 6 Sync/Manifest Safety Design의 완료 상태를 감사한다. 감사 목적은 Phase 6 안전 설계가 Phase 7 `aios sync --dry-run` 구현 계획을 시작할 만큼 충분한지 판단하는 것이다.

현재 시스템은 read-only이다. 이 감사는 sync 실행, manifest persistence, transaction log persistence, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## 감사 대상

Phase 6 핵심 산출물:

- `docs/plan/sync_manifest_safety_design.md`
- `docs/plan/drift_detection_and_stop_policy.md`
- `docs/plan/sync_dry_run_result_schema.md`
- `docs/plan/managed_block_marker_contract.md`
- `docs/plan/rollback_transaction_precondition_policy.md`
- `.ai/rules/operations/sync.rules.md`

관련 위험 감사 및 보고서:

- `docs/reports/sync_manifest_risk_model_audit.md`
- `docs/reports/drift_conflict_failure_mode_audit.md`
- `docs/reports/sync_dry_run_schema_risk_audit.md`
- `docs/reports/managed_block_marker_risk_audit.md`
- `docs/reports/rollback_transaction_risk_audit.md`
- `docs/reports/sync_runtime_rules_report.md`

## Completion Matrix

| 영역 | 상태 | 근거 | Phase 7 영향 |
|---|---|---|---|
| Manifest safety architecture | completed | manifest 목표, managed entry 구조, ownership, drift model, dry-run action이 정의됨 | Phase 7 planning의 기반으로 충분 |
| Drift detection and stop policy | completed | source/target/managed block hash 비교, severity, conflict taxonomy, default stop policy가 정의됨 | 구현 전 test case로 전환 가능 |
| Sync dry-run result schema | partially completed | top-level/result item/action/status/message/summary/sample output이 정의됨 | 구현 전 JSON schema 정밀화 필요 |
| Managed block marker contract | partially completed | canonical syntax, invalid cases, parser expectation, hash boundary, dry-run mapping이 정의됨 | parser fixture와 hash normalization 결정 필요 |
| Rollback transaction preconditions | documented only | transaction schema 후보와 rollback forbidden case가 정의됨 | Phase 7 dry-run 구현에는 참고 기준, mutation 전 필수 gate |
| Runtime-facing sync rule | completed | `.ai/rules/operations/sync.rules.md`로 안전 계약이 승격됨 | runtime rule 기준선으로 사용 가능 |
| Risk audits | completed | manifest, drift, dry-run, marker, rollback 위험이 문서화됨 | Phase 7 planning risk checklist로 사용 가능 |
| Actual sync execution | deferred | 명시적 non-goal | Phase 7 구현 planning 전까지 금지 유지 |
| Manifest persistence | deferred | 명시적 non-goal | dry-run preview와 validation strategy부터 설계 필요 |
| Transaction log persistence | deferred | 명시적 non-goal | rollback 전제 설계만 완료 |
| Rollback execution | deferred | 명시적 non-goal | Phase 7 dry-run 구현 범위 밖 |
| Adapter generation | deferred | 명시적 non-goal | Phase 8 이후 대상으로 유지 |
| Force/decommission | deferred | 명시적 non-goal | 별도 안전 설계 전까지 금지 |
| Blocking issue | none | Phase 6 설계를 막는 미해결 차단 요인은 없음 | Phase 7 planning 착수 가능 |

## Completed

Phase 6에서 완료된 항목:

- `.ai/`가 source of truth이고 future manifest는 state record라는 경계가 정리되었다.
- one-way sync assumption이 runtime-facing rule에 반영되었다.
- ownership model이 `runtime-managed`, `user-owned`, `mixed-boundary`로 정리되었다.
- drift state가 `clean`, `drifted`, `missing`, `orphaned`, `unmanaged`로 정리되었다.
- conflict taxonomy와 default drift-stop policy가 정의되었다.
- dry-run-first policy가 sync와 rollback 모두에 적용되도록 정리되었다.
- dry-run result schema 후보와 sample outputs가 작성되었다.
- managed block marker syntax와 invalid marker cases가 정의되었다.
- marker line을 managed content hash에서 제외하는 권장 정책이 정의되었다.
- rollback과 transaction precondition이 mutation 전 gate로 정리되었다.
- Phase 6 safety contract가 `.ai/rules/operations/sync.rules.md`로 승격되었다.

## Partially Completed

Phase 7 planning에서 정밀화해야 하는 항목:

- manifest schema는 후보 수준이다. JSON Schema 수준의 required field, enum, nullable field, versioning policy가 아직 확정되지 않았다.
- dry-run schema는 충분한 예시를 갖지만 실제 CLI output contract로 고정하려면 field optionality와 compatibility policy가 더 필요하다.
- marker parser expectation은 정의되었지만 fixture set과 parser acceptance/rejection matrix가 아직 없다.
- hash boundary는 정의되었지만 line ending normalization과 byte/text hashing 선택이 최종 결정되지 않았다.
- insertion anchor는 필요성이 정의되었지만 anchor syntax와 discovery policy가 없다.
- rollback transaction schema는 precondition 후보이며 persistence location, retention, validation 방식은 정의되지 않았다.

## Documented Only

다음 항목은 Phase 6에서 의도적으로 문서화만 되었다.

- transaction log schema candidate
- rollback dry-run expectation
- future observability event mapping
- envelope v2 mapping
- activation v1 compatibility boundary
- future force boundary
- future decommission boundary

이 항목들은 Phase 7 dry-run 구현의 직접 범위가 아니라, future mutation phase가 반드시 넘겨받아야 할 safety context이다.

## Deferred

다음은 계속 deferred 상태이다.

- sync execution
- manifest persistence
- transaction log persistence
- rollback execution
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation

## Blocked

Phase 6 completion 자체를 막는 blocker는 없다.

다만 Phase 7 implementation을 즉시 시작하기에는 다음 결정들이 아직 blocker에 가깝다.

- manifest schema precision
- marker parser test fixture
- hash normalization decision
- insertion anchor contract
- manifest validation strategy

따라서 blocker는 Phase 6 completion blocker가 아니라 Phase 7 implementation entry blocker로 분류한다.

## Remaining Gaps Before Phase 7

### Manifest Schema Precision

현재 manifest schema는 design candidate이다. Phase 7 planning에서는 최소한 다음을 확정해야 한다.

- `manifest_version` 값
- required top-level fields
- managed entry required fields
- ownership enum
- sync mode enum
- hash field naming
- marker metadata field
- nullable field policy
- schema evolution policy

### Marker Parser Test Fixture

marker contract는 충분히 정의되었지만 parser fixture가 없다.

필요 fixture:

- valid Markdown marker
- valid plain text marker
- valid YAML comment marker
- missing begin
- missing end
- mismatched entry_id
- duplicated marker
- nested marker
- malformed marker
- marker-looking text inside fenced code block

### Hash Normalization Decision

managed block hash는 marker lines를 제외한다는 정책은 정해졌지만, hash normalization은 미정이다.

결정 필요:

- observed bytes 기반 hash인지
- UTF-8 decoded text 기반 hash인지
- CRLF/LF normalization을 할지
- trailing newline policy를 둘지

### Insertion Anchor Contract

first-create candidate는 explicit anchor가 있어야 한다. 하지만 anchor syntax와 ambiguity policy가 아직 없다.

결정 필요:

- anchor marker syntax
- one anchor per target rule
- missing anchor conflict code
- duplicated anchor conflict code
- unmanaged target insertion 금지 방식

### Transaction Storage Location

transaction precondition은 정의되었지만 persistence는 non-goal이었다.

Phase 7 dry-run 구현은 transaction persistence를 구현하지 않아도 되지만, future mutation planning을 위해 후보 위치와 retention policy를 별도 설계해야 한다.

### Rollback Dry-run Schema

rollback dry-run은 정책 수준에서 정의되었다.

Phase 7에서 rollback을 구현하지 않는다면 상세 schema는 deferred로 둘 수 있다. 다만 mutation phase 전에는 sync dry-run schema와 같은 수준으로 정밀화해야 한다.

### Manifest Validation Strategy

Phase 7 dry-run이 manifest preview나 manifest input을 다룰 경우 validator strategy가 필요하다.

결정 필요:

- `aios validate <manifest>` target을 지원할지
- manifest schema validation을 별도 validator로 둘지
- manifest reference resolution을 inventory와 연결할지
- drift-stop policy validation을 정적 validation과 dry-run evaluation 중 어디에 둘지

## Phase 7 Entry Decision

Phase 6 safety design은 완료로 판단한다.

그러나 Phase 7 implementation은 즉시 시작하지 않는 것이 맞다. 다음 단계는 Phase 7 dry-run implementation planning이어야 한다.

판단 근거:

- safety principles와 runtime-facing rule은 충분히 정리되었다.
- dry-run output contract는 후보 수준으로 충분하지만 implementation contract로 고정하려면 schema precision이 더 필요하다.
- marker parser는 future sync safety의 핵심인데 test fixture가 아직 없다.
- hash normalization과 insertion anchor는 implementation 중 임의 결정하면 호환성과 safety risk가 커진다.
- manifest validation strategy가 없으면 dry-run implementation이 validation boundary를 임의로 만들 가능성이 있다.

따라서 결론은 다음과 같다.

- Phase 6: complete
- Phase 7 planning: may start now
- Phase 7 implementation: should wait until planning outputs are complete

## Recommended Next 3 Tasks

1. `docs/plan/phase_7_sync_dry_run_implementation_plan.md` 작성
   - `aios sync --dry-run`의 scope, non-goals, CLI shape, input source, output schema, exit code, envelope v2 mapping을 고정한다.

2. `docs/plan/sync_manifest_schema_and_validation_plan.md` 작성
   - manifest JSON schema candidate를 required/optional/nullability/enum 수준으로 정밀화하고 `aios validate`와의 관계를 정의한다.

3. `docs/plan/managed_block_parser_fixture_plan.md` 작성
   - marker parser acceptance/rejection fixture, code fence handling, hash normalization decision, insertion anchor contract를 Phase 7 구현 전 gate로 정리한다.

## 결론

Roadmap v1.2 Phase 6은 safety design 관점에서 완료되었다. 핵심 safety contracts는 plan, risk audit, runtime-facing operation rule까지 승격되었다.

다만 Phase 7은 곧바로 code implementation으로 들어가면 안 된다. Phase 7의 첫 단계는 dry-run implementation planning이어야 하며, 특히 manifest schema precision, marker parser fixture, hash normalization, insertion anchor, manifest validation strategy가 구현 전 gate로 남아 있다.
