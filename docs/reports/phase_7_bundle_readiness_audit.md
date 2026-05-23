# Phase 7 번들 준비 감사

## 개요

이 문서는 Phase 7 `aios sync --dry-run` 런타임 구현을 시작하기 전에 readiness bundle이 충분한지 감사한다. 감사 대상은 구현 코드가 아니라 구현 진입 조건, 번들 경계, fixture 최소 세트, CLI 계약, read-only 불변 조건이다.

이번 감사는 문서 작업만 수행한다. 런타임 코드, `.ai` 규칙, sync 실행, manifest persistence, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation은 구현하지 않는다.

## 감사 대상

- `docs/reports/task_execution_mode_audit.md`
- `docs/plan/task_bundle_transition_plan.md`
- `docs/plan/phase_7_sync_dry_run_implementation_plan.md`
- `docs/plan/sync_manifest_schema_and_validation_plan.md`
- `docs/plan/managed_block_parser_and_anchor_contract.md`
- `docs/plan/hash_normalization_and_fixture_policy.md`
- `docs/plan/sync_dry_run_result_schema.md`
- `docs/plan/drift_detection_and_stop_policy.md`
- `docs/plan/phase_7_sync_dry_run_task_breakdown.md`

## Readiness 판단

Phase 7 runtime implementation은 이제 시작 가능하다. 단, 시작 가능한 범위는 전체 `aios sync --dry-run` 구현이 아니라 Bundle 1 `Manifest/Hash Foundation`이다.

감사 판단:

- micro-step planning은 이 지점에서 종료해도 된다.
- bundled runtime implementation으로 전환해도 된다.
- 첫 번들은 manifest/hash foundation으로 제한해야 한다.
- CLI-visible sync command는 Bundle 3까지 기다리는 것이 안전하다.

## 완료된 게이트

| 게이트 | 상태 | 근거 | 판단 |
|---|---|---|---|
| manifest schema precision | 완료 | `sync_manifest_schema_and_validation_plan.md` | 구현 가능 |
| manifest validation boundary | 완료 | `sync_manifest_schema_and_validation_plan.md` | 구현 가능 |
| dry-run output schema | 완료 | `sync_dry_run_result_schema.md` | 구현 가능 |
| drift/conflict taxonomy | 완료 | `drift_detection_and_stop_policy.md` | 구현 가능 |
| marker contract | 완료 | `managed_block_marker_contract.md`, `managed_block_parser_and_anchor_contract.md` | 구현 가능 |
| parser fixture contract | 완료 | `managed_block_parser_and_anchor_contract.md` | 구현 가능 |
| insertion anchor contract | 완료 | `managed_block_parser_and_anchor_contract.md` | 구현 가능 |
| hash normalization policy | 완료 | `hash_normalization_and_fixture_policy.md` | 구현 가능 |
| envelope v2 mapping boundary | 완료 | `sync_dry_run_result_schema.md`, `phase_7_sync_dry_run_implementation_plan.md` | 구현 가능 |
| task bundle sequence | 완료 | `phase_7_sync_dry_run_task_breakdown.md` | 구현 가능 |

## 남은 리스크

| 리스크 | 심각도 | 현재 대응 | 구현 중 stop 조건 |
|---|---:|---|---|
| fixture가 아직 실제 파일로 없음 | 중간 | Bundle 1-2에서 fixture와 구현을 같이 추가 | fixture 없이 정책 구현 필요 시 중단 |
| CLI 구조와 sync command 연결 방식 미확인 | 중간 | Bundle 3으로 지연 | 기존 CLI behavior를 깨야 하면 중단 |
| generated preview 부재 | 중간 | 초기 구현은 generated hash를 null/unavailable로 제한 | preview generation이 필요해지면 중단 |
| default manifest discovery 미정 | 낮음~중간 | 첫 구현은 `--manifest` required로 고정 | discovery가 필요해지면 별도 설계 |
| manifest validation을 `aios validate`에 즉시 통합하고 싶어질 가능성 | 중간 | 첫 구현은 sync internal validation 우선 | validate integration이 필요하면 별도 bundle |
| orphan/unmanaged discovery 범위 확대 | 중간 | manifest-driven evaluation 우선 | repository-wide scan이 필요해지면 중단 |

## 구현 번들 승인 범위

### 승인: Bundle 1

Bundle 1은 시작 가능하다.

승인 범위:

- `src/aios/sync/` package skeleton
- manifest model
- manifest schema validation
- path safety validation
- hash format validation
- observed UTF-8 bytes hash helper
- manifest/hash unit fixtures
- compileall and regression checks

조건:

- CLI-visible `sync` command는 추가하지 않아도 된다.
- target write는 없어야 한다.
- manifest write는 없어야 한다.
- fixture와 tests는 같은 bundle에 포함할 수 있다.

### 조건부 승인: Bundle 2

Bundle 2는 Bundle 1이 통과한 뒤 시작 가능하다.

조건:

- marker parser는 read-only analyzer여야 한다.
- parser는 action을 최종 결정하지 않는다.
- parser는 marker insertion/repair를 수행하지 않는다.

### 보류: Bundle 3

Bundle 3은 Bundle 1-2가 통과한 뒤 시작해야 한다.

보류 이유:

- CLI-visible command는 회귀 영향이 더 크다.
- evaluator는 manifest/hash/parser/result 경계가 먼저 안정되어야 한다.
- envelope v2 mapping은 result shape가 안정된 뒤 연결해야 한다.

## CLI 계약 감사

| 항목 | 결정 | 상태 |
|---|---|---|
| `sync` without `--dry-run` | usage error, exit code 2 | 확정 |
| `--manifest <path>` | 첫 구현의 필수 input | 확정 |
| missing `--manifest` | usage/config error, exit code 2 | 확정 |
| `--json --envelope-v2` | 허용 | 확정 |
| `--envelope-v2` without `--json` | usage error, exit code 2 | 확정 |
| warning-only dry-run | status `warn`, exit code 0 | 확정 |
| blocking dry-run | status `fail`, exit code 1 | 확정 |
| default manifest discovery | 첫 구현 제외 | freeze |
| manifest preview generation | 첫 구현 제외 | freeze |

## Read-only invariant 감사

다음 동작은 Phase 7 첫 구현 번들 전체에서 금지된다.

- target file create/update/delete
- manifest create/update/delete
- transaction log create/update/delete
- marker begin/end insertion
- anchor insertion
- marker repair
- adapter file generation
- rollback execution
- force overwrite
- decommission
- `.ai/registry/` creation
- source mutation

감사 판단:

- 현재 계획은 read-only invariant를 만족한다.
- Bundle 1은 특히 filesystem read와 fixture/test 파일 추가 외 런타임 쓰기 동작이 없다.
- Bundle 3에서 CLI가 추가되더라도 dry-run evaluator는 write path를 포함하면 안 된다.

## Dependency graph 감사

```text
shared primitives and repository root handling
  -> manifest validation
  -> dry-run evaluator

manifest schema
  -> manifest.py
  -> result item source fields

hash policy
  -> hash.py
  -> drift-stop classification

marker contract
  -> markers.py
  -> managed block hash boundary

result schema
  -> result.py
  -> native JSON
  -> envelope v2 mapping

CLI
  -> dry_run.py
  -> result.py
```

감사 판단:

- 의존성은 단방향이며 Bundle 1-3 순서와 일치한다.
- envelope v2는 evaluator core가 아니라 serialization boundary에 두는 것이 맞다.
- inventory/shared primitives는 path/root/reference validation에만 제한적으로 사용해야 한다.

## 구현 중 freeze boundary

다음 요구가 나타나면 Phase 7 구현을 확장하지 말고 별도 설계 또는 후속 bundle로 분리해야 한다.

- manifest preview가 없으면 CLI가 쓸모없다는 판단
- default manifest path를 자동으로 만들고 싶다는 요구
- adapter generation으로 generated content를 만들자는 요구
- marker missing을 자동 삽입하자는 요구
- drift-stop을 자동 repair하자는 요구
- force 옵션이 필요하다는 요구
- rollback dry-run을 같이 넣자는 요구
- `aios validate <manifest>` 통합을 같은 bundle에 넣자는 요구
- activation v1에서 sync selection을 바로 끌어오자는 요구

## Phase 7 readiness summary

완료된 gates:

- Phase 6 safety design
- sync runtime rule promotion
- Phase 6 completion audit
- Phase 7 implementation plan
- manifest schema and validation plan
- managed block parser and anchor contract
- hash normalization and fixture policy
- task execution mode audit
- task bundle transition plan
- Phase 7 task breakdown

remaining risks:

- 실제 fixture 파일은 아직 없다.
- 기존 CLI 구조에 sync command를 연결하는 방식은 구현 시 확인해야 한다.
- generated preview가 없는 동안 update candidate의 generated hash는 제한적으로 표현해야 한다.
- repository-wide orphan/unmanaged scan은 첫 구현에서 제외해야 한다.

approved first runtime slice:

- Bundle 1: Manifest/Hash Foundation

## 최종 결론

Phase 7 readiness bundle은 완료되었다. 이제 마이크로 planning을 계속하지 말고 bundled runtime implementation으로 전환하는 것이 적절하다.

다음 작업은 코드 구현이지만 범위는 반드시 Bundle 1 `Manifest/Hash Foundation`으로 제한해야 한다. 전체 `aios sync --dry-run` CLI까지 한 번에 구현하는 것은 아직 과도하다.
