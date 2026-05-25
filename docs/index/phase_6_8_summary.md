# Phase 6-8 요약

> 이 문서는 summary-first human context이다. 런타임 계약은 아니며, 현재 런타임 권한은 `.ai/rules/`에 있다.

## 목적

이 문서는 Phase 6-8의 핵심 결정을 빠르게 파악하기 위한 요약 색인이다. 상세 근거가 필요할 때만 `docs/plan/`과 `docs/reports/`의 개별 문서를 lazy-load한다.

## Phase 6: Sync/manifest safety design

Phase 6은 mutation 기능을 구현하기 전에 sync safety contract를 설계하는 단계였다.

핵심 결정:

- `.ai/`는 runtime source of truth로 유지한다.
- Manifest는 state record이며 source of truth가 아니다.
- Sync는 별도 설계가 승인되기 전까지 one-way assumption을 따른다.
- Dry-run-first policy를 채택한다.
- Drift-stop은 destructive overwrite를 막기 위한 기본 정책이다.
- Managed block marker는 mixed-boundary safety와 drift detection의 핵심이다.
- Rollback과 transaction은 mutation 구현 전 precondition으로 설계되어야 한다.

주요 산출물:

- `docs/plan/sync_manifest_safety_design.md`
- `docs/plan/drift_detection_and_stop_policy.md`
- `docs/plan/sync_dry_run_result_schema.md`
- `docs/plan/managed_block_marker_contract.md`
- `docs/plan/rollback_transaction_precondition_policy.md`
- `.ai/rules/operations/sync.rules.md`

상태:

- Safety design은 완료됨.
- Runtime rules로 핵심 정책이 승격됨.
- Mutation/apply는 계속 차단됨.

## Phase 7: Read-only sync runtime

Phase 7은 Phase 6 safety design을 바탕으로 read-only sync dry-run runtime v0를 구현한 단계다.

구현된 기능:

- `aios sync --dry-run --manifest <path>`
- native `aios.sync_dry_run.v0` output
- envelope v2 sync output
- sync manifest JSON validation
- manifest/hash foundation
- managed marker parser
- drift-stop evaluation
- orphan-warning evaluation
- `aios validate <sync-manifest.json>`
- output contract tests

핵심 결정:

- `aios sync`는 `--dry-run` 없이 실행될 수 없다.
- `aios sync --dry-run`은 `--manifest <path>`가 필요하다.
- Usage/config error는 exit code `2`를 사용한다.
- Blocking conflict는 `status: fail`, exit code `1`이다.
- Warning-only state는 `status: warn`, exit code `0`이다.
- `meta.mutation_performed`는 항상 `false`다.

상태:

- Phase 7 read-only runtime v0는 완료됨.
- Runtime governance rules에 승격됨.
- Sync apply, manifest write, transaction log, rollback, marker mutation은 차단됨.

## Phase 8: Fixture preview runtime

Phase 8은 read-only dry-run에서 generated preview comparison을 안전하게 도입하기 위한 단계다.

완료된 범위:

- Generated preview contract plan
- Generated preview risk audit
- Fixture input/output/expected contract
- Concrete fixture JSON and schema tests
- Fixture-backed preview provider
- Opt-in dry-run preview integration
- Preview output contract tests
- Sync runtime rules promotion
- Phase 8 preview runtime completion audit

지원되는 preview path:

```bash
python -m aios sync --dry-run --manifest <path> --json --preview-provider fixture --preview-fixtures <path>
```

핵심 결정:

- Preview provider는 opt-in이다.
- 기본 preview provider는 없다.
- 현재 지원 provider는 fixture provider뿐이다.
- Clean target에서 generated hash가 다르면 read-only `action: update` 후보를 만들 수 있다.
- `update` 후보는 informational result이며 write authorization이 아니다.
- Preview unavailable은 update 후보를 만들지 않는다.
- Source-missing, marker conflict, drift-stop이 preview보다 우선한다.
- Native JSON과 envelope v2는 preview metadata와 generated hashes를 보존한다.

상태:

- Fixture-preview read-only runtime v0는 완료됨.
- Real preview provider는 아직 없음.
- Adapter execution과 generated content creation은 차단됨.

## Real preview provider planning

Phase 8 이후 다음 방향은 real preview provider contract 설계다.

정의된 계획:

- `docs/plan/real_preview_provider_contract.md`
- `docs/reports/real_preview_provider_risk_audit.md`

핵심 원칙:

- Provider는 deterministic read-only comparison output만 제공한다.
- 동일 input과 동일 provider version은 동일 output hash를 만들어야 한다.
- Provider identity와 version은 output metadata에 보존되어야 한다.
- Provider가 deterministic output을 보장하지 못하면 `nondeterministic-output` unavailable state를 사용한다.
- Provider output은 sync apply를 승인하지 않는다.

상태:

- Contract와 risk audit은 완료됨.
- Provider implementation은 아직 없음.
- Adapter runtime은 아직 승인되지 않음.

## Deterministic replay planning

Real provider 구현 전에 deterministic replay architecture가 필요하다.

정의된 계획:

- `docs/plan/deterministic_replay_test_architecture.md`
- `docs/reports/deterministic_replay_risk_audit.md`
- `docs/plan/real_preview_replay_fixture_contract.md`
- `docs/reports/real_preview_replay_fixture_risk_audit.md`
- `docs/reports/real_preview_replay_fixture_bundle_report.md`
- `docs/reports/replay_manifest_validate_integration_report.md`
- `docs/reports/replay_validate_output_contract_report.md`
- `docs/reports/replay_validation_rule_promotion_audit.md`
- `docs/reports/replay_validation_runtime_rule_promotion_report.md`
- `docs/reports/replay_comparison_next_step_audit.md`
- `docs/plan/fixture_backed_replay_comparison_validation_plan.md`
- `docs/reports/fixture_backed_replay_comparison_risk_audit.md`
- `docs/reports/replay_comparison_helper_implementation_report.md`

핵심 원칙:

- 동일 input은 동일 generated hash, provenance, provider metadata, unavailable reason을 재현해야 한다.
- Replay mismatch는 validation failure다.
- Automatic retry는 금지한다.
- Same provider version에서 output drift는 허용되지 않는다.
- Provider version change는 explicit snapshot migration을 요구한다.

상태:

- Replay architecture와 risk audit은 완료됨.
- Replay fixture contract와 fixture risk audit은 완료됨.
- Replay JSON fixtures와 schema/contract tests는 구현됨.
- `aios validate <replay-manifest.json>` 정적 검증 통합은 구현됨.
- Replay validation native JSON/envelope v2 output contract tests는 구현됨.
- Replay validation rule promotion audit는 완료되었고 split promotion을 권장함.
- Replay validation behavior는 `sync.rules.md`와 `validation.rules.md`에 승격됨.
- Replay comparison next step audit는 fixture-backed replay comparison validation design을 다음 단계로 권장함.
- Fixture-backed replay comparison validation design과 risk audit는 완료됨.
- Pure replay comparison helper와 mismatch tests는 구현됨.
- Replay comparison integration policy audit는 default validate 통합을 거부하고 opt-in validation integration 설계를 권장함.
- Opt-in replay comparison native JSON/envelope v2 output contract와 risk audit는 완료됨.
- `aios validate <replay-manifest.json> --replay-compare fixture` opt-in integration은 구현됨.
- Opt-in replay comparison native JSON/envelope v2 output contract tests는 안정화됨.
- Phase 8 replay comparison runtime v0 completion audit는 완료되었고 v0 closure를 인정함.
- Opt-in replay comparison runtime behavior는 `sync.rules.md`와 `validation.rules.md`에 승격됨.
- Provider isolation requirements audit와 plan은 완료되었고 real provider execution 전 capability, sandbox, no-write, deterministic replay gate가 필요하다고 확인함.
- Provider capability fixture contract와 risk audit는 완료되었고 capability declaration이 execution authorization, provider registration, sandbox approval이 아님을 명확히 함.
- Provider capability fixture-only bundle은 구현되었고 valid/invalid/edge fixture와 fixture-only contract tests가 추가됨.
- Provider capability validator helper는 구현되었고 helper 자체는 parsed dict 정적 검증만 수행함.
- Provider capability validate output contract와 risk audit는 완료되었고 future `aios validate <provider-capability.json>` native JSON/envelope v2 경계를 정의함.
- `aios validate <provider-capability.json>` static-only 통합은 구현되었고 native JSON/envelope v2 경계와 non-execution metadata를 보존함.
- Provider capability validate output contract tests는 안정화되었고 shaped JSON detection, unrelated JSON non-misclassification, sync/replay target priority를 고정함.
- Provider capability rule promotion audit는 완료되었고 `validation.rules.md` primary, `sync.rules.md` short safety pointer의 split promotion을 권장함.
- Provider capability validation behavior는 `validation.rules.md`와 `sync.rules.md`에 승격됨.
- Deterministic mock provider boundary plan과 risk audit는 완료되었고 mock provider를 fixture-backed deterministic simulation으로만 정의함.
- Deterministic mock provider fixture-only bundle은 구현되었고 fixture index, valid/invalid input/output/snapshot fixtures, 구조 검증 테스트를 추가함.
- Provider execution trace schema plan과 risk audit는 완료되었고 trace를 observability/replay evidence로만 정의함. Trace success는 execution authorization, sandbox approval, sync apply authorization이 아님.
- Provider execution trace fixture-only bundle은 구현되었고 valid/invalid/edge trace fixtures와 구조 검증 테스트를 추가함.
- Provider execution trace validator helper는 구현되었고 parsed dict 정적 검증만 수행함.
- `aios validate <provider-trace.json>` static-only 통합은 구현되었고 target kind `provider-execution-trace`, native JSON, envelope v2, non-execution metadata를 지원함.
- Provider execution trace validate output contract tests는 안정화되었고 native JSON/envelope v2의 pass/fail, detection priority, non-execution metadata를 고정함.
- Provider execution trace validation rule promotion audit는 완료되었고 `validation.rules.md` primary, `sync.rules.md` short pointer로 split promotion을 권장함.
- Provider execution trace validation behavior는 `validation.rules.md`와 `sync.rules.md`에 승격되었고 static-only boundary와 non-execution prohibition을 runtime governance에 반영함.
- Subprocess sandbox architecture risk audit와 plan은 design-only track으로 완료되었고 temporary cwd, sanitized env, explicit input/output, timeout/resource limits, no-write verification requirement를 정의함.
- Sandbox policy fixture contract plan과 risk audit는 완료되었고 `aios.sandbox_policy.v0` fixture-only schema, valid/invalid/edge layout, env/filesystem/resource policy, no-write evidence model을 정의함.
- Sandbox policy fixture-only bundle은 구현되었고 valid/invalid/edge JSON fixtures, fixture index, fixture-only contract tests를 추가함.
- Sandbox policy validator helper는 구현되었고 parsed dict 정적 검증만 수행함. `aios validate`, envelope v2, CLI, sandbox launcher, subprocess execution에는 아직 통합되지 않음.
- Sandbox policy validate output contract plan과 risk audit는 완료되었고 future `aios validate <sandbox-policy.json>` target kind `sandbox-policy`, native JSON/envelope v2 non-execution metadata, detection priority를 정의함.
- `aios validate <sandbox-policy.json>` static-only 통합은 구현되었고 target kind `sandbox-policy`, native JSON, envelope v2, non-execution metadata를 지원함.
- Sandbox policy validate output contract tests는 안정화되었고 native JSON/envelope v2 pass/fail, shaped invalid schema, target detection priority, non-execution metadata를 고정함.
- Sandbox policy validation rule promotion audit는 완료되었고 `validation.rules.md` primary, `sync.rules.md` short safety pointer의 split promotion을 권장함.
- Sandbox policy validation behavior는 `validation.rules.md`와 `sync.rules.md`에 승격되었고 static-only boundary와 non-execution prohibition을 runtime governance에 반영함.
- Replay provider execution, output replay comparison, snapshot update는 아직 구현되지 않음.

## 현재 지원 런타임 기능

현재 `.ai OS` runtime은 다음을 지원한다.

- `aios inspect`
- `aios inventory`
- `aios validate`
- `aios validate <activation.yaml>`
- `aios validate <sync-manifest.json>`
- `aios validate <replay-manifest.json>`
- `aios validate <replay-manifest.json> --replay-compare fixture`
- `aios activation <path>`
- activation v0/v1 parsing and validation
- `aios load-context` with character budget awareness
- envelope v2 opt-in JSON output
- `aios sync --dry-run --manifest <path>`
- fixture-backed preview comparison when explicitly configured

## 계속 차단된 기능

다음은 차단 상태다.

- sync apply
- target mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- real preview provider execution
- adapter execution
- generated content creation
- default preview provider
- default manifest discovery
- repository-wide unmanaged/orphan scan
- activation-driven sync selection
- force
- decommission
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source mutation

## 다음 권장 방향

다음 안전한 방향은 sandbox trace fixture contract를 별도 design-only track으로 진행하거나 sandbox execution result fixture contract를 설계하는 것이다. 현재 sandbox policy validation은 static-only이며 real provider execution이나 sandbox execution이 아니다.

권장 다음 작업:

1. Sandbox trace fixture contract design
2. Sandbox execution result fixture contract design
3. Sandbox policy runtime rule promotion follow-up audit only if future behavior changes

Mutation/apply 설계는 real provider와 replay 검증 경계가 안정된 뒤에 검토한다.

## 권장 로딩 순서

1. `.ai/rules/rules.md`
2. relevant operation rule, usually `.ai/rules/operations/sync.rules.md`
3. `docs/index/current_runtime_context.md`
4. this document
5. detailed plans/reports only if needed
