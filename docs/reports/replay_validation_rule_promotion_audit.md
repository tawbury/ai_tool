# Replay validation rule promotion 감사

## 개요

Replay manifest/provider snapshot 정적 검증은 현재 `aios validate <replay_manifest.json>`로 실행 가능하며, native validate JSON과 envelope v2 출력 계약 테스트도 안정화되어 있다. 이 문서는 해당 동작을 runtime-facing governance rules로 승격할지, 승격한다면 어느 규칙 파일에 반영할지 판단한다.

이번 작업은 감사와 권고만 수행한다. `.ai/rules`는 수정하지 않았고 runtime code도 변경하지 않았다.

## 검토 대상

검토한 문서와 규칙:

- `docs/reports/replay_manifest_validate_integration_report.md`
- `docs/reports/replay_validate_output_contract_report.md`
- `docs/plan/deterministic_replay_test_architecture.md`
- `docs/plan/real_preview_replay_fixture_contract.md`
- `.ai/rules/operations/sync.rules.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/documentation-governance.rules.md`

## 현재 구현 상태

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| `aios validate <replay_manifest.json>` 지원 | 구현됨 | replay manifest validate integration report |
| Replay manifest static validation | 구현됨 | `src/aios/sync/replay.py` |
| Provider snapshot static validation | 구현됨 | `src/aios/sync/replay.py` |
| Native validate JSON output contract | 안정화됨 | replay validate output contract report |
| Envelope v2 output contract | 안정화됨 | replay validate output contract report |
| Provider execution | 없음 | 명시적 non-goal |
| Adapter execution | 없음 | 명시적 non-goal |
| Generated content generation | 없음 | 명시적 non-goal |
| Replay output comparison | 없음 | 아직 구현 전 |
| Snapshot auto-update | 없음 | 명시적 non-goal |
| Sync apply/mutation | 차단됨 | sync runtime rules |

## Promotion Readiness 판단

Replay manifest validation behavior는 runtime-facing rule promotion에 충분히 durable하다.

이유:

- CLI-visible behavior가 존재한다.
- `aios validate <replay_manifest.json>` target detection과 validation 결과가 구현되어 있다.
- Native JSON과 envelope v2 출력 계약이 테스트로 고정되어 있다.
- 동작 범위가 static-only로 좁고 안전하다.
- provider execution, adapter execution, generated content generation, snapshot update, mutation/apply가 모두 명시적으로 제외되어 있다.
- 현재 `.ai/rules/operations/sync.rules.md`는 sync manifest validation과 fixture preview runtime은 설명하지만 replay manifest validation은 아직 설명하지 않는다.

따라서 이 동작은 docs/report에만 남기기보다 runtime-facing governance로 승격하는 것이 맞다.

## Promotion Target 판단

| 후보 | 판단 | 이유 |
| --- | --- | --- |
| `sync.rules.md` | primary target | replay manifest는 real preview provider와 sync dry-run safety boundary에 속한다. provider execution 금지, snapshot update 금지, mutation 차단은 sync governance와 직접 연결된다. |
| `validation.rules.md` | secondary short pointer | `aios validate` target behavior이므로 validation rule에 짧은 cross-reference가 있으면 발견성이 좋아진다. 단, 상세 schema와 sync safety boundary를 validation.rules에 중복하면 domain-independent 원칙이 약해진다. |
| both | 권장 | 상세 runtime boundary는 sync.rules, command-level validation pointer는 validation.rules에 나누는 방식이 가장 작고 명확하다. |
| neither | 비권장 | 이미 CLI-visible behavior와 output contract가 안정화되어 docs-only 상태로 두면 future agents가 runtime rules만 읽고 replay validation boundary를 놓칠 수 있다. |

권장 promotion target은 `sync.rules.md`와 `validation.rules.md`의 split promotion이다.

## Promote할 내용

`sync.rules.md`에 승격할 내용:

- `python -m aios validate <replay-manifest.json>` 지원
- `python -m aios validate <replay-manifest.json> --json`
- `python -m aios validate <replay-manifest.json> --json --envelope-v2`
- Replay manifest schema:
  - `aios.preview_replay_manifest.v0`
- Provider snapshot schema:
  - `aios.preview_provider_snapshot.v0`
- Static-only validation boundary:
  - required fields
  - provider id/version match
  - hash policy match
  - case id uniqueness
  - fixture path safety
  - referenced input/output fixture existence
  - input/output fixture schema versions
  - hash format and placeholder hash rejection
  - unavailable output generated hash null policy
  - provider metadata and provenance presence
- Explicitly forbidden:
  - provider execution
  - adapter execution
  - generated content generation
  - replay output comparison
  - snapshot auto-update
  - replay CLI
  - sync apply and mutation
- Envelope v2 preservation:
  - `command: validate`
  - `target.kind: replay-manifest`
  - `meta.legacy_schema_version: aios.validate.result.v0`
  - `payload.results` and `messages` preserve replay validation details

`validation.rules.md`에 승격할 내용:

- `aios validate` may validate replay manifests as first-class JSON targets.
- Replay manifest validation remains static-only.
- Sync-specific schema details and mutation boundary live in `sync.rules.md`.

## Human-context only로 남길 내용

다음 항목은 runtime rule에 넣지 않는 것이 좋다.

- 전체 fixture directory layout
- 개별 fixture filename 목록
- 특정 테스트 파일 이름 전체 목록
- migration note 예시 상세
- future replay CLI 아이디어
- future real provider replay comparison algorithm 상세
- provider implementation sequence 세부 단계

이 항목들은 구현/테스트 문맥에서는 유용하지만 runtime-facing rule에 넣으면 규칙 파일이 과도하게 길어지고 stale risk가 커진다.

## 권고

권고: promote now, split promotion.

후속 작업으로 `.ai/rules/operations/sync.rules.md`를 primary로 업데이트하고, `.ai/rules/operations/validation.rules.md`에는 짧은 pointer만 추가한다.

Promotion을 replay comparison helper 이후로 미루는 것은 권장하지 않는다. 현재 구현된 것은 replay comparison이 아니라 static validation이며, 이미 안정화된 CLI-visible behavior다. 오히려 지금 승격해야 future real provider 작업이 provider execution 금지, snapshot auto-update 금지, mutation 차단을 명확히 상속한다.

## 후속 작업의 정확한 변경 제안

후속 promotion task에서 수행할 변경:

1. `.ai/rules/operations/sync.rules.md`
   - Supported Runtime Commands에 replay manifest validate 세 줄 추가:
     - `python -m aios validate <replay-manifest.json>`
     - `python -m aios validate <replay-manifest.json> --json`
     - `python -m aios validate <replay-manifest.json> --json --envelope-v2`
   - 새 섹션 `Replay Manifest Validation` 추가
   - static-only scope와 forbidden actions 명시
   - `aios.preview_replay_manifest.v0`, `aios.preview_provider_snapshot.v0` schema 명시
   - Envelope v2 validate mapping에 `target.kind: replay-manifest` 추가

2. `.ai/rules/operations/validation.rules.md`
   - `aios validate` first-class runtime targets 목록에 replay manifest 추가
   - 상세 schema와 sync safety boundary는 `sync.rules.md`를 참조한다고 명시

3. 보고서 작성
   - `docs/reports/replay_validation_runtime_rule_promotion_report.md`

4. 검증
   - `python -m aios validate`
   - `python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json --json --envelope-v2`
   - `python -m aios inspect`
   - `git diff --check`

## Non-goals

이번 감사와 후속 promotion 모두 다음을 구현하거나 승인하지 않는다.

- provider execution
- replay output comparison
- adapter runtime
- generated content generation
- replay CLI
- snapshot auto-update
- sync apply
- mutation
- manifest persistence
- transaction persistence
- rollback execution
- marker mutation
- repository-wide scan
- activation-driven preview selection
- source mutation

## 결론

Replay manifest validation은 지금 runtime governance rule로 승격할 만큼 안정화되어 있다. 승격 위치는 `sync.rules.md`를 primary, `validation.rules.md`를 short pointer로 하는 split promotion이 적절하다. 다음 안전한 작업은 실제 `.ai/rules` 수정과 promotion report 작성이다.
