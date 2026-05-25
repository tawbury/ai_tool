# Replay compare output contract report

> 이 문서는 human implementation evidence이다. 런타임 계약은 아니며, opt-in replay comparison 출력 계약 안정화 결과를 기록한다.

## 개요

`aios validate <replay-manifest.json> --replay-compare fixture`의 native JSON 및 envelope v2 출력 계약을 별도 contract test로 고정했다. 이번 작업은 테스트 안정화만 수행했으며 runtime semantics는 변경하지 않았다.

## 추가된 테스트

추가 파일:

- `tests/test_replay_compare_output_contract.py`

검증 범위:

- no-flag native JSON은 static-only 출력으로 유지
- no-flag envelope v2는 replay comparison meta 없이 유지
- opt-in native JSON은 `aios.validate.result.v0`와 `target.kind: replay-manifest` 유지
- opt-in native JSON은 `replay_comparison_checked`와 `details.comparison_mode: fixture`, `details.cases` 보존
- opt-in envelope v2는 `aios.command_result.v2`, `command: validate`, `target.kind: replay-manifest` 유지
- opt-in envelope v2는 `meta.replay_compare`, `meta.comparison_mode`, `meta.provider_execution`, `meta.mutation_performed` 보존
- mismatch는 helper code와 comparison details를 native JSON에 보존
- mismatch는 envelope v2 `payload.results`와 `messages`에 보존
- static validation failure는 comparison helper 호출 없이 short-circuit
- usage/config error는 exit code `2` 유지

## 고정된 출력 계약

No-flag replay validation:

- comparison result를 추가하지 않는다.
- `meta.replay_compare`를 추가하지 않는다.
- 기존 static validation result count를 유지한다.

Opt-in replay comparison:

- `--replay-compare fixture`가 있을 때만 comparison result를 추가한다.
- success result code는 `replay_comparison_checked`이다.
- mismatch result code는 `ReplayComparisonIssue.code`를 그대로 사용한다.
- comparison details는 `case_id`, `comparison_field`, `comparison_mode`를 포함한다.
- scalar mismatch는 expected/actual value를 보존한다.
- large object mismatch는 expected/actual summary를 보존한다.

## 명시적으로 변경하지 않은 것

이번 작업은 다음을 변경하지 않았다.

- runtime classification semantics
- replay manifest static validation behavior
- replay comparison helper behavior
- envelope builder base behavior
- `.ai/rules`
- provider execution
- adapter execution
- generated content generation
- snapshot update
- replay CLI
- sync apply
- mutation

## 검증

실행 및 통과:

- `python -m pytest tests/test_replay_compare_output_contract.py`

최종 검증은 커밋 전 요청된 전체 validation command로 다시 수행한다.

## 잔여 작업

권장 다음 단계:

1. Opt-in replay comparison behavior를 runtime governance rules에 승격할지 감사한다.
2. 승격이 적절하면 `sync.rules.md`와 `validation.rules.md`의 최소 변경 범위를 설계한다.
3. real provider execution boundary는 계속 별도 설계와 승인 전까지 차단한다.
