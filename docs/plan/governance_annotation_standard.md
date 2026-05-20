# .ai OS 거버넌스 주석 표준

## 1. 목적

이 문서는 `.ai OS` 문서에 섞여 있는 실행 계약, 구조 규칙, runtime policy, guidance, philosophy, human-review-only 기준을 물리적으로 분리하기 전에 사용할 경량 주석 및 섹션 경계 표준을 정의한다.

목표는 대규모 디렉터리 이동 없이 다음을 가능하게 하는 것이다.

- `aios validate`가 실행 가능한 contract만 안정적으로 식별
- runtime worker가 필요한 섹션만 선택 로딩
- 사람과 AI가 guidance와 philosophy를 실행 규칙으로 오해하지 않음
- 기존 문서를 작은 패치 단위로 점진 정리

이 표준은 계획 문서이며 sync, manifest, adapter generation, orchestration, worker execution 구현을 포함하지 않는다.

## 2. 표준 섹션명

기존 `.ai` 문서는 영어를 사용하므로 실제 적용 섹션명도 영어로 통일한다.

| 표준 섹션명 | 용도 | 기계 로딩 |
|---|---|---|
| `## Executable Contract` | 코드로 판정 가능한 필수 조건, 허용 값, 입력/출력, 결과 스키마 | 가능 |
| `## Structural Rules` | Markdown 구조, frontmatter, 파일명, 필수 블록, 링크 구조 | 가능 |
| `## Runtime Policy` | 공식 runtime, adapter, filesystem, encoding, symlink, loading policy | 가능 |
| `## Human Review Guidance` | 사람이 검토할 때 참고하는 판단 가이드 | 기본 제외 |
| `## Review Criteria` | 사람 또는 AI reviewer가 보는 품질 체크리스트 | 기본 제외, opt-in 가능 |
| `## Philosophy` | 원칙, 방향성, 설계 의도, 가치 판단 | 제외 |
| `## Examples` | 예시, 샘플 코드, 샘플 출력, 사용 예 | 제외, opt-in 가능 |

보조 섹션명:

| 섹션명 | 용도 |
|---|---|
| `## Scope` | 문서 적용 범위 |
| `## Non-Goals` | 실행하지 않는 범위 |
| `## Compatibility` | validate/runtime worker와의 호환성 설명 |
| `## Migration Notes` | 점진 이전 메모 |

## 3. 로딩 등급

각 섹션은 다음 로딩 등급 중 하나로 취급한다.

| 등급 | 의미 | 기본 소비자 |
|---|---|---|
| `machine-loadable` | 자동 검사 또는 runtime policy 판단에 사용할 수 있음 | `aios validate`, inspect 확장 |
| `runtime-loadable` | worker가 작업 수행 전에 읽을 수 있는 실행 지침 | 향후 runtime worker |
| `human-guidance` | 사람 또는 AI가 참고하되 fail 조건으로 쓰지 않음 | reviewer, agent |
| `example-only` | 예시이며 계약으로 해석 금지 | 사람, 문서 작성자 |
| `non-executable` | 철학, 배경, 판단 원칙 | 사람, 설계자 |

기본 매핑:

| 섹션 | 기본 등급 |
|---|---|
| `Executable Contract` | `machine-loadable` |
| `Structural Rules` | `machine-loadable` |
| `Runtime Policy` | `machine-loadable` 또는 `runtime-loadable` |
| `Human Review Guidance` | `human-guidance` |
| `Review Criteria` | `human-guidance` |
| `Philosophy` | `non-executable` |
| `Examples` | `example-only` |

## 4. Inline Annotation 표준

섹션 경계만으로 충분하지 않은 경우, 줄 단위 주석을 추가한다. 주석은 HTML comment를 사용한다. Markdown 렌더링에 보이지 않고, `aios validate`가 안정적으로 추출할 수 있기 때문이다.

### 권장 태그

```markdown
<!-- ai-governance:contract -->
<!-- ai-governance:structural-rule -->
<!-- ai-governance:runtime-policy -->
<!-- ai-governance:human-guidance -->
<!-- ai-governance:review-criteria -->
<!-- ai-governance:philosophy -->
<!-- ai-governance:example-only -->
<!-- ai-governance:non-executable -->
```

### 범위형 boundary

긴 블록에는 start/end boundary를 사용한다.

```markdown
<!-- ai-governance:start contract v1 -->
## Executable Contract

- Required field: `name`
- Required field: `version`

<!-- ai-governance:end -->
```

이름 규칙:

- annotation 이름은 kebab-case를 사용한다.
- 버전은 `v1`, `v2`처럼 짧게 쓴다.
- boundary가 없는 단일 주석은 바로 다음 목록, 표, 코드 블록, 문단에만 적용한다.
- `Examples` 안의 코드는 계약으로 해석하지 않는다.

## 5. Markdown Boundary Convention

가장 가벼운 표준은 “섹션명 + 선택적 HTML boundary”다.

권장 형태:

```markdown
<!-- ai-governance:start contract v1 -->
## Executable Contract

...
<!-- ai-governance:end -->

<!-- ai-governance:start human-guidance v1 -->
## Human Review Guidance

...
<!-- ai-governance:end -->
```

최소 형태:

```markdown
## Executable Contract

...

## Human Review Guidance

...
```

`aios validate`의 미래 동작은 다음 순서를 권장한다.

1. `ai-governance:start` boundary가 있으면 boundary를 우선 사용
2. boundary가 없으면 표준 섹션명을 기준으로 추출
3. 둘 다 없으면 기존 v0 방식으로 conservative하게 전체 문서를 guidance로 취급

## 6. Optional Metadata / Frontmatter Markers

문서 전체의 기본 의도를 frontmatter에 표시할 수 있다. 필수는 아니다.

```yaml
---
governance_profile: hybrid
machine_loadable_sections:
  - Executable Contract
  - Structural Rules
  - Runtime Policy
human_guidance_sections:
  - Human Review Guidance
  - Review Criteria
  - Philosophy
example_sections:
  - Examples
---
```

권장 `governance_profile` 값:

| 값 | 의미 |
|---|---|
| `contract-only` | 대부분 실행 계약 |
| `policy-only` | runtime 또는 운영 정책 |
| `guidance-only` | 자동 fail 조건 없음 |
| `hybrid` | 계약과 guidance가 함께 있음 |
| `example-only` | 예시/샘플 중심 |

v0 migration에서는 frontmatter 추가를 강제하지 않는다. 기존 문서에 frontmatter가 이미 있거나, 파일 성격이 매우 혼재된 경우에만 추가한다.

## 7. `aios validate` 호환성

`aios validate`는 이 표준을 다음처럼 사용할 수 있다.

| 섹션 | validate 처리 |
|---|---|
| `Executable Contract` | rule extraction 후보 |
| `Structural Rules` | 구조 validator 후보 |
| `Runtime Policy` | policy validator 후보 |
| `Human Review Guidance` | 자동 fail 제외, `skipped` 또는 `info` |
| `Review Criteria` | 자동 fail 제외, future `--include-review-guidance` opt-in |
| `Philosophy` | 제외 |
| `Examples` | 제외 |

v0/v1의 중요한 원칙:

- `Review Criteria`에 있는 `MUST`, `Required`, `PASS`, `FAIL`은 자동 fail 조건이 아니다.
- `Examples`의 코드 블록은 실행 코드나 validator contract가 아니다.
- `Executable Contract` 내부에서도 자연어 품질 표현은 warning 이하로 취급한다.
- fail은 파일 존재, 필드 존재, 값 형식, 링크 존재처럼 판정 가능한 조건에만 사용한다.

## 8. Runtime Worker Loading 호환성

향후 runtime worker는 전체 파일을 항상 로딩하지 않고 필요한 섹션만 읽어야 한다.

| worker 상황 | 로딩 권장 섹션 |
|---|---|
| 작업 실행 전 | `Runtime Policy`, 필요한 경우 `Executable Contract` |
| skill 실행 전 | skill의 `Executable Contract`, `Structural Rules`, 최소 `Runtime Policy` |
| 리뷰 수행 전 | `Review Criteria`, `Human Review Guidance` |
| 설계/판단 작업 | 필요한 경우 `Philosophy`, 단 always-load 금지 |
| 예시 기반 작성 | `Examples`, 단 명시적 요청 또는 생성 작업 시에만 |

항상 로딩 금지:

- `Philosophy`
- 장문 `Examples`
- L2 review guidance
- performance metric philosophy
- domain-specific review criteria

## 9. 최소 마이그레이션 전략

대규모 rewrite를 하지 않는다. 기존 문서에 작은 경계를 추가하는 방식으로 시작한다.

### 원칙

1. 파일 이동 금지
2. 파일명 변경 금지
3. 기존 본문 의미 변경 최소화
4. 표준 섹션명만 우선 추가
5. 애매한 품질 기준은 `Human Review Guidance`로 이동 또는 표시
6. 예시 코드는 `Examples`로 감싸 계약 오해 방지
7. `aios validate`가 읽을 수 있는 부분만 `Executable Contract`에 둠

### no-massive-rewrite 방식

기존 문서 전체를 재작성하지 않고 다음 중 하나만 적용한다.

- 상단에 `## Executable Contract`를 추가하고 기존 필수 규칙 일부를 이동
- 기존 `## Validation Rules` 바로 위에 `<!-- ai-governance:start contract v1 -->` 추가
- 기존 `## Quality Standards` 바로 위에 `<!-- ai-governance:start human-guidance v1 -->` 추가
- 기존 예시 코드 블록 앞에 `<!-- ai-governance:example-only -->` 추가
- 파일 전체가 guidance라면 상단에 `governance_profile: guidance-only`만 추가

## 10. 단계별 도입 전략

### P0

| 대상 | 작업 |
|---|---|
| `_base/document_base_validator.md` | `Executable Contract`, `Examples`, `Human Review Guidance` 경계 추가 |
| `_base/agent_skill_base_validator.md` | 필수 블록 계약과 L1/L2 guidance 분리 주석 |
| `workflow_base.md` | metadata-first/status rule을 contract로 표시, L1/L2 철학은 guidance로 표시 |
| `skill_loading_validator.md` | 실제 파일/참조 검사는 contract, 성능/캐시 기준은 future runtime guidance로 표시 |

### P1

| 대상 | 작업 |
|---|---|
| `l2_review_validator.md`, `senior_decision_validator.md`, `mentorship_validator.md`, `cross_agent_validator.md` | `guidance-only` 또는 `human-review-only` 표시 |
| 주요 shared skill | `Inputs (Contract)`, `Outputs (Contract)`, `Human Review Guidance` 패턴 적용 |
| workflow index | inventory와 policy 문장 경계 분리 |
| code quality workflow | workflow contract와 CI/IDE example 분리 |

### P2

| 대상 | 작업 |
|---|---|
| 전체 `.skill.md` | contract/guidance 섹션명 점진 통일 |
| 전체 `.workflow.md` | workflow stage contract와 quality guidance 분리 |
| validator 문서 전체 | contract coverage 확인 |
| 미래 구조 | `.ai/contracts/` 또는 `.ai/guidance/` 물리 분리 검토 |

## 11. Before / After 예시

### Validator 예시

Before:

```markdown
## Validation Rules

### Required Fields
- Project Name
- File Name
- Version

### Quality Standards
- Content completeness: 95%+
- Strategic depth must be sufficient

```python
def validate_meta_fields(document):
    ...
```
```

After:

````markdown
<!-- ai-governance:start contract v1 -->
## Executable Contract

### Required Fields
- `Project Name`
- `File Name`
- `Version`

### Allowed Status Values
- `Draft`
- `Active`
- `Completed`
- `Deprecated`
<!-- ai-governance:end -->

<!-- ai-governance:start human-guidance v1 -->
## Human Review Guidance

- Content completeness should be reviewed by a human reviewer.
- Strategic depth is not an automatic fail condition.
<!-- ai-governance:end -->

<!-- ai-governance:start example-only v1 -->
## Examples

```python
def validate_meta_fields(document):
    ...
```
<!-- ai-governance:end -->
````

### Workflow 예시

Before:

```markdown
## Workflow Stages

1. Planning
2. Design
3. Review

## Quality Gates

- Business impact must be high.
- Senior approval required.
```

After:

```markdown
<!-- ai-governance:start contract v1 -->
## Executable Contract

### Required Workflow Stages
1. Planning
2. Design
3. Review

### Required Metadata
- `Parent Document`
- `Related Reference`
<!-- ai-governance:end -->

<!-- ai-governance:start human-guidance v1 -->
## Review Criteria

- Business impact should be reviewed by the assigned reviewer.
- Senior approval is recorded in the reviewer field after review.
<!-- ai-governance:end -->
```

### Skill 예시

Before:

```markdown
## Input/Output

Input: requirements
Output: design document

## Quality Standards

- Strategic clarity score
- Stakeholder understanding
```

After:

```markdown
<!-- ai-governance:start contract v1 -->
## Executable Contract

### Inputs
- `requirements`: required

### Outputs
- `design_document`: required

### Required Blocks
- `Core Logic`
- `Input/Output`
- `Execution Logic`
<!-- ai-governance:end -->

<!-- ai-governance:start human-guidance v1 -->
## Human Review Guidance

- Strategic clarity is reviewed by the task reviewer.
- Stakeholder understanding is not machine-validated.
<!-- ai-governance:end -->
```

## 12. 파일 유형별 권장 템플릿

### Validator 문서

```markdown
# [Name] Validator

## Scope

## Executable Contract

## Structural Rules

## Runtime Policy

## Human Review Guidance

## Examples
```

### Workflow 문서

```markdown
# [Name] Workflow

## Scope

## Executable Contract

## Workflow Stages

## Runtime Policy

## Review Criteria

## Examples
```

### Skill 문서

```markdown
# [Name] Skill

## Scope

## Executable Contract

## Core Logic

## Input/Output

## Execution Logic

## Runtime Policy

## Human Review Guidance

## Examples
```

## 13. 채택 규칙

새 문서에는 표준 섹션명을 사용한다. 기존 문서는 다음 변경이 발생할 때만 annotation을 추가한다.

- validator 실행화 작업
- stale reference 정리
- workflow 구조 정리
- skill 통합 또는 rename
- runtime policy 변경
- 문서가 `aios validate` 대상이 되는 작업

한 번에 전체 저장소를 rewrite하지 않는다. P0 파일부터 작은 patch로 시작하고, `aios inspect`와 `aios validate`가 annotation을 읽을 준비가 된 뒤 범위를 넓힌다.

## 14. 결론

이 표준의 핵심은 물리적 분리 전에 의미 경계를 먼저 만드는 것이다. `Executable Contract`, `Structural Rules`, `Runtime Policy`는 future machine-loadable 영역으로 취급하고, `Human Review Guidance`, `Review Criteria`, `Philosophy`, `Examples`는 기본적으로 자동 fail 조건에서 제외한다. 이 방식이면 기존 `.ai` 문서의 맥락을 유지하면서도 CLI-first AI workforce 운영체제에 필요한 실행 계약 계층을 점진적으로 만들 수 있다.
