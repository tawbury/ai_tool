# Real preview provider 위험 감사

## 개요

이 문서는 `.ai OS` future real preview provider의 주요 위험을 감사한다. Fixture provider는 deterministic fixture mapping만 수행했지만, real provider는 실제 source/context를 사용해 비교 가능한 generated preview output을 만들 수 있다. 이 단계는 sync apply나 mutation으로 가까워 보일 수 있으므로 경계를 명확히 해야 한다.

이번 감사는 문서 작업만 수행한다. Provider 구현, adapter 실행, generated content 생성, sync apply, mutation은 구현하지 않는다.

## 위험 매트릭스

| 위험 | 심각도 | 가능성 | 설명 | 완화 |
| --- | --- | --- | --- | --- |
| nondeterministic output | 높음 | 중간 | 동일 입력이 매번 다른 hash를 만들면 dry-run update 후보가 불안정해진다. | deterministic flag, provider version, replay tests, nondeterministic-output unavailable reason |
| provider identity drift | 높음 | 중간 | provider logic이 바뀌었는데 version이 유지되면 hash 의미가 바뀐다. | output-affecting change마다 provider_version 증가 |
| line ending drift | 중간 | 높음 | provider가 CRLF/LF를 정규화하면 hash policy와 충돌한다. | observed UTF-8 bytes, no normalization, line ending fixture tests |
| over-broad source selection | 높음 | 중간 | provider가 명시되지 않은 source/context를 포함하면 preview output이 noisy해진다. | explicit source_evidence만 허용 |
| adapter execution boundary confusion | 높음 | 중간 | provider 계약이 adapter 실행 승인으로 오해될 수 있다. | adapter execution은 별도 승인 필요, contract는 execution 권한 아님 |
| false update candidate | 높음 | 중간 | provider output만 보고 update 후보를 만들면 drift/marker/source 문제가 가려질 수 있다. | clean-target-only comparison, precedence 유지 |
| marker boundary misuse | 높음 | 낮음 | invalid marker 상태에서 managed-block hash를 비교하면 잘못된 boundary를 신뢰한다. | marker integrity가 valid일 때만 provider comparison |
| ownership inference | 높음 | 낮음 | provider가 target ownership을 추론하면 user-owned 영역을 침범할 수 있다. | ownership은 manifest에서만 읽고 provider가 변경하지 못함 |
| stale source | 높음 | 중간 | source hash가 현재 파일과 다르면 preview가 오래된 입력을 기준으로 생성될 수 있다. | source hash check가 provider comparison보다 우선 |
| unavailable state hidden | 중간 | 중간 | provider failure가 출력에 보존되지 않으면 왜 update 후보가 없는지 알 수 없다. | unavailable_reason enum과 provenance 보존 |
| provider timeout instability | 중간 | 중간 | provider timeout이 command failure인지 no-preview인지 불명확해질 수 있다. | provider-timeout unavailable state로 분류 |
| preview/apply boundary confusion | 높음 | 중간 | `update` 후보가 write authorization처럼 해석될 수 있다. | `update`는 informational, mutation_performed false, mutation gate 유지 |

## 주요 위험 상세

### Nondeterministic output

Real provider가 모델, 외부 프로세스, 시간, 랜덤 순서, 네트워크 상태에 의존하면 같은 입력에서 다른 generated hash가 나올 수 있다. 이는 output contract test와 dry-run 신뢰성을 동시에 약화한다.

완화:

- 동일 input은 동일 output hash를 만들어야 한다.
- deterministic guarantee가 없으면 `preview_available: false`와 `unavailable_reason: nondeterministic-output`을 반환한다.
- provider replay tests를 필수화한다.
- provider version과 hash policy를 output metadata에 포함한다.

### Provider identity drift

Provider 내부 로직이 바뀌었는데 `provider_version`이 유지되면 동일 provider identity가 다른 hash 의미를 갖게 된다. Manifest와 dry-run output의 설명력이 떨어진다.

완화:

- output에 영향을 주는 변경은 반드시 provider version을 증가시킨다.
- provider id/version을 generated metadata와 provenance에 보존한다.
- future validation에서 provider version 존재 여부를 검사한다.

### Line ending drift

Phase 8 hash policy는 observed UTF-8 bytes를 유지한다. Real provider가 line ending을 자동 정규화하거나 trailing newline을 보정하면 false update 후보가 생길 수 있다.

완화:

- CRLF/LF 정규화 금지.
- trailing newline과 whitespace 보존.
- LF/CRLF/trailing newline fixture replay tests 추가.
- hash policy version이 바뀌기 전까지 normalization mode를 추가하지 않는다.

### Over-broad source selection

Provider가 명시 input 외에 docs/reports/plans, broad rule context, activation context를 임의로 포함하면 generated output에 runtime target과 무관한 noise가 섞일 수 있다.

완화:

- provider는 `source_evidence.source_paths`와 명시 context reference만 사용한다.
- context reference는 unrestricted loading 권한이 아니다.
- activation-driven selection은 별도 설계 전까지 금지한다.
- provenance에 사용한 source paths/hash를 모두 기록한다.

### Adapter execution boundary confusion

Adapter가 미래 provider 구현이 될 수 있지만, provider contract가 adapter execution 승인으로 해석되면 안 된다. Adapter execution은 외부 프로세스, model invocation, file write 가능성 때문에 별도 위험 모델이 필요하다.

완화:

- adapter execution policy를 별도 승인 gate로 분리한다.
- provider contract에는 adapter identity 기록만 허용한다.
- adapter runtime 구현 전 deterministic contract와 safety gate를 먼저 통과해야 한다.

### False update candidate

Generated hash가 현재 target hash와 다르다는 이유만으로 update 후보를 만들면 위험하다. 현재 target이 drifted이거나 marker가 깨졌거나 source가 missing인 경우 preview는 비교 대상이 아니다.

완화:

- manifest validation, source check, marker check, target hash drift check가 preview보다 우선한다.
- target이 clean일 때만 provider output을 비교한다.
- drift-stop, marker conflict, source-missing은 preview보다 항상 우선한다.

### Marker boundary misuse

Managed-block과 mixed-boundary 비교에서 marker가 invalid이면 provider output의 generated managed block hash를 안전하게 적용할 boundary가 없다.

완화:

- marker integrity가 valid가 아니면 provider comparison을 하지 않는다.
- invalid marker는 existing conflict로 유지한다.
- provider는 marker를 repair하거나 infer하지 않는다.

### Ownership inference

Provider가 source나 target content를 보고 ownership을 추론하면 user-owned 영역을 침범할 수 있다. Preview 단계에서 ownership 변경은 허용되지 않는다.

완화:

- ownership은 manifest entry의 값을 사용한다.
- provider output은 ownership을 변경하거나 제안하지 않는다.
- mixed-boundary 외부 content는 provider 비교 대상이 아니다.

### Stale source

Source file이 manifest source hash와 다르면 provider가 어떤 상태를 기준으로 preview를 만들었는지 불명확해진다.

완화:

- source hash mismatch는 provider comparison보다 우선한다.
- provider input과 output 모두 source hash provenance를 보존한다.
- stale source 상태에서는 update 후보를 만들지 않는다.

### Unavailable state hidden

Provider가 실패했는데 dry-run output에 이유가 남지 않으면 사용자는 update 후보가 없는 이유를 알 수 없다.

완화:

- unavailable output은 `unavailable_reason`을 필수로 가진다.
- generated hash fields는 모두 `null`이어야 한다.
- provider metadata와 provenance는 가능한 범위에서 유지한다.
- envelope v2 `payload.results[].details`에 unavailable reason을 보존한다.

### Provider timeout instability

Real provider가 timeout을 command failure로 처리할지 no-preview 상태로 처리할지 불분명하면 CLI 안정성이 떨어진다.

완화:

- timeout은 `unavailable_reason: provider-timeout`으로 분류한다.
- timeout만으로 sync dry-run command를 fail로 만들지 않는다.
- 기존 blocking source/marker/drift 상태가 있으면 그 상태가 우선한다.

### Preview/apply boundary confusion

Real provider가 생기면 `update` 후보가 실제 apply 가능한 상태처럼 보일 수 있다. 그러나 transaction, rollback, marker write, manifest persistence가 없으면 apply는 여전히 불가능하다.

완화:

- `update`는 informational result로 유지한다.
- `meta.mutation_performed: false`를 유지한다.
- sync apply architecture와 mutation readiness gate가 승인되기 전까지 write를 금지한다.

## 검증 기대

Future implementation 전 다음 검증 전략이 필요하다.

- 동일 input replay test
- provider version drift test
- generated hash format test
- LF/CRLF/trailing newline stability test
- unavailable reason enum test
- provider timeout classification test
- unsupported sync mode test
- marker conflict precedence test
- drift-stop precedence test
- envelope v2 preservation test

## 차단 유지 항목

다음 항목은 계속 차단한다.

- provider implementation
- adapter runtime
- generated content generation
- sync apply
- target mutation
- manifest persistence
- transaction persistence
- rollback execution
- marker insertion, repair, deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- orchestration
- workflow execution
- worker execution
- `.ai/registry/`
- auto-fix
- source mutation

## 결론

Real preview provider는 fixture provider 이후의 자연스러운 다음 단계지만, 가장 큰 위험은 deterministic guarantee와 preview/apply boundary 혼동이다. Provider implementation 전에 provider identity, deterministic replay, unavailable/failure semantics, adapter boundary를 계약으로 고정해야 한다. Mutation/apply는 계속 차단해야 한다.
