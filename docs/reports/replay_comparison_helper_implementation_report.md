# Replay comparison helper 구현 보고서

## 개요

Fixture-backed replay comparison validation의 첫 구현 단계를 완료했다. 이번 작업은 pure comparison helper와 unit tests만 추가했으며, `aios validate`, envelope v2, CLI, provider execution, adapter execution, generated content generation, snapshot update, sync apply, mutation에는 통합하지 않았다.

## 변경 사항

수정한 런타임 모듈:

- `src/aios/sync/replay.py`
- `src/aios/sync/__init__.py`

추가한 테스트:

- `tests/test_replay_comparison_helper.py`

추가한 helper:

- `compare_replay_outputs(expected, candidate, case_id=None)`
- `ReplayComparisonIssue`

## Helper Scope

`compare_replay_outputs`는 다음만 수행한다.

- expected dict와 candidate dict를 입력받는다.
- 정해진 replay output fields를 exact value equality로 비교한다.
- mismatch를 `ReplayComparisonIssue` 목록으로 반환한다.
- file IO를 수행하지 않는다.
- provider를 실행하지 않는다.
- adapter를 실행하지 않는다.
- generated content를 만들지 않는다.
- snapshot을 갱신하지 않는다.
- mutation을 수행하지 않는다.

## 비교 필드

비교 대상 필드:

- `schema_version`
- `entry_id`
- `preview_available`
- `generated_content_kind`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `deterministic`
- `provider_metadata`
- `provenance`
- `unavailable_reason`

## Equality Policy

비교는 숨은 normalization 없이 수행된다.

- hash normalization 없음
- type coercion 없음
- `null`과 missing field를 동치 처리하지 않음
- list order는 의미 있음
- provenance source path order는 의미 있음
- nested object도 type과 key order를 포함해 exact 비교

## Failure Codes

구현한 failure codes:

- `replay-schema-mismatch`
- `replay-entry-id-mismatch`
- `replay-preview-available-mismatch`
- `replay-content-kind-mismatch`
- `replay-hash-mismatch`
- `replay-deterministic-flag-mismatch`
- `replay-provider-metadata-mismatch`
- `replay-provenance-mismatch`
- `replay-unavailable-reason-mismatch`

모든 comparison mismatch는 severity `error`와 status `fail`로 표현된다.

## 테스트 범위

추가 테스트는 다음을 검증한다.

- exact match returns no issues
- schema mismatch
- entry id mismatch
- preview_available mismatch
- content kind mismatch
- each generated hash field mismatch maps to `replay-hash-mismatch`
- deterministic flag mismatch
- provider metadata mismatch
- provenance mismatch
- unavailable reason mismatch
- missing field is mismatch, not equal to null
- list order mismatch is mismatch
- string `"true"` differs from boolean `true`
- issue `to_dict()` preserves comparison details

## Integration Boundary

이번 작업은 helper-first 범위에 머문다.

구현하지 않은 항목:

- `aios validate` integration
- envelope v2 integration
- CLI command
- replay CLI
- provider execution
- adapter execution
- generated content generation
- snapshot update
- sync apply
- mutation

## 검증

수행 대상:

- `python -m pytest tests/test_replay_comparison_helper.py`
- `python -m pytest tests/test_validate_replay_manifest.py`
- `python -m pytest tests/test_replay_validate_output_contract.py`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json`
- `python -m aios validate`
- `python -m aios inspect`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Replay comparison의 field-level exact comparison semantics가 순수 helper로 구현되었다. 다음 단계는 helper output을 native validate JSON/envelope v2에 어떻게 연결할지 별도 contract design을 확정하는 것이다.
