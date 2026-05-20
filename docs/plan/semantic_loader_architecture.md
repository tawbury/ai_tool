# .ai OS 시맨틱 로더 아키텍처 설계

## 1. 목적

이 문서는 `.ai OS`의 미래 시맨틱 로더를 설계한다. 목표는 orchestration runtime이나 worker execution을 구현하기 전에, 어떤 문서를 어떤 의미 계층으로 읽고 어떤 내용을 제외할지 결정하는 read-only context selection 구조를 정의하는 것이다.

명시적 제외 범위:

- tmux
- worker execution
- sync
- manifest
- adapter generation
- orchestration runtime implementation
- 파일 자동 수정

## 2. Semantic Loader 책임

시맨틱 로더는 작업을 실행하지 않는다. 로더의 책임은 “필요한 context를 작게, 설명 가능하게, 추적 가능하게 선택하는 것”이다.

핵심 책임:

1. 사용자 요청, agent, runtime, target path, command, workflow intent를 입력으로 받는다.
2. 로딩 프로필을 선택한다.
3. 후보 파일을 찾는다.
4. governance annotation 또는 표준 섹션명을 기준으로 semantic layer를 추출한다.
5. exclusion policy와 token budget을 적용한다.
6. 로딩된 context와 제외된 context의 provenance를 기록한다.
7. runtime worker, validator, reviewer가 사용할 수 있는 context bundle을 반환한다.

비책임:

- 실제 skill 실행
- workflow orchestration
- validator 판정 실행
- 파일 생성/수정
- adapter 생성
- sync/drift 처리

## 3. 전체 Flow

```text
User Request / CLI Args
        |
        v
Intent + Target Resolver
        |
        v
Loading Profile Selector
        |
        v
Candidate File Resolver
        |
        v
Semantic Layer Extractor
        |
        v
Exclusion Policy Filter
        |
        v
Token Budget Planner
        |
        v
Context Bundle Builder
        |
        v
Loading Trace + Provenance
```

## 4. Context Selection Lifecycle

1. **입력 수집**
   - runtime: `codex-cli`, `gemini-cli`, `claude-code-cli`
   - agent: `developer`, `pm`, `hr`, `finance`, `contents-creator`
   - task intent: `implementation`, `validation`, `review`, `strategy`, `workflow`, `documentation`
   - target paths
   - explicit skills/workflows/validators

2. **기본 context 고정**
   - `.ai/rules/rules.md`
   - 최신 사용자 요청
   - active runtime adapter의 얇은 지시

3. **프로필 선택**
   - minimal worker
   - reviewer
   - strategist
   - validation runtime
   - runtime execution

4. **후보 파일 결정**
   - domain rule
   - operation rule
   - selected skill
   - selected workflow
   - selected validator
   - reference documents

5. **semantic layer 선택**
   - include layer와 exclude layer를 적용
   - annotation boundary 우선
   - 표준 섹션명 fallback

6. **budget 처리**
   - 필수 context 우선
   - optional guidance 제한
   - examples와 philosophy는 기본 제외

7. **bundle 생성**
   - 로딩된 조각
   - 제외된 조각
   - provenance metadata
   - trace

## 5. Semantic Filtering Lifecycle

```text
Candidate Markdown
      |
      |-- frontmatter check
      |
      |-- annotation boundary scan
      |     - ai-governance:start contract v1
      |     - ai-governance:start human-guidance v1
      |
      |-- section heading fallback
      |     - ## Executable Contract
      |     - ## Structural Rules
      |     - ## Runtime Policy
      |     - ## Human Review Guidance
      |     - ## Review Criteria
      |     - ## Philosophy
      |     - ## Examples
      |
      |-- layer normalization
      |
      |-- exclusion filter
      |
      |-- budget filter
      |
      v
Selected Context Chunks
```

기본 include:

- `executable_contract`
- `structural_rules`
- `runtime_policy`
- selected skill의 `input_output`
- selected skill의 `execution_logic`
- target workflow의 stage contract

기본 exclude:

- `examples`
- `philosophy`
- `performance_metrics`
- broad `quality_standards`
- long `related_documents`
- `human_review_guidance`, 단 reviewer profile 제외

## 6. Layer Extraction Flow

추출 우선순위:

1. `<!-- ai-governance:start <layer> v1 -->` boundary
2. `<!-- ai-governance:<layer> -->` inline annotation
3. 표준 섹션명
4. 파일 유형별 legacy section mapping
5. fallback summary

legacy section mapping:

| 기존 섹션명 | normalized layer |
|---|---|
| `Validation Rules` | `executable_contract` 후보 |
| `Required Field List` | `structural_rules` |
| `Structure Verification` | `structural_rules` |
| `Input/Output` | `input_output` |
| `Execution Logic` | `execution_logic` |
| `Constraints` | `runtime_policy` 후보 |
| `Quality Standards` | `human_review_guidance` |
| `Performance Metrics` | `never_auto_load` |
| `Special Considerations` | `human_review_guidance` |
| `Examples`, `Usage Example` | `examples` |

주의:

- legacy mapping은 확정 계약이 아니라 conservative fallback이다.
- `Validation Rules` 안에 품질 판단 문장이 섞여 있으면 warning provenance를 남긴다.
- 코드 블록은 `Examples` 또는 `example-only`로 분류하는 것이 기본이다.

## 7. Token Budget Handling

로더는 token 수를 실제 tokenizer로 정확히 계산하지 않아도 v0에서는 문자 수와 줄 수 기반의 근사치를 사용할 수 있다.

budget 처리 원칙:

| 우선순위 | 내용 | 처리 |
|---|---|---|
| 1 | 사용자 요청, system/developer instruction | 항상 포함 |
| 2 | `.ai/rules/rules.md` | 항상 포함 |
| 3 | task-specific rules | budget 내 포함 |
| 4 | selected target contract | 포함 |
| 5 | selected skill/workflow execution slice | 포함 |
| 6 | validator contract | validate/review 시 포함 |
| 7 | review guidance | reviewer profile에서만 포함 |
| 8 | examples/philosophy | explicit request 또는 남는 budget이 있을 때만 |

budget 초과 시 동작:

1. examples 제외
2. philosophy 제외
3. performance metrics 제외
4. related documents를 링크 목록만 남김
5. review guidance를 요약으로 축소
6. skill/workflow 본문을 selected layer만 남김
7. 그래도 초과하면 `budget_exceeded` warning을 trace에 기록

## 8. Loader Input Schema

```yaml
loader_input:
  schema_version: aios.semantic_loader.input.v0
  runtime: codex-cli
  agent: developer
  task_intent: implementation
  mode: minimal-worker
  repo_root: D:/development/_templates/ai_tool

  targets:
    paths:
      - .ai/skills/developer/dev_backend_stack_unified.skill.md
    skills:
      - dev_backend_stack_unified
    workflows: []
    validators: []

  requested_layers:
    - executable_contract
    - runtime_policy
    - input_output
    - execution_logic

  excluded_layers:
    - examples
    - philosophy
    - performance_metrics

  budget:
    max_chars: 30000
    strategy: prefer-contracts

  options:
    include_trace: true
    include_excluded_report: true
    allow_legacy_fallback: true
```

## 9. Loading Profile Schema

```yaml
loading_profile:
  id: minimal-worker
  description: Minimal execution context for a task worker.

  always:
    paths:
      - .ai/rules/rules.md
    layers:
      - governance_core
      - runtime_policy

  include_layers:
    - executable_contract
    - structural_rules
    - runtime_policy
    - input_output
    - execution_logic
    - constraints

  exclude_layers:
    - human_review_guidance
    - review_criteria
    - philosophy
    - examples
    - performance_metrics

  task_rules:
    max_domain_rules: 1
    max_operation_rules: 1

  fallback:
    unannotated_document: section-heading
    unknown_section: exclude-with-trace
```

## 10. Semantic Layer Selector

selector는 profile, task intent, target kind를 조합해 include/exclude를 결정한다.

```yaml
semantic_layer_selector:
  target_kind: skill
  profile: runtime-execution
  include:
    - executable_contract
    - runtime_policy
    - input_output
    - execution_logic
    - constraints
  include_if_explicit:
    - examples
    - philosophy
  exclude:
    - review_criteria
    - human_review_guidance
    - performance_metrics
```

우선순위:

1. explicit user layer request
2. profile include/exclude
3. target kind defaults
4. annotation metadata
5. global exclusion policy

`never-auto-load`는 explicit user request 없이는 포함하지 않는다.

## 11. Exclusion Policy

```yaml
exclusion_policy:
  never_auto_load:
    - philosophy
    - examples
    - performance_metrics
    - long_related_documents
    - historical_notes

  exclude_by_default:
    - human_review_guidance
    - review_criteria
    - special_considerations
    - benefits
    - version_history

  allow_when:
    review_criteria:
      - profile: reviewer
      - task_intent: review
    philosophy:
      - explicit_user_request: true
      - profile: strategist
    examples:
      - explicit_user_request: true
      - task_intent: authoring
```

제외된 내용은 silent drop하지 않고 trace에 남긴다.

## 12. Runtime Context Definitions

### Minimal Runtime Context

용도: 일반 task worker가 실행 전 읽는 최소 context.

포함:

- `.ai/rules/rules.md`
- task domain rule 최대 1개
- operation rule 최대 1개
- selected skill의 contract/input/output/execution slice
- target path metadata

제외:

- 모든 examples
- philosophy
- review criteria
- workflow index
- full validator docs

### Reviewer Runtime Context

용도: L2 review, quality review, approval.

포함:

- `.ai/rules/rules.md`
- relevant domain rule
- `.ai/rules/operations/validation.rules.md`
- target artifact
- related validator contract
- `Review Criteria`
- `Human Review Guidance`

제외:

- unrelated skill details
- examples unless explicit
- strategy philosophy unless review asks

### Strategist Runtime Context

용도: roadmap, architecture, decision, long-term planning.

포함:

- `.ai/rules/rules.md`
- documentation/development/domain rules
- selected strategy skill contract
- selected strategy skill guidance summary
- workflow base의 operational loop summary
- decision/roadmap validator contract

제외:

- full skill index
- agent-specific skill matrices
- execution examples
- unrelated runtime policy

### Validation Runtime Context

용도: `aios validate` 또는 validator runtime.

포함:

- target file
- target kind metadata
- selected validator executable contract
- structural rules
- reference resolution data

제외:

- human review guidance
- philosophy
- examples
- quality metrics without executable criteria

### Runtime Execution Context

용도: 미래 worker activation 직전.

포함:

- global priority and SSoT policy
- activation profile
- selected skill contract
- selected workflow stage contract
- runtime policy
- constraints
- output contract

제외:

- reviewer-only criteria
- broad philosophy
- long examples
- unrelated references

## 13. Runtime Loading Trace Schema

```yaml
loading_trace:
  schema_version: aios.semantic_loader.trace.v0
  run_id: trace-20260520-001
  profile: minimal-worker
  runtime: codex-cli
  agent: developer
  task_intent: implementation
  status: pass

  loaded:
    - path: .ai/rules/rules.md
      reason: always-load core
      layers:
        - governance_core
        - runtime_policy
      chars: 7402
      source: section-fallback

    - path: .ai/skills/developer/dev_backend_stack_unified.skill.md
      reason: explicit skill target
      layers:
        - input_output
        - execution_logic
        - constraints
      chars: 2800
      source: legacy-section-mapping

  excluded:
    - path: .ai/skills/developer/dev_backend_stack_unified.skill.md
      layer: examples
      reason: excluded_by_profile

  warnings:
    - code: unannotated_document
      path: .ai/skills/developer/dev_backend_stack_unified.skill.md
      message: Used legacy section fallback because governance annotations were not found.
```

## 14. Context Provenance Metadata

각 context chunk는 출처와 선택 이유를 가져야 한다.

```yaml
context_chunk:
  id: chunk-001
  path: .ai/validators/structure_validator.md
  line_start: 6
  line_end: 54
  semantic_layer: structural_rules
  loading_tier: runtime-load
  selected_by:
    - profile: validation-runtime
    - target_kind: skill
  extraction_method: section-heading
  confidence: medium
  budget:
    chars: 1240
    truncated: false
  provenance:
    repo_root: D:/development/_templates/ai_tool
    source_of_truth: .ai
    modified_by_loader: false
```

confidence 값:

| 값 | 의미 |
|---|---|
| `high` | annotation boundary로 추출 |
| `medium` | 표준 섹션명으로 추출 |
| `low` | legacy section mapping으로 추출 |

## 15. Excluded Layer Reporting

제외 리포트는 context bloat와 오해를 줄이기 위한 핵심 산출물이다.

```yaml
excluded_layers:
  summary:
    files_considered: 8
    files_loaded: 3
    files_excluded: 5
    layers_excluded:
      examples: 4
      philosophy: 2
      performance_metrics: 3

  items:
    - path: .ai/workflows/workflow_index.md
      layer: full_document
      reason: lazy_load_only
      trigger_required: workflow_discovery

    - path: .ai/validators/l2_review_validator.md
      layer: review_criteria
      reason: reviewer_profile_not_active
      trigger_required: review_intent
```

## 16. Annotation이 없을 때 Fallback

fallback은 보수적으로 동작해야 한다.

1. 표준 섹션명을 찾는다.
2. 표준 섹션명이 없으면 legacy section mapping을 적용한다.
3. mapping confidence를 `low`로 기록한다.
4. 품질/철학/예시로 의심되는 섹션은 제외한다.
5. mixed document warning을 남긴다.
6. validate/runtime이 fail 조건으로 쓰려면 annotation 또는 명확한 contract section이 필요하다.

fallback 정책:

| 상황 | 처리 |
|---|---|
| annotation 없음, 표준 섹션 있음 | 표준 섹션으로 추출 |
| 표준 섹션 없음, legacy 섹션 있음 | low confidence로 추출 |
| 전체가 guidance처럼 보임 | `guidance-only`로 취급 |
| contract와 guidance가 섞임 | contract 후보만 추출, warning 기록 |
| examples 안에 MUST가 있음 | example-only로 제외 |

## 17. Mixed Document Handling

혼합 문서는 `.ai OS`의 현재 기본 상태다. 로더는 혼합을 오류로 처리하지 않고, 추적 가능한 warning으로 처리한다.

mixed signals:

- `Validation Rules` 안에 `Strategic depth`, `Leadership`, `Business impact` 포함
- `Examples` 안에 실행 코드처럼 보이는 Python 포함
- `Workflow Stages`와 `Quality Gates`가 같은 fail 기준처럼 작성됨
- `Performance Metrics`가 validator fail 조건처럼 작성됨

처리:

1. 실행 가능한 구조 조건만 선택
2. 사람 판단 문장은 human guidance로 분류
3. examples는 제외
4. mixed-document warning 기록
5. 향후 annotation migration 후보로 표시

## 18. Worker-Specific Loading Flow

### Minimal Worker

```text
intent=implementation
  -> profile=minimal-worker
  -> load rules.md
  -> load development rule if code task
  -> load selected skill contract + execution logic
  -> exclude review/philosophy/examples
```

### Reviewer

```text
intent=review
  -> profile=reviewer
  -> load rules.md
  -> load validation.rules.md
  -> load target artifact
  -> load validator contract
  -> load review criteria
  -> exclude unrelated skill details
```

### Strategist

```text
intent=strategy
  -> profile=strategist
  -> load rules.md
  -> load documentation/development/domain rules
  -> load selected strategic skill summary
  -> load workflow base summary
  -> lazy-load philosophy only when explicitly useful
```

### Validation Runtime

```text
intent=validation
  -> profile=validation-runtime
  -> load target file
  -> resolve target kind
  -> load validator executable contract
  -> load structural rules
  -> exclude human review guidance
```

## 19. Suggested Loader Module Boundaries

미래 구현 시 권장 모듈 경계:

```text
src/aios/semantic_loader/
  __init__.py
  input.py              # loader input dataclasses/schema helpers
  profiles.py           # built-in loading profiles
  resolver.py           # candidate file and target resolver
  annotations.py        # ai-governance boundary parser
  sections.py           # heading and legacy section extractor
  selector.py           # semantic layer selector
  policy.py             # exclusion and fallback policy
  budget.py             # budget planning and truncation
  bundle.py             # context bundle model
  trace.py              # loading trace/provenance model
```

기존 모듈 재사용 후보:

- `src/aios/filesystem.py`
- `src/aios/markdown_refs.py`
- `src/aios/result.py`
- future `validate` target resolver

## 20. activation.yaml 호환성

시맨틱 로더는 future `activation.yaml`의 소비자가 될 수 있다. 단, `activation.yaml`은 sync manifest가 아니며 drift 추적도 아니다.

호환 방향:

```yaml
activation:
  agent: developer
  runtime: codex-cli
  profile: minimal-worker

semantic_loading:
  include_layers:
    - executable_contract
    - runtime_policy
    - input_output
    - execution_logic
  exclude_layers:
    - examples
    - philosophy
    - performance_metrics
  budget:
    max_chars: 30000
```

로더는 activation 설정이 없으면 built-in profile을 사용한다.

## 21. validate runtime 호환성

`aios validate`와의 관계:

- validate는 판단 엔진이고, semantic loader는 context selection 엔진이다.
- validate는 target file과 validator contract를 필요로 할 때 로더를 사용할 수 있다.
- validate 결과의 fail/warn 판정은 loader가 하지 않는다.
- loader는 validator 문서의 `Executable Contract`와 `Structural Rules`만 반환해야 한다.
- `Human Review Guidance`는 validate에서 자동 fail 조건으로 사용하지 않는다.

호환 예:

```text
aios validate .ai/skills/foo.skill.md
  -> target kind: skill
  -> semantic loader profile: validation-runtime
  -> load skill target
  -> load skill_validator executable contract
  -> return context bundle
  -> validate engine evaluates
```

## 22. Worker Orchestration 호환성

향후 orchestration이 생겨도 semantic loader는 orchestration을 수행하지 않는다. worker scheduler가 생기면 다음 방식으로만 결합한다.

```text
worker scheduler
  -> asks semantic loader for context bundle
  -> receives read-only bundle + trace
  -> starts worker with selected context
  -> worker execution happens outside loader
```

결합 원칙:

- loader는 worker를 만들지 않는다.
- loader는 tmux/session/process를 다루지 않는다.
- loader는 파일을 수정하지 않는다.
- loader는 context bundle과 trace만 반환한다.

## 23. P0 / P1 / P2 로더 구현 로드맵

### P0

| 작업 | 산출물 |
|---|---|
| loader input/result schema 정의 | dataclass 또는 JSON schema 초안 |
| built-in profile 정의 | minimal-worker, reviewer, strategist, validation-runtime |
| annotation boundary parser 설계 | `ai-governance:start/end` 추출 |
| 표준 섹션명 fallback 설계 | heading 기반 추출 |
| exclusion policy 구현 계획 | examples/philosophy/performance 기본 제외 |
| trace/provenance 모델 설계 | loaded/excluded/warnings |

### P1

| 작업 | 산출물 |
|---|---|
| read-only semantic loader v0 구현 | `aios inspect`/`validate`와 독립 실행 가능 |
| `--trace` 또는 JSON trace 출력 | 로딩 이유와 제외 이유 확인 |
| validate runtime에서 선택적으로 사용 | validator contract loading |
| token budget 근사 처리 | 문자 수 기반 |
| mixed document warning | annotation migration 후보 출력 |

### P2

| 작업 | 산출물 |
|---|---|
| activation.yaml 입력 지원 | built-in profile override |
| profile별 budget 정책 | runtime/reviewer/strategy 차등 |
| section summarization hook | 장문 guidance 요약 |
| worker scheduler 연동 준비 | context bundle API 안정화 |
| contract coverage 리포트 | annotation adoption 측정 |

## 24. 결론

시맨틱 로더의 첫 단계는 orchestration이 아니라 read-only context selection이다. 이 로더는 `.ai/rules/rules.md`를 작은 always-load core로 두고, 작업 의도와 profile에 따라 필요한 semantic layer만 추출해야 한다. annotation이 없는 현재 문서들은 표준 섹션명과 legacy mapping으로 보수적으로 처리하되, 혼합 문서는 warning과 migration 후보로 남긴다.

이 설계는 future `activation.yaml`, `aios validate`, runtime worker, orchestration과 호환되지만 어느 것도 지금 구현하지 않는다.
