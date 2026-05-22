# Registry Architecture 감사 보고서

## 개요

Roadmap v1.2 Phase 5의 runtime contract and activation planning 범위에서 현재 저장소의 registry-like source를 감사했다. 감사 대상은 `.ai/rules/operations/agent.rules.md`, `.ai/agents/*.agent.md`, `.ai/validators/validator_index.md`, `.ai/workflows/*.workflow.md`, `.ai/templates/activation.template.yaml`이다.

이번 감사는 설계 문서 작업이며 기존 `.ai` runtime source 파일은 수정하지 않았다.

## 감사 대상

| 대상 | 현재 역할 | registry 성격 |
|---|---|---|
| `.ai/rules/operations/agent.rules.md` | agent governance와 embedded `agent-routing` YAML 보관 | agent routing registry 후보 |
| `.ai/agents/*.agent.md` | agent별 역할, rule, validator, skill 정보 보관 | agent source registry |
| `.ai/validators/validator_index.md` | validator 목록, 분류, dependency 설명 보관 | validator human-readable registry |
| `.ai/workflows/*.workflow.md` | workflow별 목적, stage, 관련 agent/template/validator 설명 보관 | workflow source registry |
| `.ai/templates/activation.template.yaml` | active agent, skill, workflow, validator, loader profile 선택 예시 | activation registry template |

## 현재 Registry 기능 판정

### Agent Registry

현재 agent registry 역할은 두 계층으로 나뉘어 있다.

| 계층 | 파일 | 기능 |
|---|---|---|
| source registry | `.ai/agents/*.agent.md` | 실제 agent inventory, frontmatter metadata, rule/validator reference |
| routing registry | `.ai/rules/operations/agent.rules.md` embedded `agent-routing` | agent 선택, 기본 rule set, validator, use case 매핑 |

`aios inventory`는 `.ai/agents/*.agent.md`를 기준으로 agent item을 발견한다. 따라서 실행 가능한 source of truth는 agent 파일이며, embedded YAML은 routing convenience index에 가깝다.

### Validator Registry

`.ai/validators/validator_index.md`는 validator registry 역할을 하지만 현재 형식은 Markdown 표와 설명 중심이다. 사람이 읽기에는 충분하지만 machine-readable dispatch table로 쓰기에는 다음 한계가 있다.

- validator id가 명시적 schema로 고정되어 있지 않다.
- target kind, severity policy, runtime use 여부가 구조화되어 있지 않다.
- dependency map 일부에 인코딩 손상으로 보이는 문자가 포함되어 있다.

현재 `aios validate`의 실제 dispatch registry는 `src/aios/validate/registry.py`와 `engine.py`의 코드 상수 및 분기이다. 즉 `.ai/validators/validator_index.md`는 human registry이고, Python 코드는 executable registry이다.

### Workflow Registry

`.ai/workflows/*.workflow.md`가 workflow source registry로 동작한다. `aios inventory`와 `aios validate --workflow`는 파일명 규칙과 canonical path를 기준으로 workflow를 발견한다.

현재 workflow 문서는 stage, responsible role, templates, related documents를 포함하지만 공통 YAML registry는 없다. 따라서 workflow registry는 파일 시스템 규칙 기반 discovery에 의존한다.

### Activation Registry

`.ai/templates/activation.template.yaml`은 실제 activation registry라기보다 activation contract template이다. 다만 `active_set`이 agent, skill, workflow, validator를 한 번에 선택하므로 future runtime activation registry의 최소 구조를 이미 보여준다.

현재 `aios activation`과 `aios validate <activation.yaml>`은 이 schema를 읽고 inventory reference와 semantic loader profile을 검증할 수 있다.

## Embedded YAML 유지 여부

단기적으로는 `.ai/rules/operations/agent.rules.md`의 embedded `agent-routing` YAML을 유지하는 편이 적절하다.

판단 근거:

- 현재 `.ai/registry/` 디렉터리는 존재하지 않는다.
- `aios inventory`, `aios activation`, `aios validate`, `aios load-context`가 이미 읽기 전용 흐름으로 안정화되는 중이다.
- registry 파일을 즉시 분리하면 source of truth가 늘어나고 동기화 검증을 먼저 구현해야 한다.
- embedded YAML은 현재 agent governance 문맥 안에서 설명과 함께 유지되고 있어 사람이 검토하기 쉽다.

중기적으로는 다음 standalone registry 후보를 도입할 수 있다.

| 후보 파일 | 도입 조건 | 목적 |
|---|---|---|
| `.ai/registry/agents.yaml` | agent routing을 여러 runtime command가 직접 읽어야 할 때 | agent id, file, rule set, validators, loader profile 매핑 |
| `.ai/registry/validators.yaml` | validate dispatch와 validator index를 `.ai` contract로 승격할 때 | validator id, file, target kinds, dependencies, executable adapter 매핑 |
| `.ai/registry/workflows.yaml` | workflow selection과 validation 대상 관계가 구조화될 때 | workflow id, file, stages, required agents, validators 매핑 |

## 관계 모델

### Inventory와 Registry

Inventory는 repository discovery layer이다. Registry는 discovered item에 의미와 routing 관계를 부여하는 optional contract layer가 되어야 한다.

- inventory는 파일이 존재하는지, canonical path가 무엇인지, frontmatter metadata가 무엇인지 제공한다.
- registry는 어떤 agent가 어떤 rule, validator, workflow, loader profile과 연결되는지 선언한다.
- registry reference는 inventory item name 또는 canonical path로 해석되어야 한다.
- registry가 존재하지 않아도 inventory와 validate의 기본 동작은 유지되어야 한다.

### Activation과 Registry

Activation은 runtime selection contract이다. Registry는 선택 가능한 대상과 기본 관계를 정의하고, activation은 그중 활성화할 set을 선택한다.

- activation `active_set.agents`는 agent registry 또는 inventory의 agent item을 참조한다.
- activation `active_set.workflows`는 workflow registry 또는 inventory의 workflow item을 참조한다.
- activation `active_set.validators`는 validator registry 또는 inventory의 validator item을 참조한다.
- activation은 registry를 수정하지 않는다.

### Semantic Loader Profile과 Registry

Semantic loader profile은 context extraction policy이다. Registry는 기본 profile 또는 target별 recommended profile을 선언할 수 있지만 context loading 자체를 수행하지 않는다.

- activation `profiles.default_loader`가 runtime selection의 기본 profile을 지정한다.
- agent registry 후보는 agent별 default loader profile을 선언할 수 있다.
- validator registry 후보는 validator contract loading에 적합한 profile을 선언할 수 있다.
- semantic loader는 profile 이름의 유효성을 검증할 수 있지만 registry policy 판단 엔진이 되어서는 안 된다.

### Validate와 Registry

`aios validate`는 registry integrity를 검사하는 소비자가 되어야 한다.

검증 후보:

- registry schema validity
- registry item reference가 inventory에 존재하는지
- registry에 선언된 validator file이 실제 존재하는지
- registry에 선언된 loader profile이 `VALID_PROFILES`에 포함되는지
- activation이 registry 또는 inventory에 없는 항목을 참조하는지
- duplicate id와 duplicate canonical path가 있는지

`aios validate`는 registry를 읽더라도 workflow 실행, worker dispatch, orchestration, sync, auto-fix를 수행하지 않아야 한다.

## 최소 Schema 후보

### Agent Registry 후보

```yaml
schema_version: aios.registry.agents.v0
agents:
  - id: developer
    file: .ai/agents/developer.agent.md
    default_domain_rules:
      - .ai/rules/domains/development.rules.md
      - .ai/rules/domains/documentation.rules.md
    default_operation_rules:
      - .ai/rules/operations/agent.rules.md
      - .ai/rules/operations/workflow.rules.md
      - .ai/rules/operations/validation.rules.md
    validators:
      - .ai/validators/developer_skill_validator.md
    default_loader: minimal-worker
    primary_use_cases:
      - software architecture
      - implementation
      - code review
```

### Validator Registry 후보

```yaml
schema_version: aios.registry.validators.v0
validators:
  - id: developer_skill_validator
    file: .ai/validators/developer_skill_validator.md
    target_kinds:
      - skill
      - agent
    dependencies:
      - .ai/validators/_base/agent_skill_base_validator.md
    default_loader: validation-runtime
    executable: false
```

### Workflow Registry 후보

```yaml
schema_version: aios.registry.workflows.v0
workflows:
  - id: l2_review
    file: .ai/workflows/l2_review.workflow.md
    agents:
      - developer
      - pm
    validators:
      - .ai/validators/l2_review_validator.md
    default_loader: reviewer
    executable: false
```

## 비목표

Registry architecture는 다음 기능을 포함하지 않는다.

- workflow execution
- worker dispatch
- orchestration
- sync
- manifest writing
- adapter generation
- registry auto-fix
- activation file auto-generation

## 감사 결론

현재 저장소는 이미 registry 기능을 여러 계층에 분산해 가지고 있다. 가장 안정적인 순서는 기존 embedded YAML과 Markdown index를 당장 분리하지 않고, 먼저 registry schema 후보와 validate integrity contract를 문서화한 뒤 `.ai/registry/*.yaml` 도입 시점을 별도 단계로 두는 것이다.

단기 source of truth는 계속 다음과 같이 유지한다.

- agent 존재성: `.ai/agents/*.agent.md`
- validator 존재성: `.ai/validators/**/*.md`
- workflow 존재성: `.ai/workflows/*.workflow.md`
- activation selection: activation YAML contract
- routing convenience: `.ai/rules/operations/agent.rules.md` embedded `agent-routing`
