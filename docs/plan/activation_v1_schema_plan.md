# Activation v1 Schema 계획

## 목적

activation v1은 activation v0의 read-only active selection contract를 유지하면서, sync와 orchestration 전에 실제로 유용한 runtime context 선택 정보를 추가하는 schema이다.

이 문서는 구현 전 설계 문서이며 다음을 수행하지 않는다.

- activation v1 구현
- registry parser 구현
- `.ai/registry/` 생성
- `.ai` runtime 파일 수정
- sync, manifest, adapter generation, orchestration, worker execution, workflow execution, auto-fix 구현

## 설계 원칙

- Activation은 active selection layer이다.
- Inventory는 discovery layer이다.
- Registry는 future relationship layer이다.
- Validate는 integrity checker이다.
- Load-context는 context extraction layer이다.
- Activation v1은 context selection hint를 제공할 수 있지만 context loading을 직접 수행하지 않는다.
- Runtime mode는 execution mode가 아니라 validation과 context selection을 위한 declared intent이다.

## Activation v1 Schema 후보

```yaml
schema_version: aios.activation.v1
runtime_mode: validation
active_set:
  agents:
    - developer
    - pm
  skills:
    - requirements_analysis
    - system_design
  workflows:
    - l2_review
  validators:
    - developer_skill_validator
  rules:
    - .ai/rules/operations/activation.rules.md
    - .ai/rules/operations/registry.rules.md
profiles:
  default_loader: minimal-worker
  agent_loader_overrides:
    developer: reviewer
  workflow_loader_overrides:
    l2_review: reviewer
rule_sets:
  default:
    domain_rules:
      - .ai/rules/domains/documentation.rules.md
    operation_rules:
      - .ai/rules/operations/activation.rules.md
      - .ai/rules/operations/registry.rules.md
```

## 필드 정의

### `schema_version`

필수 필드이다.

허용 값:

- `aios.activation.v1`

v0와 v1은 명시적으로 구분되어야 한다. v1 validator는 v0 파일을 자동 변환하지 않는다.

### `runtime_mode`

필수 후보 필드이다.

`runtime_mode`는 activation 파일의 의도를 설명한다. 이 값은 worker dispatch나 workflow execution을 의미하지 않는다.

허용 enum 후보:

| 값 | 의미 |
|---|---|
| `validation` | validate 중심의 runtime contract 확인 |
| `context` | semantic context extraction 준비 |
| `review` | reviewer profile 또는 review-oriented context 선택 |
| `planning` | planning-oriented context 선택 |

초기 구현에서는 enum만 검증하고 동작 변경은 하지 않는 것이 안전하다.

### `active_set`

필수 필드이다.

v1의 기본 active set은 v0와 호환된다.

필수 category:

- `agents`
- `skills`
- `workflows`
- `validators`

선택 category 후보:

- `rules`

`active_set.rules`는 domain rule 또는 operation rule의 canonical path를 선택적으로 선언한다. 이 필드는 `.ai/rules` source of truth를 대체하지 않고, runtime context selection에서 참고할 rule scope를 명시하는 역할이다.

### `profiles.default_loader`

필수 필드이다.

기본 semantic loader profile을 지정한다. 값은 semantic loader의 supported profile이어야 한다.

현재 profile 후보:

- `minimal-worker`
- `reviewer`
- `strategist`
- `validation-runtime`

### `profiles.agent_loader_overrides`

선택 필드이다.

agent별 loader profile override를 선언한다.

```yaml
profiles:
  agent_loader_overrides:
    developer: reviewer
    pm: strategist
```

key는 agent inventory name, canonical path, 또는 future registry id로 해석될 수 있다.

value는 supported semantic loader profile이어야 한다.

### `profiles.workflow_loader_overrides`

선택 필드이다.

workflow별 loader profile override를 선언한다.

```yaml
profiles:
  workflow_loader_overrides:
    l2_review: reviewer
```

key는 workflow inventory name, canonical path, 또는 future registry id로 해석될 수 있다.

value는 supported semantic loader profile이어야 한다.

### `rule_sets`

선택 필드이다.

`rule_sets`는 reusable rule grouping을 선언한다. 이 필드는 runtime context selection을 위한 관계 정보이며 rule 파일을 생성하거나 수정하지 않는다.

```yaml
rule_sets:
  default:
    domain_rules:
      - .ai/rules/domains/documentation.rules.md
    operation_rules:
      - .ai/rules/operations/activation.rules.md
      - .ai/rules/operations/registry.rules.md
```

초기 v1 구현에서는 `rule_sets`를 optional validation target으로만 취급하고, context loading은 수행하지 않는다.

## Registry 관계

`.ai/registry/*.yaml`은 future extraction candidate이며 v1 schema가 즉시 요구하지 않는다.

v1은 registry-aware resolution과 호환되도록 설계하되, registry parser가 없으면 inventory 기반 resolution만 수행해야 한다.

Future resolution order 후보:

1. registry parser가 존재하고 registry file이 있으면 registry id로 해석
2. registry miss 또는 registry 부재 시 inventory name으로 해석
3. inventory name miss 시 canonical `.ai` path로 해석
4. 모두 실패하면 unknown reference error

이 계획은 `.ai/registry/`를 만들지 않는다.

## Validation Rules 후보

### Schema version

- `schema_version` 누락: error
- `schema_version`이 `aios.activation.v1`이 아님: error 또는 version-specific warning
- v0 validator와 v1 validator는 결과 메시지에서 schema version을 명확히 표시해야 한다.

### Active set references

- `active_set` 누락: error
- 필수 category 누락: warning 또는 error로 정책 결정 필요
- unknown agent, skill, workflow, validator reference: error
- unknown rule reference: error
- duplicate reference: warning
- empty category list: info

### Loader profile references

- `profiles` 누락: error
- `profiles.default_loader` 누락: error
- unknown `profiles.default_loader`: error
- unknown `agent_loader_overrides.*` profile: error
- unknown `workflow_loader_overrides.*` profile: error
- override key가 unknown agent 또는 workflow를 참조하면 error
- override key가 inactive agent 또는 workflow를 참조하면 warning 후보

### Runtime mode

- `runtime_mode` 누락: warning 후보
- unknown `runtime_mode`: error
- 허용 enum 후보: `validation`, `context`, `review`, `planning`

초기 구현에서 `runtime_mode`는 validate 결과에만 반영하고 execution behavior를 바꾸지 않는다.

### Empty runtime warnings/info

- 모든 active_set category가 비어 있음: warning
- 개별 category가 비어 있음: info
- active agents는 있는데 validators가 비어 있음: warning 후보
- active workflows는 있는데 workflow loader override가 없음: info가 아니라 pass 상태로 허용

## v0에서 v1로의 Migration Path

### v0 입력

```yaml
schema_version: aios.activation.v0
active_set:
  agents:
    - developer
    - pm
  skills:
    - requirements_analysis
    - system_design
  workflows:
    - l2_review
  validators:
    - developer_skill_validator
profiles:
  default_loader: minimal-worker
```

### v1 후보

```yaml
schema_version: aios.activation.v1
runtime_mode: validation
active_set:
  agents:
    - developer
    - pm
  skills:
    - requirements_analysis
    - system_design
  workflows:
    - l2_review
  validators:
    - developer_skill_validator
profiles:
  default_loader: minimal-worker
  agent_loader_overrides: {}
  workflow_loader_overrides: {}
```

### Migration 원칙

- v0 파일을 자동 수정하지 않는다.
- v0와 v1 validator는 같은 read-only boundary를 유지한다.
- v1 도입 후에도 v0는 deprecation 기간 동안 계속 검증 가능해야 한다.
- migration helper가 필요하더라도 초기에는 report-only 제안으로 제한한다.
- activation v1 template은 별도 작업에서 추가한다.

## Deferred Items

다음은 activation v1 schema 또는 초기 validation 구현 범위에 포함하지 않는다.

- sync selection
- file materialization
- manifest writing
- adapter generation
- orchestration
- worker dispatch
- workflow execution
- activation-driven context loading
- registry parser
- `.ai/registry/` 생성
- auto-fix

## Implementation 후보 순서

이 문서 이후의 후속 구현은 별도 요청이 있을 때만 진행한다.

1. activation v1 parser strategy 결정
2. `ActivationConfig` v1 model 후보 추가
3. v0/v1 schema dispatch 추가
4. v1 validation rules 추가
5. `aios validate <activation-v1.yaml>` 지원
6. v1 template 추가 여부 결정
7. v0/v1 compatibility test 작성

## 완료 기준

- activation v0 한계가 명확히 문서화된다.
- activation v1 schema 후보가 sync와 orchestration 전 범위로 제한된다.
- validation rules와 migration path가 정의된다.
- `.ai` runtime 파일과 구현 코드는 수정하지 않는다.
