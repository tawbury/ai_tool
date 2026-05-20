# 문서 거버넌스 마이그레이션 계획

---
doc_type: plan
status: active
authority: planning
runtime_consumption: forbidden
created: 2026-05-20
updated: 2026-05-20
supersedes: []
superseded_by: null
related:
  - docs/specs/documentation_governance_spec.md
  - docs/adr/0001-documentation-governance.md
---

> Status: Active
> Authority: Planning
> Runtime Consumption: Forbidden

## 1. 목적

이 계획은 현재 증가 중인 `.ai OS` 문서를 안정적인 taxonomy와 authority hierarchy로 정리하기 위한 최소 마이그레이션 절차를 정의한다.

이 계획은 runtime 구현, loader 구현, sync, manifest, orchestration을 포함하지 않는다.

## 2. 원칙

- massive rewrite를 하지 않는다.
- 기존 audit/report/plan을 이동하지 않는다.
- 새 문서부터 taxonomy와 metadata를 적용한다.
- runtime contract가 필요한 내용만 `.ai` 또는 `docs/specs`로 승격한다.
- `docs/reports`와 `docs/plan`은 runtime이 자동 소비하지 않는다.

## 3. 현재 상태

현재 `docs/`에는 다음 유형이 섞여 있다.

- 계획: `docs/plan/*.md`
- 감사/보고: `docs/reports/*.md`
- roadmap: `docs/roadmap/*.md`
- Claude Code 참고: `docs/cc/*.md`
- 새 명세 후보: semantic loader, governance annotation, validation runtime 관련 계획 문서

문제:

- plan과 audit의 권위 수준이 metadata로 표시되어 있지 않다.
- future runtime이 docs 전체를 검색하면 audit/plan을 contract로 오해할 수 있다.
- ADR 위치가 없어 결정 이력이 plan/report에 섞인다.

## 4. P0 작업

| 순서 | 작업 | 산출물 |
|---|---|---|
| 1 | `docs/specs/` 도입 | `documentation_governance_spec.md` |
| 2 | `docs/adr/` 도입 | `0001-documentation-governance.md` |
| 3 | 문서 taxonomy와 authority hierarchy 확정 | governance spec |
| 4 | `.ai/rules/rules.md` suggested patch block 작성 | spec 내 제안 블록 |
| 5 | 새 문서에 frontmatter 적용 | spec/ADR/plan |

## 5. P1 작업

| 작업 | 설명 |
|---|---|
| active plan 상태 표시 | 구현 완료된 plan은 `implemented` 또는 `superseded` 표시 |
| 주요 audit 승격 후보 선별 | durable rule 후보만 spec 또는 `.ai`로 승격 |
| runtime-facing spec 후보 분리 | semantic loader, validate runtime, governance annotation 중 active spec 후보 선정 |
| reports index 작성 검토 | 단, index는 runtime source가 아님을 명시 |
| ADR 추가 | 큰 방향 결정마다 ADR 작성 |

## 6. P2 작업

| 작업 | 설명 |
|---|---|
| historical 분류 | 오래된 계획과 보고서를 historical로 표시 |
| superseded 관계 정리 | 대체 문서가 명확한 경우 metadata 추가 |
| docs/specs 확장 | runtime spec, loader spec, validation spec 등 필요 시 추가 |
| `.ai` contract 반영 | spec 중 실행 규칙만 `.ai`에 짧게 반영 |
| 문서 validation 도입 검토 | frontmatter와 status marker 검사 |

## 7. 최소 Rewrite 정책

기존 문서에는 다음 경우에만 metadata를 추가한다.

- 새 문서가 기존 문서를 대체함
- runtime이 혼동할 위험이 큰 문서임
- active plan이 구현 완료됨
- ADR이 해당 문서를 decision record로 참조함

하지 않을 것:

- 모든 기존 문서 일괄 이동
- 모든 기존 문서 frontmatter 일괄 추가
- audit/report 본문 재작성
- plan을 spec처럼 편집

## 8. 승격 규칙

audit 또는 plan의 내용이 durable rule이 되려면 다음 중 하나로 승격한다.

| 승격 대상 | 조건 |
|---|---|
| `.ai/rules/*.md` | runtime agent가 따라야 하는 짧은 규칙 |
| `.ai/validators/*.md` | validate 가능한 contract |
| `.ai/workflows/*.workflow.md` | workflow stage 또는 runtime policy |
| `.ai/skills/**/*.skill.md` | skill input/output/execution contract |
| `docs/specs/*.md` | 긴 설명이 필요한 normative spec |
| `docs/adr/*.md` | 중요한 결정과 tradeoff |

## 9. Suggested `.ai/rules/rules.md` Patch

아래 블록은 적용 제안이다. 이 계획에서는 `.ai/rules/rules.md`를 수정하지 않는다.

```markdown
## Documentation Governance

- Treat `.ai/` as the canonical runtime source of truth.
- Treat `docs/specs/` as detailed specifications. Specs are authoritative only when active, normative, and explicitly relevant.
- Treat `docs/adr/` as decision records, not runtime contracts.
- Treat `docs/plan/` as planning artifacts, not runtime contracts.
- Treat `docs/reports/` as observational audit or implementation records, not runtime contracts.
- Runtime loaders and validators must not automatically consume audits, plans, ADRs, examples, philosophy, or human-review-only criteria.
- Promote durable rules discovered in audits or plans into the smallest relevant `.ai` source file or active spec.
```

## 10. 검증 계획

문서 거버넌스 작업 후 확인할 항목:

- 새 문서가 `docs/specs`, `docs/adr`, `docs/plan`에 올바르게 위치하는가
- 새 문서가 한국어로 작성되었는가
- UTF-8 BOM이 없는가
- `.ai` 파일을 의도치 않게 수정하지 않았는가
- suggested patch가 실제 적용과 분리되어 있는가
- runtime consumption boundary가 각 문서에 표시되어 있는가

## 11. 다음 작업 후보

1. `.ai/rules/rules.md`에 documentation governance short rules를 적용할지 결정한다.
2. `semantic_loader_architecture.md`를 future spec으로 승격할지 검토한다.
3. `governance_annotation_standard.md`를 future spec으로 승격할지 검토한다.
4. 기존 active plan 중 구현 완료된 문서를 `implemented`로 표시할지 검토한다.

## 12. 결론

문서 마이그레이션은 이동이나 rewrite가 아니라 권위 표시부터 시작해야 한다. 새 문서에는 taxonomy와 metadata를 적용하고, 기존 audit/plan은 runtime이 소비하지 않도록 명확히 제한한다. durable rule만 `.ai` 또는 active spec으로 승격하는 방식이 가장 안전하다.
