# Phase 8 replay comparison runtime completion audit

> 이 문서는 human audit context이다. 런타임 계약은 아니며, Phase 8 replay comparison runtime v0의 완료 여부와 다음 안전 방향을 판단한다.

## 감사 목적

Fixture-backed replay comparison runtime이 현재 단계에서 충분히 완성되었는지 판단한다. 특히 `aios validate <replay-manifest.json> --replay-compare fixture`가 기존 static replay validation 계약을 깨지 않고 opt-in validation으로 안정화되었는지, 그리고 다음 단계로 넘어가기 전에 남은 governance gap이 무엇인지 확인한다.

## 검토한 근거

- `docs/reports/replay_comparison_helper_implementation_report.md`
- `docs/reports/replay_comparison_integration_policy_audit.md`
- `docs/reports/replay_compare_output_contract_report.md`
- `tests/test_replay_compare_output_contract.py`
- `tests/test_replay_compare_integration.py`
- `.ai/rules/operations/sync.rules.md`
- `.ai/rules/operations/validation.rules.md`

## 완료 역량 매트릭스

| 역량 | 상태 | 근거 | 판단 |
| --- | --- | --- | --- |
| Replay manifest validation | 완료 | `aios validate <replay-manifest.json>` | static validation target으로 안정화됨 |
| Provider snapshot validation | 완료 | replay manifest static validation | provider id/version, hash policy, fixture 참조 검증 포함 |
| Replay input/output fixture validation | 완료 | replay validation tests | schema, hash, provenance, unavailable output null hash 검증 |
| Replay comparison helper | 완료 | `compare_replay_outputs` | exact equality, no IO, no provider execution |
| Opt-in comparison integration | 완료 | `--replay-compare fixture` | 명시적 flag가 있을 때만 비교 수행 |
| Default no-flag behavior | 완료 | output contract tests | static-only native JSON/envelope v2 유지 |
| Native JSON comparison contract | 완료 | `tests/test_replay_compare_output_contract.py` | success/mismatch details 고정 |
| Envelope v2 comparison contract | 완료 | `tests/test_replay_compare_output_contract.py` | meta, payload, messages 고정 |
| Static validation short-circuit | 완료 | integration/contract tests | static error 시 helper 미호출 |
| Usage/config errors | 완료 | integration/contract tests | unsupported value, non replay target, missing target는 exit code `2` |
| Provider execution boundary | 완료 | 구현 및 테스트 범위 | provider 실행 경로 없음 |
| Mutation boundary | 완료 | 구현 및 non-goals | 파일 쓰기, snapshot update, sync apply 없음 |

## 현재 지원되는 replay comparison 동작

지원 명령:

```bash
python -m aios validate <replay-manifest.json> --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --envelope-v2 --replay-compare fixture
```

동작 경계:

- static replay validation이 먼저 실행된다.
- static validation error가 있으면 comparison은 실행되지 않는다.
- comparison은 expected output fixture와 fixture-derived candidate object를 비교한다.
- `compare_replay_outputs` helper의 issue code와 details를 validate result로 보존한다.
- no-flag validate output은 계속 static-only이다.

## 차단된 영역

다음은 현재 단계에서 계속 차단되어야 한다.

| 영역 | 상태 | 이유 |
| --- | --- | --- |
| Provider execution | 차단 | real provider contract와 isolation model이 아직 runtime으로 구현되지 않음 |
| Adapter execution | 차단 | adapter runtime 승인 경계가 없음 |
| Generated content generation | 차단 | replay comparison은 fixture-backed comparison일 뿐 생성이 아님 |
| Actual provider replay | 차단 | provider output을 실제로 만들거나 비교하지 않음 |
| Snapshot update | 차단 | 자동 갱신은 deterministic replay 의미를 약화함 |
| Replay CLI | 차단 | validate opt-in path로 충분하며 별도 CLI는 설계되지 않음 |
| Sync apply | 차단 | mutation readiness gate가 없음 |
| Mutation | 차단 | Phase 8 replay runtime은 read-only v0 |

## 완료 판단

판단: **Phase 8 replay comparison runtime v0는 완료로 볼 수 있다.**

이 판단의 근거:

- helper, integration, output contract가 모두 구현 및 테스트되었다.
- no-flag static validation behavior가 안정적으로 보존된다.
- opt-in comparison path가 native JSON과 envelope v2 모두에서 고정되었다.
- failure path와 usage/config error가 테스트된다.
- provider execution, adapter execution, generated content, snapshot update, mutation이 모두 구현되지 않았다.

추가 안정화가 필수로 남아 있지는 않다. 다만 runtime governance rules는 현재 구현 상태를 완전히 반영하지 못하므로, v0를 공식 운영 규칙으로 닫기 전에 rule promotion이 필요하다.

## 공식 closure boundary

Phase 8 replay comparison runtime v0 closure는 다음까지 포함한다.

- replay manifest/provider snapshot/input/output fixture static validation
- pure fixture-backed replay comparison helper
- opt-in validate integration via `--replay-compare fixture`
- static validation short-circuit
- native JSON output contract
- envelope v2 output contract
- usage/config error behavior
- read-only invariant

Closure에 포함하지 않는 future work:

- provider-backed replay comparison
- adapter-backed generation
- generated content creation
- replay snapshot migration/update tooling
- standalone replay CLI
- provider sandbox execution
- real provider timeout/resource control
- sync apply or mutation

## Runtime governance rule gap

현재 `.ai/rules/operations/sync.rules.md`와 `.ai/rules/operations/validation.rules.md`는 replay manifest static validation을 설명한다. 그러나 다음 구현 동작은 아직 충분히 승격되어 있지 않다.

- `python -m aios validate <replay-manifest.json> --replay-compare fixture`
- opt-in comparison만 허용한다는 정책
- no-flag validation은 static-only로 유지된다는 정책
- comparison success code `replay_comparison_checked`
- envelope v2 meta:
  - `replay_compare: fixture`
  - `comparison_mode: fixture`
  - `provider_execution: false`
  - `mutation_performed: false`
- usage/config error 조건
- provider execution, adapter execution, generated content, snapshot update 금지 경계

따라서 governance rules는 현재 구현을 부분적으로만 설명한다. 기능 안정화는 완료되었지만 rule promotion task가 다음 단계로 필요하다.

## 후보 다음 방향 평가

| 후보 | 위험 | 의존성 | 사용자 가치 | 준비도 | 판단 |
| --- | --- | --- | --- | --- | --- |
| Real provider contract refinement | 중간 | rule promotion 이후 | 높음 | 중간 | 다음 큰 설계 방향 후보 |
| Deterministic replay execution architecture | 중간-높음 | provider isolation model | 높음 | 중간 | provider 실행 전 필수 |
| Provider isolation model | 높음 | runtime rule promotion | 높음 | 중간 | real provider 전 가장 중요한 설계 |
| Replay sandbox design | 높음 | isolation model | 높음 | 낮음-중간 | provider 실행과 가까워 별도 phase 필요 |
| Additional stabilization | 낮음 | 없음 | 낮음 | 높음 | 현재 필수 아님 |
| Runtime rule promotion | 낮음 | 현재 감사 결과 | 높음 | 높음 | 즉시 다음 작업으로 적합 |

## 권장 다음 안전 방향

즉시 다음 작업은 **opt-in replay comparison behavior를 runtime governance rules에 승격하는 것**이다.

이유:

- 구현과 output contract는 안정화되었다.
- `.ai/rules`는 현재 static replay validation까지만 충분히 설명한다.
- 다음 phase에서 provider isolation이나 replay execution architecture를 다루기 전에, 현재 read-only v0 경계를 공식 규칙으로 닫아야 한다.

Rule promotion 이후의 다음 큰 방향은 **provider isolation model** 설계가 적절하다. Real provider 실행은 isolation, timeout, no-write, no-network, deterministic replay boundary가 정의되기 전까지 시작하지 않는다.

## 권장 다음 3개 작업

1. Promote opt-in replay comparison validation behavior into runtime governance rules.
2. Audit provider isolation requirements for future real replay execution.
3. Design deterministic replay execution architecture with no provider mutation and no snapshot update.

## 결론

Phase 8 replay comparison runtime v0는 기능적으로 완료되었다. 현재 상태는 read-only fixture-backed comparison runtime으로 닫을 수 있다. 단, 이 완료 상태를 공식 운영 규칙과 일치시키기 위해 `.ai/rules/operations/sync.rules.md`와 `.ai/rules/operations/validation.rules.md`의 최소 승격 작업이 다음 안전 단계로 필요하다.
