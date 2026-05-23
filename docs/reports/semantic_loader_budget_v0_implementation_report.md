# Semantic Loader Budget v0 구현 보고서

## 개요

`aios load-context`에 문자 수 기반 budget awareness를 추가했다. 이 변경은 read-only context extraction 범위에 머물며 source file을 수정하지 않는다.

## 변경 사항

- 기존 semantic loader profile별 budget 상수를 추가했다.
- `python -m aios load-context <path> --max-chars <int>` 옵션을 추가했다.
- JSON output에 `budget` object를 추가했다.
- human output에 used, soft, hard, excluded, budget-excluded chunk 정보를 표시하도록 했다.
- profile include/exclude 이후 남은 candidate chunk에 hard budget filtering을 적용했다.
- hard budget 초과 시 lower-priority chunk를 제외하고 `budget_excluded_low_priority` provenance를 `excluded`에 남기도록 했다.
- content truncation은 구현하지 않고 `truncated_chunks`를 `0`으로 보고한다.

## Budget 상수

| Profile | Soft chars | Hard chars |
|---|---:|---:|
| `validation-runtime` | 6,000 | 10,000 |
| `minimal-worker` | 12,000 | 20,000 |
| `reviewer` | 24,000 | 40,000 |
| `strategist` | 36,000 | 60,000 |

`--max-chars`는 profile hard budget을 override한다. Soft budget은 profile 기본값을 유지한다.

## Warning 정책

- `budget_soft_exceeded`: included chars가 profile soft budget을 초과하면 warning으로 보고한다.
- `budget_hard_exceeded`: hard budget 때문에 chunk를 제외하면 warning으로 보고한다.
- `budget_excluded_low_priority`: budget 때문에 제외된 chunk가 있으면 warning record로 보고하고, excluded provenance에도 같은 reason을 남긴다.

`load-context`는 extraction command이므로 budget warning만으로 fail하지 않는다.

## 유지한 경계

다음은 구현하지 않았다.

- live model token counting
- semantic summarization
- content truncation
- activation-driven loading
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
python -m aios load-context .ai/rules/rules.md
python -m aios load-context .ai/rules/rules.md --json --summary-only
python -m aios load-context .ai/rules/rules.md --max-chars 1000 --json
python -m aios load-context .ai/rules/operations/activation.rules.md --profile validation-runtime --json --no-content
python -m aios activation .ai/templates/activation.v1.template.yaml
python -m aios validate .ai/templates/activation.v1.template.yaml
python -m aios inspect
python -m compileall -q src/aios aios
git diff --check
```
