# ADR-0001: 문서 거버넌스 모델 도입

---
doc_type: adr
status: active
authority: decision-record
runtime_consumption: forbidden
created: 2026-05-20
updated: 2026-05-20
supersedes: []
superseded_by: null
related:
  - docs/specs/documentation_governance_spec.md
  - docs/plan/documentation_migration_plan.md
---

> Status: Active
> Authority: Decision Record
> Runtime Consumption: Forbidden

## Context

`.ai OS`는 prompt/skill 저장소에서 CLI-first AI workforce 운영체제로 진화하고 있다. 최근 repository에는 감사 보고서, 구현 계획, 아키텍처 설계, runtime 명세, governance 명세가 빠르게 증가했다.

문서가 늘어나면서 future runtime, loader, validator가 audit나 plan을 canonical runtime contract로 오해할 위험이 생겼다. 특히 `docs/reports/`는 관찰과 권고를 담고 있고, `docs/plan/`은 작업 순서를 담지만 둘 다 실행 규칙이 아니다.

## Decision

문서 유형을 `spec`, `adr`, `plan`, `audit`, `historical`, `reference`로 구분한다.

결정 사항:

- `docs/specs/`를 active normative specification 위치로 도입한다.
- `docs/adr/`을 설계 결정 기록 위치로 도입한다.
- `docs/plan/`은 계획 문서로 유지하되 runtime contract로 사용하지 않는다.
- `docs/reports/`는 감사/보고 문서로 유지하되 runtime contract로 사용하지 않는다.
- runtime-facing canonical contract는 `.ai/`와 annotated executable contract에 둔다.
- audit나 plan의 durable rule은 `.ai` 또는 `docs/specs`로 승격해야 효력을 가진다.

## Consequences

장점:

- runtime과 loader가 소비할 수 있는 문서 경계가 명확해진다.
- audit/plan 증가가 runtime behavior를 오염시키지 않는다.
- 문서가 많아져도 권위 계층을 따라 해석할 수 있다.
- 향후 semantic loader와 validate runtime이 더 안전하게 동작할 수 있다.

비용:

- 새 문서 작성 시 metadata와 status를 관리해야 한다.
- 기존 plan/report 중 일부는 나중에 superseded 또는 implemented 상태를 표시해야 한다.
- durable rule을 audit에만 남기지 않고 별도 승격하는 작업이 필요하다.

## Alternatives Considered

### 모든 docs를 runtime이 검색 가능하게 두기

기각했다. audit, plan, report가 runtime contract로 오해될 위험이 크다.

### `.ai`만 유지하고 docs 명세를 만들지 않기

기각했다. `.ai`는 runtime source로 작고 실행 중심이어야 하며, 긴 설계 설명과 의사결정 이력은 docs에 남기는 편이 낫다.

### 모든 문서를 즉시 재분류하고 이동하기

기각했다. 현재 작업은 planning/specification 단계이며 massive rewrite는 위험하다.

## Supersedes / Superseded By

- Supersedes: 없음
- Superseded By: 없음

## Related Documents

- `docs/specs/documentation_governance_spec.md`
- `docs/plan/documentation_migration_plan.md`
- `docs/reports/governance_normalization_audit.md`
- `docs/reports/semantic_loading_audit.md`
- `docs/plan/semantic_loader_architecture.md`

## Runtime Boundary

이 ADR은 runtime이 직접 소비하지 않는다. runtime에 필요한 규칙은 `.ai/rules/rules.md`에 짧게 반영하거나, active normative spec의 명확한 contract 섹션으로 승격해야 한다.
