# Sandbox Result Validate Output Contract Risk Audit

## 목적

이 감사는 future `aios validate <sandbox-result.json>` 출력 계약이 sandbox execution authorization으로 오해될 위험을 점검한다. 현재 작업은 design-only이며 runtime code, `.ai/rules`, validate integration을 변경하지 않는다.

## 현재 상태

완료된 기반:

- sandbox execution result fixture contract
- sandbox execution result fixture-only bundle
- `validate_sandbox_execution_result_data(data)` helper
- helper unit tests

아직 없는 것:

- `aios validate <sandbox-result.json>`
- envelope v2 integration
- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation

## 주요 위험

| 위험 | 설명 | 완화 |
| --- | --- | --- |
| execution authorization confusion | valid sandbox result가 sandbox execution 승인으로 오해될 수 있음 | output details와 envelope meta에 execution false 값을 반복 |
| result evidence overclaim | no-write evidence가 host 전체 무결성을 증명한다고 오해될 수 있음 | result validation은 parsed JSON evidence shape만 검증한다고 명시 |
| target misclassification | unrelated JSON이 sandbox-result로 감지될 수 있음 | detection priority와 shaped heuristic을 보수적으로 적용 |
| envelope metadata confusion | envelope v2 meta가 runtime execution evidence로 오해될 수 있음 | meta는 validation result metadata이며 execution authorization이 아님을 명시 |
| sync apply confusion | sandbox result pass가 mutation readiness로 오해될 수 있음 | sync apply/mutation authorization 금지 명시 |

## Target Detection Risk

Sandbox result는 provider execution trace, sandbox policy와 필드가 일부 겹친다. 따라서 detection priority는 기존 runtime JSON targets 뒤에 두어야 한다.

권장 priority:

1. activation
2. sync manifest
3. replay manifest
4. provider capability
5. provider execution trace
6. sandbox policy
7. sandbox result

Sandbox-result-shaped heuristic은 `request_id`, `status`, `no_write_evidence`, `sandbox_mode`, `failure_code`, `trace_id` 같은 결과 evidence 필드 조합을 요구해야 한다. 단순히 `sandbox_mode`만 있는 JSON은 sandbox policy와 혼동될 수 있으므로 충분하지 않다.

## Output Contract Risk

Native JSON과 envelope v2는 helper issue code를 보존해야 한다. Issue code를 변환하거나 합치면 fixture/helper test와 validate output contract 사이의 원인 추적성이 약해진다.

필수 metadata:

- `sandbox_execution: false`
- `subprocess_execution: false`
- `provider_execution: false`
- `replay_execution: false`
- `mutation_performed: false`

이 metadata는 validation command가 아무 실행도 하지 않았음을 나타내며, sandbox result fixture 내부 evidence를 승인하지 않는다.

## Static-only Boundary

Future integration은 parsed JSON validation만 수행해야 한다.

금지 사항:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- dynamic loading
- provider registry/discovery
- adapter execution
- generated content
- snapshot update
- file writes
- sync apply/mutation authorization

## Compatibility Risk

기존 target detection이 흔들리면 validate output contract가 광범위하게 변경될 수 있다. 따라서 future implementation tests는 sandbox policy, provider execution trace, provider capability, replay manifest, sync manifest detection regression을 함께 고정해야 한다.

## 병렬화 평가

병렬 가능:

- sandbox trace fixture contract design
- sandbox trace fixture risk audit

순차 필요:

1. sandbox result validate output contract
2. validate integration
3. output contract stabilization
4. rule promotion audit

계속 차단:

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation

## 결론

Sandbox result validate output contract는 future static validate integration을 진행할 수 있을 만큼 충분히 정의되었다. 다음 단계는 runtime execution 없이 `aios validate <sandbox-result.json>` 정적 통합을 구현하는 것이며, sandbox execution은 계속 별도 readiness gate가 필요하다.
