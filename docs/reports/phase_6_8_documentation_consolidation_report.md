# Phase 6-8 문서 통합 보고서

## 개요

Phase 6-8 동안 증가한 계획서와 보고서로 인한 context bloat, token overuse, stale plan confusion, wrong document selection 위험을 줄이기 위해 summary-first documentation indexes를 추가했다.

이번 작업은 문서 색인 추가에 한정했다. 런타임 코드, `.ai` 규칙, semantic loader behavior, activation behavior는 변경하지 않았다.

## 추가한 문서

새 디렉터리:

- `docs/index/`

새 색인:

- `docs/index/document_status_registry.md`
- `docs/index/phase_6_8_summary.md`
- `docs/index/current_runtime_context.md`

새 보고서:

- `docs/reports/phase_6_8_documentation_consolidation_report.md`

## `document_status_registry.md`

역할:

- 주요 Phase 6-8 문서의 상태를 분류한다.
- runtime-facing contract, active implementation plan, completed implementation report, risk audit, historical/superseded, reference-only를 구분한다.
- 각 문서의 authority와 load policy를 명시한다.
- promoted runtime rule 또는 superseded context를 연결한다.

포함 필드:

- path
- phase
- status
- authority
- load_policy
- promoted_to
- superseded_by
- notes

## `phase_6_8_summary.md`

역할:

- Phase 6 sync safety design을 요약한다.
- Phase 7 read-only sync runtime을 요약한다.
- Phase 8 fixture preview runtime을 요약한다.
- real preview provider contract와 deterministic replay planning 상태를 요약한다.
- 현재 지원 기능, 차단 기능, 다음 권장 방향을 제공한다.

## `current_runtime_context.md`

역할:

- 현재 runtime source of truth를 요약한다.
- `.ai/rules`와 active operation rules를 맵핑한다.
- supported commands와 supported schemas를 정리한다.
- read-only boundary와 deferred capabilities를 명시한다.
- do-not-load-by-default guidance와 summary-first loading guidance를 제공한다.

## 명시한 경계

세 index 문서 모두 runtime contract가 아님을 명시했다.

핵심 경계:

- `.ai/rules/`가 canonical runtime authority다.
- `docs/plan/`은 human planning artifact다.
- `docs/reports/`는 audit/evidence artifact다.
- Index 문서는 context navigation용이며 runtime loader가 자동 계약으로 소비해서는 안 된다.

## 변경하지 않은 항목

이번 작업은 다음을 수행하지 않았다.

- runtime code 변경
- `.ai` rule 변경
- semantic loader behavior 변경
- activation behavior 변경
- automatic docs loading 추가
- 파일 이동
- 파일 삭제
- 문서 archive 처리
- automatic indexing logic 구현

## 권장 로딩 순서

색인 문서에 다음 순서를 고정했다.

1. `.ai/rules/rules.md`
2. relevant operation rule
3. `docs/index/current_runtime_context.md`
4. `docs/index/phase_6_8_summary.md`
5. `docs/index/document_status_registry.md` when document authority/status is needed
6. detailed plans/reports only if needed

## 기대 효과

기대 효과:

- Phase 6-8 맥락 재구성 비용 감소
- 불필요한 detailed report loading 감소
- stale plan을 현재 rule로 오해할 위험 감소
- real preview provider/replay 후속 작업에서 초기 context 선택 비용 감소
- mutation/apply 차단 경계의 재확인 비용 감소

## 검증

요청된 검증:

- `git diff --check`
- `git diff --cached --check`

## 결론

Phase 6-8 문서 통합 번들은 파일 재배치 없이 summary-first navigation layer를 추가했다. 이후 real preview provider 또는 deterministic replay 후속 작업은 상세 계획/보고서를 먼저 읽기보다 `current_runtime_context.md`, `phase_6_8_summary.md`, `document_status_registry.md`를 우선 로드하는 방식으로 context와 token 사용량을 줄일 수 있다.
