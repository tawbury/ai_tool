# Provider Capability Validate Output Contract Risk Audit

> 이 문서는 human context용 위험 감사 보고서다. 런타임 계약은 `.ai/rules/`가 정본이며, 이 문서는 future `aios validate <provider-capability.json>` 출력 계약의 혼동과 안정성 위험을 검토한다.

## 목적

Provider capability validation helper가 존재하므로 다음 자연스러운 단계는 `aios validate <provider-capability.json>` 정적 통합이다. 하지만 출력 계약을 잘못 설계하면 capability validation이 provider 실행 승인처럼 보이거나, unrelated JSON을 잘못 분류하거나, envelope v2에서 실행 경계가 흐려질 수 있다.

## 주요 위험

### Static validation이 execution authorization으로 보이는 위험

`provider_capability_checked`라는 성공 결과는 사용자가 "provider를 실행해도 안전하다"고 오해할 수 있다. Capability declaration은 provider의 주장이고, sandbox/no-mutation/deterministic replay가 실행 전 별도 필요하다.

완화:

- success message에 "without provider execution"을 포함한다.
- details와 meta에 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`를 항상 포함한다.
- runtime rule promotion 전까지 이 behavior는 docs plan 수준에 머문다.

### Target detection 오분류 위험

Provider capability-shaped JSON을 schema error validation 대상으로 잡는 것은 유용하지만, threshold가 낮으면 unrelated JSON을 provider capability로 오분류할 수 있다.

완화:

- `schema_version: aios.provider_capability.v0`는 명확히 감지한다.
- missing/invalid schema detection은 충분한 required-field shape가 있을 때만 수행한다.
- 단일 `provider_id`, `provider`, `network_policy` 같은 일반 키만으로는 감지하지 않는다.
- sync manifest와 replay manifest target detection이 우선되어야 한다.

### Existing validate JSON shape churn 위험

Validate는 이미 activation, sync manifest, replay manifest 등을 지원한다. Provider capability 결과를 추가하면서 기존 repository-wide `validate --json --summary-only` shape가 변하면 output contract가 흔들릴 수 있다.

완화:

- Explicit target validation부터 통합한다.
- Repository-wide discovery는 별도 설계 전까지 확장하지 않는다.
- 기존 summary-only behavior를 변경하지 않는다.

### Envelope v2 meta 누락 위험

Envelope v2가 native result를 감싸면서 static-only boundary가 사라지면 provider execution 여부가 불명확해진다.

완화:

- envelope meta에 `provider_execution: false`, `sandbox_execution: false`, `mutation_performed: false`를 포함한다.
- payload results와 messages에 issue details를 보존한다.

### Error detail 과다 노출 위험

Provider capability는 현재 secret을 포함하지 않지만 future `output_affecting_config`가 환경 이름이나 내부 설정을 담을 수 있다.

완화:

- v0 details에는 identity, modes, flags, network policy만 넣는다.
- `output_affecting_config` 전체를 success details에 기본 포함하지 않는다.
- future secret-like fields는 redaction policy를 추가한 뒤 출력한다.

## Risk Matrix

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Capability validation을 실행 승인으로 오해 | 높음 | 중간 | static-only message/meta 필수 |
| Unrelated JSON 오분류 | 중간 | 중간 | shape threshold와 existing target 우선순위 |
| Existing validate output churn | 중간 | 낮음-중간 | explicit target만 먼저 지원 |
| Envelope v2 boundary 누락 | 중간 | 중간 | meta flags 필수 |
| Provider config 과다 노출 | 낮음-중간 | 낮음 | details 최소화 |

## Output Contract Readiness

이 출력 계약은 다음 구현에 충분하다.

- provider capability explicit target validation
- native JSON pass/fail output
- envelope v2 pass/fail output
- output contract tests
- unrelated JSON misclassification tests

아직 충분하지 않은 범위:

- provider execution
- sandbox approval
- provider discovery/registry
- deterministic replay execution
- external model/API provider
- sync apply readiness

## 권장 구현 순서

1. Provider capability validate target detection 구현
2. Static validator result를 validate result primitive로 매핑
3. Native JSON output contract tests 작성
4. Envelope v2 output contract tests 작성
5. Unrelated JSON misclassification tests 작성

## 결론

Provider capability validate output contract는 static validation을 공식 CLI 경로로 노출하기 위한 충분한 준비 단계다. 단, 출력은 반드시 provider execution과 sandbox execution이 수행되지 않았음을 명시해야 하며, validation pass는 execution authorization이 아니라 declaration schema check로만 해석되어야 한다.

Provider execution, sandbox execution, adapter execution, generated content, snapshot update, sync apply/mutation은 계속 차단한다.
