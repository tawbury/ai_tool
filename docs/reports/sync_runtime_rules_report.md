# Sync Runtime Rules Report

## 개요

Phase 6 sync/manifest 안전 설계를 runtime-facing operation rule로 승격했다. 이번 변경은 문서와 규칙 승격만 포함하며, sync 실행, manifest 저장, transaction log 저장, rollback 실행, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation은 구현하지 않았다.

## 변경 사항

추가한 runtime rule:

- `.ai/rules/operations/sync.rules.md`

업데이트한 인덱스:

- `.ai/rules/rules.md`
- `.ai/rules/operations/README.md`

## 승격한 핵심 계약

`sync.rules.md`에는 다음 Phase 6 안전 계약을 반영했다.

- Phase 6은 안전 설계 단계이며 sync 구현이 아니다.
- `.ai/`는 계속 runtime source of truth이다.
- future manifest는 state record이며 source of truth가 아니다.
- 별도 설계 전까지 future sync는 `.ai/`에서 managed target으로 향하는 one-way assumption을 따른다.
- ownership model은 `runtime-managed`, `user-owned`, `mixed-boundary`로 구분한다.
- drift state는 `clean`, `drifted`, `missing`, `orphaned`, `unmanaged`를 사용한다.
- blocking drift와 conflict는 fail-closed 및 drift-stop을 요구한다.
- future sync와 rollback은 dry-run-first 정책을 따라야 한다.
- managed block marker는 mixed-boundary target의 유일한 managed write boundary이다.
- rollback은 transaction record, pre-image, post-hash match, valid marker boundary, user-owned boundary preservation을 전제로 한다.
- activation v1은 future sync planning input이 될 수 있지만 write authority나 drift-stop 우회 권한이 아니다.
- future sync/rollback 결과는 envelope v2와 opt-in observability event model에 맞춰야 한다.

## Non-goal 확인

이번 변경은 다음을 추가하지 않았다.

- sync command
- manifest persistence
- transaction log persistence
- rollback command
- adapter generation
- worker dispatch
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation

## 검증

요청된 검증 명령을 실행해 runtime rule 승격 후 기존 read-only 명령들이 유지되는지 확인했다.
