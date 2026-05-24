# Document consolidation and context control plan

## 개요

이 문서는 Phase 6-8 동안 증가한 계획서와 보고서를 정리하고, AI context/token 사용량을 제어하기 위한 후속 consolidation 전략을 정의한다.

이번 계획은 파일 이동, 삭제, 런타임 코드 변경, `.ai` 규칙 변경을 수행하지 않는다. 실제 통합은 별도 번들로 진행한다.

## 목표

목표는 다음과 같다.

- AI agent가 최신 runtime contract와 과거 계획서를 혼동하지 않게 한다.
- Phase 6-8 문서의 상태와 권한을 한눈에 파악하게 한다.
- summary-first loading을 가능하게 한다.
- report/audit는 필요할 때만 lazy-load하도록 한다.
- token overuse와 latency를 줄인다.
- future real preview provider 구현 전 context 혼동을 줄인다.

## 문서 상태 모델

문서는 다음 상태로 분류한다.

| 상태 | 의미 | 기본 로딩 정책 |
| --- | --- | --- |
| `runtime-facing contract` | `.ai/`에 있는 현재 운영 계약 | 태스크 관련 시 로드 |
| `active implementation plan` | 아직 구현 전이거나 다음 작업에 직접 필요한 계획 | 태스크 관련 시 로드 |
| `completed implementation report` | 완료 작업 기록 | lazy-load |
| `risk audit` | 위험 분석과 완화 제안 | lazy-load |
| `historical/superseded` | 승격되었거나 현재 상태보다 오래된 문서 | 기본 로드 금지 |
| `reference-only` | 배경, 근거, 세부 설명 | lazy-load |

## 권장 신규 색인 문서

### `docs/index/document_status_registry.md`

목적:

- `docs/plan`과 `docs/reports` 문서의 현재 상태를 중앙에서 분류한다.
- active, completed, superseded, reference-only를 명시한다.
- 문서별 canonical successor 또는 promoted runtime rule을 연결한다.

권장 필드:

- path
- title
- phase
- status
- authority
- superseded_by
- promoted_to
- load_policy
- notes

예시:

```markdown
| Path | Phase | Status | Promoted to | Load policy |
| --- | --- | --- | --- | --- |
| docs/plan/sync_manifest_safety_design.md | 6 | historical | .ai/rules/operations/sync.rules.md | lazy |
```

### `docs/index/phase_6_8_summary.md`

목적:

- Phase 6-8의 주요 결정과 현재 상태를 하나의 summary-first 문서로 제공한다.
- 상세 계획/보고서 대신 먼저 읽을 수 있는 compact context를 제공한다.

권장 섹션:

- Phase 6 safety design summary
- Phase 7 read-only sync runtime summary
- Phase 8 fixture preview runtime summary
- Real provider/replay planning status
- Mutation blocked status
- Current next recommended work

### `docs/index/current_runtime_context.md`

목적:

- 현재 runtime-facing source of truth map을 제공한다.
- `.ai/rules`, implemented commands, supported schemas, blocked capabilities를 요약한다.

권장 섹션:

- Runtime source of truth
- Supported commands
- Supported schemas
- Active runtime rules
- Deferred capabilities
- Do-not-load-by-default documents

## Consolidation timing

권장 시점:

1. Phase 8 provider contract/replay planning 완료 후
2. Real provider implementation 시작 전
3. Mutation/apply design 시작 전

이 시점이 적절한 이유:

- Phase 6-8의 read-only runtime과 preview planning이 충분히 쌓였다.
- Real provider 구현은 많은 선행 문서와 runtime rules를 참조하므로 stale context 위험이 크다.
- Mutation/apply 설계는 위험도가 높아 문서 권한 경계를 먼저 정리해야 한다.

## Token/context control strategy

### Always-load minimum

항상 또는 거의 항상 읽을 최소 문서:

- `.ai/rules/rules.md`
- 태스크에 직접 관련된 `.ai/rules/operations/*.rules.md`
- explicit user request에서 지정한 문서

### Task-load only

태스크 주제와 직접 관련될 때만 읽는 문서:

- active implementation plan
- relevant runtime rule
- relevant current summary index

### Report/audit lazy-load only

보고서와 감사 문서는 다음 경우에만 읽는다.

- 사용자가 명시적으로 요청한 경우
- active plan의 근거 확인이 필요한 경우
- regression이나 정책 충돌을 조사해야 하는 경우
- commit/report 작성에 출처가 필요한 경우

### Summary-first loading

권장 로딩 순서:

1. `.ai/rules/rules.md`
2. relevant operation rule
3. `docs/index/current_runtime_context.md`
4. `docs/index/phase_6_8_summary.md`
5. 필요한 경우에만 detailed plan/report

### Budget warning policy

AI 작업에서 문서를 5개 이상 로드해야 하거나, Phase 전체 문서 묶음을 읽어야 하는 경우:

- 먼저 summary/index 문서를 찾는다.
- 없으면 필요한 문서 범위를 명시적으로 줄인다.
- task output에서 “읽은 문서 범위”를 간단히 기록한다.
- semantic loader를 사용할 때는 profile budget과 `--max-chars`를 우선 적용한다.

### Source citation/provenance requirements

문서 기반 결론은 다음을 남겨야 한다.

- 어떤 문서를 기준으로 판단했는지
- runtime contract인지 human context인지
- plan/report가 `.ai` rules로 승격되었는지
- 오래된 plan을 근거로 삼지 않았는지

## Do-not-load-by-default policy

다음 문서는 기본 로드 대상이 아니어야 한다.

- `docs/reports/*_implementation_report.md`
- `docs/reports/*_risk_audit.md`
- `docs/reports/*_completion_audit.md`
- `docs/plan/*_plan.md` 중 완료되거나 superseded된 문서
- historical migration reports
- old readiness audits

예외:

- 사용자가 명시한 경우
- 현재 작업의 정확한 근거가 필요한 경우
- 문서 상태 registry 작성 또는 갱신 중인 경우

## Future consolidation bundle

권장 번들명:

- Phase 6-8 documentation consolidation bundle

포함 작업:

1. `docs/index/` 디렉터리 생성
2. `docs/index/document_status_registry.md` 작성
3. `docs/index/phase_6_8_summary.md` 작성
4. `docs/index/current_runtime_context.md` 작성
5. 오래된 문서에 직접 상태 표식을 추가할지 별도 결정
6. 필요 시 `.ai/rules/operations/documentation-governance.rules.md`에 짧은 summary-first pointer promotion 검토

제외 작업:

- 파일 이동
- 파일 삭제
- runtime code 변경
- `.ai` rules 즉시 변경
- 자동 loader 동작 변경
- docs 자동 색인 생성 구현

## 권장 여부

세 index 문서는 생성하는 것이 맞다. 다만 현재 태스크에서는 만들지 않고 후속 consolidation bundle로 분리한다.

권장 순서:

1. `docs/index/document_status_registry.md`
2. `docs/index/phase_6_8_summary.md`
3. `docs/index/current_runtime_context.md`

후속 bundle에서 세 문서를 함께 만들되, 처음부터 모든 과거 문서를 완벽히 분류하려고 하지 않는다. Phase 6-8 read-only sync/preview/replay 문서부터 우선 분류하고, 나머지는 incremental하게 보강한다.

## Promotion 검토

이번 계획만으로 `.ai` 규칙을 수정하지 않는다.

후속 consolidation bundle 이후 다음 조건이 충족되면 documentation governance rule에 짧은 pointer를 승격할 수 있다.

- `docs/index/`가 생성됨
- document status registry가 최소 Phase 6-8 문서를 포함함
- summary-first loading 정책이 실제 작업에서 검증됨
- runtime loaders가 docs index를 자동 runtime contract로 오해하지 않도록 문구가 명확함

## 결론

문서 통합은 지금 즉시 파일 재배치를 하는 문제가 아니라, real provider 구현 전에 AI context 선택 비용을 줄이는 안전장치다. `docs/index` 기반의 document status registry, phase summary, runtime context map을 후속 번들로 만들고, detailed plan/report는 lazy-load로 유지하는 전략이 가장 안전하다.
