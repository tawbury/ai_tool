# 제공자 실행 trace schema 리스크 감사

> 이 문서는 human context 감사 보고서이다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 감사는 provider execution trace schema가 실행 승인으로 오해되는 위험을 검토한다.

## 목적

Provider execution trace schema는 future provider-like path를 관측하기 위한 구조다. 그러나 "execution trace"라는 이름은 실제 실행 승인, sandbox approval, sync apply readiness로 오해될 수 있다. 이 감사는 trace schema를 설계할 때 유지해야 할 안전 경계와 실패 모드를 정리한다.

## 현재 기준선

| Area | State |
| --- | --- |
| Deterministic mock provider boundary | 설계 완료 |
| Mock provider fixtures | fixture-only bundle 구현 |
| Provider capability validation | static-only 구현 및 rule promotion 완료 |
| Replay comparison | fixture-backed opt-in only |
| Real provider execution | 금지 |
| Sandbox execution | 금지 |
| Dynamic provider loading | 금지 |
| Adapter execution | 금지 |
| Generated content creation | 금지 |
| Snapshot update | 금지 |
| Replay execution | 금지 |
| Sync apply/mutation | 금지 |

## 주요 리스크

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Trace를 execution authorization으로 오해 | provider execution 금지 경계 약화 | trace 문서에 "not authorization" 명시 |
| Trace success를 write authorization으로 오해 | sync apply/mutation 차단 약화 | `mutation_performed: false`와 non-goal 반복 |
| `no_write_confirmed` 과신 | 실제 mutation safety를 대체한다고 오해 | no-write confirmation은 provider-like path 증거일 뿐이라고 명시 |
| Failure code가 update candidate로 오해 | unsafe dry-run classification | failure/unavailable은 update authorization이 아님을 명시 |
| Future sandbox mode 선점 | sandbox 설계 없이 mode 사용 | `subprocess-sandbox`는 reserved only로 유지 |
| 민감 정보 노출 | env/config secret 유출 | v0는 hashes/summaries 우선, future secret redaction 요구 |
| Provider metadata drift | replay evidence 신뢰 하락 | provider id/version과 output-affecting config를 trace에 보존 |
| Hidden normalization | hash mismatch 은폐 | trace hash fields는 normalization 없이 exact value 보존 |
| Observability 부족 | failure 원인 추적 불가 | trace id, provider id/version, input/output hash, duration, failure code 필수화 |

## Success semantics 리스크

Trace success는 다음만 의미한다.

- 선언된 mode에서 deterministic output이 관측되었다.
- no-write confirmation이 통과했다.
- network disabled 정책이 보존되었다.
- mutation은 수행되지 않았다.
- failure code가 없다.

Trace success는 다음을 의미하지 않는다.

- real provider execution 승인
- sandbox approval
- adapter execution 승인
- generated content 정합성 승인
- sync apply 승인
- mutation readiness 확보

## Failure/unavailable 리스크

Failure와 unavailable은 반드시 명시적이어야 한다. 모호한 failure는 false confidence를 만든다.

필수 원칙:

- generated hashes가 없으면 null로 표현한다.
- unavailable reason은 생략하지 않는다.
- failure code는 정해진 enum만 사용한다.
- failure 상태에서도 `mutation_performed`는 false여야 한다.
- no-write verification을 완료하지 못했다면 성공 trace로 취급하지 않는다.

## Envelope v2 리스크

Envelope v2에 trace metadata가 들어가면 runtime command result처럼 보일 수 있다.

통제 원칙:

- `provider_execution`을 명확히 보존한다.
- `sandbox_execution`을 명확히 보존한다.
- `mutation_performed`를 명확히 보존한다.
- `provider_mode`가 `fixture-mock`인 경우 real execution이 아님을 보존한다.
- trace detail은 payload evidence이며 command authorization이 아니다.

## Mock fixture compatibility

현재 mock provider fixture는 trace schema 후보와 호환되는 필드를 이미 가진다. 하지만 이것은 fixture-only contract다.

위험:

- 기존 mock output을 trace로 바로 간주하면 별도 trace schema validation 없이 계약이 흐려질 수 있다.
- trace fixture bundle 없이 helper부터 구현하면 실행 경계가 먼저 생길 수 있다.

권장 통제:

- 먼저 trace fixture bundle을 만든다.
- 이후 trace validator helper를 만든다.
- 그 다음에야 mock provider helper design을 검토한다.

## Redaction 리스크

v0에는 secret이 없다는 가정이 가능하지만, future provider config에는 secret이 들어갈 수 있다.

초기 정책:

- hash와 provider id/version은 표시 가능하다.
- source-relative path는 provenance 목적으로 표시 가능하다.
- raw generated content는 trace에 넣지 않는다.
- env/config fields는 future schema에서 redaction policy를 먼저 정의해야 한다.

## 결론

Provider execution trace schema 설계는 다음 단계로 진행해도 안전하다. 단, 다음 구현 slice는 execution이 아니라 trace fixture bundle이어야 한다. Trace schema는 observability와 replay evidence를 위한 것이며 provider execution, sandbox execution, adapter execution, generated content creation, replay execution, snapshot update, sync apply, mutation을 승인하지 않는다.

권장 다음 작업:

1. Provider execution trace fixture bundle
2. Trace validator helper
3. Mock provider helper design
4. Subprocess sandbox architecture plan
