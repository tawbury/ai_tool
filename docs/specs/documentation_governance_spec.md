# 문서 거버넌스 명세

## 1. 목적

이 명세는 `.ai OS`의 문서가 빠르게 증가하는 상황에서 runtime, loader, validator가 어떤 문서를 신뢰하고 어떤 문서를 참고 또는 무시해야 하는지 정의한다.

핵심 원칙:

- `.ai/`는 runtime source of truth다.
- `docs/specs/`는 인간이 승인한 상세 명세다.
- `docs/adr/`은 결정 이력이다.
- `docs/reports/`의 audit/report는 관찰 기록이며 canonical runtime contract가 아니다.
- `docs/plan/`의 plan은 실행 계획이며 완료 후에도 runtime contract가 아니다.

이 명세는 문서 거버넌스만 다루며 runtime 구현, loader 구현, sync, manifest, orchestration을 포함하지 않는다.

## 2. 문서 Taxonomy

| 유형 | 목적 | 권위 수준 | Runtime 소비 |
|---|---|---|---|
| `spec` | 승인된 명세, 규칙, 스키마, 아키텍처 계약 | 높음 | 제한적 가능 |
| `adr` | 중요한 설계 결정과 근거 기록 | 중간 | 직접 소비 금지, 사람이 해석 |
| `plan` | 앞으로 할 작업 순서와 단계 | 낮음 | 직접 소비 금지 |
| `audit` | 현재 상태 관찰, 문제 진단, 권고 | 낮음 | 직접 소비 금지 |
| `historical` | 이전 결정/상태/마이그레이션 흔적 | 낮음 | 직접 소비 금지 |
| `reference` | 사람이 찾아보는 설명, 목록, 예시 | 중간 이하 | explicit-load만 가능 |

## 3. 권위 계층

권위 우선순위:

1. 최신 명시적 사용자 요청
2. 활성 AI CLI runtime system/developer instruction
3. `.ai/rules/rules.md`
4. 작업 관련 `.ai/rules/domains/*.rules.md`
5. 작업 관련 `.ai/rules/operations/*.rules.md`
6. `.ai/commands/*.command.md`
7. `.ai/agents`, `.ai/skills`, `.ai/workflows`, `.ai/validators`의 annotated executable contract
8. `docs/specs/*.md`
9. `docs/adr/*.md`
10. `docs/plan/*.md`
11. `docs/reports/*.md`
12. historical/reference 문서

runtime 관점에서 `docs/plan`과 `docs/reports`는 권위 문서가 아니다. 계획과 감사가 유효한 통찰을 담고 있어도, 실행 규칙으로 승격되려면 `.ai/` 또는 `docs/specs/`에 반영되어야 한다.

## 4. Canonical Runtime Spec 규칙

canonical runtime contract는 다음 위치에만 둔다.

- `.ai/rules/rules.md`
- `.ai/rules/domains/*.rules.md`
- `.ai/rules/operations/*.rules.md`
- `.ai/commands/*.command.md`
- `.ai/agents/*.agent.md`
- `.ai/skills/**/*.skill.md`의 `Executable Contract`, `Structural Rules`, `Runtime Policy`
- `.ai/workflows/**/*.workflow.md`의 `Executable Contract`, `Runtime Policy`
- `.ai/validators/**/*.md`의 `Executable Contract`, `Structural Rules`
- `docs/specs/*.md` 중 `runtime_consumption: allowed`로 표시된 명세

다음 문서는 runtime contract가 아니다.

- `docs/reports/*.md`
- `docs/plan/*.md`
- `docs/adr/*.md`
- `README.md`류 navigation 문서
- 예시 코드 또는 historical note

## 5. Governance Spec 규칙

governance spec은 문서 운영, 승인, 권위, 로딩 경계, lifecycle을 정의한다.

위치:

- `docs/specs/*_governance_spec.md`
- 필요 시 `.ai/rules/operations/*.rules.md`에 짧은 runtime-facing rule로 반영

규칙:

- governance spec은 자세한 설명을 담을 수 있다.
- runtime이 항상 로딩하지 않는다.
- runtime이 사용할 핵심 규칙은 `.ai/rules/rules.md` 또는 operation rule에 짧게 반영해야 한다.
- governance spec은 audit나 plan보다 권위가 높다.

## 6. Audit 사용 규칙

audit는 관찰 문서다.

허용:

- 현재 상태 기록
- stale reference, mixed-rule, context bloat, runtime terminology 등 문제 진단
- 권고안 제시
- 다음 plan 또는 spec의 근거로 사용

금지:

- runtime이 audit 내용을 실행 규칙으로 직접 소비
- audit의 권고를 canonical contract처럼 해석
- audit 결과를 adapter 또는 loader policy로 자동 적용

audit에서 발견한 규칙 후보는 별도 plan 또는 spec으로 승격한 뒤 `.ai` contract에 반영한다.

## 7. Plan Lifecycle 규칙

plan은 작업 전개를 위한 임시 실행 계획이다.

상태:

| 상태 | 의미 |
|---|---|
| `draft` | 작성 중 |
| `active` | 현재 실행 후보 |
| `implemented` | 계획이 구현됨 |
| `superseded` | 새 plan/spec/ADR로 대체됨 |
| `abandoned` | 더 이상 추진하지 않음 |

규칙:

- plan은 runtime contract가 아니다.
- 구현 완료 후 구현 보고서나 ADR 또는 spec으로 결과를 승격한다.
- superseded plan은 삭제하지 않고 metadata로 대체 문서를 표시한다.
- 오래된 plan을 자동 로딩하지 않는다.

## 8. Naming Convention

### Specs

형식:

```text
docs/specs/<topic>_spec.md
docs/specs/<topic>_governance_spec.md
docs/specs/<topic>_runtime_spec.md
```

예:

```text
docs/specs/documentation_governance_spec.md
docs/specs/semantic_loader_runtime_spec.md
```

### ADR

형식:

```text
docs/adr/0001-short-title.md
docs/adr/0002-short-title.md
```

### Plans

형식:

```text
docs/plan/<topic>_plan.md
docs/plan/<topic>_migration_plan.md
docs/plan/<topic>_implementation_plan.md
```

### Reports / Audits

형식:

```text
docs/reports/<topic>_audit.md
docs/reports/<topic>_implementation_report.md
docs/reports/<topic>_cleanup_report.md
```

## 9. Directory Convention

| 디렉터리 | 용도 | Runtime 소비 |
|---|---|---|
| `docs/specs/` | 승인된 상세 명세 | 제한적 가능 |
| `docs/adr/` | 결정 기록 | 직접 소비 금지 |
| `docs/plan/` | 실행 계획 | 직접 소비 금지 |
| `docs/reports/` | 감사/구현/정리 보고 | 직접 소비 금지 |
| `docs/roadmap/` | 장기 roadmap | 사람/전략 작업 전용 |
| `docs/cc/` | Claude Code 관련 참고 문서 | runtime adapter가 직접 소비 금지 |

## 10. Metadata / Frontmatter 권장안

새 문서는 가능한 frontmatter를 포함한다.

```yaml
---
doc_type: spec
status: active
authority: normative
runtime_consumption: restricted
created: 2026-05-20
updated: 2026-05-20
supersedes: []
superseded_by: null
related:
  - docs/adr/0001-documentation-governance.md
---
```

필드:

| 필드 | 필수 | 설명 |
|---|---|---|
| `doc_type` | 예 | `spec`, `adr`, `plan`, `audit`, `historical`, `reference` |
| `status` | 예 | `draft`, `active`, `implemented`, `superseded`, `abandoned`, `deprecated` |
| `authority` | 예 | `normative`, `decision-record`, `observational`, `planning`, `reference` |
| `runtime_consumption` | 예 | `allowed`, `restricted`, `forbidden` |
| `created` | 권장 | 생성일 |
| `updated` | 권장 | 수정일 |
| `supersedes` | 권장 | 대체하는 문서 |
| `superseded_by` | 권장 | 대체된 문서 |
| `related` | 선택 | 관련 문서 |

## 11. Status Marker

문서 본문 상단에는 사람이 빠르게 볼 수 있는 status marker를 둔다.

```markdown
> Status: Active
> Authority: Normative
> Runtime Consumption: Restricted
```

status 의미:

| 상태 | 의미 |
|---|---|
| `Draft` | 아직 승인되지 않음 |
| `Active` | 현재 유효 |
| `Implemented` | 구현 완료 |
| `Superseded` | 다른 문서가 대체 |
| `Deprecated` | 사용 중단 예정 |
| `Abandoned` | 폐기 |

## 12. ADR 구조

ADR은 다음 구조를 사용한다.

```markdown
# ADR-0001: Title

## Status

## Date

## Context

## Decision

## Consequences

## Alternatives Considered

## Supersedes / Superseded By

## Related Documents
```

ADR 규칙:

- 결정 하나만 기록한다.
- plan이나 audit 전체를 복사하지 않는다.
- runtime contract가 아니라 결정 이력이다.
- 결정이 runtime에 영향을 주면 `.ai` rules 또는 `docs/specs`에 별도 반영한다.

## 13. Deprecation / Superseded 정책

문서를 삭제하지 않고 metadata로 대체 관계를 표시한다.

```yaml
status: superseded
superseded_by: docs/specs/new_spec.md
```

본문 상단:

```markdown
> Status: Superseded
> Superseded By: docs/specs/new_spec.md
```

정책:

- superseded 문서는 runtime이 소비하지 않는다.
- historical value가 있으면 보존한다.
- 삭제는 중복/오류/민감정보가 명확할 때만 별도 결정으로 수행한다.
- 같은 주제의 active spec은 하나만 유지한다.

## 14. Runtime Consumption Boundary

runtime, loader, validator가 읽을 수 있는 것:

- `.ai/rules/rules.md`
- 작업 관련 `.ai/rules/domains/*.rules.md`
- 작업 관련 `.ai/rules/operations/*.rules.md`
- annotated `Executable Contract`
- annotated `Structural Rules`
- annotated `Runtime Policy`
- `docs/specs/*.md` 중 `runtime_consumption: allowed` 또는 `restricted`인 명확한 schema/contract 섹션

runtime, loader, validator가 자동 소비하면 안 되는 것:

- `docs/reports/*.md`
- `docs/plan/*.md`
- `docs/adr/*.md`
- historical 문서
- audit 권고
- 구현 보고서
- examples
- philosophy
- human-review-only criteria

## 15. 현재 문서 마이그레이션 전략

대규모 rewrite를 하지 않는다.

P0:

- `docs/specs/`와 `docs/adr/`를 도입한다.
- 새 spec/ADR부터 metadata를 사용한다.
- 기존 plan/report는 그대로 둔다.
- `.ai/rules/rules.md`에 짧은 문서 거버넌스 규칙을 제안 patch로 준비한다.

P1:

- active plan 중 구현 완료된 것은 `implemented` 상태를 표시한다.
- 주요 audit는 관련 spec 또는 ADR로 승격할 항목만 선별한다.
- superseded 관계가 명확한 문서만 metadata를 추가한다.

P2:

- 오래된 plan/report를 historical로 분류한다.
- runtime-facing spec은 `.ai` contract와 연결한다.
- 문서 index를 만들되 runtime source가 되지 않도록 한다.

## 16. `.ai/rules/rules.md` Suggested Patch Block

아래 블록은 제안이며 이번 작업에서 적용하지 않는다.

```markdown
## Documentation Governance

- Documents under `docs/specs/` are detailed human-readable specifications. They are authoritative only when their metadata marks them as active and normative.
- Documents under `docs/adr/` are decision records. They explain why a decision was made, but they are not runtime contracts.
- Documents under `docs/plan/` are planning artifacts. They must not be treated as canonical runtime behavior.
- Documents under `docs/reports/` are audits, implementation reports, or cleanup reports. They are observational and must not be consumed as runtime contracts.
- Runtime loaders and validators may consume `.ai/` source files and annotated executable contract sections. They must not automatically consume audits, plans, ADRs, examples, philosophy, or human-review-only criteria.
- When an audit or plan introduces a durable rule, promote the rule into the smallest relevant `.ai/rules/`, `.ai/commands/`, `.ai/skills/`, `.ai/workflows/`, `.ai/validators/`, or `docs/specs/` file instead of relying on the audit or plan.
```

## 17. 결론

문서 거버넌스의 핵심은 “관찰과 계획을 runtime contract로 오해하지 않게 하는 것”이다. audit와 plan은 계속 작성하되, 실행 가능한 규칙은 `.ai` 또는 active normative spec으로 승격해야 한다. runtime loader와 validator는 docs 전체를 읽지 않고, 허용된 source와 annotated contract만 읽어야 한다.
