# Context Loading Runtime Rules 반영 보고서

## 개요

semantic loader budget v0 구현 결과를 runtime-facing operation rule로 승격했다.

## 변경 사항

- `.ai/rules/operations/context-loading.rules.md`를 추가했다.
- `.ai/rules/rules.md`의 operation rule 목록, selective loading 예시, migration map에 context loading rule을 연결했다.
- `.ai/rules/operations/README.md`에 context loading rule 설명을 추가했다.

## 반영한 규칙

- semantic loader 목적과 read-only extraction boundary를 명시했다.
- `minimal-worker`, `reviewer`, `strategist`, `validation-runtime` profile을 문서화했다.
- char 기반 budget estimate이며 model API tokenizer counting이 아님을 명시했다.
- soft budget, hard budget, `--max-chars` hard budget override 정책을 문서화했다.
- profile별 budget을 문서화했다.
- `budget_soft_exceeded`, `budget_hard_exceeded`, `budget_excluded_low_priority` 의미를 명시했다.
- profile filtering 후 budget filtering을 적용하고, truncation 전 lower-priority exclusion을 수행하는 정책을 명시했다.
- content truncation은 아직 구현하지 않는다고 명시했다.
- activation v1 loader override는 semantic loader profile 선택이며 context loading이나 worker dispatch가 아님을 명시했다.

## 비목표 유지

다음은 구현하거나 rule에서 허용하지 않았다.

- live model token counting
- semantic summarization
- content truncation
- orchestration
- worker execution
- workflow execution
- sync
- manifest
- adapter generation
- registry parser
- `.ai/registry/`
- auto-fix

## 검증 결과

다음 명령을 실행했고 통과했다.

```powershell
python -m aios load-context .ai/rules/rules.md --json --summary-only
python -m aios load-context .ai/rules/rules.md --max-chars 1000 --json --summary-only
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios validate .ai/templates/activation.v1.template.yaml
python -m aios inspect
python -m aios inventory --summary-only
python -m compileall -q src/aios aios
git diff --check
```
