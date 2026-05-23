# 작업 번들 전환 계획

## 개요

이 문서는 `.ai OS` Phase 7 작업을 마이크로 단계 중심에서 bundled task execution으로 전환하기 위한 실행 계획이다.

전환의 목적은 안전 설계를 유지하면서도 plan/report pair가 과도하게 늘어나는 문제를 줄이고, 구현 진입 시 검증 가능한 작업 단위로 묶는 것이다.

이 계획은 문서 작업이다. 런타임 코드, `.ai` 규칙, sync 실행, manifest persistence, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation은 구현하지 않는다.

## 전환 원칙

- 설계 불확실성이 높은 항목은 마이크로 단계로 처리한다.
- 이미 결정된 정책을 구현 가능한 단위로 묶을 때는 번들로 처리한다.
- 번들은 하나의 목표, 명확한 제외 범위, 고정된 validation command를 가져야 한다.
- 번들 하나가 여러 runtime boundary를 동시에 깨면 안 된다.
- 첫 코드 번들은 mutation 없는 read-only foundation이어야 한다.
- 모든 Phase 7 번들은 no sync apply, no manifest write, no rollback execution을 기본 제외 범위로 둔다.

## 권장 전환 결정

권장안:

```text
finish one small transition bundle, then switch to bundled execution
```

이유:

- manifest schema precision은 완료되었다.
- manifest validation boundary는 완료되었다.
- managed block parser fixture contract는 완료되었다.
- insertion anchor contract는 완료되었다.
- hash normalization decision은 완료되었다.
- dry-run output schema와 envelope v2 mapping도 이미 정의되었다.
- 남은 일은 독립 설계보다 구현 순서, fixture 최소 세트, CLI 초기 정책을 하나로 묶는 작업에 가깝다.

## 즉시 중단할 마이크로 단계 패턴

다음 패턴은 더 이상 반복하지 않는 것이 좋다.

- 단일 세부 정책마다 plan/report pair를 하나씩 추가
- 이미 결정된 non-goal을 새 문서마다 반복
- 같은 Phase 7 게이트를 다른 제목으로 재감사
- 코드 구현 없이 세부 fixture 이름만 별도 커밋으로 분리

예외:

- 새로운 safety conflict가 발견된 경우
- 기존 runtime-facing rule과 충돌하는 정책이 발견된 경우
- mutation boundary를 바꾸는 결정이 필요한 경우

## 전환 전 마지막 번들

### Bundle 0: Phase 7 Dry-run Readiness Bundle

목표:

- Phase 7 `aios sync --dry-run` 구현을 시작하기 전에 남은 실행 준비 결정을 하나로 고정한다.

포함 작업:

- implementation task breakdown 작성
- 최소 fixture inventory 작성
- manifest input mode 확정
- `--manifest` 없는 초기 동작 확정
- read-only invariant 테스트 목록 작성
- first code bundle 범위 확정
- fixture와 module 간 추적표 작성

제외 작업:

- runtime code 구현
- CLI command 추가
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

산출물:

- `docs/plan/phase_7_sync_dry_run_task_breakdown.md`
- `docs/reports/phase_7_bundle_readiness_audit.md`

검증 명령:

```bash
git diff --check
git diff --cached --check
```

커밋 메시지 후보:

```text
docs(aios): prepare phase 7 dry-run bundle
```

완료 기준:

- 구현 모듈별 첫 작업 순서가 정해져 있다.
- 최소 fixture 목록이 정해져 있다.
- 첫 코드 번들이 무엇을 구현하지 않을지 명확하다.
- `--manifest` 없는 초기 동작이 정해져 있다.
- read-only 검증 명령이 정의되어 있다.

## 첫 코드 번들 제안

### Bundle 1: Sync Dry-run Foundation

목표:

- sync dry-run의 read-only foundation을 만든다.

포함 작업:

- `src/aios/sync/` package skeleton
- manifest model and validation parser
- hash helper with v0 policy
- native result model
- fixture files for manifest/hash validation
- no CLI mutation behavior

제외 작업:

- target mutation
- manifest write
- marker insertion
- marker repair
- adapter generation
- rollback
- force
- decommission

예상 검증:

```bash
python -m pytest tests/test_sync_manifest.py
python -m pytest tests/test_sync_hash.py
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

커밋 전략:

- manifest/hash foundation을 하나의 코드 번들로 커밋한다.
- parser와 CLI wiring은 다음 번들로 분리한다.

## 두 번째 코드 번들 제안

### Bundle 2: Managed Marker Parser

목표:

- managed block marker parser를 read-only analyzer로 구현한다.

포함 작업:

- marker detection
- begin/end pairing
- code fence exclusion
- duplicate/nested/malformed classification
- parser output model
- parser fixtures

제외 작업:

- marker insertion
- marker repair
- sync apply
- target write

예상 검증:

```bash
python -m pytest tests/test_sync_markers.py
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

## 세 번째 코드 번들 제안

### Bundle 3: Sync Dry-run CLI Evaluation

목표:

- `python -m aios sync --dry-run`을 read-only evaluator로 연결한다.

포함 작업:

- CLI command registration
- `--dry-run` required policy
- `--manifest <path>` input
- manifest validation before evaluation
- source/target existence checks
- marker parser integration
- hash comparison
- drift/conflict classification
- native JSON output
- envelope v2 mapping

제외 작업:

- sync apply
- manifest write
- transaction logs
- rollback execution
- adapter generation
- force
- decommission

예상 검증:

```bash
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/valid.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/marker_conflict.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/drift_stop.json --json --envelope-v2
python -m aios sync --envelope-v2
python -m aios inspect
python -m aios validate
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
git diff --cached --check
```

## 번들 커밋 정책

- 문서 전환 번들은 문서만 포함한다.
- 코드 번들은 가능한 한 하나의 runtime slice만 포함한다.
- fixture와 해당 구현은 같은 커밋에 둘 수 있다.
- `.ai` rules 변경은 별도 promotion 작업으로 분리한다.
- validation failure가 있으면 커밋하지 않는다.
- generated artifact나 source mutation이 생기면 번들을 중단하고 범위를 재검토한다.

## 번들 모드 시작 조건

Bundle 0이 완료되면 마이크로 단계는 종료하고 번들 모드로 전환한다.

전환 후 기본 단위:

- 하나의 구현 목표
- 하나의 주요 module boundary
- 하나의 fixture family
- 하나의 validation command set
- 하나의 커밋

## 결론

현재 상태에서 계속 마이크로 계획을 추가하는 것은 이득보다 비용이 커지고 있다. 하지만 즉시 전체 `aios sync --dry-run` 구현 번들로 들어가는 것은 범위가 넓다.

따라서 다음 작업은 작은 전환 번들 하나로 Phase 7 구현 준비를 고정하고, 이후부터 manifest/hash, marker parser, CLI evaluation 순서의 코드 번들로 전환하는 것이 적절하다.
