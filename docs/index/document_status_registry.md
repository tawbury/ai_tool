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
| `.ai/rules/operations/sync.rules.md` | 6-8 | runtime-facing contract | runtime | task-load | self | none | sync dry-run, manifest, fixture preview runtime rules |

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
