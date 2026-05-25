# Replay comparison integration policy 감사

## 개요

Pure fixture-backed replay comparison helper가 구현되었지만 아직 `aios validate`, CLI, envelope v2에 통합되지는 않았다. 이 감사는 helper를 어떻게 통합할지, 특히 기존 replay validate output contract를 흔들지 않으면서 다음 단계를 진행할 수 있는 정책을 결정한다.

이번 작업은 정책 감사만 수행한다. Runtime code, `.ai` rules, fixture, test behavior는 변경하지 않았다.

## 현재 상태

| 항목 | 상태 | 판단 |
| --- | --- | --- |
| `compare_replay_outputs(expected, candidate, case_id=None)` | 구현됨 | pure helper이며 file IO가 없다. |
| `ReplayComparisonIssue` | 구현됨 | code, severity, status, case_id, comparison field, expected/actual value 또는 summary를 제공한다. |
| Exact value equality | 구현됨 | type coercion, missing/null equivalence, list order 무시가 없다. |
| Static replay validation | 구현 및 rule promotion 완료 | `aios validate <replay-manifest.json>`는 static-only다. |
| Replay validate output contract | 안정화 완료 | native JSON과 envelope v2 test가 있다. |
| Validate integration for comparison | 없음 | 의도적으로 아직 연결하지 않았다. |
| Provider execution | 없음 | 계속 금지한다. |
| Snapshot update | 없음 | 계속 금지한다. |
| Sync apply/mutation | 차단 | 계속 금지한다. |

## 통합 선택지 평가

| 선택지 | 장점 | 위험 | 판단 |
| --- | --- | --- | --- |
| Helper-only 유지 | 기존 validate output contract를 전혀 흔들지 않는다. 다음 설계를 더 명확히 할 수 있다. | 사용자가 CLI에서 comparison을 실행할 수 없다. | 단기 안전 상태로 유지 |
| Default comparison inside `aios validate <replay-manifest.json>` | 사용자가 추가 flag 없이 comparison 결과를 받는다. | result count, info/error 목록, envelope messages가 바뀐다. static validation과 comparison validation이 혼동된다. | 지금은 거부 |
| Opt-in validation flag | 기존 output contract를 보존하면서 comparison을 명시적으로 실행할 수 있다. | CLI flag와 output contract 설계가 필요하다. | 권장 경로 |
| Separate future command | validate output churn을 피할 수 있다. | command surface가 과도하게 늘고 replay가 validation에서 분리된다. | 지금은 비권장 |
| Test-only helper | 가장 안전하다. | runtime validation capability로 성장하지 못한다. | 장기 방향으로 부족 |

## 권고

권고: helper-only 상태를 유지하되, 다음 구현은 opt-in validation integration으로 설계한다.

Default integration은 지금 하지 않는다. 이유:

- `tests/test_replay_validate_output_contract.py`가 static validation output을 고정하고 있다.
- default comparison을 추가하면 valid manifest의 `results`, `info`, `messages`, `summary.results`가 변한다.
- comparison success가 real provider replay success처럼 오해될 수 있다.
- static validation과 fixture-backed comparison의 실패 의미가 다르다.
- envelope v2 message count와 payload shape가 불필요하게 흔들린다.

Separate command도 지금은 권장하지 않는다. Replay comparison은 validation 성격이 강하므로 `validate`의 opt-in extension으로 두는 것이 더 일관적이다.

## 제안 인터페이스

권장 future CLI:

```bash
python -m aios validate <replay-manifest.json> --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --envelope-v2 --replay-compare fixture
```

Flag policy:

- `--replay-compare fixture`만 v0에서 허용한다.
- `--replay-compare`는 replay manifest target에서만 유효하다.
- unsupported value는 usage/config error로 exit code `2`.
- non replay-manifest target에서 사용하면 exit code `2`.
- flag가 없으면 현재 static validation output을 그대로 유지한다.

이름 선택 이유:

- `fixture`라는 값을 요구해 real provider replay와 구분한다.
- `--replay-compare`는 provider execution이 아니라 comparison validation임을 드러낸다.
- future provider-backed mode가 필요해도 별도 승인 전까지 value를 추가하지 않는다.

## Native JSON Output Policy

Flag가 없을 때:

- 현재 `aios.validate.result.v0` output contract를 유지한다.
- `replay_manifest_checked` info result만 유지한다.

`--replay-compare fixture`가 있을 때:

- static validation을 먼저 수행한다.
- static validation error가 있으면 comparison은 실행하지 않는다.
- comparison mismatch는 severity `error`, status `fail`.
- comparison success는 optional info result로 기록한다.

권장 success code:

- `replay_comparison_checked`

권장 failure details:

- `case_id`
- `comparison_field`
- `comparison_mode: fixture`
- `expected_value` 또는 `expected_summary`
- `actual_value` 또는 `actual_summary`

Exit code:

- pass: `0`
- warn only: `0`
- comparison mismatch or static validation error: `1`
- usage/config error: `2`

## Envelope v2 Policy

`--json --envelope-v2 --replay-compare fixture`일 때:

- `command: validate`
- `target.kind: replay-manifest`
- `meta.legacy_schema_version: aios.validate.result.v0`
- `meta.replay_compare: fixture`
- `payload.results`에 static validation 및 comparison results 포함
- `messages`에 comparison errors 포함
- comparison message details에 `validator`, `case_id`, `comparison_field`, `comparison_mode` 보존

Flag가 없을 때:

- 기존 envelope v2 replay validate output을 그대로 유지한다.

## Comparison Semantics

Opt-in comparison은 다음만 수행해야 한다.

- replay manifest static validation 이후 실행
- expected output fixture load
- fixture-derived candidate object 구성
- `compare_replay_outputs` 호출
- mismatch result reporting

Opt-in comparison이 하면 안 되는 것:

- provider execution
- adapter execution
- generated content creation
- actual provider output production
- snapshot update
- replay CLI creation
- sync apply/mutation authorization

## 주요 위험과 완화

| 위험 | 평가 | 완화 |
| --- | --- | --- |
| Validate output contract churn | default integration이면 높음 | opt-in flag로 격리 |
| Real provider replay로 오해 | 중간 | flag value를 `fixture`로 고정 |
| Provider execution confusion | 중간 | rule/report/CLI help에 no provider execution 명시 |
| False confidence | 중간 | result details에 `comparison_mode: fixture` 포함 |
| Extra validation latency | 낮음 | opt-in이므로 기본 validate에는 영향 없음 |
| Envelope message churn | default이면 높음 | flag 없을 때 기존 envelope 유지 |
| Snapshot update temptation | 중간 | snapshot update command를 만들지 않음 |

## 구현 전 필요 작업

Opt-in integration 전에 필요한 작업:

1. Output contract plan 작성
2. CLI flag parse 위치 결정
3. replay manifest target 외 flag 사용 시 exit code `2` 정책 확정
4. fixture-derived candidate object 생성 규칙 확정
5. native JSON/envelope v2 contract tests 작성
6. `.ai/rules/operations/sync.rules.md` promotion 필요성 검토

## Non-goals

이 정책은 다음을 승인하지 않는다.

- provider execution
- adapter execution
- generated content generation
- actual provider replay
- snapshot update
- replay CLI
- sync apply
- mutation
- manifest persistence
- transaction persistence
- rollback execution
- marker mutation
- repository-wide scan
- activation-driven provider selection

## 결론

Replay comparison helper는 바로 default validate에 통합하지 않는다. 가장 안전한 경로는 helper-only 상태를 유지하면서 `--replay-compare fixture` opt-in validation integration을 별도 output contract plan으로 설계하는 것이다. 이 경로는 기존 static replay validate contract를 보존하고, provider execution 없이 comparison reporting을 확장할 수 있다.
