# Replay compare output contract risk audit

> 이 문서는 human audit context이다. 런타임 계약은 아니며, 구현 전 위험과 완화 기준을 정리한다.

## 감사 목적

Opt-in replay comparison output contract가 기존 `aios validate <replay-manifest.json>` 출력 계약을 흔들지 않고, provider 실행으로 오해되지 않으며, 향후 real provider replay validation으로 확장될 수 있는지 검토한다.

## 현재 기준선

| 항목 | 상태 |
| --- | --- |
| Static replay validation | 구현 및 rule promotion 완료 |
| Replay validate native JSON contract | 안정화 완료 |
| Replay validate envelope v2 contract | 안정화 완료 |
| Pure comparison helper | 구현 완료 |
| Validate comparison integration | 미구현 |
| Provider execution | 금지 |
| Adapter execution | 금지 |
| Generated content creation | 금지 |
| Snapshot update | 금지 |
| Sync apply/mutation | 차단 |

## 주요 위험

| 위험 | 영향 | 가능성 | 평가 |
| --- | --- | --- | --- |
| no-flag validate output churn | 높음 | 중간 | default integration을 피해야 한다. |
| envelope v2 message churn | 중간 | 중간 | comparison flag가 있을 때만 message를 추가한다. |
| fixture comparison을 real provider replay로 오해 | 높음 | 중간 | `comparison_mode: fixture`를 모든 result details에 포함한다. |
| static validation failure 뒤 comparison 실행 | 중간 | 중간 | static error가 있으면 comparison을 short-circuit한다. |
| snapshot update 유혹 | 높음 | 낮음 | update command를 만들지 않고 non-goal로 고정한다. |
| 민감 정보 출력 | 중간 | 낮음 | v0에는 secret이 없지만 future redaction policy를 둔다. |
| summary counter 불일치 | 중간 | 중간 | mismatch는 error counter로만 계산한다. |
| usage error와 validation error 혼동 | 중간 | 중간 | flag misuse는 exit code `2`, mismatch는 exit code `1`로 분리한다. |
| helper code 손실 | 낮음 | 중간 | `ReplayComparisonIssue.code`를 그대로 result code로 사용한다. |

## Default integration 거부 근거

Default integration은 지금 채택하지 않는다.

근거:

- replay validate output contract tests가 현재 static-only 출력을 고정하고 있다.
- default comparison은 valid replay manifest의 result count와 summary를 바꾼다.
- 사용자는 flag 없이 validate를 실행했을 때 provider replay가 수행되었다고 오해할 수 있다.
- envelope v2 `messages`와 `payload.results`가 불필요하게 커진다.
- fixture comparison latency가 기본 validate 경로에 추가된다.

따라서 comparison은 opt-in이어야 한다.

## Opt-in 방식의 완화 효과

`--replay-compare fixture`는 다음을 분명히 한다.

- 비교는 명시적으로 요청된 경우에만 실행된다.
- 비교 mode가 fixture-backed임을 드러낸다.
- default static validation은 안정적으로 보존된다.
- future provider-backed replay가 별도 승인 없이 섞이지 않는다.
- mismatch는 validation failure로 처리하되 provider failure로 표현하지 않는다.

## Native JSON 위험과 완화

위험:

- static validation result와 comparison result가 한 배열에 섞이면 구분이 어려울 수 있다.
- success info result가 message noise를 늘릴 수 있다.
- 큰 object mismatch가 JSON output을 과도하게 키울 수 있다.

완화:

- 모든 comparison result details에 `comparison_mode: fixture`를 포함한다.
- success result code는 `replay_comparison_checked` 하나로 제한한다.
- mismatch details는 scalar 값은 그대로 표시하고 큰 object는 summary로 대체한다.
- helper code를 result code로 보존해 test/debug 경로를 단순화한다.

## Envelope v2 위험과 완화

위험:

- message normalization 과정에서 comparison details가 손실될 수 있다.
- envelope meta가 replay mode를 충분히 설명하지 못하면 provider execution으로 오해될 수 있다.
- summary-only와 comparison payload 보존 정책이 충돌할 수 있다.

완화:

- `meta.replay_compare: fixture`를 추가한다.
- `meta.provider_execution: false`와 `meta.mutation_performed: false`를 명시한다.
- `payload.results`는 기존 validate mapping을 따른다.
- summary-only는 기존 validate/envelope 정책을 우선하고, omitted payload count를 meta에 남긴다.

## Exit code 위험과 완화

| 상황 | 위험 | 완화 |
| --- | --- | --- |
| unsupported flag value | validation failure로 오해 | exit code `2` |
| non replay target flag usage | target detection 혼란 | exit code `2` |
| static validation failure | comparison mismatch와 혼합 | comparison 미실행, exit code `1` |
| comparison mismatch | provider failure로 오해 | result details에 `comparison_mode: fixture` |
| pass with comparison success | 불필요한 warning | status `pass`, exit code `0` |

## Redaction 위험

현재 fixture contract에는 secret field가 없다. 그러나 real provider 계획이 진행되면 provider config나 provenance에 민감 정보가 들어올 수 있다.

권장:

- v0 구현에서도 redaction helper를 둘 수 있다.
- field name 기반 최소 redaction을 적용한다.
- large object는 값 전체 대신 summary를 출력한다.
- hash, schema, enum, id는 그대로 출력 가능하다.

## 구현 위험 체크리스트

구현 task에서 확인할 항목:

- no-flag output contract tests가 변경 없이 통과하는가
- static validation error일 때 comparison helper가 호출되지 않는가
- usage/config error가 exit code `2`를 반환하는가
- comparison mismatch가 error count와 exit code `1`로 반영되는가
- native JSON과 envelope v2 모두 `comparison_mode: fixture`를 보존하는가
- provider execution과 adapter execution 경로가 전혀 추가되지 않았는가
- snapshot update 경로가 생기지 않았는가

## 잔여 위험

Opt-in output contract를 설계해도 다음 위험은 남는다.

- fixture-derived candidate 구성 규칙이 아직 구현되지 않았다.
- fixture comparison success가 real provider determinism을 증명하지는 않는다.
- 향후 provider-backed replay mode가 추가되면 별도 위험 감사와 runtime rule promotion이 필요하다.
- output contract가 구현되기 전까지 `.ai/rules`에 runtime behavior로 승격하면 안 된다.

## 결론

Opt-in replay comparison output contract는 설계상 안전하다. 단, 기본 validate 출력은 그대로 유지하고, `--replay-compare fixture`가 있을 때만 native JSON 및 envelope v2에 comparison result를 추가해야 한다. 다음 단계는 이 계약에 맞춘 구현과 output contract tests이며, 구현 안정화 전에는 runtime governance rule로 승격하지 않는다.
