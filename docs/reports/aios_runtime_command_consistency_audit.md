# AIOS 런타임 명령 일관성 감사

## 1. 감사 범위

대상 명령:

- `python -m aios inspect`
- `python -m aios load-context`
- `python -m aios validate`

현재 단계의 전제:

- 세 명령은 모두 읽기 전용이어야 한다.
- sync, manifest, adapter generation, orchestration, worker execution, auto-fix는 범위 밖이다.
- `inspect`는 현재 `0 fail, 0 warning` 기준선을 유지한다.

## 2. 명령 책임 매트릭스

| 명령 | 주 책임 | 입력 대상 | 출력 성격 | 실패 기준 | 현재 책임 경계 평가 |
|---|---|---|---|---|---|
| `inspect` | 저장소 구조, 참조 무결성, 호환성 위험 검사 | 저장소 전체 | repository integrity report | 구조 누락, stale reference, BOM, symlink, missing reference | 적절함. 단, 일부 agent frontmatter 검증은 `validate`와 겹침 |
| `load-context` | Markdown 문서에서 semantic layer 추출 | 단일 Markdown 파일 | context bundle / provenance | CLI crash 또는 root/profile 오류. 파일 누락은 warning | 적절함. validation이 아니라 extraction임을 유지해야 함 |
| `validate` | 대상 contract 검증 | 저장소 전체 또는 agent/workflow/path | executable validation result | missing target, missing required contract field/section | 적절함. 단, inspect의 참조 검사와 중복되는 부분이 있음 |

## 3. 스키마 비교

| 항목 | `inspect` | `load-context` | `validate` | 일관성 이슈 |
|---|---|---|---|---|
| schema version | 없음 | `aios.semantic_loader.bundle.v0` | `aios.validate.result.v0` | `inspect`만 schema_version 없음 |
| top-level status | `pass`, `warning`, `fail` | `pass`, `warning` | `pass`, `warn`, `fail` | warning 상태명이 `warning`/`warn`으로 다름 |
| item container | `checks` | `chunks`, `excluded`, `warnings` | `results` | 목적은 다르지만 machine consumer는 별도 파서 필요 |
| item status | `pass`, `info`, `warning`, `fail` | warning item에는 status 없음 | `pass`, `warn`, `fail` | item severity/status 모델이 통일되지 않음 |
| severity field | 없음. `status`가 severity 역할 | warning만 `warnings[]`에 분리 | `severity`: `info`, `warning`, `error` | inspect와 validate의 심각도 표현이 다름 |
| location field | `source` | `path`, `line_start`, `line_end` | `path`, `line` | 파일 위치 표현이 다름 |
| summary fields | inventory 중심 포함 | chunks/excluded/warnings/chars | errors/warnings/info/results | command 특화 summary는 타당하지만 공통 count 이름 필요 |
| compact option | `--summary-only` | `--summary-only`, `--no-content` | 없음 | validate JSON 축약 옵션 없음 |
| JSON crash shape | `{"status":"crash","error":...}` | 동일 CLI boundary | 동일 CLI boundary | crash shape는 CLI에서 공통 처리됨 |

## 4. 종료 코드 비교

| 상황 | `inspect` | `load-context` | `validate` | 평가 |
|---|---:|---:|---:|---|
| pass | `0` | `0` | `0` | 일관됨 |
| warning only | `0` | `0` | `0` | 일관됨 |
| fail/error | `1` | 현재 일반 결과에는 fail 없음 | `1` | load-context는 extraction command라 fail 모델이 약함 |
| unknown command | `2` | `2` | `2` | 일관됨 |
| root 탐지 실패 | `2` | `2` | `2` | 일관됨 |
| unknown profile | 해당 없음 | `2` | 해당 없음 | 적절함 |
| invalid target selector | 해당 없음 | 해당 없음 | `2` | 적절함 |
| missing target | 해당 없음 | `0` + warning | `1` + error | 명령 책임 차이는 있으나 문서화 필요 |

## 5. 중복 및 겹침 발견

### 5.1 Agent frontmatter 검사 중복

`inspect`와 `validate`가 모두 agent frontmatter 필수 필드와 참조 경로 존재 여부를 검사한다.

- `inspect`: repository/reference integrity 관점에서 pass 항목까지 상세히 생성
- `validate`: contract validation 관점에서 error/warning/info만 생성

현재 중복은 허용 가능하지만, 장기적으로는 frontmatter 파싱과 필수 필드 정의가 분리된 공통 모듈로 이동해야 한다.

### 5.2 Markdown reference 검사 중복

다음 로직이 `inspect`와 `validate`에 분산되어 있다.

- Markdown/Obsidian 링크 추출
- 상대 링크 resolve
- validator index 참조 존재 확인
- `.ai/...` 경로 resolve

`markdown_refs.py`는 이미 일부 공통화되어 있지만, resolve 정책은 각 명령에 남아 있다.

### 5.3 Target resolve와 inventory 로직 분산

`inspect`는 저장소 전체 inventory를 직접 계산하고, `validate`는 `validate/targets.py`에서 대상 목록을 계산한다.

- skill inventory: `filesystem.list_skill_files()` 공유
- workflow inventory: inspect는 `list_workflow_files()`를 사용하고 validate는 `.workflow.md`만 직접 glob
- agent inventory: 각자 직접 glob

저장소 inventory는 공통 모듈화할 가치가 있다.

### 5.4 Result model 분리

현재 result model은 세 계열로 분리되어 있다.

- `src/aios/result.py`: inspect 전용
- `src/aios/semantic_loader/models.py`: load-context 전용
- `src/aios/validate/result.py`: validate 전용

명령별 특화 데이터는 유지할 수 있지만, status/severity/location/summary convention은 공통화해야 한다.

## 6. validate가 inspect를 과하게 복제하는가?

결론: 아직은 과한 복제는 아니지만, v1 전에 정리하지 않으면 빠르게 중복이 커질 가능성이 높다.

허용 가능한 중복:

- agent frontmatter 필수 필드 확인
- validator index 참조 존재 확인
- missing target 처리

문제가 될 중복:

- 같은 frontmatter parser가 `inspect.py`와 `validate/validators/agent.py`에 각각 존재
- reference resolve 정책이 `inspect.py`와 `validate/validators/references.py`에 각각 존재
- 필수 agent field 목록이 두 위치에 존재

권장 방향:

- `inspect`는 “저장소가 깨졌는가”를 넓게 확인한다.
- `validate`는 “선택한 대상이 실행 가능한 contract를 만족하는가”를 깊게 확인한다.
- 같은 primitive는 공유하되, 같은 report item을 두 명령이 그대로 반복하지 않도록 한다.

## 7. load-context 결과 convention 평가

`load-context`는 validation command가 아니므로 `chunks`, `excluded`, `warnings` 중심의 JSON shape는 타당하다. 다만 다음은 통일이 필요하다.

- top-level status는 `warning` 대신 공통 status를 따를지 결정 필요
- warning item에도 `severity` 또는 `status`가 있으면 downstream parser가 단순해짐
- missing target이 warning인 이유를 명확히 문서화해야 함
- extraction confidence(`high`, `medium`, `low`)는 validation severity와 별도 개념으로 유지해야 함

권장:

- `load-context`는 `schema_version`, `status`, `summary`, `messages`, `payload` 형태로 감싸고, `chunks`는 payload 성격으로 유지한다.
- `confidence`는 severity로 승격하지 않는다.

## 8. 권장 통합 명령/결과 convention

### 8.1 공통 top-level 형태

향후 모든 command JSON은 다음 공통 envelope를 갖는 것이 좋다.

```json
{
  "schema_version": "aios.<command>.<kind>.vN",
  "command": "inspect|load-context|validate",
  "status": "pass|warn|fail",
  "root": "...",
  "target": {},
  "summary": {},
  "messages": [],
  "payload": {}
}
```

### 8.2 공통 status

권장 status:

- `pass`
- `warn`
- `fail`

현재 `inspect`와 `load-context`의 `warning`은 장기적으로 `warn`으로 맞추는 것이 좋다. 단, 바로 변경하면 호환성이 깨질 수 있으므로 v2 schema에서 전환한다.

### 8.3 공통 severity

권장 severity:

- `info`
- `warning`
- `error`

`status`는 실행 결과 요약이고, `severity`는 개별 message의 심각도로 분리한다.

### 8.4 공통 message item

```json
{
  "code": "missing_target",
  "severity": "error",
  "status": "fail",
  "message": "Target file does not exist.",
  "path": ".ai/...",
  "line": 10,
  "details": {}
}
```

명령별 필드는 `details` 또는 `payload`에 둔다.

## 9. 권장 공유 추상화

| 후보 모듈 | 역할 | 우선순위 |
|---|---|---|
| `src/aios/status.py` | 공통 status/severity mapping, exit code mapping | P0 |
| `src/aios/messages.py` | 공통 diagnostic/message dataclass | P0 |
| `src/aios/frontmatter.py` | 단순 frontmatter 추출/파싱 | P0 |
| `src/aios/references.py` | `.ai` 경로, Markdown/Obsidian 링크 resolve 정책 | P0 |
| `src/aios/inventory.py` | agents, skills, workflows, validators inventory | P1 |
| `src/aios/targets.py` | command 공통 target descriptor | P1 |
| `src/aios/output.py` | human summary formatting helper | P2 |

## 10. P0/P1/P2 리팩터 권장안

### P0: schema/status 중복 방지

- 공통 `pass|warn|fail` status convention을 문서화한다.
- `validate`의 `warn`과 `inspect/load-context`의 `warning` 차이를 다음 schema major 변경에서 해소하도록 ADR 또는 plan에 기록한다.
- frontmatter parser를 공통 모듈로 추출한다.
- agent required field 목록을 단일 상수로 이동한다.
- Markdown/Obsidian relative link resolver를 공통 모듈로 추출한다.

### P1: command envelope 정리

- inspect v2, validate v1, loader bundle v1의 JSON envelope 초안을 정의한다.
- 모든 command에 `schema_version`, `command`, `root`, `target`, `summary`, `messages`, `payload` 개념을 도입한다.
- `validate --summary-only` 또는 `validate --json --summary-only` 옵션을 추가해 출력량을 제어한다.
- `load-context` warning을 공통 message 형식으로 추가하되, 기존 `warnings` 배열은 한동안 유지한다.

### P2: human output 및 registry 정리

- CLI human summary formatter를 command별 함수에서 공통 출력 helper로 일부 이동한다.
- validate registry를 실제 dispatch에 사용하도록 정리한다.
- inspect check id, validate code, loader warning code naming convention을 통합한다.
- command별 contract 문서를 `.ai/rules/operations/validation.rules.md` 또는 별도 runtime spec으로 승격한다.

## 11. 위험 평가

| 위험 | 심각도 | 설명 | 권장 대응 |
|---|---|---|---|
| status naming 불일치 | Medium | `warning`과 `warn`이 섞여 자동 소비자가 별도 처리 필요 | 다음 schema version에서 `warn`으로 통일 |
| frontmatter parser 중복 | Medium | 필드 처리 차이로 inspect pass, validate fail 같은 불일치 발생 가능 | 공통 `frontmatter.py` 추출 |
| reference resolver 중복 | Medium | 상대 링크 기준, `.ai` 경로 처리 차이가 생길 수 있음 | 공통 `references.py` 추출 |
| loader missing target이 warning | Low | validate와 정책이 다르지만 extraction command라 합리적 | 명령 책임 문서화 |
| validate result에 pass item 없음 | Low | 출력은 간결하지만 전체 검증 범위를 추적하기 어려움 | 필요 시 `--include-pass` 옵션 검토 |

## 12. 결론

현재 세 명령의 책임 분리는 대체로 건강하다.

- `inspect`: 저장소/reference integrity
- `load-context`: semantic extraction
- `validate`: executable contract validation

즉시 기능을 추가하기보다, 다음 단계에서는 공통 primitive를 먼저 정리하는 것이 좋다. 특히 frontmatter parsing, reference resolving, status/severity convention은 v1 기능 확장 전에 공통화해야 한다. 다만 지금 당장 JSON schema를 변경하면 기존 보고서와 사용 예시가 흔들릴 수 있으므로, 호환성 있는 v1/v2 전환 계획을 먼저 세우는 편이 안전하다.
