# Phase 6-8 문서 상태 레지스트리

> 이 색인은 런타임 계약이 아니다. `.ai/rules/`가 현재 런타임 권한의 정본이며, `docs/plan/`과 `docs/reports/`는 명시적으로 필요한 경우에만 human context로 읽는다.

## 목적

Phase 6-8 동안 생성된 주요 계획서와 보고서의 상태, 권한, 로딩 정책을 한곳에서 확인하기 위한 색인이다. 이 문서는 파일을 이동하거나 폐기하지 않으며, 어떤 문서가 현재 규칙인지도 새로 정의하지 않는다.

## 상태 기준

| 상태 | 의미 | 기본 로딩 정책 |
| --- | --- | --- |
| `runtime-facing contract` | 현재 런타임 운영 계약 | 관련 태스크에서 로드 |
| `active implementation plan` | 다음 구현/설계에 직접 필요한 계획 | 관련 태스크에서 로드 |
| `completed implementation report` | 완료 작업 증빙 | lazy-load |
| `risk audit` | 위험 식별과 완화 근거 | lazy-load |
| `historical/superseded` | 후속 구현 또는 `.ai` 규칙으로 대체된 설계 | 기본 로드 금지 |
| `reference-only` | 배경/증빙/상태 확인용 | lazy-load |

## Runtime-facing contracts

| Path | Phase | Status | Authority | Load policy | Promoted to | Superseded by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `.ai/rules/rules.md` | all | runtime-facing contract | runtime | always minimum | self | none | shared rule source of truth |
| `.ai/rules/operations/documentation-governance.rules.md` | all | runtime-facing contract | runtime | task-load | self | none | docs authority boundary |
| `.ai/rules/operations/context-loading.rules.md` | 5-8 | runtime-facing contract | runtime | task-load | self | none | semantic loader budget and provenance |
| `.ai/rules/operations/activation.rules.md` | 5-8 | runtime-facing contract | runtime | task-load | self | none | activation v0/v1 runtime contract |
| `.ai/rules/operations/sync.rules.md` | 6-8 | runtime-facing contract | runtime | task-load | self | none | sync dry-run, manifest, fixture preview, replay validation runtime rules |

## Phase 6 safety design

| Path | Phase | Status | Authority | Load policy | Promoted to | Superseded by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/plan/sync_manifest_safety_design.md` | 6 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` | `docs/reports/roadmap_v1_2_phase_6_completion_audit.md` | manifest safety goals |
| `docs/reports/sync_manifest_risk_model_audit.md` | 6 | risk audit | human context | lazy | none | none | manifest risk model |
| `docs/plan/drift_detection_and_stop_policy.md` | 6 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` | `docs/reports/roadmap_v1_2_phase_6_completion_audit.md` | drift-stop policy |
| `docs/reports/drift_conflict_failure_mode_audit.md` | 6 | risk audit | human context | lazy | none | none | conflict taxonomy evidence |
| `docs/plan/sync_dry_run_result_schema.md` | 6 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` | Phase 7 runtime implementation | native dry-run schema planning |
| `docs/reports/sync_dry_run_schema_risk_audit.md` | 6 | risk audit | human context | lazy | none | none | dry-run schema risks |
| `docs/plan/managed_block_marker_contract.md` | 6 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` | Phase 7 marker parser | marker contract |
| `docs/reports/managed_block_marker_risk_audit.md` | 6 | risk audit | human context | lazy | none | none | marker risk model |
| `docs/plan/rollback_transaction_precondition_policy.md` | 6 | reference-only | human context | lazy | `.ai/rules/operations/sync.rules.md` | none | future mutation prerequisite |
| `docs/reports/rollback_transaction_risk_audit.md` | 6 | risk audit | human context | lazy | none | none | rollback risks |
| `docs/reports/sync_runtime_rules_report.md` | 6 | completed implementation report | human context | lazy | `.ai/rules/operations/sync.rules.md` | Phase 7/8 sync rule updates | Phase 6 rule promotion evidence |
| `docs/reports/roadmap_v1_2_phase_6_completion_audit.md` | 6 | reference-only | human context | lazy | none | `docs/reports/phase_7_closure_phase_8_entry_audit.md` | Phase 6 closure |

## Phase 7 read-only sync runtime

| Path | Phase | Status | Authority | Load policy | Promoted to | Superseded by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/plan/phase_7_sync_dry_run_implementation_plan.md` | 7 | historical/superseded | human context | lazy | none | Phase 7 bundles | dry-run implementation plan |
| `docs/reports/phase_7_entry_risk_assessment.md` | 7 | risk audit | human context | lazy | none | none | entry risk |
| `docs/plan/sync_manifest_schema_and_validation_plan.md` | 7 | historical/superseded | human context | lazy | sync manifest validator | Phase 7 Bundle 4 | manifest validation plan |
| `docs/reports/sync_manifest_validation_boundary_audit.md` | 7 | risk audit | human context | lazy | none | none | validation boundary |
| `docs/plan/managed_block_parser_and_anchor_contract.md` | 7 | historical/superseded | human context | lazy | marker parser | Phase 7 Bundle 2 | parser fixture contract |
| `docs/reports/managed_block_parser_risk_audit.md` | 7 | risk audit | human context | lazy | none | none | parser risks |
| `docs/plan/hash_normalization_and_fixture_policy.md` | 7 | historical/superseded | human context | lazy | sync hash helpers | Phase 7 Bundle 1 | hash policy planning |
| `docs/reports/hash_normalization_risk_audit.md` | 7 | risk audit | human context | lazy | none | none | hash policy risks |
| `docs/plan/phase_7_sync_dry_run_task_breakdown.md` | 7 | historical/superseded | human context | lazy | none | Phase 7 bundles | implementation bundle breakdown |
| `docs/reports/phase_7_bundle_readiness_audit.md` | 7 | reference-only | human context | lazy | none | none | readiness audit |
| `docs/reports/phase_7_bundle_1_manifest_hash_report.md` | 7 | completed implementation report | human context | lazy | sync manifest/hash modules | none | Bundle 1 evidence |
| `docs/reports/phase_7_bundle_2_marker_parser_report.md` | 7 | completed implementation report | human context | lazy | sync marker parser | none | Bundle 2 evidence |
| `docs/reports/phase_7_bundle_3_sync_dry_run_report.md` | 7 | completed implementation report | human context | lazy | sync dry-run CLI | none | Bundle 3 evidence |
| `docs/reports/phase_7_bundle_4_manifest_validate_report.md` | 7 | completed implementation report | human context | lazy | `aios validate <sync-manifest>` | none | Bundle 4 evidence |
| `docs/reports/phase_7_read_only_runtime_completion_audit.md` | 7 | reference-only | human context | lazy | none | `docs/reports/phase_7_closure_phase_8_entry_audit.md` | v0 completion |
| `docs/reports/phase_7_stabilization_output_contract_report.md` | 7 | completed implementation report | human context | lazy | sync output tests | none | output contract evidence |
| `docs/reports/phase_7_runtime_rule_promotion_report.md` | 7 | completed implementation report | human context | lazy | `.ai/rules/operations/sync.rules.md` | Phase 8 rule update | rule promotion evidence |
| `docs/reports/phase_7_closure_phase_8_entry_audit.md` | 7 | reference-only | human context | lazy | none | Phase 8 preview docs | Phase 8 entry decision |

## Phase 8 fixture preview runtime and provider planning

| Path | Phase | Status | Authority | Load policy | Promoted to | Superseded by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/plan/generated_preview_contract_plan.md` | 8 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` | fixture preview integration | initial preview contract |
| `docs/reports/generated_preview_risk_audit.md` | 8 | risk audit | human context | lazy | none | none | preview risk model |
| `docs/plan/generated_preview_fixture_contract.md` | 8 | historical/superseded | human context | lazy | preview fixtures/tests | fixture bundle | fixture contract |
| `docs/reports/generated_preview_fixture_readiness_audit.md` | 8 | risk audit | human context | lazy | none | none | fixture readiness |
| `docs/reports/generated_preview_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | preview fixture tests | none | fixture-only evidence |
| `docs/reports/generated_preview_fixture_provider_report.md` | 8 | completed implementation report | human context | lazy | fixture preview provider | none | provider evidence |
| `docs/plan/dry_run_preview_integration_plan.md` | 8 | historical/superseded | human context | lazy | sync preview integration | implementation report | dry-run integration plan |
| `docs/reports/dry_run_preview_integration_risk_audit.md` | 8 | risk audit | human context | lazy | none | none | integration risks |
| `docs/reports/dry_run_preview_integration_implementation_report.md` | 8 | completed implementation report | human context | lazy | sync preview runtime | none | implementation evidence |
| `docs/reports/phase_8_preview_output_contract_report.md` | 8 | completed implementation report | human context | lazy | preview output tests | none | output contract evidence |
| `docs/reports/phase_8_preview_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/sync.rules.md` | none | Phase 8 rule promotion |
| `docs/reports/phase_8_preview_runtime_completion_audit.md` | 8 | reference-only | human context | lazy | none | real provider planning | fixture-preview v0 closure |
| `docs/plan/real_preview_provider_contract.md` | 8 | active implementation plan | human context | task-load | none | none | next design direction |
| `docs/reports/real_preview_provider_risk_audit.md` | 8 | risk audit | human context | lazy | none | none | real provider risk model |
| `docs/plan/deterministic_replay_test_architecture.md` | 8 | active implementation plan | human context | task-load | none | none | future replay test architecture |
| `docs/reports/deterministic_replay_risk_audit.md` | 8 | risk audit | human context | lazy | none | none | replay risk model |
| `docs/plan/real_preview_replay_fixture_contract.md` | 8 | historical/superseded | human context | lazy | replay fixture tests | `docs/reports/real_preview_replay_fixture_bundle_report.md` | replay fixture contract before implementation |
| `docs/reports/real_preview_replay_fixture_risk_audit.md` | 8 | risk audit | human context | lazy | none | none | replay fixture risk model |
| `docs/reports/real_preview_replay_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | replay fixture tests | none | fixture-only replay bundle evidence |
| `docs/reports/replay_manifest_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <replay-manifest.json>` | none | replay manifest static validation integration evidence |
| `docs/reports/replay_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | replay validate output contract tests | none | native JSON and envelope v2 contract evidence |
| `docs/reports/replay_validation_rule_promotion_audit.md` | 8 | historical/superseded | human context | lazy | `.ai/rules/operations/sync.rules.md` and `.ai/rules/operations/validation.rules.md` | `docs/reports/replay_validation_runtime_rule_promotion_report.md` | recommended split promotion |
| `docs/reports/replay_validation_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/sync.rules.md` and `.ai/rules/operations/validation.rules.md` | none | replay validation rule promotion evidence |
| `docs/reports/replay_comparison_next_step_audit.md` | 8 | historical/superseded | human context | lazy | none | `docs/plan/fixture_backed_replay_comparison_validation_plan.md` | recommended fixture-backed replay comparison design |
| `docs/plan/fixture_backed_replay_comparison_validation_plan.md` | 8 | historical/superseded | human context | lazy | replay comparison helper | `docs/reports/replay_comparison_helper_implementation_report.md` | design for no-provider replay comparison validation |
| `docs/reports/fixture_backed_replay_comparison_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | risks for fixture-backed replay comparison |
| `docs/reports/replay_comparison_helper_implementation_report.md` | 8 | completed implementation report | human context | lazy | `compare_replay_outputs` helper | none | pure helper implementation evidence |
| `docs/reports/replay_comparison_integration_policy_audit.md` | 8 | risk audit | human context | task-load | none | none | recommends deferred opt-in validate integration instead of default comparison |
| `docs/plan/replay_compare_output_contract_plan.md` | 8 | historical/superseded | human context | lazy | opt-in replay comparison validation | `docs/reports/replay_compare_integration_implementation_report.md` | opt-in replay comparison native JSON/envelope v2 output contract |
| `docs/reports/replay_compare_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | risks for opt-in replay comparison output contract |
| `docs/reports/replay_compare_integration_implementation_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <replay-manifest.json> --replay-compare fixture` | none | opt-in replay comparison integration evidence |
| `docs/reports/replay_compare_output_contract_report.md` | 8 | completed implementation report | human context | lazy | replay comparison output contract tests | none | opt-in replay comparison native JSON/envelope v2 contract evidence |
| `docs/reports/phase_8_replay_comparison_runtime_completion_audit.md` | 8 | reference-only | human context | summary-first | none | none | closes replay comparison runtime v0 and recommends rule promotion next |
| `docs/reports/replay_compare_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/sync.rules.md` and `.ai/rules/operations/validation.rules.md` | none | opt-in replay comparison rule promotion evidence |
| `docs/reports/provider_isolation_requirements_audit.md` | 8 | risk audit | human context | task-load | none | none | audits real provider execution isolation risks and required gates |
| `docs/plan/provider_isolation_requirements_plan.md` | 8 | active implementation plan | human context | task-load | none | none | defines provider isolation prerequisites before real execution design |
| `docs/plan/provider_capability_fixture_contract.md` | 8 | historical/superseded | human context | lazy | provider capability fixtures/tests | `docs/reports/provider_capability_fixture_bundle_report.md` | defines provider capability fixture schema, layout, and validation boundaries |
| `docs/reports/provider_capability_fixture_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits capability fixture confusion and execution authorization risks |
| `docs/reports/provider_capability_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | provider capability fixture tests | none | fixture-only provider capability bundle evidence |
| `docs/reports/provider_capability_validator_helper_report.md` | 8 | completed implementation report | human context | lazy | provider capability validator helper | none | pure static helper evidence without validate integration |
| `docs/plan/provider_capability_validate_output_contract_plan.md` | 8 | historical/superseded | human context | lazy | provider capability validate integration | `docs/reports/provider_capability_validate_integration_report.md` | defines future validate native JSON/envelope v2 output contract for provider capability static validation |
| `docs/reports/provider_capability_validate_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits static validation output risks and provider execution confusion |
| `docs/reports/provider_capability_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <provider-capability.json>` | none | provider capability static validation integration evidence |
| `docs/reports/provider_capability_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | provider capability validate output contract tests | none | native JSON/envelope v2 contract stabilization evidence |
| `docs/reports/provider_capability_rule_promotion_audit.md` | 8 | risk audit | human context | task-load | none | none | recommends split promotion to validation rules with sync safety pointer |
| `docs/reports/provider_capability_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | none | provider capability validation rule promotion evidence |
| `docs/plan/deterministic_mock_provider_boundary_plan.md` | 8 | active implementation plan | human context | task-load | none | none | defines deterministic mock provider boundary before execution or sandbox work |
| `docs/reports/deterministic_mock_provider_boundary_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits mock provider simulation risks and execution-boundary confusion |
| `docs/reports/deterministic_mock_provider_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | deterministic mock provider fixture tests | none | fixture-only mock provider bundle evidence without execution runtime |
| `docs/plan/provider_execution_trace_schema_plan.md` | 8 | active implementation plan | human context | task-load | none | none | defines provider-like execution trace schema before mock helper or sandbox work |
| `docs/reports/provider_execution_trace_schema_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits trace schema authorization, privacy, and false-confidence risks |
| `docs/reports/provider_execution_trace_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | provider execution trace fixture tests | none | fixture-only trace bundle evidence without provider execution runtime |
| `docs/reports/provider_execution_trace_validator_helper_report.md` | 8 | completed implementation report | human context | lazy | provider execution trace validator helper | none | pure parsed-dict trace validator evidence without validate integration or execution runtime |
| `docs/plan/provider_execution_trace_validate_output_contract_plan.md` | 8 | historical/superseded | human context | lazy | provider execution trace validate integration | `docs/reports/provider_execution_trace_validate_integration_report.md` | defines future validate target/output contract for provider execution trace static validation |
| `docs/reports/provider_execution_trace_validate_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits trace validate output misclassification and execution-authorization confusion risks |
| `docs/reports/provider_execution_trace_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <provider-trace.json>` | none | provider execution trace static validation integration evidence |
| `docs/reports/provider_execution_trace_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | provider execution trace validate output contract tests | none | native JSON/envelope v2 contract stabilization evidence |
| `docs/reports/provider_execution_trace_rule_promotion_audit.md` | 8 | historical/superseded | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | `docs/reports/provider_execution_trace_runtime_rule_promotion_report.md` | recommended provider execution trace validation rule promotion targets and safe parallel follow-up tracks |
| `docs/reports/provider_execution_trace_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | none | provider execution trace validation rule promotion evidence |
| `docs/reports/subprocess_sandbox_architecture_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits subprocess sandbox risk tier, containment limits, and execution-blocking gates |
| `docs/plan/subprocess_sandbox_architecture_plan.md` | 8 | active implementation plan | human context | task-load | none | none | defines design-only subprocess sandbox architecture requirements before any launcher or execution work |
| `docs/plan/sandbox_policy_fixture_contract_plan.md` | 8 | historical/superseded | human context | lazy | sandbox policy fixtures/tests | `docs/reports/sandbox_policy_fixture_bundle_report.md` | defines fixture-only sandbox policy schema, layout, validation expectations, and no-write evidence model |
| `docs/reports/sandbox_policy_fixture_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox policy fixture confusion, path/env/resource risks, and execution-blocking boundaries |
| `docs/reports/sandbox_policy_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | sandbox policy fixture tests | none | fixture-only sandbox policy bundle evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_policy_validator_helper_report.md` | 8 | completed implementation report | human context | lazy | sandbox policy validator helper | none | pure parsed-dict sandbox policy validator evidence without validate integration or execution runtime |
| `docs/plan/sandbox_policy_validate_output_contract_plan.md` | 8 | historical/superseded | human context | lazy | `aios validate <sandbox-policy.json>` | `docs/reports/sandbox_policy_validate_integration_report.md` | defines future `aios validate <sandbox-policy.json>` native JSON/envelope v2 output contract without execution runtime |
| `docs/reports/sandbox_policy_validate_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox policy validate output, target detection, and execution-authorization confusion risks |
| `docs/reports/sandbox_policy_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <sandbox-policy.json>` | none | sandbox policy static validation integration evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_policy_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | sandbox policy validate output contract tests | none | native JSON/envelope v2 contract stabilization evidence for sandbox policy static validation |
| `docs/reports/sandbox_policy_rule_promotion_audit.md` | 8 | historical/superseded | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | `docs/reports/sandbox_policy_runtime_rule_promotion_report.md` | recommends split promotion to validation rules with sync safety pointer for sandbox policy static validation |
| `docs/reports/sandbox_policy_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | none | sandbox policy validation runtime rule promotion evidence |
| `docs/plan/sandbox_execution_result_fixture_contract_plan.md` | 8 | historical/superseded | human context | lazy | sandbox execution result fixtures/tests | `docs/reports/sandbox_execution_result_fixture_bundle_report.md` | defines fixture-only sandbox execution result schema, no-write evidence, and status/failure-code contract before launcher work |
| `docs/reports/sandbox_execution_result_fixture_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox result fixture authorization, no-write evidence, and trace/result boundary risks |
| `docs/reports/sandbox_execution_result_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | sandbox execution result fixture tests | none | fixture-only sandbox result bundle evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_execution_result_validator_helper_report.md` | 8 | completed implementation report | human context | lazy | sandbox execution result validator helper | none | pure parsed-dict sandbox result validator evidence without validate integration or execution runtime |
| `docs/plan/sandbox_result_validate_output_contract_plan.md` | 8 | historical/superseded | human context | lazy | `aios validate <sandbox-result.json>` | `docs/reports/sandbox_result_validate_integration_report.md` | defines future `aios validate <sandbox-result.json>` native JSON/envelope v2 output contract without execution runtime |
| `docs/reports/sandbox_result_validate_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox result validate target detection and execution-authorization confusion risks |
| `docs/reports/sandbox_result_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <sandbox-result.json>` | none | sandbox result static validation integration evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_result_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | sandbox result validate output contract tests | none | native JSON/envelope v2 contract stabilization evidence for sandbox result static validation |
| `docs/reports/sandbox_result_rule_promotion_audit.md` | 8 | historical/superseded | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | `docs/reports/sandbox_result_runtime_rule_promotion_report.md` | recommends split promotion to validation rules with sync safety pointer for sandbox result static validation |
| `docs/reports/sandbox_result_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | none | sandbox result validation runtime rule promotion evidence |
| `docs/plan/sandbox_trace_fixture_contract_plan.md` | 8 | historical/superseded | human context | lazy | sandbox trace fixtures/tests | `docs/reports/sandbox_trace_fixture_bundle_report.md` | defines fixture-only sandbox trace schema linking sandbox result evidence to provider execution trace metadata without execution authorization |
| `docs/reports/sandbox_trace_fixture_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox trace fixture relationship, authorization, output approval, and false-confidence risks |
| `docs/reports/sandbox_trace_fixture_bundle_report.md` | 8 | completed implementation report | human context | lazy | sandbox trace fixture tests | none | fixture-only sandbox trace bundle evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_trace_validator_helper_report.md` | 8 | completed implementation report | human context | lazy | sandbox trace validator helper | none | pure parsed-dict sandbox trace validator evidence without validate integration or execution runtime |
| `docs/plan/sandbox_trace_validate_output_contract_plan.md` | 8 | active implementation plan | human context | task-load | none | none | defines future sandbox trace validate native JSON/envelope v2 output contract without runtime integration |
| `docs/reports/sandbox_trace_validate_output_contract_risk_audit.md` | 8 | risk audit | human context | task-load | none | none | audits sandbox trace validate target detection, output metadata, and execution-authorization risks |
| `docs/reports/sandbox_trace_validate_integration_report.md` | 8 | completed implementation report | human context | lazy | `aios validate <sandbox-trace.json>` | none | sandbox trace static validation integration evidence without sandbox launcher or execution runtime |
| `docs/reports/sandbox_trace_validate_output_contract_report.md` | 8 | completed implementation report | human context | lazy | sandbox trace validate output contract tests | none | native JSON/envelope v2 contract stabilization evidence for sandbox trace static validation |
| `docs/reports/sandbox_trace_rule_promotion_audit.md` | 8 | risk audit | human context | task-load | none | none | recommends split promotion for sandbox trace static validation into validation rules with sync safety pointer |
| `docs/reports/sandbox_trace_runtime_rule_promotion_report.md` | 8 | completed implementation report | human context | lazy | `.ai/rules/operations/validation.rules.md` and `.ai/rules/operations/sync.rules.md` | none | sandbox trace validation runtime rule promotion evidence |
| `docs/reports/static_validation_surface_completion_audit.md` | 8 | reference-only | human context | summary-first | none | none | closes Phase 8 static validation surface v0 and permits execution readiness audit as the next gate without authorizing execution |
| `docs/reports/execution_readiness_audit.md` | 9 | risk audit | human context | summary-first | none | none | audits readiness for execution architecture approval while keeping sandbox/provider/replay execution blocked |
| `docs/plan/execution_architecture_approval_plan.md` | 9 | active implementation plan | human context | summary-first | none | none | approves design-only execution architecture boundary for future prototype planning without authorizing execution implementation |
| `docs/reports/execution_architecture_approval_risk_audit.md` | 9 | risk audit | human context | task-load | none | none | audits risks of confusing architecture approval with execution implementation authorization |
| `docs/plan/execution_prototype_planning.md` | 10 | active implementation plan | human context | summary-first | none | none | design-only prototype planning boundary, test harness requirements, abort conditions, and implementation readiness gates |
| `docs/reports/execution_prototype_planning_risk_audit.md` | 10 | risk audit | human context | task-load | none | none | audits risks of confusing prototype planning with sandbox/provider execution implementation |
| `docs/reports/current_repository_status_and_remaining_work_audit.md` | 8 | reference-only | human context | summary-first | none | none | audits current repository status, completed capabilities, remaining static work, blocked execution areas, and workflow transition recommendation |
| `docs/roadmap/static_validation_and_execution_readiness_roadmap.md` | 8 | active implementation plan | human context | summary-first | none | none | consolidated roadmap for remaining static validation work, execution readiness gates, blocked execution areas, and bundle-based workflow |

## Context control documents

| Path | Phase | Status | Authority | Load policy | Promoted to | Superseded by | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/reports/context_token_document_sprawl_audit.md` | 8 | risk audit | human context | lazy | none | this index bundle | document sprawl audit |
| `docs/plan/document_consolidation_and_context_control_plan.md` | 8 | historical/superseded | human context | lazy | none | `docs/index/*` | consolidation plan |
| `docs/index/document_status_registry.md` | 8 | reference-only | human context | summary-first | none | none | this registry |
| `docs/index/phase_6_8_summary.md` | 8 | reference-only | human context | summary-first | none | none | compact phase summary |
| `docs/index/current_runtime_context.md` | 8 | reference-only | human context | summary-first | none | none | runtime map, not runtime contract |

## Loading guidance

Recommended order:

1. `.ai/rules/rules.md`
2. relevant `.ai/rules/operations/*.rules.md`
3. `docs/index/current_runtime_context.md`
4. `docs/index/phase_6_8_summary.md`
5. detailed plans/reports only when needed

Do not load completed implementation reports, risk audits, or historical plans by default.
