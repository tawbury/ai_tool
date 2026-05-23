# Activation v1 Runtime Rules 반영 보고서

## 개요

activation v1 구현 결과를 runtime-facing operation rule에 반영했다.

## 변경 사항

- `.ai/rules/operations/activation.rules.md`를 v1.1.0으로 갱신했다.
- 지원 schema version을 `aios.activation.v0`, `aios.activation.v1`로 명시했다.
- v1 `runtime_mode`, `active_set.rules`, loader override, optional `rule_sets` 동작을 문서화했다.
- `.ai/rules/operations/README.md`의 activation rule 설명에 v0/v1 지원을 짧게 반영했다.

## 명확히 한 경계

- `runtime_mode`는 declared intent이며 execution이 아니다.
- `rule_sets`는 context selection hint이며 `.ai/rules/` source of truth를 대체하지 않는다.
- loader override는 semantic loader profile 선택이며 worker behavior나 dispatch를 의미하지 않는다.
- v0 파일은 계속 지원되며 v1로 자동 migration하지 않는다.

## 비목표 유지

다음은 구현하거나 문서상 허용하지 않았다.

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

## 검증 결과

다음 명령을 실행했고 통과했다.

```powershell
python -m aios activation .ai/templates/activation.template.yaml
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios validate .ai/templates/activation.template.yaml
python -m aios validate .ai/templates/activation.v1.template.yaml
python -m aios inspect
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
```
