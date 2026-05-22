# Activation v0 한계 감사 보고서

## 개요

Roadmap v1.2 Phase 5 범위에서 activation v1 설계 전 현재 activation v0 구현과 runtime-facing 규칙을 감사했다.

감사 대상:

- `src/aios/activation.py`
- `.ai/templates/activation.template.yaml`
- `.ai/rules/operations/activation.rules.md`
- `.ai/rules/operations/registry.rules.md`

이번 작업은 문서 감사이며 `.ai` runtime 파일과 Python 구현은 수정하지 않았다.

## Activation v0 현재 구조

현재 activation v0 schema는 다음 최소 구조를 사용한다.

```yaml
schema_version: aios.activation.v0
active_set:
  agents: []
  skills: []
  workflows: []
  validators: []
profiles:
  default_loader: minimal-worker
```

`src/aios/activation.py`는 다음 동작을 제공한다.

- activation YAML을 제한적인 parser로 읽는다.
- `schema_version`을 검사한다.
- `active_set.agents`, `active_set.skills`, `active_set.workflows`, `active_set.validators`를 문자열 목록으로 정규화한다.
- `profiles.default_loader`가 semantic loader의 `VALID_PROFILES`에 있는지 검사한다.
- activation reference를 inventory item name, canonical path, relative path, frontmatter `name` 기준으로 해석한다.
- `aios activation`과 `aios validate <activation.yaml>`에서 읽기 전용 검증을 수행한다.

## 확인된 장점

- activation contract가 sync나 execution과 분리되어 있다.
- inventory reference resolution이 이미 구현되어 있다.
- semantic loader profile 이름 검증이 이미 구현되어 있다.
- `aios validate`가 activation YAML을 first-class validation target으로 처리한다.
- activation v0는 현재 read-only boundary를 유지한다.

## 확인된 한계

### Per-agent loader profile 부재

v0는 `profiles.default_loader`만 지원한다. 특정 agent에는 더 넓은 reviewer profile이나 더 좁은 minimal profile이 필요할 수 있지만, v0에서는 agent별 override를 표현할 수 없다.

### Per-workflow loader profile 부재

workflow는 review-oriented context 또는 validation-runtime context를 요구할 수 있다. v0는 workflow별 loader profile을 선언할 수 없어서 모든 activation target이 같은 default loader에 의존한다.

### Runtime mode 부재

v0는 activation file이 어떤 runtime 목적을 갖는지 명시하지 않는다. 예를 들어 validation-only, review, planning 같은 mode를 구분할 수 없다.

단, runtime mode는 worker dispatch나 workflow execution으로 해석되어서는 안 된다. v1에서 mode가 추가되더라도 validation과 context selection hint 수준에 머물러야 한다.

### Domain/rule activation 부재

v0는 agents, skills, workflows, validators만 active set으로 선언한다. 특정 domain rule 또는 operation rule set을 activation 관점에서 명시할 수 없다.

다만 rule activation은 `.ai/rules` source of truth를 대체해서는 안 되며, runtime context selection을 위한 optional rule set이어야 한다.

### Registry-aware resolution 부재

현재 reference resolution은 inventory 기반이다. `.ai/registry/*.yaml`은 아직 없고 parser도 없으므로 registry id 우선 해석이나 registry relationship validation은 수행하지 않는다.

이는 현재 단계에서는 적절하지만, future registry extraction 이후에는 activation reference가 registry id와 inventory name 중 무엇을 우선하는지 정해야 한다.

### Future `.ai/registry/*.yaml` 관계 부재

v0 schema는 future registry file과의 관계를 명시하지 않는다. registry architecture rules는 `.ai/registry/*.yaml`을 future extraction candidate로 정의했지만 activation v0는 이 후보와 연결되는 필드를 갖지 않는다.

### 제한적인 YAML 구조

현재 parser는 단순 key, section, list 구조에 맞춰져 있다. v1에서 nested map인 `agent_loader_overrides`, `workflow_loader_overrides`, `rule_sets`를 지원하려면 parser 또는 YAML 처리 전략을 별도로 설계해야 한다.

## v1에서 해결할 범위

activation v1은 sync와 orchestration 전에 유용한 범위로만 확장해야 한다.

포함 후보:

- `schema_version`
- `active_set`
- `profiles.default_loader`
- `profiles.agent_loader_overrides`
- `profiles.workflow_loader_overrides`
- `runtime_mode`
- optional `rule_sets`

제외해야 할 항목:

- sync target
- materialization path
- worker assignment
- workflow execution plan
- adapter output
- generated manifest
- auto-fix policy

## Validation 영향

activation v1 validation은 다음을 추가로 고려해야 한다.

- `schema_version`이 `aios.activation.v1`인지 검사
- v0와 같은 active_set reference resolution 유지
- agent loader override key가 active agent 또는 known agent를 참조하는지 검사
- workflow loader override key가 active workflow 또는 known workflow를 참조하는지 검사
- 모든 loader profile 값이 `VALID_PROFILES`에 포함되는지 검사
- `runtime_mode`가 허용된 enum인지 검사
- duplicate references는 warning으로 유지
- empty active set 또는 empty category는 info 또는 warning으로 구분
- registry parser가 없을 때 registry-aware validation은 수행하지 않음

## 결론

activation v0는 read-only active selection contract로 충분히 작고 안정적이다. v1은 이 장점을 유지하면서 loader profile override, runtime mode, optional rule set만 추가해야 한다.

`.ai/registry/*.yaml`과의 관계는 문서상 호환성을 정의하되, registry parser나 standalone registry file 생성은 activation v1 구현 전 단계에서 계속 deferred로 유지하는 것이 적절하다.
