# Semantic Loader Budget Risk 감사 보고서

## 개요

Roadmap v1.2 범위에서 `aios load-context` v1의 현재 semantic loading 동작과 token/context budget 관련 위험을 감사했다.

감사 대상:

- `src/aios/semantic_loader/models.py`
- `src/aios/semantic_loader/loader.py`
- `src/aios/semantic_loader/sections.py`
- activation v1 loader override 구조
- 현재 profile include/exclude 정책

이번 감사는 문서 작업이며 runtime code는 수정하지 않았다.

## 현재 동작 요약

### Loader 입력

`LoaderInput`은 다음 입력을 받는다.

- `path`
- `profile`
- `include_layers`
- `excluded_layers`

CLI는 다음 옵션을 제공한다.

- `--profile`
- `--include-layer`
- `--exclude-layer`
- `--json`
- `--no-content`
- `--summary-only`

현재 예산 관련 CLI 옵션은 없다.

### Profile 정책

현재 지원 profile은 네 가지이다.

| Profile | Include layer | Exclude layer |
|---|---|---|
| `minimal-worker` | executable contract, structural rules, runtime policy, input/output, execution logic, constraints | examples, philosophy, performance metrics, human review guidance, review criteria |
| `reviewer` | minimal-worker 포함 항목 + human review guidance, review criteria | examples, philosophy, performance metrics |
| `strategist` | reviewer 포함 항목 + philosophy | examples, performance metrics |
| `validation-runtime` | executable contract, structural rules, runtime policy | examples, philosophy, performance metrics, human review guidance, review criteria, input/output, execution logic, constraints |

### Exclusion 우선순위

현재 동작은 다음과 같다.

1. profile include layer를 계산한다.
2. CLI `--include-layer`를 include set에 추가한다.
3. profile exclude layer를 계산한다.
4. CLI `--exclude-layer`를 exclude set에 추가한다.
5. CLI include는 같은 layer가 exclude set에 있어도 제외에서 제거되어 우선 적용된다.
6. section이 include set에 없으면 `not_included_by_profile`로 제외된다.
7. section이 exclude set에 있으면 `excluded_by_profile`로 제외된다.

### Section extraction

section extraction은 다음 순서로 수행된다.

1. `ai-governance:start/end` annotation
2. inline `ai-governance` annotation
3. standard heading mapping
4. legacy heading mapping
5. rules file fallback
6. no semantic section warning

각 loaded chunk는 provenance를 가진다.

- `path`
- `semantic_layer`
- `line_start`
- `line_end`
- `extraction_method`
- `confidence`
- `chars`

### 현재 warning

현재 warning은 profile 오류, target 누락, fallback extraction, semantic section 미발견 중심이다.

Budget warning은 아직 없다.

## 현재 위험

### Context bloat

현재 loader는 `summary.chars`를 계산하지만 budget을 적용하지 않는다. 큰 workflow, validator, rule 파일이 target이 되면 profile이 허용한 모든 section이 그대로 반환된다.

위험:

- consumer가 model context limit을 넘길 수 있다.
- `--json`에서 content를 포함하면 출력 크기가 급격히 커질 수 있다.
- downstream orchestration이 생기기 전에 context 크기 기대치가 불명확해질 수 있다.

### Duplicate semantic loading

activation v1은 agent loader override와 workflow loader override를 지원하지만 현재 loader는 단일 target file 중심이다. future consumer가 agent, workflow, rule set을 개별로 load하면 같은 rule이나 workflow section이 반복될 수 있다.

위험:

- 같은 `.ai/rules/operations/*.rules.md`가 여러 agent context에 중복 포함될 수 있다.
- workflow와 validator가 같은 rule 또는 review guidance를 반복 로드할 수 있다.
- provenance가 있어도 bundle 간 deduplication 정책이 없으면 전체 context가 커진다.

### High-noise rules

rules file fallback은 rule file 전체를 `runtime_policy`로 반환할 수 있다. annotation이 없는 rule file은 필요한 section만 고르기 어렵다.

위험:

- global rule, operation rule 전체가 항상 load되면 low-signal context가 늘어난다.
- human guidance와 runtime contract 경계가 명확하지 않은 파일은 profile intent와 다르게 과다 포함될 수 있다.

### Oversized workflow context

workflow 문서는 stage, role, related documents, review criteria 등 구조가 길어질 수 있다. reviewer나 strategist profile은 human review guidance와 review criteria를 포함하므로 workflow target에서 크게 증가할 수 있다.

위험:

- L2 review workflow 같은 문서가 reviewer profile에서 크게 로드될 수 있다.
- workflow 전체 stage가 필요한 경우와 특정 stage만 필요한 경우를 구분하지 못한다.

### Over-broad activation

activation v1은 `active_set.rules`, `rule_sets`, agent/workflow loader override를 표현한다. 이는 runtime selection에 유용하지만, future activation-driven context selection이 생기면 active set이 넓을수록 context가 커질 수 있다.

위험:

- active agents와 workflows가 많을수록 같은 shared rules와 validators가 반복될 수 있다.
- `rule_sets.default`가 과도하게 넓으면 모든 context에 broad rule set이 포함될 수 있다.

### Loader profile ambiguity

현재 profile은 include/exclude layer의 차이만 정의한다. 각 profile의 expected budget, truncation behavior, warning threshold가 없다.

위험:

- `strategist`가 얼마나 큰 context를 허용하는지 불명확하다.
- `validation-runtime`이 가장 작아야 한다는 기대가 코드나 문서에서 budget으로 표현되어 있지 않다.
- activation v1 override가 profile을 바꿔도 budget 기대치가 함께 바뀌는지 정의되어 있지 않다.

## Risk 평가

| 위험 | 심각도 | 현재 완화책 | 남은 문제 |
|---|---|---|---|
| Context bloat | High | profile include/exclude, `--no-content`, `--summary-only` | budget enforcement 없음 |
| Duplicate semantic loading | Medium | chunk provenance | bundle 간 dedup 없음 |
| High-noise rules | Medium | rules file fallback warning | fallback content가 클 수 있음 |
| Oversized workflow context | Medium | profile exclusions | workflow stage-level budget 없음 |
| Over-broad activation | Medium | activation은 아직 context loading을 수행하지 않음 | future activation-driven loading 전에 정책 필요 |
| Loader profile ambiguity | Medium | profile 이름과 layer policy 존재 | profile별 budget 기대치 없음 |

## 감사 결론

현재 semantic loader는 read-only context extraction 계층으로 잘 제한되어 있다. 그러나 orchestration이나 activation-driven loading이 생기기 전, budget governance가 먼저 정의되어야 한다.

우선 구현이 필요한 것은 실제 token counting이 아니라 문자 수 기반의 budget contract이다. 이 contract는 profile별 soft/hard budget, exclusion priority, truncation policy, provenance preservation, warning policy를 정의해야 한다.
