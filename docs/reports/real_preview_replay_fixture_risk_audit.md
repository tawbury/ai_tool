# Real preview replay fixture 위험 감사

## 개요

이 문서는 future real preview provider replay fixture 계약의 위험을 감사한다. Replay fixture는 deterministic validation의 기준점이 되므로, fixture가 부정확하거나 stale하면 provider가 불안정해도 안정적으로 보이는 문제가 생길 수 있다.

이번 감사는 문서 작업만 수행한다. Provider implementation, adapter runtime, generated content generation, sync apply, mutation은 구현하지 않는다.

## 위험 매트릭스

| 위험 | 심각도 | 가능성 | 설명 | 완화 |
| --- | --- | --- | --- | --- |
| placeholder hash accepted | 높음 | 중간 | `sha256:<source>` 같은 placeholder가 fixture에 남으면 replay 검증이 무의미해진다. | no-placeholder validation, lowercase hex check |
| stale snapshot | 높음 | 중간 | provider output logic이 바뀌었는데 snapshot이 갱신되지 않거나 반대로 무단 갱신될 수 있다. | no auto-update, provider version bump, migration note |
| provider version drift | 높음 | 중간 | 같은 provider version에서 output이 바뀌면 deterministic contract가 깨진다. | same version exact match, drift failure code |
| incomplete replay dimensions | 중간 | 중간 | LF/CRLF/BOM/trailing newline case가 빠지면 bytes policy 위반을 놓친다. | required case inventory |
| unavailable output misclassified | 높음 | 낮음 | unavailable output이 update 후보처럼 해석될 수 있다. | null generated hashes and exact unavailable reason |
| source path order instability | 중간 | 중간 | source order가 불안정하면 provenance mismatch가 반복된다. | explicit ordered source paths |
| provider snapshot under-specified | 높음 | 중간 | output-affecting config가 빠지면 replay 결과 원인을 설명할 수 없다. | required output_affecting_config |
| fixture path traversal | 중간 | 낮음 | replay manifest fixture path가 안전하지 않으면 잘못된 파일을 읽을 수 있다. | relative path, no parent traversal |
| automatic retry hides nondeterminism | 높음 | 낮음 | replay mismatch 후 retry가 nondeterminism을 숨긴다. | retry prohibition |
| migration note missing | 중간 | 중간 | intentional snapshot change의 이유가 사라진다. | migration note required |
| over-broad fixture scope | 중간 | 중간 | fixture suite가 real provider implementation까지 암묵적으로 요구할 수 있다. | fixture contract is validation input only |
| mutation boundary confusion | 높음 | 낮음 | replay pass가 sync apply readiness로 오해될 수 있다. | replay validates stability only |

## 주요 위험 상세

### Placeholder hash accepted

Replay fixture는 expected output의 기준이 된다. Placeholder hash가 남아 있으면 hash equality test가 실제 deterministic behavior를 증명하지 못한다.

완화:

- 모든 non-null hash는 `sha256:<lowercase-hex>` 형식이어야 한다.
- `<source>`, `<generated>`, `TODO`, `placeholder` 문자열을 금지한다.
- Fixture schema test에서 placeholder를 validation failure로 처리한다.

### Stale snapshot

Snapshot이 오래되면 provider가 올바르게 변경되어도 실패하거나, 반대로 잘못된 output이 기준으로 남을 수 있다. 자동 snapshot update는 이 문제를 더 악화한다.

완화:

- Snapshot auto-update 금지.
- Output-affecting change는 provider version bump를 요구한다.
- Intentional snapshot change는 migration note를 요구한다.
- Snapshot 변경은 일반 source change처럼 review되어야 한다.

### Provider version drift

같은 provider version에서 output hash가 바뀌면 replay fixture의 핵심 가정이 깨진다.

완화:

- `provider_id`와 `provider_version` exact match.
- Drift는 `replay-provider-version-drift` 또는 `replay-hash-mismatch`로 fail.
- Provider version과 hash policy version을 함께 확인한다.

### Incomplete replay dimensions

Observed UTF-8 bytes 정책은 LF/CRLF, trailing newline, BOM 차이를 보존한다. 이 차원을 fixture가 다루지 않으면 provider가 암묵적으로 정규화해도 놓칠 수 있다.

완화:

- whole-file LF
- whole-file CRLF
- whole-file trailing newline
- whole-file BOM
- managed-block LF
- managed-block CRLF
- mixed-boundary
- unavailable cases를 최소 필수로 둔다.

### Unavailable output misclassified

Unavailable output이 generated hash를 가지고 있거나 `preview_available` 상태가 흔들리면 dry-run update 후보 판단을 오염시킬 수 있다.

완화:

- unavailable output의 generated hash fields는 모두 `null`.
- unavailable reason exact match.
- deterministic flag exact match.
- unavailable output replay pass는 no-update를 의미한다.

### Source path order instability

Source paths가 filesystem traversal 순서에 의존하면 replay mismatch가 불안정하게 발생한다.

완화:

- Input fixture에 source path order를 명시한다.
- Provenance comparison은 exact ordered comparison으로 한다.
- Provider는 input order를 보존하거나 명시 정렬 정책을 가져야 한다.

### Provider snapshot under-specified

Provider snapshot에 output-affecting config가 빠지면 output drift의 원인을 설명할 수 없다.

완화:

- Provider snapshot은 `output_affecting_config`를 필수로 가진다.
- Hash policy, supported sync modes, deterministic capability를 필수화한다.
- Provider metadata와 snapshot consistency를 검증한다.

### Fixture path traversal

Replay manifest가 `../` 또는 absolute path를 허용하면 fixture root 밖의 파일을 읽을 수 있다.

완화:

- Fixture path는 replay root 기준 상대 경로만 허용한다.
- Parent traversal 금지.
- Absolute path 금지.
- Missing fixture는 validation failure.

### Automatic retry hides nondeterminism

Replay mismatch 후 retry하면 flakey provider가 우연히 snapshot과 일치할 수 있다.

완화:

- Replay mismatch는 즉시 failure.
- Retry 금지.
- Timeout과 nondeterminism은 unavailable reason으로 분류한다.

### Migration note missing

Provider version bump와 snapshot change가 있어도 이유가 없으면 과거 output과 현재 output의 차이를 추적할 수 없다.

완화:

- Migration note 필수.
- Affected cases와 reason for output drift 기록.
- Hash policy impact 기록.
- Mutation remains blocked 확인.

### Over-broad fixture scope

Fixture contract가 provider implementation이나 adapter execution까지 암묵적으로 요구하면 read-only planning boundary를 흐릴 수 있다.

완화:

- Fixture는 validation input일 뿐이다.
- Provider implementation과 adapter runtime은 non-goal로 유지한다.
- Generated content creation은 구현하지 않는다.

### Mutation boundary confusion

Replay pass는 generated output 안정성을 의미할 뿐이다. Sync apply readiness와는 무관하다.

완화:

- Replay fixture contract에 sync apply와 mutation non-goal을 반복 명시한다.
- `update` 후보는 여전히 informational이다.
- Mutation gate가 별도로 필요하다.

## Failure handling expectations

Replay validation은 다음 failure codes를 사용해야 한다.

- `replay-hash-mismatch`
- `replay-provenance-mismatch`
- `replay-provider-metadata-mismatch`
- `replay-unavailable-reason-mismatch`
- `replay-deterministic-flag-mismatch`
- `replay-schema-mismatch`
- `replay-fixture-missing`
- `replay-provider-version-drift`

Failure는 validation failure로 처리해야 하며 자동 수정이나 snapshot update를 수행하면 안 된다.

## Index impact

이 계약과 감사는 Phase 8의 active planning context에 해당한다.

필요한 index 업데이트:

- `docs/index/document_status_registry.md`: 새 plan/report entry 추가.
- `docs/index/phase_6_8_summary.md`: next recommended direction을 replay fixture contract 이후 fixture-only bundle로 갱신.
- `docs/index/current_runtime_context.md`: real preview/replay schema planning 목록에 replay fixture contract를 반영.

## 차단 유지 항목

다음 항목은 계속 차단한다.

- provider implementation
- adapter runtime
- generated content generation
- sync apply
- target mutation
- manifest persistence
- transaction log persistence
- rollback execution
- marker insertion, repair, deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- orchestration
- workflow execution
- `.ai/registry/`
- auto-fix
- source mutation

## 결론

Replay fixture contract의 핵심 위험은 fixture 자체가 불안정하거나 불완전한 기준이 되는 것이다. Placeholder hash 금지, provider snapshot 필수화, required replay cases, exact comparison, no auto-update 정책을 통해 fixture가 deterministic validation의 신뢰 가능한 기준이 되도록 해야 한다.
