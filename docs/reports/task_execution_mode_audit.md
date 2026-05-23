# 작업 실행 모드 감사

## 개요

이 문서는 `.ai OS` 작업을 계속 마이크로 단계로 진행할지, 즉시 번들 작업으로 전환할지, 또는 소수의 Phase 7 게이트를 마친 뒤 번들 작업으로 전환할지 감사한다.

감사 기준은 선호가 아니라 현재 산출물의 상태, 남은 구현 리스크, 문서 분산 비용, 검증 가능성이다.

이번 감사는 문서 작업만 수행한다. 런타임 코드, `.ai` 규칙, sync 실행, manifest persistence, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation은 구현하지 않는다.

## 검토 대상

- `docs/roadmap/ai-os-execution-roadmap-v1.2.md`
- `docs/reports/roadmap_v1_2_phase_0_5_completion_audit.md`
- `docs/reports/roadmap_v1_2_phase_6_completion_audit.md`
- `docs/plan/phase_7_sync_dry_run_implementation_plan.md`
- `docs/reports/phase_7_entry_risk_assessment.md`
- `docs/plan/sync_manifest_schema_and_validation_plan.md`
- `docs/plan/managed_block_parser_and_anchor_contract.md`
- `docs/plan/hash_normalization_and_fixture_policy.md`
- `docs/plan/sync_dry_run_result_schema.md`
- `docs/plan/drift_detection_and_stop_policy.md`
- `docs/plan/sync_manifest_safety_design.md`
- `docs/plan/managed_block_marker_contract.md`
- `docs/plan/rollback_transaction_precondition_policy.md`

## 현재 Phase 상태

| 영역 | 상태 | 근거 | 판단 |
|---|---|---|---|
| Phase 0-5 runtime kernel | 구현 또는 안정화 완료 | inspect, inventory, validate, activation v0/v1, load-context budget, envelope v2 | 구현 기반은 충분하다 |
| Phase 6 sync/manifest safety design | 완료 | manifest safety, drift stop, dry-run schema, marker contract, rollback policy, sync rules | Phase 7 계획 진입 가능 |
| Phase 7 planning | 진행 중 | implementation plan, entry risk, manifest schema, parser/anchor, hash normalization | 구현 직전 정리 단계 |
| Phase 7 runtime implementation | 미시작 | sync runtime code 없음 | 아직 코드 번들 진입 전 |
| 시스템 쓰기 동작 | 없음 | read-only boundary 유지 | 안전 경계 유지됨 |

## 완료된 Phase 7 게이트 매트릭스

| 게이트 | 상태 | 근거 문서 | 구현 전 신뢰도 |
|---|---|---|---|
| dry-run output schema | 완료 | `docs/plan/sync_dry_run_result_schema.md` | 높음 |
| envelope v2 mapping | 완료 | `docs/plan/sync_dry_run_result_schema.md`, `docs/plan/phase_7_sync_dry_run_implementation_plan.md` | 높음 |
| manifest schema precision | 완료 | `docs/plan/sync_manifest_schema_and_validation_plan.md` | 높음 |
| manifest validation boundary | 완료 | `docs/plan/sync_manifest_schema_and_validation_plan.md` | 높음 |
| managed block parser fixture contract | 완료 | `docs/plan/managed_block_parser_and_anchor_contract.md` | 높음 |
| insertion anchor contract | 완료 | `docs/plan/managed_block_parser_and_anchor_contract.md` | 높음 |
| hash normalization decision | 완료 | `docs/plan/hash_normalization_and_fixture_policy.md` | 높음 |
| hash fixture strategy | 완료 | `docs/plan/hash_normalization_and_fixture_policy.md` | 높음 |
| drift/conflict taxonomy | 완료 | `docs/plan/drift_detection_and_stop_policy.md` | 높음 |
| marker safety contract | 완료 | `docs/plan/managed_block_marker_contract.md`, `docs/plan/managed_block_parser_and_anchor_contract.md` | 높음 |

## 미완료 또는 부분 완료 게이트 매트릭스

| 게이트 | 상태 | 남은 내용 | 번들 전 필요성 |
|---|---|---|---|
| implementation task breakdown | 미완료 | 모듈별 구현 순서, 테스트 순서, 커밋 단위, CLI wiring 순서 | 필수 |
| concrete fixture file list | 부분 완료 | fixture category는 있으나 실제 파일명, expected JSON, 최소 fixture 세트가 하나의 실행 목록으로 묶이지 않음 | 필수에 가까움 |
| manifest preview strategy | 부분 완료 | manifest file input 우선 권고는 있으나 preview 미지원 상태의 CLI 동작을 첫 구현 범위로 고정해야 함 | 필수 |
| default manifest path policy | 부분 완료 | `--manifest` 없는 dry-run의 초기 동작을 fail로 둘지 preview unavailable로 둘지 확정 필요 | 필수 |
| result ordering contract | 부분 완료 | manifest order 우선 원칙은 있으나 orphan/unmanaged 발견 순서 fixture가 필요 | 권장 |
| native schema fixture examples | 부분 완료 | 샘플은 있으나 테스트 fixture expected output으로 고정되지 않음 | 권장 |
| CLI usage-error fixture | 부분 완료 | exit code 2 원칙은 있으나 sync command용 fixture/test 목록으로 고정 필요 | 권장 |
| package integration boundary | 부분 완료 | 후보 모듈은 있으나 기존 `aios` CLI 구조에 붙이는 순서가 미정 | 필수 |

## 즉시 번들 작업으로 전환할 때의 위험

| 위험 | 가능성 | 영향 | 근거 | 완화 가능성 |
|---|---:|---:|---|---|
| 용어 drift | 중간 | 중간 | Phase 6-7 문서가 많고 일부 용어가 후보에서 확정으로 전환됨 | 구현 작업 분해 문서에서 canonical 용어 표를 만들면 완화 가능 |
| 숨은 설계 충돌 | 낮음~중간 | 높음 | 핵심 게이트는 닫혔지만 manifest input/default path 정책은 아직 부분 결정 | 첫 번들을 코드가 아닌 구현 준비 번들로 잡으면 완화 가능 |
| Codex 변경 범위 과대화 | 중간 | 높음 | sync dry-run은 CLI, parser, hash, manifest, result, envelope를 모두 건드림 | 첫 코드 번들을 manifest/hash/parser 중 하나로 제한해야 함 |
| 문서 난립 | 높음 | 중간 | 최근 작업이 plan/report pair 단위로 누적됨 | 이후에는 하나의 bundle plan/report로 묶어야 함 |
| 검증 누락 | 중간 | 높음 | sync 구현은 exit code, JSON shape, fixture, read-only 보장을 같이 검증해야 함 | 번들별 validation checklist가 필요 |

## 마이크로 단계 지속의 위험

| 위험 | 가능성 | 영향 | 근거 | 완화 가능성 |
|---|---:|---:|---|---|
| 작업 overhead | 높음 | 중간 | 한 게이트당 plan/report pair와 커밋이 반복됨 | 전환 기준을 명시하면 완화 |
| momentum 저하 | 높음 | 중간 | 구현 진입 전 문서 작업이 계속 늘어남 | 남은 게이트를 하나의 전환 번들로 묶어야 함 |
| 문서 파편화 | 높음 | 중간 | 같은 정책이 여러 문서에서 반복됨 | 실행용 bundle transition plan으로 연결해야 함 |
| 반복적인 context reconstruction | 높음 | 중간 | 매 작업마다 Phase 6-7 문서 재검토가 필요 | bundle plan이 현재 상태를 요약해야 함 |
| 의사결정 지연 | 중간 | 높음 | 구현에 필요한 결정 대부분이 이미 내려짐 | micro-step 종료 지점을 확정해야 함 |

## 마이크로 단계와 번들 실행 비교

| 기준 | 마이크로 단계 | 번들 실행 | 현재 적합성 |
|---|---|---|---|
| 설계 불확실성 처리 | 강함 | 약함 | 핵심 불확실성은 대부분 해소됨 |
| 변경 범위 통제 | 강함 | 중간 | 코드 구현 전에는 여전히 중요 |
| 커밋 수 | 많음 | 적음 | 현재 커밋 수가 과도해지는 문제가 있음 |
| 검증 집중도 | 낮아질 수 있음 | 높일 수 있음 | 번들별 검증 목록이 있으면 번들이 유리 |
| 문서 일관성 | 파편화 위험 | 통합 가능 | 현재는 번들 쪽이 유리 |
| 구현 속도 | 느림 | 빠름 | Phase 7 진입에는 번들이 유리 |
| 안전성 | 매우 높음 | 범위 설계에 의존 | 첫 번들은 read-only 준비 작업으로 제한해야 안전 |

## 감사 판단

즉시 런타임 코드 번들로 전환하는 것은 아직 이르다. 그러나 지금처럼 plan/report pair를 하나씩 계속 만드는 마이크로 단계도 더 이상 효율적이지 않다.

권고는 세 번째 선택지다.

1. 남은 Phase 7 전환 게이트를 하나의 작은 번들로 마친다.
2. 그 뒤부터는 bundled task execution으로 전환한다.
3. 첫 코드 번들은 `aios sync --dry-run` 전체 구현이 아니라 read-only foundation slice로 제한한다.

## 권장 전환 지점

번들 실행으로 전환할 정확한 지점은 다음 산출물이 완료된 직후다.

- Phase 7 implementation task breakdown
- 최소 fixture inventory
- 첫 구현 번들 범위와 제외 범위
- validation command set
- commit strategy

이 산출물은 별도 마이크로 작업 여러 개가 아니라 하나의 전환 번들로 처리하는 것이 적절하다.

## 첫 제안 번들

첫 안전 번들은 런타임 구현이 아니라 `Phase 7 dry-run implementation readiness bundle`이어야 한다.

목표:

- Phase 7 코드를 시작하기 전에 구현 순서와 fixture 최소 세트를 하나로 고정한다.

포함 작업:

- sync dry-run 모듈별 작업 분해
- 최소 fixture 세트 정의
- manifest input 정책 확정
- `--manifest` 없는 초기 동작 확정
- read-only 보장 테스트 목록 정의
- 첫 코드 번들 범위 정의

제외 작업:

- runtime code 작성
- sync 실행
- manifest persistence
- transaction log persistence
- rollback 실행
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

예상 산출물:

- `docs/plan/phase_7_sync_dry_run_task_breakdown.md`
- `docs/reports/phase_7_bundle_readiness_audit.md`

검증:

```bash
git diff --check
git diff --cached --check
```

커밋 전략:

- 위 두 문서를 하나의 커밋으로 묶는다.
- 이후 코드 구현은 기능 slice별 번들 커밋으로 전환한다.

## 결론

마이크로 단계는 Phase 6 안전 설계와 Phase 7 핵심 게이트를 닫는 데 효과적이었다. 하지만 현재는 핵심 설계 결정이 충분히 축적되었고, 마이크로 커밋을 계속할수록 문서 파편화와 작업 overhead가 커진다.

따라서 `.ai OS` 작업은 즉시 대형 코드 번들로 넘어가지 말고, 한 번의 작은 전환 번들을 완료한 뒤 bundled task execution으로 전환하는 것이 가장 안전하다.
