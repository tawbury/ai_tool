# Sync Dry-run Schema Risk Audit

## 개요

이 문서는 future `aios sync --dry-run` result schema를 설계하면서 발생할 수 있는 표현, 안전, 호환성 위험을 감사한다. 현재 시스템은 read-only이며, 이 감사는 mutation logic이 생기기 전 출력 계약이 어떤 실패를 막아야 하는지 정리한다.

이 문서는 sync execution, manifest persistence, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, source mutation을 구현하지 않는다.

## 감사 범위

감사 대상:

- top-level status 모호성
- action enum 불충분
- severity와 action 불일치
- stop_reason 누락
- recovery_hint 부재
- hash provenance 부족
- marker 상태 표현 부족
- unmanaged target과 orphan marker 혼동
- envelope v2 message mapping 손실
- observability event detail 손실
- force 또는 rollback 구현으로 오해될 위험

## Risk Matrix

| Risk | 영향 | 권장 완화 |
|---|---|---|
| 전체 status가 result 위험도를 숨김 | blocking conflict가 있는데 사용자가 pass로 오해 | blocking item이 하나라도 있으면 `fail` |
| action enum이 drift와 conflict를 구분하지 못함 | target-modified와 marker failure 복구 절차 혼동 | `drift-stop`과 `conflict`를 분리 |
| severity와 action이 불일치 | CLI exit/status 정책 혼란 | action별 기본 severity와 override 조건 명시 |
| stop_reason이 없음 | 사람이 왜 멈췄는지 추적 불가 | blocking/warning item에 stable code 요구 |
| recovery_hint가 없음 | force 사용 유혹 증가 | 모든 stop/warning item에 recovery hint 제공 |
| hash 필드 출처가 불명확 | source drift와 target drift 혼동 | expected, actual, generated hash prefix 구분 |
| marker 표현이 단순 boolean | duplicated/corrupted/missing을 구분하지 못함 | marker object에 count, integrity, problems 포함 |
| unmanaged target과 orphan marker 혼동 | 안전한 skip 대상과 stale managed block 혼동 | `unmanaged`와 `orphaned` drift_state 분리 |
| messages가 results와 어긋남 | envelope v2 소비자가 위험을 놓침 | blocking/warning results는 message 생성 |
| summary counter 부족 | 자동화가 전체 위험도 판정 어려움 | action counter와 severity counter 모두 제공 |

## Top-level Schema Risks

### Status Ambiguity

위험:

- dry-run result 중 일부만 실패했는데 top-level status가 `pass`로 보일 수 있다.
- warning-only 상태와 safe skip 상태가 구분되지 않을 수 있다.

정책:

- `blocking` severity가 하나라도 있으면 전체 status는 `fail`이다.
- blocking은 없고 warning이 하나라도 있으면 전체 status는 `warn`이다.
- safe create/update/skip만 있으면 전체 status는 `pass`이다.

### Mode Ambiguity

위험:

- dry-run 결과가 실제 sync 실행 결과처럼 오해될 수 있다.

정책:

- top-level `mode`는 항상 `dry-run`이어야 한다.
- `meta.mutation_performed`는 항상 false로 표현하는 것이 권장된다.
- future non-dry-run command는 별도 schema 또는 mode를 가져야 한다.

### Manifest Path Ambiguity

위험:

- manifest persistence가 없는 상태에서 `manifest_path`가 실제 파일 존재를 암시할 수 있다.

정책:

- manifest file이 실제로 없으면 `manifest_path: null`을 허용한다.
- preview path 또는 default candidate path는 `meta.manifest_path_candidate`로 분리할 수 있다.

## Result Item Risks

### Entry Identity Risk

위험:

- orphan 또는 unmanaged target에는 manifest `entry_id`가 없을 수 있다.
- synthetic id가 불안정하면 dry-run diff가 매번 흔들릴 수 있다.

정책:

- manifest entry는 manifest `entry_id`를 그대로 사용한다.
- unmanaged target은 `observed_unmanaged_<normalized_target_path>` 형식을 후보로 사용한다.
- orphan marker는 `orphan_<marker_entry_id>` 형식을 후보로 사용한다.

### Action and Severity Drift

위험:

- `skip`이 warning일 수도 있고 informational일 수도 있다.
- `create`가 unsafe insertion인데 informational로 표시될 수 있다.

정책:

- action은 수행 후보이고 severity는 안전도이다.
- `skip`은 observe-only 또는 no-op이면 informational, unmanaged target이면 warning이다.
- `create`는 policy가 허용하는 최초 생성 후보일 때만 informational이다.
- marker missing으로 인한 생성 불확실성은 `create`가 아니라 `conflict`이다.

### Stop Reason Loss

위험:

- `conflict`만으로는 marker missing, ownership violation, source missing을 구분할 수 없다.

정책:

- 모든 `conflict`, `drift-stop`, `orphan-warning`, warning `skip`에는 stable `stop_reason`이 있어야 한다.
- safe `create`, `update`, no-op `skip`은 `stop_reason: null`을 사용할 수 있다.

## Hash Reporting Risks

### Expected vs Actual Confusion

위험:

- manifest에 기록된 hash와 현재 filesystem hash가 뒤섞이면 잘못된 drift 판정으로 이어진다.

정책:

- `expected_*`는 manifest 또는 manifest preview 기준이다.
- `actual_*`는 현재 filesystem 관찰 기준이다.
- `generated_*`는 future generator preview 기준이다.

### Whole-file vs Managed-block Hash Confusion

위험:

- mixed-boundary target에서 파일 전체 hash를 drift 기준으로 삼으면 user-owned content 변경이 blocking drift로 오판될 수 있다.

정책:

- `mixed-boundary`와 `managed-block`은 managed block hash를 기본 drift 기준으로 삼는다.
- `runtime-managed`와 `whole-file`은 whole target hash를 기본 drift 기준으로 삼는다.
- marker 밖 content hash는 informational 또는 details로만 다룬다.

### Missing Hash Values

위험:

- 아직 생성 preview가 없는데 generated hash를 필수로 요구하면 Phase 6 설계와 충돌한다.

정책:

- `hashes` object는 필수지만 내부 hash 값은 null 또는 생략 가능해야 한다.
- result item은 hash 부재 이유를 `details`에 설명할 수 있어야 한다.

## Marker Reporting Risks

### Marker Boolean Collapse

위험:

- `marker_present: true`만으로는 duplicated, corrupted, wrong entry id를 표현하지 못한다.

정책:

- marker object는 `expected`, `present`, `count`, `entry_id`, `integrity`, `problems`를 포함해야 한다.
- integrity enum은 `valid`, `missing`, `duplicated`, `corrupted`, `not-expected`, `unknown`을 포함한다.

### Marker Missing vs Create Candidate Confusion

위험:

- expected marker가 없을 때 자동으로 새 marker를 삽입하려 하면 user-owned content를 침범할 수 있다.

정책:

- expected existing marker가 missing이면 기본 action은 `conflict`이다.
- 최초 생성 candidate는 manifest/policy가 first-create를 명확히 허용할 때만 `create`이다.

### Orphan Marker Removal Risk

위험:

- manifest entry가 없는 marker를 자동 삭제하면 과거 managed content 또는 수동 보존 영역을 잃을 수 있다.

정책:

- orphan marker는 `orphan-warning`만 생성한다.
- 자동 removal, cleanup, auto-fix는 명시적 non-goal이다.

## Message Mapping Risks

### Result-message Divergence

위험:

- result item에는 conflict가 있지만 envelope message가 없으면 machine consumer가 위험을 놓칠 수 있다.

정책:

- blocking result는 반드시 message를 생성한다.
- warning result는 반드시 message를 생성한다.
- informational result는 message 생성을 생략할 수 있다.

### Severity Vocabulary Drift

위험:

- dry-run severity `blocking`과 envelope status `fail`이 매핑되지 않으면 호환성이 깨진다.

정책:

- dry-run `blocking`은 envelope message `severity: blocking`, `status: fail`로 매핑한다.
- dry-run `warning`은 envelope message `severity: warning`, `status: warn`으로 매핑한다.
- top-level status는 envelope v2의 `pass`, `warn`, `fail` canonical vocabulary를 따른다.

## Summary Counter Risks

### Action-only Summary Insufficiency

위험:

- `conflict: 0`이어도 `drift_stop: 1`이면 fail이어야 한다.
- `skip: 10`만으로는 safe skip인지 unmanaged target warning인지 알 수 없다.

정책:

- action counter와 severity counter를 함께 제공한다.
- 필수 counter는 `create`, `update`, `skip`, `conflict`, `drift_stop`, `orphan_warning`, `blocking`, `warnings`이다.

### Naming Drift

위험:

- action enum은 `drift-stop`인데 summary는 `drift-stop` key를 쓰면 JSON consumer에서 다루기 불편할 수 있다.

정책:

- action enum은 사람이 읽기 쉬운 hyphenated string을 유지한다.
- summary key는 snake_case `drift_stop`, `orphan_warning`을 사용한다.

## Sample Output Risks

### Happy-path Bias

위험:

- clean update sample만 있으면 구현자가 blocking case를 뒤로 미룰 수 있다.

정책:

- sample에는 clean update, drift-stop, marker-corrupted conflict, unmanaged target skip, orphan-warning을 모두 포함한다.

### Over-implied Implementation

위험:

- sample에 generated hash가 있으면 generator가 이미 존재해야 하는 것처럼 보일 수 있다.

정책:

- sample은 schema contract 예시이며 Phase 6에서는 generation을 구현하지 않는다고 명시한다.
- generated hash는 future preview 값으로만 취급한다.

## Compatibility Risks

### Drift Stop Policy Compatibility

위험:

- dry-run schema가 stop policy보다 느슨하면 future mutation 구현이 안전 경계를 우회할 수 있다.

정책:

- `target-modified`는 항상 `drift-stop`.
- marker failure는 항상 `conflict`.
- ownership violation은 항상 `conflict`.
- source missing은 항상 `conflict`.

### Manifest Safety Design Compatibility

위험:

- dry-run result가 manifest entry field와 다르면 manifest 구현 때 변환 비용이 커진다.

정책:

- result item은 `entry_id`, `source_path`, `target_path`, `ownership`, `sync_mode`를 manifest entry와 동일한 의미로 사용한다.
- hash fields는 manifest expected value와 current observed value를 분리한다.

### Envelope v2 Compatibility

위험:

- native dry-run schema와 envelope v2가 서로 다른 status/message vocabulary를 사용하면 client가 둘 다 처리해야 한다.

정책:

- top-level status는 envelope v2와 동일하게 `pass`, `warn`, `fail`이다.
- message shape는 envelope v2 message model과 호환되게 둔다.
- native results는 envelope `payload.results`로 손실 없이 들어가야 한다.

### Observability Compatibility

위험:

- event emission을 나중에 붙일 때 dry-run item 정보가 부족하면 event detail을 재구성해야 한다.

정책:

- result item은 event detail로 재사용 가능한 `action`, `severity`, `stop_reason`, `source_path`, `target_path`, `drift_state`, `details`를 포함한다.
- event emission은 future opt-in이며 persistence, telemetry, networking을 암시하지 않는다.

## Non-goal Risk

Dry-run schema는 안전하게 보이지만, 다음 구현으로 오해되면 안 된다.

- actual sync execution
- mutation
- auto-fix
- force
- rollback
- manifest persistence
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- source mutation

권장 문구:

- `mode: dry-run`
- `meta.mutation_performed: false`
- force와 rollback은 explicit non-goal로 반복 명시

## 감사 결론

Future `aios sync --dry-run` schema는 단순한 diff 출력이 아니라 stop policy를 machine-readable하게 보존해야 한다.

권장 결론:

- native schema version은 `aios.sync_dry_run.v0`로 시작한다.
- top-level status는 `pass`, `warn`, `fail`을 사용한다.
- `drift-stop`과 `conflict`는 분리한다.
- blocking result는 항상 message를 생성한다.
- hash provenance는 expected, actual, generated로 분리한다.
- marker 상태는 boolean이 아니라 structured object로 표현한다.
- unmanaged target과 orphan marker는 서로 다른 warning 상태로 유지한다.
- dry-run schema는 envelope v2 payload와 future observability event detail로 손실 없이 연결되어야 한다.
