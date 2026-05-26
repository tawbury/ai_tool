# Current Repository Status and Remaining Work Audit

## 목적

이 보고서는 현재 로컬 `.ai OS` 저장소 상태를 기준으로 완료된 기능, 남은 정적 작업, 차단된 실행 영역, 다음 작업 방식 전환 필요성을 정리한다. 이 문서는 audit/report only 작업이며 runtime code, `.ai/rules`, roadmap을 변경하지 않는다.

## 검사 기준

검사한 항목:

- `git status --short`
- 최근 commit history
- `docs/index/current_runtime_context.md`
- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `.ai/rules/operations/validation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- `src/aios/validate/*`
- `src/aios/providers/*`
- `src/aios/sync/*`
- sync, replay, provider, sandbox 관련 tests

검사 시점의 working tree는 clean 상태였다.

최근 주요 commit 흐름:

- `f676367 docs(aios): design sandbox trace validate output`
- `d73a176 feat(aios): add sandbox trace validator`
- `aa99ceb test(aios): add sandbox trace fixtures`
- `a63dea6 docs(aios): design sandbox trace fixtures`
- `3a60b26 docs(aios): promote sandbox result rules`
- `893055b test(aios): stabilize sandbox result output`
- `6908ef3 feat(aios): validate sandbox results`
- `40da810 feat(aios): validate sandbox policies`
- `e0f29ab docs(aios): promote sandbox policy rules`

## 현재 구현 상태 요약

### Sync dry-run runtime

완료 상태:

- `aios sync --dry-run --manifest <path>` 지원
- native JSON output
- envelope v2 output
- sync manifest validation
- marker parsing
- hash comparison
- drift-stop/conflict classification
- orphan warning
- opt-in fixture preview comparison
- no-preview default output contract 보존

Runtime rule 상태:

- `.ai/rules/operations/sync.rules.md`에 read-only sync, preview, replay validation/comparison, mutation block이 반영되어 있다.

### Replay manifest validation and comparison

완료 상태:

- replay manifest fixture bundle
- replay manifest/provider snapshot static validation
- `aios validate <replay-manifest.json>`
- native JSON/envelope v2 output contract tests
- pure replay comparison helper
- opt-in `--replay-compare fixture`
- no-flag replay validation static-only behavior 보존
- replay comparison runtime rule promotion

차단 상태:

- real provider execution 없음
- actual provider replay 없음
- snapshot update 없음

### Provider capability validation

완료 상태:

- provider capability fixture bundle
- pure provider capability validator helper
- `aios validate <provider-capability.json>`
- native JSON/envelope v2 output contract tests
- runtime rule promotion

경계:

- capability validation은 declaration shape와 safety flags만 검증한다.
- provider registry/discovery나 execution authorization이 아니다.

### Provider execution trace validation

완료 상태:

- provider execution trace fixture bundle
- pure provider execution trace validator helper
- `aios validate <provider-trace.json>`
- native JSON/envelope v2 output contract tests
- runtime rule promotion

경계:

- provider trace validation은 parsed JSON structure와 safety evidence만 검증한다.
- provider execution, sandbox execution, replay execution을 수행하지 않는다.

### Sandbox policy validation

완료 상태:

- sandbox policy fixture bundle
- pure sandbox policy validator helper
- `aios validate <sandbox-policy.json>`
- native JSON/envelope v2 output contract tests
- runtime rule promotion

경계:

- sandbox policy validation은 policy shape와 safety flags만 검증한다.
- sandbox launcher/subprocess execution을 승인하지 않는다.

### Sandbox result validation

완료 상태:

- sandbox execution result fixture bundle
- pure sandbox result validator helper
- `aios validate <sandbox-result.json>`
- native JSON/envelope v2 output contract tests
- runtime rule promotion

경계:

- sandbox result validation은 sandbox result evidence structure만 검증한다.
- sandbox result success는 sync apply, provider output approval, launcher approval이 아니다.

### Sandbox trace fixtures and helper

완료 상태:

- sandbox trace fixture contract plan/risk audit
- `tests/fixtures/providers/sandbox_traces/` fixture bundle
- `tests/test_sandbox_trace_fixtures.py`
- `src/aios/providers/sandbox_trace.py`
- `tests/test_sandbox_trace_validator.py`
- sandbox trace validate output contract plan/risk audit

현재 미완료 상태:

- `aios validate <sandbox-trace.json>` target detection 미구현
- `src/aios/validate/validators/sandbox_trace.py` 미구현
- sandbox trace native JSON/envelope v2 output contract tests 미구현
- sandbox trace validation rule promotion audit/promotion 미수행

중요한 확인:

- `src/aios/validate/targets.py`는 현재 sandbox result까지만 감지한다.
- `src/aios/validate/engine.py`는 sandbox trace validator branch를 아직 갖고 있지 않다.
- 즉 sandbox trace는 helper-only 상태이며 runtime validate target은 아니다.

## 남은 작업

현재 남은 안전한 정적 작업은 다음 순서가 적절하다.

1. Sandbox trace validate integration
   - target kind: `sandbox-trace`
   - schema: `aios.sandbox_trace.v0`
   - priority: sandbox result 이후
   - no execution

2. Sandbox trace output contract stabilization
   - native JSON pass/fail
   - envelope v2 pass/fail
   - shaped invalid/missing schema
   - unrelated JSON non-misclassification
   - existing target detection regression

3. Sandbox trace rule promotion audit
   - validation rules primary target 여부 판단
   - sync rules short safety pointer 여부 판단

4. Sandbox trace runtime rule promotion
   - audit가 권고할 경우에만 진행
   - static-only validation behavior만 승격

5. Static validation completion/readiness audit
   - provider/sandbox static evidence layer가 execution design으로 넘어갈 준비가 되었는지 평가
   - execution implementation 승인 아님

## 계속 차단된 작업

다음은 여전히 차단되어 있다.

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic provider loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- sync apply
- target/source mutation
- manifest write
- transaction log write
- rollback execution
- marker insertion/repair/delete

차단 해제 전 필요한 조건:

- 현재 static validation surface completion audit
- execution readiness audit
- sandbox isolation architecture readiness
- output contract stabilization
- runtime rule promotion
- 명시적인 execution gate

## Ping-pong micro prompt에서 task-bundle 실행으로 전환 필요성

현재는 작은 순차 prompt가 너무 길게 이어져 문맥 피로와 문서 탐색 비용이 증가했다. 기능 단위가 이제 명확해졌으므로 다음 단계부터는 micro prompt보다 task-bundle 실행이 더 안전하다.

권장 전환:

- 단일 prompt에 "integration + output contract tests + report" 같은 정적 bundle을 묶는다.
- rule promotion audit과 rule promotion은 분리한다.
- execution 관련 설계와 구현은 별도 readiness gate 전까지 묶지 않는다.
- 각 bundle 시작 시 `docs/index/current_runtime_context.md`와 관련 rule만 먼저 읽고, 세부 report는 필요한 경우에만 lazy-load한다.

이 전환은 roadmap 생성이 아니라 workflow 조정 권고다.

## 병렬화 가능한 트랙

안전하게 병렬화하거나 묶을 수 있는 트랙:

- docs/report consolidation
- output contract tests
- rule promotion audits
- static validator integrations
- docs index update와 implementation report
- fixture-only bundle과 fixture contract tests

조건:

- 같은 runtime target을 수정하는 integration과 output stabilization은 충돌을 줄이기 위해 한 bundle 안에서 수행하거나 순차 실행한다.
- `.ai/rules` promotion은 audit 결론 이후에만 수행한다.

## 엄격히 순차적인 트랙

다음은 순차로 유지해야 한다.

1. validate integration before output stabilization
2. output stabilization before rule promotion audit
3. rule promotion audit before rule promotion
4. static validation completion audit before execution readiness audit
5. readiness audit before any execution implementation
6. execution architecture approval before sandbox launcher/provider execution

특히 sandbox launcher, subprocess execution, provider execution은 현재 어떤 bundle에도 포함하면 안 된다.

## 문서/context/token 위험 평가

현재 상태:

- `docs/index/document_status_registry.md`는 sandbox trace validate output contract까지 반영되어 있다.
- `docs/index/phase_6_8_summary.md`는 sandbox trace helper/output contract 상태를 반영한다.
- `docs/index/current_runtime_context.md`는 다음 안전 방향을 sandbox trace static integration으로 가리킨다.

위험:

- Phase 6-8 문서가 매우 많아졌다.
- completed report와 risk audit을 무작위로 많이 로드하면 context bloat와 latency가 증가한다.
- 현재 `validation.rules.md`와 `sync.rules.md`는 sandbox trace validate integration을 아직 runtime capability로 언급하지 않는다. 이는 올바른 상태다.

평가:

- docs index는 현재 task routing에는 충분하다.
- 지금 당장 대규모 문서 재정리는 필요하지 않다.
- 다만 다음 큰 전환 전에 "current static validation surface summary" 같은 짧은 요약 문서를 별도 생성하는 것은 도움이 될 수 있다.

## 권장 다음 workflow

다음 작업은 micro prompt가 아니라 정적 bundle로 진행하는 편이 좋다.

권장 bundle:

```text
Sandbox trace validate integration bundle
- implement target detection after sandbox result
- add validator integration module
- add native JSON/envelope output contract tests
- preserve existing target detection regressions
- write integration/report docs
- update docs indexes
- run focused validation
```

그 다음:

```text
Sandbox trace governance bundle
- audit rule promotion
- promote rules only if audit recommends
- update docs indexes/report
```

그 이후:

```text
Static provider/sandbox validation surface completion audit
- decide whether static evidence layer is complete
- decide whether execution readiness design may begin
- keep execution implementation blocked
```

## 결론

현재 저장소는 read-only sync/runtime validation 계층이 넓게 구현되어 있으며, sandbox trace만 helper-only 상태로 남아 있다. 다음 가장 안전한 작업은 `aios validate <sandbox-trace.json>` static integration과 output contract tests를 하나의 bundle로 구현하는 것이다.

실행 계층으로 넘어가면 안 된다. Sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply/mutation은 readiness audit과 명시적 gate 전까지 계속 차단해야 한다.
