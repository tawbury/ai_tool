# Activation v1 구현 보고서

## 개요

activation v0 호환성을 유지하면서 `aios activation`과 `aios validate`가 `schema_version: aios.activation.v1` 파일을 처리하도록 확장했다.

## 변경 사항

- `src/aios/activation.py`가 `aios.activation.v0`와 `aios.activation.v1`을 모두 지원하도록 확장했다.
- activation model에 `runtime_mode`, `active_set.rules`, `profiles.agent_loader_overrides`, `profiles.workflow_loader_overrides`, `rule_sets`를 추가했다.
- 외부 YAML 의존성 없이 v1 template에 필요한 최소 YAML subset parser를 확장했다.
- rule inventory reference, agent/workflow loader override target, loader profile, runtime mode 검증을 추가했다.
- duplicate activation reference와 empty activation category 정책을 activation primitive로 이동해 `aios activation`과 `aios validate`가 같은 정책을 공유하도록 했다.
- `.ai/templates/activation.v1.template.yaml`을 추가했다.
- activation human summary와 JSON summary에 activation schema version을 노출했다.

## Validation 정책

- `aios.activation.v0`와 `aios.activation.v1`은 지원 schema로 처리한다.
- unknown schema version은 기존 정책을 유지해 warning으로 보고한다.
- v1 `runtime_mode` 허용 값은 `validation`, `context`, `review`, `planning`이다.
- v1에서 `runtime_mode`가 없으면 warning이다.
- unknown `runtime_mode`는 error이다.
- `active_set.rules`는 rule inventory 또는 canonical `.ai/rules/...md` path로 resolve되어야 한다.
- `agent_loader_overrides` key는 agent inventory로 resolve되어야 한다.
- `workflow_loader_overrides` key는 workflow inventory로 resolve되어야 한다.
- 모든 loader override profile 값은 semantic loader `VALID_PROFILES`에 포함되어야 한다.
- duplicate activation reference는 warning이다.
- empty activation category는 info이다.

## 유지한 경계

다음은 구현하지 않았다.

- sync
- manifest
- adapter generation
- orchestration
- worker execution
- workflow execution
- context loading
- registry parser
- `.ai/registry/`
- auto-fix
- v0 자동 migration

## 검증 결과

다음 명령을 실행했고 통과했다.

```powershell
python -m aios activation .ai/templates/activation.template.yaml
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios activation .ai/templates/activation.v1.template.yaml --json --summary-only
python -m aios validate .ai/templates/activation.template.yaml
python -m aios validate .ai/templates/activation.v1.template.yaml
python -m aios validate --json --summary-only
python -m aios inspect
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
```
