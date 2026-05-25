# Replay compare output contract plan

> 이 문서는 human planning context이다. 런타임 계약은 아니며, 실제 효력은 향후 구현과 `.ai/rules/` 승격이 완료된 뒤에만 생긴다.

## 목적

`compare_replay_outputs(expected, candidate, case_id=None)` helper를 향후 `aios validate <replay-manifest.json>`에 opt-in 방식으로 연결할 때의 native JSON 및 envelope v2 출력 계약을 정의한다. 기본 replay manifest validation은 계속 static-only이며, `--replay-compare fixture`가 없는 출력은 현재 안정화된 계약을 그대로 유지해야 한다.

## CLI 계약

지원 후보:

```bash
python -m aios validate <replay-manifest.json> --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --envelope-v2 --replay-compare fixture
```

기본 정책:

- `--replay-compare fixture`만 v0에서 허용한다.
- flag가 없으면 현재 static replay validation 출력은 변경하지 않는다.
- 비교는 replay manifest target에서만 유효하다.
- 비교는 provider 실행이 아니라 fixture-backed exact comparison이다.
- 비교는 snapshot update, generated content creation, adapter execution, sync apply를 절대 수행하지 않는다.

Usage/config error:

| 상황 | 처리 |
| --- | --- |
| unsupported `--replay-compare` value | exit code `2` |
| replay manifest가 아닌 target에서 `--replay-compare` 사용 | exit code `2` |
| target 없이 `--replay-compare` 사용 | exit code `2` |
| `--envelope-v2`를 `--json` 없이 사용 | 기존 validate 정책대로 exit code `2` |

## 실행 순서

Opt-in comparison은 다음 순서로만 실행한다.

1. replay manifest static validation을 먼저 수행한다.
2. static validation error가 있으면 comparison을 실행하지 않는다.
3. replay manifest case의 expected output fixture를 읽는다.
4. v0에서는 fixture-derived candidate object를 구성한다.
5. `compare_replay_outputs(expected, candidate, case_id=case_id)`를 호출한다.
6. comparison issue를 validate result로 변환한다.

중요 경계:

- static validation은 fixture 존재, schema, hash format, provenance/provider metadata 같은 구조 검증이다.
- replay comparison은 expected와 candidate의 exact value equality 검증이다.
- real provider output은 아직 생성하지 않는다.

## Native JSON 출력 계약

`--json --replay-compare fixture` 출력은 기존 validate schema를 유지한다.

- `schema_version`: `aios.validate.result.v0`
- `target.kind`: `replay-manifest`
- static validation results는 계속 포함한다.
- comparison success는 info result로 표현할 수 있다.
- comparison mismatch는 error result로 표현한다.

Success result:

| Field | Value |
| --- | --- |
| `code` | `replay_comparison_checked` |
| `severity` | `info` |
| `status` | `pass` |
| `message` | fixture-backed replay comparison completed |
| `details.comparison_mode` | `fixture` |
| `details.cases` | checked case count |

Mismatch result:

| Field | Value |
| --- | --- |
| `code` | `ReplayComparisonIssue.code` |
| `severity` | `error` |
| `status` | `fail` |
| `message` | helper issue message |
| `details.case_id` | replay case id |
| `details.comparison_field` | compared field |
| `details.comparison_mode` | `fixture` |
| `details.expected_value` or `details.expected_summary` | expected side |
| `details.actual_value` or `details.actual_summary` | candidate side |

Mismatch code는 helper의 기존 code를 그대로 보존한다.

- `replay-schema-mismatch`
- `replay-entry-id-mismatch`
- `replay-preview-available-mismatch`
- `replay-content-kind-mismatch`
- `replay-hash-mismatch`
- `replay-deterministic-flag-mismatch`
- `replay-provider-metadata-mismatch`
- `replay-provenance-mismatch`
- `replay-unavailable-reason-mismatch`

## Summary와 exit code

Summary 정책:

- static validation이 pass이고 comparison issue가 없으면 overall `pass`.
- static validation error가 있으면 overall `fail`.
- comparison mismatch가 하나라도 있으면 overall `fail`.
- comparison mismatch는 error counter를 증가시킨다.
- comparison success info는 info counter를 증가시킬 수 있다.

Exit code:

| 상태 | Exit code |
| --- | --- |
| pass | `0` |
| warn only | `0` |
| static validation error | `1` |
| comparison mismatch | `1` |
| usage/config error | `2` |

## Envelope v2 매핑

`--json --envelope-v2 --replay-compare fixture`는 기존 envelope v2 구조를 유지하면서 comparison metadata를 추가한다.

Top-level:

- `schema_version`: `aios.command_result.v2`
- `command`: `validate`
- `status`: canonical `pass|warn|fail`
- `target.kind`: `replay-manifest`

Meta:

- `legacy_schema_version`: `aios.validate.result.v0`
- `legacy_status`: native validate status
- `replay_compare`: `fixture`
- `comparison_mode`: `fixture`
- `provider_execution`: `false`
- `mutation_performed`: `false`

Payload:

- `payload.results`는 static validation results와 comparison results를 포함한다.
- summary-only 모드가 있다면 기존 validate summary-only 정책을 우선한다.
- omitted payload counter가 필요한 경우 기존 envelope meta 패턴을 따른다.

Messages:

- comparison mismatch는 `messages`에 error severity로 포함한다.
- comparison success info는 message로 포함할 수 있으나, message churn을 줄이려면 native result에는 남기고 envelope message에서는 생략하는 정책도 허용한다.
- 비교 메시지의 `details`는 `case_id`, `comparison_field`, `comparison_mode`를 보존해야 한다.

## No-flag 보존 계약

아래 명령은 현재 출력 계약을 그대로 유지해야 한다.

```bash
python -m aios validate <replay-manifest.json>
python -m aios validate <replay-manifest.json> --json
python -m aios validate <replay-manifest.json> --json --envelope-v2
```

보존 요구사항:

- result count가 변하지 않는다.
- `replay_manifest_checked` static info result가 변하지 않는다.
- envelope v2 `payload.results`와 `messages`가 변하지 않는다.
- 비교 성공/실패 result는 flag가 있을 때만 추가된다.

## Redaction policy

v0 fixture에는 secret field가 없다는 전제를 둔다. 그래도 출력 계약은 future-safe하게 둔다.

출력 가능:

- schema version
- entry id
- case id
- enum 값
- boolean 값
- scalar hash 값
- provider id/version

요약 사용:

- 큰 object
- provenance 전체 object
- provider metadata 전체 object
- future context payload

Redaction 필요:

- field name이 `secret`, `token`, `key`, `credential`, `password`를 포함하는 경우
- future provider config 중 민감한 값으로 표시된 경우

Redaction된 값은 `expected_summary` 또는 `actual_summary`에 `redacted` 또는 object size/type summary로 표현한다.

## 테스트 계약

향후 구현 시 필요한 contract tests:

- no-flag native JSON 출력이 기존 snapshot/contract와 동일함
- no-flag envelope v2 출력이 기존 contract와 동일함
- `--replay-compare fixture` success가 `replay_comparison_checked`를 포함함
- mismatch code가 helper code 그대로 보존됨
- mismatch details에 `case_id`, `comparison_field`, `comparison_mode`가 포함됨
- static validation failure 시 comparison이 실행되지 않음
- unsupported compare value는 exit code `2`
- non replay-manifest target에서 flag 사용 시 exit code `2`
- target 없이 flag 사용 시 exit code `2`
- envelope v2 meta에 `replay_compare: fixture`가 포함됨

## Non-goals

이 계약은 다음을 허용하지 않는다.

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

## 구현 전 체크포인트

구현 전에 다음을 확인한다.

1. 현재 replay validate output contract tests가 no-flag 상태에서 계속 통과해야 한다.
2. 비교 flag parser 위치가 validate target detection 이후인지 확인한다.
3. static validation failure가 comparison을 short-circuit하는지 확인한다.
4. expected/candidate fixture mapping이 provider execution처럼 보이지 않도록 명명한다.
5. `.ai/rules/operations/sync.rules.md`와 `validation.rules.md` 승격은 구현과 contract test 안정화 이후 별도 task로 진행한다.
