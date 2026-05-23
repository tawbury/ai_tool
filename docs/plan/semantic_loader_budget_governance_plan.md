# Semantic Loader Budget Governance 계획

## 목적

이 문서는 runtime orchestration 이전에 semantic loader의 token/context budget governance를 정의한다.

현재 단계는 설계 문서 작성이며 다음을 구현하지 않는다.

- runtime code 변경
- model API token counting
- live model execution
- orchestration
- workflow execution
- worker dispatch
- sync
- manifest
- adapter generation
- registry parser
- `.ai/registry/`
- auto-fix

## 기본 모델

현재 `aios load-context`는 정확한 tokenizer를 사용하지 않는다. 따라서 budget governance의 초기 단위는 `chars`이다.

용어:

- **soft budget**: 넘으면 warning을 내지만 bundle을 계속 만들 수 있는 권장 상한이다.
- **hard budget**: 넘으면 future implementation에서 추가 chunk 포함을 중단하거나 truncation을 적용해야 하는 절대 상한이다.
- **budget profile**: semantic loader profile과 별도로 budget 크기만 정의하는 정책 이름이다.
- **provenance**: chunk의 `path`, `semantic_layer`, `line_start`, `line_end`, `extraction_method`, `confidence`, `chars` 정보이다.

## Profile별 Budget 기대치

초기 budget은 문자 수 기준으로 정의한다. 실제 token 수는 future model adapter가 알 수 있으며, semantic loader는 근사치를 제공한다.

| Profile | Soft budget | Hard budget | 의도 |
|---|---:|---:|---|
| `validation-runtime` | 6,000 chars | 10,000 chars | validation contract만 작게 로드 |
| `minimal-worker` | 12,000 chars | 20,000 chars | worker가 실행 전 필요한 runtime contract 중심 |
| `reviewer` | 24,000 chars | 40,000 chars | review guidance와 criteria 포함 |
| `strategist` | 36,000 chars | 60,000 chars | philosophy와 strategic context 일부 허용 |

이 값은 model API limit이 아니라 `.ai OS` 내부 context bundle 품질 기준이다.

## Budget 적용 순서

Future implementation은 다음 순서를 따라야 한다.

1. target file을 resolve한다.
2. semantic sections를 추출한다.
3. profile include/exclude layer를 적용한다.
4. CLI include/exclude override를 적용한다.
5. chunk별 provenance와 char count를 계산한다.
6. 중복 chunk 후보를 제거한다.
7. priority 순서대로 chunk를 budget에 맞춰 포함한다.
8. soft budget 초과 시 warning을 추가한다.
9. hard budget 초과 시 lower-priority chunk를 제외하거나 truncation한다.
10. 제외 또는 truncation된 항목도 provenance summary를 보존한다.

## Inclusion Priority

Budget이 부족할 때 포함 우선순위는 다음 순서를 따른다.

| Priority | Semantic layer | 이유 |
|---:|---|---|
| 1 | `executable_contract` | runtime 판단에 가장 직접적 |
| 2 | `structural_rules` | 파일 구조와 contract 검증에 필요 |
| 3 | `runtime_policy` | 실행 경계와 금지 사항 확인 |
| 4 | `constraints` | 제약 조건 보존 |
| 5 | `input_output` | 작업 입출력 이해 |
| 6 | `execution_logic` | 구현 또는 검토 흐름 이해 |
| 7 | `review_criteria` | reviewer 이상 profile에서 우선 |
| 8 | `human_review_guidance` | reviewer 이상 profile에서만 유지 |
| 9 | `philosophy` | strategist profile에서만 유지 |
| 10 | `examples` | 명시 include 또는 남는 budget이 있을 때만 |
| 11 | `performance_metrics` | 기본적으로 낮은 우선순위 |

`validation-runtime`은 priority 1-3을 중심으로 유지해야 한다.

## Exclusion Priority

Budget 초과 시 제외 우선순위는 inclusion priority의 역순을 기본으로 한다.

1. `performance_metrics`
2. `examples`
3. `philosophy`
4. `human_review_guidance`
5. `review_criteria`
6. `execution_logic`
7. `input_output`
8. `constraints`
9. `runtime_policy`
10. `structural_rules`
11. `executable_contract`

`executable_contract`, `structural_rules`, `runtime_policy`는 hard budget 초과 상황에서도 가능한 한 보존해야 한다.

## Truncation Policy

Truncation은 마지막 수단이다.

권장 정책:

- 먼저 lower-priority chunk를 제외한다.
- 그래도 hard budget을 넘으면 큰 chunk를 section 단위가 아니라 paragraph 또는 list block 단위로 잘라야 한다.
- truncation된 chunk는 `truncated=true` 같은 future metadata를 가져야 한다.
- truncation은 원본 파일을 수정하지 않는다.
- line range는 원본 provenance를 유지하되, truncation range를 별도 metadata로 추가해야 한다.
- code fence나 table을 중간에서 자르는 것은 피해야 한다.

초기 구현에서는 hard budget 초과 시 truncation보다 exclusion을 우선하는 것이 안전하다.

## Provenance Preservation

Budget filtering 이후에도 다음 정보는 유지되어야 한다.

- loaded chunk provenance
- excluded layer provenance
- budget-excluded chunk provenance
- truncation reason
- original char count
- included char count
- profile과 budget profile

JSON summary 후보:

```json
{
  "budget": {
    "profile": "minimal-worker",
    "soft_chars": 12000,
    "hard_chars": 20000,
    "used_chars": 9800,
    "excluded_chars": 4300,
    "truncated_chunks": 0
  }
}
```

## Warning Policy

Future warning code 후보:

| Code | Severity 성격 | 조건 |
|---|---|---|
| `budget_soft_exceeded` | warning | used chars가 soft budget을 초과 |
| `budget_hard_exceeded` | warning 또는 fail 후보 | hard budget을 초과해 chunk 제외 또는 truncation 발생 |
| `budget_truncated_chunk` | warning | chunk content가 잘림 |
| `budget_excluded_low_priority` | info | budget 때문에 낮은 priority chunk 제외 |
| `budget_profile_unknown` | crash 또는 warning 후보 | 알 수 없는 budget profile |
| `budget_estimate_only` | info | 문자 수 기반 근사치임을 명시 |

`aios load-context`는 validation command가 아니므로 초기에는 budget 문제를 fail보다 warning으로 보고하는 편이 안전하다.

## Activation v1 호환성

Activation v1의 loader profile 필드는 context budget governance와 다음처럼 연결된다.

| Activation v1 field | Budget 관계 |
|---|---|
| `profiles.default_loader` | 기본 semantic profile과 기본 budget profile을 결정 |
| `profiles.agent_loader_overrides` | agent별 semantic profile과 budget expectation override |
| `profiles.workflow_loader_overrides` | workflow별 semantic profile과 budget expectation override |
| `active_set.rules` | budget 대상 rule 후보를 늘릴 수 있음 |
| `rule_sets` | context selection hint로 사용될 수 있으나 rule source를 대체하지 않음 |

Activation은 context loading을 직접 수행하지 않는다. Future consumer가 activation을 입력으로 사용하더라도 budget filtering은 semantic loader 단계에서 적용해야 한다.

## Future Inventory-aware Selection

Inventory-aware context selection이 도입되면 다음 원칙을 따른다.

- inventory는 candidate file discovery만 담당한다.
- budget governance는 discovered files 중 어떤 semantic chunk를 포함할지 결정한다.
- duplicate canonical path는 한 번만 load해야 한다.
- 같은 file의 같은 line range가 여러 activation path에서 참조되면 provenance에 all source references를 기록하되 content는 중복 포함하지 않는다.

## Future Registry-aware Resolution

Registry-aware resolution이 도입되더라도 budget governance는 다음 경계를 유지한다.

- registry는 relationship layer이다.
- registry는 default loader 또는 target loader profile을 제안할 수 있다.
- registry는 budget enforcement를 수행하지 않는다.
- semantic loader가 budget profile과 chunk inclusion을 최종 계산한다.
- `.ai/registry/*.yaml`이 없어도 current built-in profile budget은 동작해야 한다.

## Future CLI 후보

### `--max-chars`

명시적 hard budget override이다.

예시:

```powershell
python -m aios load-context .ai/rules/rules.md --profile minimal-worker --max-chars 12000
```

정책:

- `--max-chars`는 profile hard budget보다 우선한다.
- 너무 작은 값이면 core layer 보존 실패 warning을 낸다.
- 값은 실제 token 수가 아니라 character budget이다.

### `--budget-profile`

semantic profile과 budget profile을 분리한다.

예시:

```powershell
python -m aios load-context .ai/workflows/l2_review.workflow.md --profile reviewer --budget-profile compact
```

후보 budget profile:

| Budget profile | 의미 |
|---|---|
| `compact` | soft/hard를 기본보다 작게 |
| `standard` | profile 기본값 |
| `expanded` | reviewer/strategist 작업에서 더 넓게 |
| `strict` | validation-runtime에 가까운 보수적 예산 |

### Budget warnings

CLI human output은 다음을 표시해야 한다.

- budget profile
- used chars
- soft/hard budget
- excluded chars
- truncation 여부
- warning list

JSON output은 `summary.budget` 또는 top-level `budget` object를 포함할 수 있다.

## Non-goals

이 계획은 다음을 포함하지 않는다.

- 실제 model API token counting
- live model execution
- orchestration
- workflow execution
- worker dispatch
- sync
- manifest
- adapter generation
- registry parser
- `.ai/registry/`
- auto-fix
- semantic summarization

## 단계별 도입 후보

1. budget constants를 profile별로 정의한다.
2. `ContextBundle.summary`에 budget estimate를 추가한다.
3. `--max-chars`를 hard budget override로 추가한다.
4. budget warning code를 추가한다.
5. lower-priority exclusion을 구현한다.
6. truncation metadata를 설계한다.
7. activation v1 loader override와 future activation-driven loading의 budget relationship을 연결한다.

## 완료 기준

- 현재 semantic loader의 budget 관련 위험이 문서화된다.
- profile별 soft/hard budget 기대치가 정의된다.
- exclusion, truncation, provenance, warning policy가 정의된다.
- activation v1, future inventory-aware selection, future registry-aware resolution과의 관계가 정의된다.
- runtime code는 수정하지 않는다.
