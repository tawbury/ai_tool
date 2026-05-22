# Registry Runtime Rules 승격 보고서

## 개요

Registry architecture 감사와 계획 문서의 핵심 결정을 runtime-facing operation rule로 승격했다.

## 변경 사항

- `.ai/rules/operations/registry.rules.md`를 추가했다.
- `.ai/rules/rules.md`의 operation rule 목록, selective loading 예시, migration map을 갱신했다.
- `.ai/rules/operations/README.md`의 현재 운영 규칙 목록에 registry rule을 추가했다.

## 반영한 Runtime 규칙

- inventory는 discovery layer이다.
- registry는 relationship layer이다.
- activation은 active selection layer이다.
- validate는 integrity checker이다.
- load-context는 context extraction layer이다.
- `.ai/rules/operations/agent.rules.md`의 embedded `agent-routing` YAML은 단기 유지한다.
- `.ai/registry/*.yaml`은 즉시 만들지 않고 future extraction candidate로 둔다.
- future registry schema는 agents, validators, workflows 각각에 최소 필드를 가져야 한다.
- registry 규칙은 읽기 전용이며 sync, manifest, adapter generation, orchestration, worker execution, workflow execution, auto-fix를 포함하지 않는다.

## 범위 제한

다음은 수행하지 않았다.

- registry parser 구현
- `.ai/registry/` 생성
- `.ai/agents` 수정
- `.ai/validators` 수정
- `.ai/workflows` 수정
- embedded `agent-routing` YAML 수정
- sync, manifest, adapter generation, orchestration, worker execution, workflow execution, auto-fix 구현

## 검증

다음 명령을 실행해 통과를 확인했다.

```powershell
python -m aios inspect
python -m aios validate
python -m aios inventory --summary-only
python -m aios activation .ai/templates/activation.template.yaml
python -m compileall -q src/aios aios
git diff --check
```
