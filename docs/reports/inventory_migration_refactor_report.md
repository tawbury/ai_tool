# Inventory Discovery 마이그레이션 리팩터 보고서

## 개요

`inspect`와 `validate`의 안전한 runtime discovery 경로를 `inventory.py` primitive 기반으로 이전했다.

이번 변경은 read-only discovery refactor이며 source file mutation, sync, manifest, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix는 구현하지 않았다.

## 감사 결과

중복 discovery가 있던 위치:

- `src/aios/inspect.py`
  - agent file discovery
  - skill file discovery
  - workflow file discovery
- `src/aios/validate/targets.py`
  - repository-wide agent target discovery
  - repository-wide skill target discovery
  - repository-wide workflow target discovery
  - `--agent` path resolution
  - `--workflow` path resolution
- `src/aios/inventory.py`
  - agent, skill, workflow, validator, rule, command inventory discovery

## 변경 사항

### Inspect

- `run_inspection`에서 `build_inventory(root)`를 한 번 호출해 agent, skill, workflow inventory item을 사용하도록 변경했다.
- `skills_found`는 inventory skill count를 사용한다.
- `workflows_found`는 inventory workflow count를 사용한다.
- agent frontmatter 검사는 inventory item의 metadata를 사용한다.
- skill reference resolution은 inventory skill item을 사용한다.
- workflow reference resolution은 inventory workflow item을 사용한다.

`files_scanned`, check id, status convention, JSON shape는 유지했다.

### Validate

- repository-wide validation target discovery가 inventory item을 사용하도록 변경했다.
- agent, skill, workflow target discovery는 inventory item의 path와 name을 사용한다.
- `--agent`와 `--workflow`는 inventory lookup을 먼저 사용하고, 기존 fallback path resolution을 유지한다.
- activation YAML detection과 validator index singleton target은 기존 방식을 유지했다.

Validation result schema와 status convention은 변경하지 않았다.

## 의도한 출력 변화

`inspect`의 `workflows_found`는 기존 `.ai/workflows` 디렉터리의 모든 파일 수가 아니라 inventory workflow count로 바뀐다.

현재 값:

- 기존 방식: workflow directory file count
- 변경 후: `*.workflow.md` inventory count

이는 Roadmap v1.2의 inventory layer 기준과 맞추기 위한 의도된 변화이다.

## 유지한 경계

다음은 변경하지 않았다.

- inventory output schema
- validate result schema
- inspect result schema
- activation validation policy
- context loading behavior
- sync
- manifest
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix

## 검증 결과

다음 명령을 실행했고 통과했다.

```powershell
python -m aios inventory --summary-only
python -m aios inspect
python -m aios inspect --json --summary-only
python -m aios validate
python -m aios validate --agent developer
python -m aios validate --workflow l2_review
python -m aios validate .ai/templates/activation.v1.template.yaml
python -m aios load-context .ai/rules/rules.md --json --summary-only
python -m compileall -q src/aios aios
git diff --check
```
