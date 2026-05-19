# AIOS 참조 정리 보고서

## 1. 개요

현재 `aios inspect` 실패 원인이었던 stale content reference를 정리했다.

작업 범위는 사용자 요청에 따라 다음 두 `.ai` 파일로 제한했다.

- `.ai/skills/_shared/skill_index.md`
- `.ai/workflows/README.md`

소스 코드, agent 파일, validator 파일, sync, adapter generation, manifest 관련 구현은 수정하지 않았다.

## 2. 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `.ai/skills/_shared/skill_index.md` | 존재하지 않는 skill 참조를 현재 존재하는 canonical skill 파일로 교체 |
| `.ai/workflows/README.md` | stale workflow 파일명, archive 예시, `.cursorrules` 링크 정리 |

## 3. 수정한 Stale Reference

### Skill Reference

| 기존 참조 | 변경 참조 | 이유 |
|---|---|---|
| `dev_frontend.skill.md` | `dev_frontend_stack_unified.skill.md` | frontend skill이 unified 파일로 통합되어 있음 |
| `pm_planning.skill.md` | `pm_strategy_unified.skill.md` | PM planning 역할을 현재 PM strategy unified skill로 연결 |
| `product_analytics.skill.md` | `pm_analytics_unified.skill.md` | PM analytics가 unified 파일로 통합되어 있음 |
| `market_research.skill.md` | `research_framework.skill.md` | 독립 PM market research 파일이 없고 shared research framework가 존재함 |
| `pm_roadmap_management.skill.md` | `operational_roadmap_management.skill.md` | roadmap 관리는 shared operational skill로 존재함 |
| `product_growth.skill.md` | `product_retention.skill.md` | 독립 growth 파일이 없고 현재 growth 관련 PM skill은 retention 중심으로 존재함 |
| `product_launch.skill.md` | `product_lifecycle_management.skill.md` | launch는 product lifecycle skill로 흡수되어 있음 |
| `global_product_strategy.skill.md` | `pm_strategy_unified.skill.md` | global strategy 전용 파일이 없고 PM strategy unified skill이 존재함 |
| `data_driven_decision_making.skill.md` | `decision_analysis.skill.md` | data-driven decision 전용 파일이 없고 shared decision analysis skill이 존재함 |
| `user_research.skill.md` | `research_framework.skill.md` | user research 전용 파일이 없고 shared research framework가 존재함 |

### Workflow Reference

| 기존 참조 | 변경 참조 | 이유 |
|---|---|---|
| `l2_review_workflow.md` | `l2_review.workflow.md` | 실제 파일명이 `l2_review.workflow.md`임 |
| `backup/software_development.workflow.md.backup_20260120` | 제거 | 현재 archive 디렉터리가 없고 stale 예시라서 새 디렉터리를 만들지 않고 제거 |
| `[[../.cursorrules]]` | `[[../rules/rules.md]]` | 현재 SSoT rule entrypoint가 `.ai/rules/rules.md`임 |

## 4. Inspect 결과 Before / After

### Before

작업 전 `python -m aios inspect` 결과:

```text
Status: fail
Summary: 13 fail, 1 warning, 2 info, 171 pass
```

주요 실패:

- `.ai/skills/_shared/skill_index.md`의 missing skill reference 10건
- `.ai/workflows/README.md`의 missing workflow reference 3건
- `.ai/workflows/README.md`의 stale `.ai/.cursorrules` warning 1건

### After

작업 후 `python -m aios inspect` 결과:

```text
Status: pass
Summary: 0 fail, 0 warning, 2 info, 184 pass
Inventory: 308 files scanned, 101 skills, 13 workflow files
```

## 5. 남은 Warning / Failure

현재 `aios inspect` 기준 남은 failure와 warning은 없다.

남은 info 항목:

- `src` directory exists.
- `.ai/skills`에서 101개 skill file 발견.

## 6. Validation Results

| 명령 | 결과 |
|---|---|
| `python -m aios inspect` | 통과, exit code 0 |
| `python -m aios inspect --json` | 통과, exit code 0 |
| `git diff --check` | 통과 |

참고:

- `git diff --check` 실행 시 `.ai/skills/_shared/skill_index.md`, `.ai/workflows/README.md`에 대해 Git의 LF/CRLF 변환 경고가 출력되었으나 whitespace error는 없었다.
- 기존 `.ai` 콘텐츠 파일 중 허용된 두 파일만 수정했다.

