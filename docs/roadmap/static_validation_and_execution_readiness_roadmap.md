# 정적 검증 및 실행 준비 로드맵

> 이 문서는 summary-first human context이다. 런타임 계약은 아니며, 현재 런타임 권한의 기준은 `.ai/rules/`에 있다. 이 로드맵은 남은 정적 검증 작업과 실행 준비 게이트를 묶음 단위로 진행하기 위한 운영 기준이다.

## 목적

현재 `.ai OS`는 sync dry-run, replay, provider, sandbox 계층에 걸친 넓은 정적 검증 표면을 갖추었다. 동시에 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply/mutation은 의도적으로 차단되어 있다.

이 문서는 긴 micro prompt 흐름을 중단하고, 남은 작업을 roadmap-driven bundle로 정리하기 위해 작성한다. 새 런타임 동작을 승인하거나 구현하지 않는다.

## A. Completed Surface

### Sync runtime

- `aios sync --dry-run --manifest <path>` read-only dry-run runtime이 구현되어 있다.
- sync manifest validation, managed marker parsing, hash comparison, drift-stop, orphan-warning, native JSON, envelope v2 output contract가 안정화되어 있다.
- fixture preview provider는 명시적으로 opt-in한 경우에만 dry-run preview comparison에 사용된다.
- sync apply, manifest write, transaction log, rollback, marker mutation은 계속 차단되어 있다.

### Replay validation/comparison

- `aios validate <replay-manifest.json>`는 replay manifest, provider snapshot, referenced input/output fixtures를 정적으로 검증한다.
- `aios validate <replay-manifest.json> --replay-compare fixture`는 opt-in fixture-backed comparison만 수행한다.
- default replay validation은 static-only이며 provider execution, adapter execution, generated content, snapshot update를 수행하지 않는다.
- native JSON과 envelope v2 output contract가 안정화되고 runtime governance rules에 승격되어 있다.

### Provider capability validation

- provider capability fixtures, parsed-dict validator helper, `aios validate <provider-capability.json>` static integration이 구현되어 있다.
- native JSON과 envelope v2는 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`를 보존한다.
- capability declaration은 provider registration, discovery, execution authorization이 아니다.

### Provider execution trace validation

- provider execution trace fixtures, parsed-dict validator helper, `aios validate <provider-trace.json>` static integration이 구현되어 있다.
- trace validation은 evidence shape만 검증하며 provider execution, sandbox launch, dynamic loading을 수행하지 않는다.
- native JSON과 envelope v2 output contract가 안정화되고 governance rules에 승격되어 있다.

### Sandbox policy validation

- sandbox policy fixtures, parsed-dict validator helper, `aios validate <sandbox-policy.json>` static integration이 구현되어 있다.
- policy validation은 sandbox launcher나 subprocess execution 없이 policy shape와 safety flags만 검증한다.
- non-execution metadata와 target detection regression이 안정화되어 governance rules에 승격되어 있다.

### Sandbox result validation

- sandbox execution result fixtures, parsed-dict validator helper, `aios validate <sandbox-result.json>` static integration이 구현되어 있다.
- result validation은 sandbox execution evidence shape만 검증하며 sandbox launcher, subprocess execution, provider execution, replay execution을 수행하지 않는다.
- native JSON과 envelope v2 output contract가 안정화되고 governance rules에 승격되어 있다.

### Sandbox trace fixture/helper layer

- `aios.sandbox_trace.v0` fixture bundle과 fixture contract tests가 구현되어 있다.
- `validate_sandbox_trace_data(data)` helper가 구현되어 parsed dict를 정적으로 검증한다.
- `aios validate <sandbox-trace.json>` integration은 아직 구현되지 않았다.
- sandbox trace는 sandbox result evidence와 provider execution trace metadata를 연결하기 위한 fixture/helper layer이며 execution authorization이 아니다.

## B. Remaining Static Validation Work

남은 정적 검증 작업은 sandbox trace 계층을 현재 검증 표면과 동일한 성숙도로 끌어올리는 것이다.

1. **Sandbox trace validate integration**
   - `aios validate <sandbox-trace.json>` target detection을 추가한다.
   - target kind는 `sandbox-trace`로 유지한다.
   - sandbox result 이후 우선순위로 detection한다.
   - unrelated JSON은 misclassification하지 않는다.
   - native JSON, envelope v2, non-execution metadata를 구현한다.

2. **Sandbox trace output stabilization**
   - native JSON pass/fail contract를 고정한다.
   - envelope v2 pass/fail contract를 고정한다.
   - shaped invalid/missing schema detection을 고정한다.
   - existing target detection regression을 고정한다.
   - helper issue code/message/field/details 보존을 검증한다.

3. **Sandbox trace rule promotion audit**
   - sandbox trace validation behavior가 governance promotion에 충분히 안정적인지 감사한다.
   - primary target은 likely `.ai/rules/operations/validation.rules.md`이다.
   - sync safety context pointer가 필요한지 별도로 판단한다.

4. **Sandbox trace rule promotion**
   - audit가 권장할 경우에만 `.ai/rules`를 갱신한다.
   - static-only boundary와 explicit prohibitions만 승격한다.
   - fixture inventory, helper internals, detection heuristic counts는 runtime rules에 넣지 않는다.

5. **Static validation surface completion audit**
   - sync/replay/provider/sandbox static validation surface가 동일한 governance 수준에 도달했는지 감사한다.
   - execution readiness audit로 넘어갈 수 있는지 판단한다.

## C. Blocked Execution Layer

다음 작업은 현재 차단되어 있으며, 이 로드맵이 승인하지 않는다.

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation
- rollback execution
- dynamic loading
- registry/discovery
- adapter execution
- manifest persistence
- transaction log persistence
- marker insertion, repair, delete
- source mutation
- target mutation

이 항목들은 static validation surface completion audit와 execution readiness audit 이후에도 별도의 architecture approval 없이는 시작할 수 없다.

## D. Sequential Gates

실행 관련 작업은 아래 순서를 건너뛸 수 없다.

1. Sandbox trace validate integration
2. Sandbox trace stabilization
3. Sandbox trace governance promotion
4. Static validation surface completion audit
5. Execution readiness audit
6. Execution architecture approval
7. ONLY THEN possible execution prototype planning

이 순서는 의도적으로 보수적이다. 정적 검증이 통과했다는 사실은 실행 권한을 뜻하지 않으며, governance promotion 역시 execution implementation approval이 아니다.

## E. Parallelizable Tracks

다음 묶음은 안전하게 bundle 단위로 진행할 수 있다.

- validate integration + output contract tests + docs report/index update
- fixture bundle + fixture contract tests + fixture bundle report
- audit + docs index update
- rule promotion + promotion report + docs index update
- output contract stabilization + stabilization report

다음 작업은 병렬 설계 트랙으로 분리할 수 있지만 execution implementation과 묶으면 안 된다.

- sandbox trace follow-up audit
- static validation surface completion audit 준비
- docs/report consolidation
- context/token governance refresh

다음 작업은 순차적이어야 한다.

- validate integration before output stabilization
- output stabilization before rule promotion audit
- rule promotion audit before rule promotion
- rule promotion before static validation surface completion audit
- static validation surface completion audit before execution readiness audit
- execution readiness audit before execution architecture approval
- execution architecture approval before execution prototype planning

## F. Context/Token Governance

앞으로는 summary-first loading을 기본으로 한다.

권장 loading order:

1. `.ai/rules/rules.md`
2. relevant `.ai/rules/operations/*.rules.md`
3. `docs/index/current_runtime_context.md`
4. `docs/roadmap/static_validation_and_execution_readiness_roadmap.md`
5. `docs/index/phase_6_8_summary.md`
6. `docs/index/document_status_registry.md` when document authority/status is needed
7. detailed plans/reports only when needed

운영 원칙:

- `.ai/rules/`는 canonical runtime authority이다.
- `docs/index/`는 summary-first human context이다.
- `docs/reports/`는 historical audit trail이다.
- `docs/plan/`은 future design boundary이다.
- completed reports, risk audits, fixture reports, old plans는 do-not-load-by-default이다.
- 상세 근거가 필요할 때만 개별 plan/report를 lazy-load한다.

추천 consolidation bundle:

- sandbox trace validation integration, output stabilization, governance promotion이 끝난 뒤 `docs/index/phase_6_8_summary.md`를 다시 압축한다.
- static validation surface completion audit 이후에는 long-tail implementation reports를 기본 loading 대상에서 더 명확히 제외하는 consolidation bundle을 별도 수행한다.
- roadmap 문서는 다음 큰 phase가 시작되기 전까지 active planning entry로 유지한다.

## G. Execution Readiness Conditions

다음 조건은 명시적으로 구분해야 한다.

- Static validation success != execution authorization
- Sandbox evidence != sandbox safety proof
- Provider evidence != provider approval
- Replay success != deterministic safety guarantee
- Capability declaration != provider registration
- Provider trace validation != provider execution approval
- Sandbox policy validation != sandbox launcher approval
- Sandbox result validation != subprocess execution proof
- Sandbox trace validation != provider output approval

Execution readiness audit는 다음을 별도로 확인해야 한다.

- execution boundary가 `.ai/rules`에 승격되어 있는지
- no-write verification이 runtime에서 검증 가능한지
- network prohibition이 실제로 강제 가능한지
- subprocess/container boundary가 portable하게 동작하는지
- output trace와 envelope metadata가 execution facts를 숨기지 않는지
- failure code가 sync apply나 mutation authorization으로 오해되지 않는지

## Why workflow changed from micro prompts to roadmap bundles

최근 작업은 작은 설계, fixture, helper, validate integration, output stabilization, rule promotion audit, rule promotion이 반복되는 방식으로 진행되었다. 이 방식은 각 단계의 안전성을 높였지만 문서 수, context load, token 사용, target detection 회귀 확인 비용을 키웠다.

이제 남은 작업은 패턴이 충분히 고정되어 있다. 따라서 개별 micro prompt보다 roadmap 기반 bundle 실행이 더 적합하다. bundle은 검증 명령과 문서 갱신을 함께 묶되, execution implementation은 readiness gate 전까지 계속 분리한다.

## Recommended Future Operating Model

앞으로의 운영 모델:

- roadmap-driven execution: 작업은 이 로드맵의 gate와 bundle 범위를 먼저 확인한 뒤 시작한다.
- bundle-based implementation: static validate integration, output contract tests, report/index update는 가능한 한 한 bundle로 처리한다.
- lazy-loading context strategy: `.ai/rules`, runtime context index, roadmap을 먼저 읽고 세부 plan/report는 필요한 경우에만 로드한다.
- readiness-gated execution design: sandbox/provider/replay execution은 static validation surface completion audit와 execution readiness audit 이후에만 설계 논의를 시작한다.

## Immediate Next Recommended Bundle

다음 안전한 bundle은 다음 범위이다.

- `aios validate <sandbox-trace.json>` static integration
- sandbox trace native JSON output contract tests
- sandbox trace envelope v2 output contract tests
- existing target detection regression tests
- sandbox trace validate integration report
- concise docs index update

이 bundle은 sandbox launcher, subprocess execution, provider execution, replay execution, generated content, snapshot update, sync apply/mutation을 포함하지 않는다.
