# Registry Architecture 계획

## 목적

이 문서는 `aios inventory`, `aios activation`, `aios validate`, `aios load-context`를 장기적으로 연결할 registry architecture를 설계한다. 현재 단계에서는 문서 설계만 수행하며 `.ai` runtime source 파일을 수정하지 않는다.

## 설계 원칙

- `.ai/`는 runtime source of truth로 유지한다.
- Inventory는 discovery layer이고 registry는 relationship layer이다.
- Activation은 registry 또는 inventory에서 선택 가능한 항목의 active set만 선언한다.
- Validate는 registry integrity를 검사하되 실행하지 않는다.
- Semantic loader는 context extraction을 담당하고 registry 판단 엔진이 되지 않는다.
- Sync, manifest, adapter generation, orchestration, worker execution, workflow execution, auto-fix는 이 단계의 비목표이다.

## 현재 상태

| 기능 | 현재 구현 | Registry 관련 상태 |
|---|---|---|
| `aios inventory` | 구현됨 | agent, skill, workflow, validator, rule, command discovery 제공 |
| `aios activation` | 구현됨 | activation schema, inventory reference, loader profile 검증 |
| `aios validate` | 구현됨 | activation validation 포함, 코드 내부 validator dispatch 사용 |
| `aios load-context` | 구현됨 | built-in semantic loader profile 사용 |
| agent routing | embedded YAML | `.ai/rules/operations/agent.rules.md` 내부에 존재 |
| validator registry | Markdown index | `.ai/validators/validator_index.md`가 human-readable index 역할 |
| workflow registry | 파일 시스템 discovery | `.ai/workflows/*.workflow.md`가 source 역할 |

## Architecture 결정

### 결정 1: Embedded agent-routing YAML은 단기 유지

현재 embedded YAML은 agent governance 문서와 같은 위치에 있어 유지 비용이 낮다. 즉시 `.ai/registry/agents.yaml`로 분리하면 agent frontmatter, embedded YAML, registry YAML 사이의 drift를 검사하는 검증기가 먼저 필요하다.

따라서 단기에는 embedded YAML을 유지하고, registry extraction은 validate가 registry reference integrity를 검사할 준비가 된 뒤 진행한다.

### 결정 2: `.ai/registry/*.yaml`은 후속 단계 후보로 정의

후속 단계에서 다음 파일을 도입할 수 있다.

```text
.ai/registry/
  agents.yaml
  validators.yaml
  workflows.yaml
```

각 파일은 독립 schema version을 가져야 한다.

- `aios.registry.agents.v0`
- `aios.registry.validators.v0`
- `aios.registry.workflows.v0`

### 결정 3: Registry는 실행 계획이 아니라 참조 계약이다

Registry는 어떤 agent, validator, workflow가 존재하고 서로 어떤 관계를 갖는지 선언한다. Registry가 존재해도 runtime command는 다음을 수행하지 않는다.

- worker dispatch
- workflow execution
- orchestration
- sync target materialization
- adapter generation
- auto-fix

## 최소 Schema 후보

### Agents

필수 필드:

| 필드 | 설명 |
|---|---|
| `schema_version` | `aios.registry.agents.v0` |
| `agents[].id` | inventory name 또는 stable registry id |
| `agents[].file` | `.ai/agents/*.agent.md` canonical path |
| `agents[].default_domain_rules` | 기본 domain rule canonical path 목록 |
| `agents[].default_operation_rules` | 기본 operation rule canonical path 목록 |
| `agents[].validators` | agent와 연결된 validator canonical path 목록 |

선택 필드:

| 필드 | 설명 |
|---|---|
| `agents[].default_loader` | 기본 semantic loader profile |
| `agents[].primary_use_cases` | routing hint |
| `agents[].tools` | 지원 CLI 도구 |

예시:

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
```

### Validators

필수 필드:

| 필드 | 설명 |
|---|---|
| `schema_version` | `aios.registry.validators.v0` |
| `validators[].id` | stable validator id |
| `validators[].file` | `.ai/validators/**/*.md` canonical path |
| `validators[].target_kinds` | `agent`, `skill`, `workflow`, `activation`, `validator-index` 등 |
| `validators[].executable` | 현재는 `false` 기본, future adapter 여부 표시 |

선택 필드:

| 필드 | 설명 |
|---|---|
| `validators[].dependencies` | 참조 validator canonical path 목록 |
| `validators[].default_loader` | validator contract loading profile |
| `validators[].severity_policy` | validator별 fail/warn/info 정책 후보 |

예시:

```yaml
schema_version: aios.registry.validators.v0
validators:
  - id: activation
    file: src/aios/validate/validators/activation.py
    target_kinds:
      - activation
    dependencies:
      - .ai/rules/operations/activation.rules.md
    default_loader: validation-runtime
    executable: true
```

### Workflows

필수 필드:

| 필드 | 설명 |
|---|---|
| `schema_version` | `aios.registry.workflows.v0` |
| `workflows[].id` | inventory name 또는 stable workflow id |
| `workflows[].file` | `.ai/workflows/*.workflow.md` canonical path |
| `workflows[].validators` | workflow 검증에 사용할 validator canonical path 목록 |

선택 필드:

| 필드 | 설명 |
|---|---|
| `workflows[].agents` | workflow에 관련된 agent id 목록 |
| `workflows[].default_loader` | workflow contract loading profile |
| `workflows[].executable` | 현재는 `false`, future execution capability 표시 |

예시:

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

## Runtime Command 관계

### Inventory

Inventory는 registry의 하위 의존성이다. Registry loader는 먼저 `build_inventory(root)` 결과를 사용해 파일 존재성과 canonical path를 확인해야 한다.

Registry가 없는 경우에도 inventory command는 계속 동작해야 한다.

### Activation

Activation은 registry를 생성하거나 수정하지 않는다. Activation은 registry 또는 inventory에 있는 id와 canonical path를 active set으로 선택한다.

Future validation order 후보:

1. activation YAML schema 검증
2. registry 파일이 있으면 registry schema 검증
3. activation reference를 registry id로 우선 해석
4. registry miss이면 inventory name 또는 canonical path로 해석
5. loader profile 이름 검증

### Semantic Loader

Registry는 loader profile 이름만 참조할 수 있다. 실제 context extraction은 `aios load-context` 또는 future consumer가 명시적으로 호출할 때만 수행한다.

권장 관계:

| Registry 위치 | Loader profile 역할 |
|---|---|
| activation `profiles.default_loader` | active runtime context의 기본 profile |
| agents `default_loader` | agent context loading 기본값 |
| validators `default_loader` | validator contract loading 기본값 |
| workflows `default_loader` | workflow review 또는 contract loading 기본값 |

### Validate

`aios validate`는 registry 도입 후 다음 target을 지원할 수 있다.

```text
python -m aios validate .ai/registry/agents.yaml
python -m aios validate .ai/registry/validators.yaml
python -m aios validate .ai/registry/workflows.yaml
python -m aios validate --json --summary-only
```

검증 범위 후보:

- schema version 유효성
- required field 존재 여부
- duplicate id
- duplicate file reference
- inventory reference resolution
- semantic loader profile validity
- validator target kind validity
- activation active set과 registry item 관계

## 단계별 계획

### Step 1: 현재 상태 고정

- embedded `agent-routing` YAML 유지
- `.ai/validators/validator_index.md` 유지
- `.ai/workflows/*.workflow.md` discovery 유지
- `.ai/templates/activation.template.yaml` 유지
- 새 `.ai/registry/` 파일은 아직 만들지 않음

### Step 2: Registry schema 설계 확정

- `agents.yaml`, `validators.yaml`, `workflows.yaml`의 required field 확정
- registry id와 inventory name의 동일성 규칙 결정
- canonical path 우선순위 결정
- loader profile reference 정책 결정

### Step 3: Read-only validator 설계

- `src/aios/validate/validators/registry.py` 후보 설계
- registry YAML target detection 설계
- embedded `agent-routing`과 future `agents.yaml`의 drift 검증 방식 설계
- validator index Markdown과 future `validators.yaml`의 관계 검증 방식 설계

### Step 4: `.ai/registry/` 도입 여부 결정

도입 조건:

- 두 개 이상의 runtime command가 동일 routing table을 machine-readable 형태로 필요로 한다.
- embedded YAML과 frontmatter 사이의 drift가 실제 maintenance risk로 확인된다.
- validate가 registry reference integrity를 읽기 전용으로 검사할 수 있다.

### Step 5: 후속 구현

후속 구현도 읽기 전용이어야 한다.

- registry file parser 추가
- registry validate target 추가
- activation reference resolution에서 registry 우선 해석 추가
- inventory summary에 registry coverage 정보를 선택적으로 표시

## 비목표

이 계획은 다음을 구현하지 않는다.

- sync
- manifest 생성 또는 갱신
- adapter generation
- orchestration
- worker execution
- workflow execution
- auto-fix
- `.ai` 파일 구조 변경

## 완료 기준

- 현재 registry-like source의 역할이 문서화된다.
- embedded YAML 유지와 future extraction 기준이 결정된다.
- 최소 schema 후보가 정의된다.
- inventory, activation, semantic loader, validate와의 관계가 정의된다.
- read-only boundary와 non-goal이 명확히 기록된다.
