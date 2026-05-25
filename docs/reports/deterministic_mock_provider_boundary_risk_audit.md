# 결정론적 목 제공자 경계 리스크 감사

> 이 문서는 human context 감사 보고서이다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 감사는 deterministic mock provider를 설계할 때 발생할 수 있는 실행 경계 혼동과 안전 리스크를 검토한다.

## 목적

현재 `.ai OS`는 fixture-backed replay comparison과 provider capability static validation까지만 지원한다. Real provider execution, sandbox execution, adapter execution, generated content creation, replay execution, sync apply, mutation은 모두 차단되어 있다.

결정론적 목 제공자는 real provider execution으로 바로 넘어가지 않기 위한 안전한 중간 단계지만, "실행처럼 보이는" 구조를 만들기 때문에 새로운 혼동과 운영 리스크가 생긴다. 이 감사는 그 리스크를 식별하고 차단 조건을 정의한다.

## 현재 기준선

| 영역 | 현재 상태 |
| --- | --- |
| Provider capability validation | static-only 구현 및 rule promotion 완료 |
| Replay manifest validation | static-only 구현 및 rule promotion 완료 |
| Replay comparison | `--replay-compare fixture` opt-in, fixture-backed only |
| Fixture preview provider | sync dry-run에서 opt-in fixture provider만 지원 |
| Real provider execution | 금지 |
| Sandbox execution | 금지 |
| Adapter execution | 금지 |
| Generated content creation | 금지 |
| Snapshot update | 금지 |
| Sync apply/mutation | 금지 |

## 새 리스크 계층

목 제공자는 실제 provider가 아니지만, provider execution boundary와 유사한 interface를 만들 가능성이 있다. 따라서 기존 fixture comparison보다 높은 리스크 계층으로 본다.

주요 차이:

- 단순 fixture validation보다 execution semantics에 가깝다.
- trace, duration, no-write confirmation 같은 실행형 metadata를 다룰 수 있다.
- 잘못 설계하면 real provider execution authorization처럼 오해될 수 있다.
- fixture-backed output이 generated content처럼 오해될 수 있다.

## 리스크 매트릭스

| Risk | Impact | Control |
| --- | --- | --- |
| 목 제공자를 real provider로 오해 | provider execution 금지 경계 약화 | 문서와 output metadata에 `mock`/`fixture-backed` 명시 |
| fixture output을 generated content로 오해 | update/apply readiness 과대평가 | generated content creation이 아님을 output contract에 명시 |
| hidden filesystem IO | read-only invariant 훼손 | in-memory input 전달을 기본으로 하고 provider 내부 IO 금지 |
| snapshot update temptation | replay baseline 변조 | snapshot auto-update 금지 유지 |
| nondeterministic randomness | replay 신뢰도 하락 | randomness, wall-clock, env dependency 금지 |
| hidden normalization | hash drift 은폐 | line ending, trailing newline, BOM 자동 정규화 금지 |
| retry로 nondeterminism 은폐 | false pass 발생 | replay mismatch auto retry 금지 |
| provider capability를 execution approval로 오해 | sandbox 없이 실행 착수 | capability validation은 static readiness only로 유지 |
| no-write metadata 과신 | 실제 mutation detection 누락 | no-write confirmation은 증거 metadata일 뿐 전체 mutation safety가 아님 |
| observability 부족 | failure 원인 추적 불가 | trace id, input/output hash, provider id/version, duration 기록 |

## 경계 통제

Deterministic mock provider를 설계할 때 다음 통제를 적용해야 한다.

- fixture-backed deterministic output만 허용한다.
- provider 내부에서 target/source/manifest/snapshot 파일을 읽거나 쓰지 않는다.
- network access를 금지한다.
- adapter execution을 금지한다.
- dynamic plugin loading을 금지한다.
- output-affecting config를 provider snapshot에 고정한다.
- no-write confirmation metadata를 남긴다.
- mismatch는 retry하지 않는다.
- preview/update candidate 또는 sync apply authorization으로 연결하지 않는다.

## 실패 및 unavailable semantics

목 제공자 경계에서는 다음 상태를 미리 정의해야 한다.

| Code | Meaning |
| --- | --- |
| `nondeterministic-output` | 동일 input/version에서 output이 재현되지 않음 |
| `provider-execution-disabled` | real provider execution이 승인되지 않음 |
| `provider-isolation-violation` | 금지된 IO, network, env mutation 등 격리 위반 |
| `provider-capability-missing` | capability declaration이 없거나 요구조건을 만족하지 않음 |
| `provider-output-invalid` | output schema 또는 required metadata 위반 |
| `provider-timeout` | future execution boundary에서 timeout 발생 |

목 제공자 단계에서는 timeout이 실제 provider timeout이 아니라 harness simulation failure일 수 있으므로, output message가 real execution으로 오해되지 않도록 해야 한다.

## False confidence 리스크

목 제공자 성공은 다음을 의미하지 않는다.

- real provider가 deterministic하다는 증명
- adapter runtime이 안전하다는 증명
- sandbox policy가 충분하다는 증명
- generated content가 올바르다는 증명
- sync apply가 안전하다는 증명
- mutation readiness가 확보되었다는 증명

목 제공자는 interface와 fixture replay semantics를 검증하는 단계다.

## 인덱스 및 문맥 리스크

이번 문서들은 runtime contract가 아니다. Future tasks는 summary-first loading을 유지해야 한다.

- `.ai/rules`가 canonical runtime authority다.
- `docs/index/current_runtime_context.md`는 현재 상태 확인용이다.
- 상세 plan/report는 관련 작업에서만 task-load한다.
- 목 제공자 설계 문서를 always-load하면 오히려 provider execution이 승인된 것처럼 오해될 수 있다.

## 권장 결론

다음 단계로 deterministic mock provider fixture bundle을 진행하는 것이 적절하다. 단, 해당 bundle도 provider execution을 구현해서는 안 되며 fixture-only 또는 helper-first 범위로 제한해야 한다.

권장 순서:

1. Deterministic mock provider fixture bundle
2. Execution trace schema design
3. Subprocess sandbox architecture plan

Real provider execution, sandbox execution, adapter execution, generated content creation, replay execution, snapshot update, sync apply, mutation은 계속 차단한다.
