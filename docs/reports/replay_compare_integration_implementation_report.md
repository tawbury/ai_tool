# Replay compare integration implementation report

> 이 문서는 human implementation evidence이다. 런타임 계약은 아니며, 구현된 동작의 근거와 검증 결과를 기록한다.

## 개요

`aios validate <replay-manifest.json>`에 fixture-backed replay comparison을 opt-in 모드로 통합했다. 기본 replay manifest validation은 계속 static-only이며, `--replay-compare fixture`가 없는 native JSON 및 envelope v2 출력 계약은 변경하지 않았다.

## 구현 범위

추가된 사용자 경로:

```bash
python -m aios validate <replay-manifest.json> --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --envelope-v2 --replay-compare fixture
```

변경 파일:

- `src/aios/cli.py`
- `src/aios/validate/engine.py`
- `src/aios/validate/validators/replay_manifest.py`
- `tests/test_replay_compare_integration.py`

## 동작 요약

`--replay-compare fixture`가 제공되면 validate는 다음 순서로 동작한다.

1. replay manifest static validation을 먼저 실행한다.
2. static validation error가 있으면 comparison을 실행하지 않는다.
3. 각 replay case의 expected output fixture를 읽는다.
4. 같은 fixture에서 fixture-derived candidate object를 구성한다.
5. `compare_replay_outputs(expected, candidate, case_id=case_id)`를 호출한다.
6. mismatch가 있으면 helper code와 comparison details를 validate result로 보존한다.
7. mismatch가 없으면 `replay_comparison_checked` info result를 추가한다.

## Usage/config error

다음은 exit code `2`를 반환한다.

- unsupported `--replay-compare` value
- replay manifest가 아닌 target에서 `--replay-compare` 사용
- target 없이 `--replay-compare` 사용
- 기존 정책: `--envelope-v2`를 `--json` 없이 사용

## Native JSON 출력

Opt-in comparison이 켜져도 native schema는 유지된다.

- `schema_version`: `aios.validate.result.v0`
- `target.kind`: `replay-manifest`
- static validation results 포함
- comparison success result:
  - `code`: `replay_comparison_checked`
  - `severity`: `info`
  - `details.comparison_mode`: `fixture`
  - `details.cases`: checked case count
- comparison mismatch result:
  - `code`: `ReplayComparisonIssue.code`
  - `severity`: `error`
  - `status`: `fail`
  - `details.case_id`
  - `details.comparison_field`
  - `details.comparison_mode`
  - `details.expected_value` 또는 `details.expected_summary`
  - `details.actual_value` 또는 `details.actual_summary`

## Envelope v2 출력

`--json --envelope-v2 --replay-compare fixture`는 기존 validate envelope에 다음 meta를 추가한다.

- `meta.replay_compare: fixture`
- `meta.comparison_mode: fixture`
- `meta.provider_execution: false`
- `meta.mutation_performed: false`

`payload.results`와 `messages`는 comparison success/error result를 보존한다.

## 보존된 기본 동작

다음 명령은 기존 static-only 출력 계약을 유지한다.

```bash
python -m aios validate <replay-manifest.json>
python -m aios validate <replay-manifest.json> --json
python -m aios validate <replay-manifest.json> --json --envelope-v2
```

`tests/test_replay_validate_output_contract.py`가 기존 native JSON 및 envelope v2 계약을 계속 검증한다.

## 명시적 non-goals

이번 구현은 다음을 추가하지 않았다.

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

## 검증

실행 및 통과:

- `python -m pytest tests/test_replay_compare_integration.py`
- `python -m pytest tests/test_replay_validate_output_contract.py tests/test_replay_comparison_helper.py`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json --replay-compare fixture`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json --envelope-v2 --replay-compare fixture`

최종 검증은 커밋 전 전체 요청 검증 명령으로 다시 수행한다.

## 잔여 작업

권장 다음 단계:

1. Replay comparison output contract stabilization tests를 별도 bundle로 강화한다.
2. 구현 안정화 후 `.ai/rules/operations/sync.rules.md`와 `validation.rules.md`에 opt-in replay comparison runtime behavior를 승격할지 감사한다.
3. real provider execution boundary는 계속 별도 설계와 승인 전까지 차단한다.
