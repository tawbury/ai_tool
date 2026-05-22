# AIOS Inventory v0 구현 보고서

## 1. 작업 요약

`.ai OS`의 향후 런타임 확장을 위한 읽기 전용 repository inventory primitive를 추가했다.

구현 범위:

- `src/aios/inventory.py` 추가
- `python -m aios inventory` CLI 추가
- JSON 출력 지원
- 타입 필터 지원
- summary-only 출력 지원
- 단일 런타임 실행 내 lightweight cache 지원

범위 밖으로 유지한 항목:

- sync
- manifest
- orchestration
- worker execution
- adapter generation
- auto-fix
- persistent cache
- inspect/validate의 전체 inventory migration

## 2. 구현 파일

추가:

- `src/aios/inventory.py`
- `docs/reports/aios_inventory_v0_implementation_report.md`

수정:

- `src/aios/cli.py`

참고:

- 이전 작업의 `aios validate` v1 출력 사용성 개선 변경이 작업 트리에 함께 존재한다.
- 이번 inventory 구현은 해당 변경을 되돌리거나 변경하지 않았다.

## 3. Inventory 모델

`InventoryItem` 필드:

- `type`
- `name`
- `path`
- `canonical_path`
- `relative_path`
- `tags`
- `metadata`

`RepositoryInventory` 필드:

- `root`
- `items`

JSON 출력 schema:

```json
{
  "schema_version": "aios.inventory.v0",
  "status": "pass",
  "root": "...",
  "summary": {
    "total": 0,
    "counts": {
      "agent": 0,
      "command": 0,
      "rule": 0,
      "skill": 0,
      "validator": 0,
      "workflow": 0
    }
  },
  "items": []
}
```

## 4. Discovery 함수

구현된 함수:

- `discover_agents(root)`
- `discover_skills(root)`
- `discover_workflows(root)`
- `discover_rules(root)`
- `discover_validators(root)`
- `discover_commands(root)`
- `build_inventory(root)`

Discovery 범위:

| Type | Discovery pattern |
|---|---|
| agent | `.ai/agents/*.agent.md` |
| skill | `.ai/skills/**/*.skill.md` |
| workflow | `.ai/workflows/*.workflow.md` |
| validator | `.ai/validators/**/*.md` |
| rule | `.ai/rules/**/*.md` |
| command | `.ai/commands/**/*.command.md` |

## 5. 공유 primitive 재사용

재사용한 기존 primitive:

- `frontmatter.extract_frontmatter`
- `frontmatter.as_list`
- `filesystem.rel_path`
- `filesystem.read_text`

Frontmatter가 있는 파일은 metadata를 최소 구조로 포함한다. `tags` frontmatter가 있으면 list로 정규화해 `tags` 필드에 반영한다.

## 6. Cache 정책

캐시는 프로세스 내부 메모리에만 존재한다.

- persistent cache 없음
- 파일 저장 없음
- manifest 없음
- sync 상태 추적 없음

Cache key:

- `root.resolve()`
- inventory item type

## 7. CLI

추가된 명령:

```bash
python -m aios inventory
python -m aios inventory --json
python -m aios inventory --type skill
python -m aios inventory --summary-only
```

지원 type:

- `agent`
- `skill`
- `workflow`
- `validator`
- `rule`
- `command`

## 8. 검증 결과

### `python -m aios inventory`

결과:

- 종료 코드: `0`
- 상태: `pass`
- total: `156`

Counts:

- agent: `6`
- command: `1`
- rule: `11`
- skill: `101`
- validator: `28`
- workflow: `9`

### `python -m aios inventory --json`

결과:

- 종료 코드: `0`
- schema_version: `aios.inventory.v0`
- items 배열 포함
- frontmatter metadata 포함

### `python -m aios inventory --type skill --summary-only`

결과:

- 종료 코드: `0`
- total: `101`
- skill count: `101`

### `python -m aios inspect`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 fail, 0 warning, 2 info, 308 pass`

### `python -m aios validate`

결과:

- 종료 코드: `0`
- 상태: `pass`
- 요약: `0 error, 0 warning, 3 info`

### `python -m compileall -q src/aios aios`

결과:

- 종료 코드: `0`
- 컴파일 성공
- 생성된 `__pycache__` 디렉터리는 제거했다.

### `git diff --check`

결과:

- 종료 코드: `0`
- 공백 오류 없음
- 변경 파일의 LF/CRLF 경고는 출력되었으나 diff check 실패는 아님

## 9. 알려진 제한

- inspect/validate는 아직 inventory layer로 전체 migration하지 않았다.
- workflow inventory는 `.workflow.md` 파일만 포함한다.
- command inventory는 `.command.md` 파일만 포함한다.
- validator/rule inventory에는 README 문서도 포함된다.
- metadata는 lightweight frontmatter parser 결과만 포함하며 YAML 전체 파싱은 하지 않는다.
- cache invalidation은 프로세스 단위 실행 종료로 처리한다.

## 10. 권장 다음 작업

P1 후보:

- inspect의 agent/skill/workflow inventory 계산을 `inventory.py`로 점진 이전
- validate target discovery를 `inventory.py` 기반으로 점진 이전
- `--type` 복수 필터 또는 comma-separated filter 검토
- `metadata` 포함 여부를 제어하는 `--no-metadata` 옵션 검토

P2 후보:

- inventory item에 semantic layer summary 추가
- inventory item에 reference summary 추가
- command/result envelope 통합 계획에 inventory schema 포함
