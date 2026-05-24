# Phase 8 preview 런타임 완료 감사

## 개요

이 문서는 `.ai OS` Phase 8 fixture-backed generated preview 런타임이 v0 기준으로 완료되었는지 감사하고, 다음 안전한 진행 방향을 결정한다.

감사 대상은 generated preview 계약, 위험 감사, fixture 계약, fixture JSON/schema 테스트, fixture-backed provider, dry-run preview 통합, 출력 계약 안정화, sync runtime rules 승격이다. 이번 감사는 문서 작업만 수행하며 런타임 코드와 `.ai` 규칙은 변경하지 않는다.

## 현재 상태

현재 sync runtime은 read-only dry-run 경로에서 opt-in fixture preview 비교를 지원한다.

- `python -m aios sync --dry-run --manifest <path>`
- `--preview-provider fixture`
- `--preview-fixtures <path>`
- clean target에서 read-only `update` 후보 분류
- native `aios.sync_dry_run.v0` preview metadata
- envelope v2 preview metadata
- preview flags가 없을 때 기존 dry-run 동작 유지

Mutation/apply는 계속 차단되어 있다.

## 완료 매트릭스

| 항목 | 상태 | 근거 | 비고 |
| --- | --- | --- | --- |
| contract defined | 완료 | `docs/plan/generated_preview_contract_plan.md` | preview input/output, unavailable reason, hash policy, envelope mapping 정의 |
| risk audited | 완료 | `docs/reports/generated_preview_risk_audit.md` | stale source, nondeterminism, false update, preview/apply 혼동 위험 식별 |
| fixture contract | 완료 | `docs/plan/generated_preview_fixture_contract.md` | fixture layout, required fields, expected classification hints 정의 |
| fixtures added | 완료 | `docs/reports/generated_preview_fixture_bundle_report.md` | input/output/expected JSON fixtures와 schema tests 추가 |
| fixture provider implemented | 완료 | `docs/reports/generated_preview_fixture_provider_report.md` | isolated read-only fixture provider 구현 |
| dry-run integration implemented | 완료 | `docs/reports/dry_run_preview_integration_implementation_report.md` | opt-in CLI flags와 clean-target update 후보 분류 구현 |
| output contract stabilized | 완료 | `docs/reports/phase_8_preview_output_contract_report.md` | native/envelope preview 출력 계약 테스트 고정 |
| runtime rules promoted | 완료 | `docs/reports/phase_8_preview_runtime_rule_promotion_report.md` 및 `.ai/rules/operations/sync.rules.md` | Phase 8 preview behavior를 공식 sync rules에 반영 |
| mutation blocked | 완료 | `.ai/rules/operations/sync.rules.md` | sync apply, mutation, manifest write, real provider, adapter execution 차단 유지 |

## v0 완료 판단

Phase 8 fixture-preview read-only runtime은 v0 기준으로 완료로 판단한다.

판단 근거:

- preview는 명시적 opt-in 경로로만 동작한다.
- fixture-backed provider만 지원되고 기본 provider는 없다.
- clean target에서만 `update` 후보를 만들며, 이는 informational dry-run result일 뿐 write authorization이 아니다.
- source-missing, marker conflict, drift-stop이 preview보다 우선한다.
- preview unavailable은 update 후보를 만들지 않는다.
- native JSON과 envelope v2에서 generated hash와 preview metadata가 보존된다.
- no-preview 기본 dry-run 동작은 유지된다.
- output contract tests가 preview-enabled behavior를 회귀 방지 대상으로 고정했다.
- runtime governance rules가 현재 구현 상태를 반영한다.

따라서 Phase 8의 fixture-preview runtime 목표는 닫을 수 있다. 다만 이는 fixture 기반 read-only 비교 경로의 완료이지, real provider나 adapter generation readiness의 완료가 아니다.

## 남은 격차

| 격차 | 상태 | 영향 |
| --- | --- | --- |
| real preview provider contract | 미완료 | fixture provider를 실제 deterministic provider로 확장하기 전 필요 |
| adapter execution boundary | 미완료 | adapter를 실행할 수 있는 조건, 입력, 출력, 실패 정책이 아직 없음 |
| repository-wide unmanaged/orphan scan | 미완료 | 현재는 manifest target scope 중심이며 broad scan은 없음 |
| default manifest discovery | 미완료 | `--manifest` 명시가 계속 필요함 |
| activation-driven preview selection | 미완료 | activation v1이 preview provider나 source selection을 선택하지 않음 |
| transaction/rollback readiness | 미완료 | mutation 전 transaction storage와 rollback dry-run 계약이 더 필요함 |
| sync apply architecture | 미완료 | mutation gate가 없으며 apply 설계도 아직 승인되지 않음 |
| docs consolidation | 부분 필요 | Phase 6-8 문서가 많아져 요약/색인 정리가 유용함 |

## 다음 방향 후보 평가

| 후보 | 위험 | 의존성 | 사용자 가치 | 구현 준비도 | mutation 근접도 | 평가 |
| --- | --- | --- | --- | --- | --- | --- |
| real preview provider contract | 중간 | Phase 8 fixture provider, preview contract | 높음 | 높음 | 낮음 | 다음 단계로 적합 |
| adapter generation planning | 높음 | real provider contract, adapter boundary | 중간 | 중간 | 중간 | 아직 이르다 |
| repository-wide unmanaged/orphan scan planning | 중간 | manifest scope policy, scan limits | 중간 | 중간 | 낮음 | 유용하지만 preview 흐름의 다음 직접 단계는 아님 |
| transaction/rollback readiness design | 높음 | apply architecture, storage policy | 높음 | 중간 | 높음 | mutation 전에는 중요하지만 Phase 8 직후 우선순위는 낮음 |
| sync apply architecture design | 매우 높음 | transaction, rollback, marker write, provider contract | 높음 | 낮음 | 매우 높음 | 아직 차단 유지 필요 |
| documentation consolidation | 낮음 | 전체 Phase 6-8 산출물 | 중간 | 높음 | 낮음 | 병행 가능하지만 runtime path를 진전시키지는 않음 |

## 권장 방향

다음 Phase 8 후속 방향은 real preview provider contract 설계가 가장 안전하다.

이유:

- 현재 fixture provider는 provider interface와 dry-run integration을 검증했지만 실제 source-to-preview 생성 계약은 아직 없다.
- real provider를 구현하기 전에 deterministic input/output, adapter boundary, source selection, failure/unavailable policy를 더 엄격히 고정해야 한다.
- 이 방향은 read-only 경계를 유지하면서도 fixture-only 한계를 줄인다.
- sync apply나 adapter generation으로 바로 이동하는 것보다 mutation 위험이 낮다.

## mutation 차단 결정

Mutation은 계속 차단한다.

다음 항목은 승인되지 않았다.

- sync apply
- target mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- adapter execution
- generated content creation
- default preview provider
- activation-driven preview selection
- force
- decommission

Fixture preview의 `action: update`는 read-only 후보 분류이며 쓰기 권한이 아니다.

## 다음 3개 작업

1. Real preview provider contract 설계
   - deterministic provider input/output, adapter boundary, allowed source selection, unavailable/failure policy를 정의한다.
   - adapter execution은 계속 금지하고 provider contract만 설계한다.

2. Real preview provider risk audit 작성
   - nondeterministic output, source/context over-selection, adapter identity drift, generated content noise, stale source, preview/apply boundary confusion을 평가한다.

3. Preview provider interface stabilization plan 작성
   - 현재 fixture provider와 미래 real provider가 공유할 최소 interface, validation hooks, envelope/native output mapping, test strategy를 정의한다.

## 결론

Phase 8 fixture-preview read-only runtime은 v0 기준 완료로 닫을 수 있다. 현재 구현은 안전한 opt-in 비교 경로를 제공하며, preview metadata와 output contract가 테스트와 runtime rules로 고정되어 있다.

다음 단계는 구현이 아니라 real preview provider contract 설계다. Mutation/apply는 별도 readiness gate가 생기기 전까지 계속 차단해야 한다.
