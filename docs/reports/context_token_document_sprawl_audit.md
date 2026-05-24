# Context/token/document sprawl 감사

## 개요

이 문서는 `.ai OS` Phase 6-8 진행 과정에서 증가한 `docs/plan/` 및 `docs/reports/` 산출물이 AI context 혼동, token 사용량 증가, latency 증가, 운영 실패 위험을 만들고 있는지 감사한다.

이번 감사는 문서 평가만 수행한다. 런타임 코드, `.ai` 규칙, 파일 구조는 변경하지 않는다.

## 감사 범위

검토한 주요 기준:

- `.ai/rules/operations/documentation-governance.rules.md`
- `.ai/rules/operations/context-loading.rules.md`
- `.ai/rules/operations/activation.rules.md`
- `.ai/rules/operations/sync.rules.md`
- Phase 6-8의 sync, preview, replay 관련 계획서와 감사/구현 보고서
- semantic loader 및 budget governance 관련 문서

현재 `docs/plan/`에는 다수의 계획 문서가 있고, `docs/reports/`에는 구현 보고서, 위험 감사, 완료 감사, runtime rule promotion 보고서가 누적되어 있다. 특히 Phase 6-8에서는 sync safety, dry-run, marker, hash, rollback, generated preview, real preview provider, deterministic replay 관련 문서가 연속적으로 추가되었다.

## 문서 분류

| 분류 | 예시 | 현재 역할 | 런타임 권한 |
| --- | --- | --- | --- |
| runtime-facing contract | `.ai/rules/operations/sync.rules.md`, `.ai/rules/operations/context-loading.rules.md` | 현재 런타임 운영 규칙 | 있음 |
| active implementation plan | `docs/plan/real_preview_provider_contract.md`, `docs/plan/deterministic_replay_test_architecture.md` | 다음 설계/구현 준비 | 없음 |
| completed implementation report | `docs/reports/phase_7_bundle_3_sync_dry_run_report.md`, `docs/reports/dry_run_preview_integration_implementation_report.md` | 완료 작업 기록 | 없음 |
| risk audit | `docs/reports/real_preview_provider_risk_audit.md`, `docs/reports/deterministic_replay_risk_audit.md` | 위험 식별 및 완화 제안 | 없음 |
| historical/superseded | 초기 Phase 6 설계 세부 문서 중 runtime rules로 승격된 내용 | 이력 보존 | 없음 |
| reference-only | schema audit, output audit, readiness audit | 근거 확인용 | 없음 |

## 주요 위험

### Context bloat

문서 수가 늘어나면 AI agent가 불필요하게 많은 계획서와 보고서를 읽을 가능성이 커진다. 특히 Phase 6-8 문서는 주제가 연속되어 있어, 작은 태스크에서도 manifest, marker, preview, replay 관련 문서를 과도하게 로드할 수 있다.

위험 수준: 중간

현재 완화:

- `.ai/rules/rules.md`가 selective loading을 요구한다.
- documentation governance가 `docs/plan`과 `docs/reports`를 runtime contract가 아닌 human context로 분류한다.

남은 문제:

- human operator나 AI agent가 “관련 문서 전부”를 읽는 습관을 가지면 token bloat가 발생한다.
- phase-level 요약/색인이 없어 어떤 문서를 먼저 읽어야 하는지 판단 비용이 커진다.

### Token overuse

Phase 6-8 문서는 서로 세부 맥락이 연결되어 있어, 한 번에 다수 문서를 읽으면 token 사용량이 빠르게 증가한다. 기존 보고서 일부는 구현 로그와 검증 명령까지 포함해 길다.

위험 수준: 중간-높음

현재 완화:

- `aios load-context`는 `.ai` source 중심이며 budget awareness가 있다.
- semantic loader는 profile별 include/exclude와 hard budget filtering을 지원한다.

남은 문제:

- 일반 대화나 Codex 작업에서는 사용자가 명시한 docs를 직접 읽게 되므로 semantic loader budget이 항상 적용되는 것은 아니다.
- docs 전용 summary-first 정책이 아직 색인 문서로 고정되어 있지 않다.

### Stale plan mistaken as current rule

완료된 계획서가 runtime rules로 승격된 뒤에도 원본 계획서가 남아 있다. AI agent가 계획서를 현재 runtime contract로 오해하면 오래된 비목표나 미구현 범위를 잘못 판단할 수 있다.

위험 수준: 높음

현재 완화:

- documentation governance가 `.ai/`를 runtime source of truth로 지정한다.
- runtime rule promotion 보고서가 존재한다.

남은 문제:

- 개별 계획서에 `status: superseded` 같은 표식이 없다.
- 문서 상태 registry가 없어 어떤 문서가 현재 active인지 한눈에 보기 어렵다.

### Conflicting reports

초기 설계, 구현 보고서, runtime rule promotion 보고서가 서로 다른 시점의 상태를 기록한다. 같은 주제의 문서가 여럿일 때 최신 runtime behavior는 `.ai/rules`에 있지만, 보고서만 보면 충돌처럼 보일 수 있다.

위험 수준: 중간

현재 완화:

- `.ai/rules/operations/sync.rules.md`가 Phase 8 runtime behavior를 반영한다.

남은 문제:

- 보고서 간 supersession 관계가 명시되어 있지 않다.
- phase closure audit가 있지만 phase-level index는 없다.

### AI reading too many docs

태스크별로 최소 문서만 읽어야 하지만, “Phase 6-8 관련 문서”라는 요청은 문서 폭발을 유발한다.

위험 수준: 중간

현재 완화:

- `.ai/rules/rules.md`의 selective loading 정책.

남은 문제:

- docs index가 없어서 AI가 검색 결과 기반으로 과다 로딩할 수 있다.

### Slow task execution

많은 문서 읽기와 context reconstruction은 latency를 증가시키고 실제 작업 시간을 줄인다.

위험 수준: 중간

현재 완화:

- micro-step에서 bundle execution으로 전환한 이력이 있다.

남은 문제:

- 문서 축약본이 없어 동일 맥락을 반복 재구성한다.

### Wrong document selected by semantic loader

Semantic loader는 주로 `.ai` source 파일을 대상으로 설계되어 있으나, future docs-aware loading이 도입될 경우 오래된 plan/report가 선택될 위험이 있다.

위험 수준: 낮음-중간

현재 완화:

- runtime loaders and validators must not automatically consume plans/reports.
- activation v1은 context selection hint일 뿐 자동 docs loading이 아니다.

남은 문제:

- future docs-aware selection이 들어오기 전 document status metadata가 필요하다.

## 현재 보호장치 평가

| 보호장치 | 충분성 | 평가 |
| --- | --- | --- |
| `docs/plan`은 runtime contract가 아님 | 충분 | governance에 명확히 정의되어 있음 |
| `docs/reports`는 runtime contract가 아님 | 충분 | audits/reports는 human context only로 정의됨 |
| `.ai/rules`가 promoted runtime contract | 충분 | Phase 8 sync behavior가 sync rules에 승격됨 |
| activation selective loading | 부분 충분 | activation은 자동 context loading이 아니며 runtime intent만 표현 |
| load-context budget | 충분 | `.ai` source loading에는 효과적 |
| semantic layer filtering | 충분 | runtime `.ai` context를 계층별로 제한 가능 |
| docs phase-level summary | 부족 | 아직 없음 |
| document status registry | 부족 | active/superseded/reference 상태가 중앙화되지 않음 |
| docs index | 부족 | plan/report 탐색 비용이 높음 |

## 종합 판단

현재 문서 증가가 즉시 runtime failure를 만들 가능성은 낮다. 이유는 `.ai/`와 `docs/`의 authority boundary가 이미 분리되어 있고, semantic loader와 activation이 모든 문서를 자동으로 로드하지 않기 때문이다.

다만 context/token/latency 위험은 실제로 증가했다. 특히 future real preview provider 구현 전에는 Phase 6-8 문서가 너무 많아 AI agent가 오래된 설계와 최신 runtime rules를 혼동할 가능성이 있다.

따라서 현재 보호장치는 runtime safety에는 충분하지만, AI 작업 효율과 문맥 정확성에는 추가 consolidation이 필요하다.

## 권장 조치

파일 이동이나 삭제는 지금 하지 않는다. 대신 Phase 8 provider contract/replay planning 직후, real provider 구현 전에 문서 통합 번들을 수행하는 것이 적절하다.

권장 산출물:

- `docs/index/current_runtime_context.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/document_status_registry.md`

우선순위:

1. `document_status_registry.md`
2. `phase_6_8_summary.md`
3. `current_runtime_context.md`

이 순서가 적절한 이유는 먼저 문서 상태를 분류해야 summary와 runtime map이 오래된 문서를 잘못 참조하지 않기 때문이다.

## 결론

문서 sprawl은 현재 runtime contract를 직접 오염시키지는 않는다. 그러나 AI context selection, token usage, latency, stale plan confusion 위험은 이미 중간 수준으로 증가했다. Real preview provider 구현에 들어가기 전에 docs index와 phase summary를 만들어 summary-first loading과 lazy-load 정책을 운영 가능하게 해야 한다.
