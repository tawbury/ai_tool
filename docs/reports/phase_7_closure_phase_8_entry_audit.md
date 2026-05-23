# Phase 7 Closure and Phase 8 Entry Decision Audit

## 개요

이 문서는 `.ai OS` Roadmap v1.2의 Phase 7 read-only sync runtime v0를 공식적으로 닫을 수 있는지 판단하고, 다음 Phase 8의 안전한 진입 방향을 결정한다.

검토 기준은 다음과 같다.

- `docs/reports/phase_7_read_only_runtime_completion_audit.md`
- `docs/reports/phase_7_stabilization_output_contract_report.md`
- `docs/reports/phase_7_runtime_rule_promotion_report.md`
- `.ai/rules/operations/sync.rules.md`
- `docs/roadmap/ai-os-execution-roadmap-v1.2.md`

Roadmap v1.2 원문은 Phase 7을 physical sync implementation으로 두고 일부 상태를 미구현으로 표시한다. 그러나 현재 구현은 mutation 없는 read-only subset으로 의도적으로 범위가 좁혀졌고, 그 범위는 완료, 안정화, 규칙 승격까지 끝났다. 따라서 이 감사는 Phase 7 전체 mutation 목표가 아니라 Phase 7 read-only sync runtime v0의 종료 여부를 판단한다.

## Phase 7 Closure Matrix

| 영역 | 상태 | 판단 |
| --- | --- | --- |
| Manifest/hash foundation | implemented | `aios.sync_manifest.v0` 로드/검증, path safety, hash format, observed UTF-8 bytes hash helper가 구현되었다. |
| Managed marker parser | implemented | marker style detection, begin/end pairing, code fence exclusion, malformed/duplicate/nested/mismatch classification이 구현되었다. |
| Sync dry-run evaluator | implemented | `aios sync --dry-run --manifest <path>`가 manifest 기반 read-only evaluation을 수행한다. |
| Native JSON output | implemented | `aios.sync_dry_run.v0` output이 `status`, `summary`, `results`, `messages`, `meta`를 제공한다. |
| Envelope v2 sync output | implemented | `--json --envelope-v2`가 `command: sync`, legacy schema, payload results, messages, dry-run meta를 보존한다. |
| Validate sync manifest | implemented | `aios validate <sync-manifest.json>`가 sync manifest를 first-class validation target으로 인식한다. |
| Drift-stop evaluation | implemented | target hash mismatch는 blocking `drift-stop`과 `target-modified`로 분류된다. |
| Orphan-warning evaluation | implemented | manifest target scope 안에서 안전하게 감지 가능한 orphan marker는 `orphan-warning`으로 보고된다. |
| Output contract tests | stabilized | native sync JSON, sync envelope v2, validate JSON, validate envelope v2, usage error exit code가 contract test로 고정되었다. |
| Runtime governance rules | rule-promoted | `.ai/rules/operations/sync.rules.md`가 Phase 7 read-only runtime v0 계약으로 갱신되었다. |
| Generated preview | deferred | adapter generation과 generated content가 금지되어 있으므로 preview contract는 별도 Phase 8 후보로 남긴다. |
| Repository-wide unmanaged/orphan scan | deferred | broad scan은 성능, scope, false positive 정책이 필요하므로 별도 설계가 필요하다. |
| Manifest persistence | blocked | mutation readiness gate 전까지 금지한다. |
| Transaction logs | blocked | rollback readiness와 storage policy 전까지 금지한다. |
| Rollback execution | blocked | transaction evidence와 dry-run rollback policy 전까지 금지한다. |
| Marker insertion/repair/delete | blocked | decommission, insertion, update safety gate 전까지 금지한다. |
| Sync apply/mutation | blocked | Phase 7 v0 완료 기준이 아니며 계속 차단한다. |

## Phase 7 Closure Decision

Phase 7 read-only sync runtime v0는 공식적으로 닫을 수 있다.

근거는 다음과 같다.

- read-only sync dry-run evaluator가 구현되었다.
- sync manifest validation이 `aios validate`에 통합되었다.
- native JSON과 envelope v2 output contract가 테스트로 고정되었다.
- runtime governance rule이 현재 구현과 일치하도록 승격되었다.
- mutation/apply, manifest persistence, rollback, marker mutation은 명시적으로 blocked 상태로 남아 있다.

단, 이 결정은 physical sync apply까지 완료되었다는 의미가 아니다. Phase 7 v0의 닫힘은 "read-only sync evaluation"의 닫힘이다. Roadmap의 기존 Phase 7 physical sync 목표 중 mutation 관련 항목은 다음 단계의 별도 readiness gate로 이관된다.

## Phase 8 Candidate Evaluation

| 후보 | Risk | Dependency | User Value | Implementation Readiness | Mutation Proximity | 평가 |
| --- | --- | --- | --- | --- | --- | --- |
| Generated preview contract | Medium | manifest/hash, dry-run result, future adapter source model | High | Medium | Medium | dry-run이 `skip` 외에 future update candidate를 판단하려면 필요하다. 구현 전 계약 설계가 적절하다. |
| Repository-wide orphan/unmanaged scan planning | Medium | marker parser, manifest target boundary, inventory-like scan policy | Medium | Medium | Low | 안전한 warning 기능이지만 false positive와 성능 정책이 필요하다. |
| Transaction/rollback readiness design | High | manifest persistence, transaction storage, marker update policy | High | Low | High | mutation 전 필수이나 아직 apply 설계와 storage 결정이 부족하다. 지금 바로 시작하면 범위가 커진다. |
| Sync apply architecture design | High | generated preview, transaction/rollback, marker write policy | High | Low | Very High | 실제 mutation과 가장 가깝다. 현재는 안전 gate가 부족하다. |
| Adapter generation planning | Medium | generated preview contract, runtime adapter boundary, root adapter policy | High | Medium | Medium | Roadmap의 원래 Phase 8이지만 generated preview contract 없이 시작하면 생성물 경계가 흐려진다. |
| Documentation consolidation | Low | reports/plans inventory | Medium | High | None | 문서 스프롤을 줄일 수 있지만 runtime capability 진전은 작다. |

## Recommended Phase 8 Direction

권장 Phase 8 방향은 **Generated Preview Contract**이다.

이유는 다음과 같다.

- 현재 dry-run evaluator는 generated preview가 없어서 clean target을 `skip`으로 판단할 수는 있지만, future generated output과 target을 비교해 `update` 후보를 판단하지 못한다.
- generated preview contract는 adapter generation이나 sync apply를 바로 구현하지 않고도 다음 capability의 경계를 선명하게 만든다.
- mutation proximity가 sync apply보다 낮고, repository-wide scan보다 사용자 가치가 높다.
- adapter generation planning의 선행 조건으로 적합하다.
- envelope v2, hash policy, dry-run result schema와 직접 연결되므로 현재 Phase 7 산출물을 재사용할 수 있다.

따라서 Phase 8은 "generated preview를 실제로 생성하는 구현"이 아니라 "generated preview contract and read-only comparison design"으로 시작해야 한다.

## Mutation Block Decision

Mutation은 계속 차단한다.

다음 항목은 Phase 8에서도 구현하면 안 된다.

- sync apply
- target file create/update/delete
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- adapter generation
- generated preview content generation
- default manifest discovery
- activation-driven sync selection
- force
- decommission
- source mutation

Generated preview contract를 설계하더라도, 실제 generated content 생성이나 target 반영은 별도 approval과 readiness audit 전까지 금지한다.

## Next Three Tasks

권장 Phase 8 하위 작업은 다음 순서다.

1. Generated preview contract plan
   - preview input source, output shape, generated hash fields, provenance, unavailable state, dry-run result mapping을 정의한다.
   - adapter generation은 non-goal로 유지한다.

2. Generated preview risk audit
   - preview와 adapter generation의 경계 혼동, stale source, over-broad activation selection, hash mismatch, false update candidate 위험을 분석한다.
   - mutation/apply로 이어지는 조건을 별도 blocked gate로 둔다.

3. Sync dry-run schema extension plan
   - `generated_target_hash`, `generated_managed_block_hash`, update candidate classification, envelope v2 message mapping을 v0-compatible extension으로 설계한다.
   - 구현은 계획 이후 별도 bundle에서만 진행한다.

## Deferred and Blocked Work

다음은 Phase 8 초입에서 다루지 않는 것이 좋다.

- Repository-wide unmanaged/orphan scan: generated preview contract 이후 별도 planning으로 다룬다.
- Transaction/rollback readiness: sync apply architecture가 구체화된 뒤 다룬다.
- Sync apply architecture: generated preview, transaction/rollback, marker mutation policy 이후에만 시작한다.
- Adapter generation planning: generated preview contract가 먼저 필요하다.
- Documentation consolidation: 필요하지만 Phase 8의 첫 runtime-facing design보다 우선순위가 낮다.

## 결론

Phase 7 read-only sync runtime v0는 종료한다.

Phase 8은 generated preview contract 설계로 시작하는 것이 가장 안전하다. 이 방향은 Phase 7의 read-only evaluator를 다음 의미 있는 runtime capability로 연결하면서도 mutation/apply를 계속 차단한다. Sync apply, manifest persistence, rollback execution, marker mutation은 여전히 blocked 상태이며, 별도 readiness gate 없이는 시작하면 안 된다.
