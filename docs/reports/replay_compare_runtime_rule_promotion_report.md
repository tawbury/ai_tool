# Replay compare runtime rule promotion report

> 이 문서는 human implementation evidence이다. 런타임 계약 자체는 `.ai/rules/operations/sync.rules.md`와 `.ai/rules/operations/validation.rules.md`에 있다.

## 개요

Phase 8 replay comparison runtime v0 완료 감사 결과에 따라 opt-in replay comparison validation behavior를 runtime governance rules에 승격했다.

## 변경 파일

- `.ai/rules/operations/sync.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

## 승격된 동작

`sync.rules.md`에 다음 지원 명령을 추가했다.

```bash
python -m aios validate <replay-manifest.json> --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --replay-compare fixture
python -m aios validate <replay-manifest.json> --json --envelope-v2 --replay-compare fixture
```

추가로 다음 정책을 명시했다.

- no-flag replay validation은 static-only로 유지한다.
- `--replay-compare fixture`는 opt-in only이다.
- 지원 mode는 `fixture`뿐이다.
- static replay validation이 성공한 뒤에만 comparison을 실행한다.
- static validation failure는 comparison을 short-circuit한다.
- comparison은 fixture-backed only이다.
- success code는 `replay_comparison_checked`이다.
- mismatch code는 `ReplayComparisonIssue.code`를 보존한다.
- comparison details는 `case_id`, `comparison_field`, `comparison_mode: fixture`, expected/actual value 또는 summary를 보존한다.
- envelope v2 meta는 `replay_compare`, `comparison_mode`, `provider_execution: false`, `mutation_performed: false`를 보존한다.
- unsupported compare value, non replay-manifest target, target 없는 compare flag는 exit code `2`이다.

## Validation rules pointer

`validation.rules.md`에는 domain-independent pointer만 추가했다.

- replay manifest validation은 기본적으로 static-only이다.
- replay comparison은 fixture-backed opt-in validation일 때만 허용된다.
- no-flag static validation behavior는 유지되어야 한다.
- provider execution, adapter execution, generated content, snapshot update, sync apply, mutation은 계속 금지된다.
- 상세 schema/output/safety boundary는 `sync.rules.md`에 둔다.

## 유지된 금지 경계

이번 rule promotion은 다음을 허용하지 않는다.

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

커밋 전 다음 명령으로 검증한다.

- `python -m aios inspect`
- `python -m aios validate`
- `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json --replay-compare fixture`
- `python -m pytest tests/test_replay_compare_output_contract.py`
- `python -m compileall -q src/aios aios`
- `git diff --check`
- `git diff --cached --check`

## 결론

Opt-in replay comparison runtime v0 behavior가 `.ai/rules` runtime governance에 반영되었다. 다음 안전 방향은 provider isolation requirements audit이며, real provider execution은 격리, determinism, no-write/no-snapshot boundary가 별도 승인되기 전까지 계속 차단한다.
