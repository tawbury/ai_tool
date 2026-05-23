# Phase 7 Read-only Runtime Completion Audit

## 개요

이 문서는 Roadmap v1.2 Phase 7의 읽기 전용 sync 평가 런타임이 Bundle 1-4 범위에서 완료되었는지 감사한다. 감사 범위는 manifest/hash foundation, managed marker parser, sync dry-run CLI evaluator, manifest validate integration까지이며, sync apply나 파일 변경 기능은 포함하지 않는다.

현재 Phase 7 런타임은 다음 읽기 전용 기능을 제공한다.

- `src/aios/sync/manifest.py`: sync manifest v0 모델, 로더, 정적 검증
- `src/aios/sync/hash.py`: observed UTF-8 bytes 기반 sha256 해시 헬퍼
- `src/aios/sync/markers.py`: managed marker와 insertion anchor 분석
- `src/aios/sync/result.py`: dry-run 결과 모델
- `src/aios/sync/dry_run.py`: manifest 기반 dry-run 평가
- `python -m aios sync --dry-run --manifest <path>`: 명시 manifest 기반 읽기 전용 평가
- `python -m aios validate <sync-manifest.json>`: sync manifest 정적 검증

## 검토 문서

검토한 Bundle 1-4 보고서는 다음과 같다.

- `docs/reports/phase_7_bundle_1_manifest_hash_report.md`
- `docs/reports/phase_7_bundle_2_marker_parser_report.md`
- `docs/reports/phase_7_bundle_3_sync_dry_run_report.md`
- `docs/reports/phase_7_bundle_4_manifest_validate_report.md`

검토한 Phase 7 계획 문서는 다음과 같다.

- `docs/plan/phase_7_sync_dry_run_task_breakdown.md`
- `docs/plan/sync_manifest_schema_and_validation_plan.md`
- `docs/plan/managed_block_parser_and_anchor_contract.md`
- `docs/plan/hash_normalization_and_fixture_policy.md`

## 완료 매트릭스

| 영역 | 상태 | 근거 | 남은 범위 |
| --- | --- | --- | --- |
| Manifest/hash foundation | 완료 | Bundle 1에서 manifest v0 schema validation, path safety, hash format validation, observed UTF-8 bytes hash policy, whole-file/managed-block hash helper가 구현되었다. | hash policy contract snapshot을 더 명시적으로 고정하는 테스트는 안정화 항목으로 남는다. |
| Marker parser | 완료 | Bundle 2에서 markdown/hash/yaml style marker, begin/end pairing, duplicate/nested/malformed/mismatched/unsupported classification, anchor parsing, code fence exclusion이 구현되었다. | fixture coverage는 충분하지만 parser output schema snapshot test는 추가 가능하다. |
| Dry-run evaluator | 완료 | Bundle 3에서 `sync --dry-run --manifest`가 manifest load, source/target existence, marker parsing, hash comparison, action/status classification, human/JSON/envelope output을 제공한다. | generated preview, default manifest discovery, broad unmanaged scan은 의도적으로 제외되었다. |
| Validate manifest integration | 완료 | Bundle 4에서 `aios validate <manifest.json>`이 `aios.sync_manifest.v0` 파일을 first-class target으로 인식하고 정적 schema 오류를 validate 결과로 변환한다. | manifest validate의 envelope v2 fixture coverage는 안정화 항목이다. |
| Envelope v2 mapping | 완료 | sync dry-run은 envelope v2를 지원하고 validate는 기존 envelope v2 경로를 보존한다. | sync manifest validate 전용 envelope fixture와 contract test는 보강 대상이다. |
| Fixture coverage | 완료 | manifest/hash, marker parser, dry-run evaluator, validate integration 각각에 핵심 정상/오류 fixture가 추가되었다. | CLI 출력 snapshot과 schema contract fixture는 추가하면 회귀 방지에 유용하다. |
| Read-only invariant | 완료 | 구현 범위는 분석, 검증, 해시 계산, 결과 출력에 한정되며 target mutation, manifest write, transaction log, marker insertion/repair/delete가 없다. | mutation 진입 전 transaction/rollback storage 설계와 별도 승인 gate가 필요하다. |

## 남은 갭

### Dry-run Human Output UX

현재 human output은 v0 사용에는 충분하지만, 장기적으로는 action별 grouping, blocking reason 강조, recovery hint 노출 방식이 더 정리될 필요가 있다. 기능 완성의 blocker는 아니며 안정화 bundle에서 다루는 것이 적절하다.

### Snapshot/Contract Tests

핵심 unit/e2e 테스트는 존재하지만 JSON shape, envelope v2 mapping, human output에 대한 snapshot 또는 contract test는 부족하다. Phase 7 v0 완료 판단을 막지는 않지만, 이후 refactor 전에 보강해야 한다.

### Manifest Validate Envelope v2 Fixture Coverage

`aios validate`의 envelope v2 지원 경로는 유지되지만, sync manifest target 전용 envelope v2 fixture는 더 명시적으로 추가할 수 있다. 이는 안정화 과제이며 runtime capability gap은 아니다.

### Repository-wide Orphan/Unmanaged Scan

현재 dry-run은 broad repository scan을 수행하지 않는다. 이는 Bundle 3 non-goal과 일치한다. repository-wide orphan/unmanaged scan은 성능, scope boundary, false positive 정책이 필요하므로 별도 계획이 필요하다.

### Generated Preview Contract

현재 dry-run은 generated preview content를 만들지 않는다. 따라서 clean target에서는 skip 또는 drift 상태를 판단할 수 있지만, future generated output과의 update 후보 비교는 하지 않는다. adapter generation과 preview generation이 아직 금지되어 있으므로 별도 contract planning 이후에만 확장해야 한다.

### Sync Runtime Rule Update

`.ai/rules/operations/sync.rules.md`는 Phase 6 safety design 중심이다. Phase 7에서 실제로 구현된 `sync --dry-run --manifest`와 `validate <sync manifest>` behavior는 별도 문서화/규칙 승격 작업에서 반영하는 것이 좋다. 이 감사 작업에서는 `.ai` rules를 수정하지 않는다.

### Docs Consolidation Risk

Phase 6-7에서 계획서와 보고서가 많이 생성되었다. 설계 추적성은 높아졌지만, 다음 작업자가 빠르게 현재 runtime contract를 파악하기 어렵다. Phase 7 안정화 후에는 sync 관련 planning 문서를 compact index 또는 implementation summary로 묶는 것이 좋다.

### Mutation Readiness Blockers

sync apply나 mutation으로 넘어가기에는 다음 blocker가 남아 있다.

- manifest persistence 위치와 lifecycle
- transaction log schema의 실제 storage 위치
- rollback dry-run result schema와 precondition evaluator
- marker insertion/update/delete 구현 정책
- generated preview content contract
- force/decommission policy
- broad unmanaged/orphan scan scope와 performance policy

## v0 완료 판단

Phase 7 읽기 전용 sync evaluation은 v0 기준으로 완료로 판단한다.

이 판단의 이유는 다음과 같다.

- manifest/hash foundation이 sync dry-run과 validate에서 재사용 가능한 형태로 구현되었다.
- marker parser가 mutation 없이 구조 분석과 conflict-ready classification을 제공한다.
- dry-run CLI가 명시 manifest를 입력으로 받아 read-only evaluation result를 산출한다.
- validate integration이 sync manifest를 first-class validation target으로 다룬다.
- envelope v2, JSON, human output이 최소 runtime contract를 제공한다.
- read-only invariant가 유지되며 mutation-adjacent 기능은 구현되지 않았다.

따라서 Bundle 1-4 구현은 중단해도 된다. Phase 7을 계속 확장하더라도 broad scan, generated preview, mutation 준비 기능을 임의로 섞지 말고 별도 bundle로 나누어야 한다.

## 권장 다음 경로

권장 순서는 다음과 같다.

1. Stabilization bundle
   - sync dry-run JSON/envelope/human output contract test를 추가한다.
   - manifest validate envelope v2 fixture를 보강한다.
   - human output을 blocking result 중심으로 정리한다.
   - 새 runtime capability는 추가하지 않는다.

2. Runtime rule promotion/update
   - `.ai/rules/operations/sync.rules.md`에 구현된 read-only `sync --dry-run --manifest`와 `validate <sync manifest>` behavior를 반영한다.
   - Phase 6 safety-only 문구와 Phase 7 read-only runtime reality를 구분한다.

3. Generated preview contract planning
   - adapter generation 없이 preview input/output shape, generated hash fields, update candidate classification boundary를 먼저 정의한다.

4. Repository-wide scan planning
   - orphan/unmanaged scan scope, directory boundary, performance limit, false positive policy를 별도 설계한다.

5. Mutation readiness design
   - sync apply 구현 전에 manifest persistence, transaction log storage, rollback dry-run, marker insertion/update/delete safety gate를 완료한다.

## Mutation Block Decision

sync apply와 모든 mutation은 계속 차단해야 한다.

차단 상태로 남아야 하는 항목은 다음과 같다.

- target file create/update/delete
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- adapter generation
- generated preview content creation
- force, decommission
- activation-driven sync selection
- default manifest discovery
- repository-wide unmanaged scan

Phase 7 v0의 완료 기준은 read-only evaluation complete이지 mutation-ready가 아니다. mutation은 별도 readiness audit과 safety gate 없이는 시작하면 안 된다.

## 검증

이 작업은 문서 감사만 추가하므로 runtime validation은 수행하지 않는다. 요청된 검증은 다음 diff check로 충분하다.

- `git diff --check`
- `git diff --cached --check`

## 결론

Phase 7 read-only runtime은 v0 범위에서 완료되었다. 다음 작업은 기능 확장보다 stabilization bundle과 runtime rule update가 안전하다. sync apply와 mutation은 여전히 명확히 blocked 상태로 유지해야 한다.
