# aios validate v0 계획

## 1. 목표

`aios validate` v0의 목표는 `.ai OS`의 첫 실행 가능한 검증 계층을 만드는 것이다. 이 명령은 `.ai`를 단일 진실 공급원으로 보고, 파일과 문서가 약속된 구조와 참조 계약을 만족하는지 읽기 전용으로 확인한다.

이 계획은 sync, manifest, adapter generation, orchestration, tmux, worker execution, auto-fix를 포함하지 않는다.

## 2. inspect와 validate의 역할 분리

| 명령 | 책임 | 예시 |
|---|---|---|
| `aios inspect` | 저장소 전체 구조, 참조 무결성, runtime 정책 신호 확인 | stale link, BOM, symlink, root adapter 존재 |
| `aios validate` | 특정 대상이 validator 계약을 만족하는지 확인 | agent frontmatter, skill block, workflow required sections |

`validate`는 inspect의 파일 탐색, Obsidian 링크 추출, frontmatter 파싱, 결과 렌더링 패턴을 재사용할 수 있다. 단, inspect의 전체 저장소 감사 결과를 그대로 validate 결과로 복제하지 않는다.

## 3. 명령 설계

### `aios validate`

저장소 루트 기준 기본 검증을 실행한다.

검증 범위:

- `.ai/validators/validator_index.md` 존재와 링크 무결성
- `.ai/agents/*.agent.md` frontmatter와 참조 경로
- `.ai/skills/**/*.skill.md` 기본 구조
- `.ai/workflows/*.workflow.md` 기본 구조
- validator 문서의 명백한 파일 참조 존재 여부

### `aios validate <path>`

지정 파일 또는 디렉터리만 검증한다.

대상 판별:

| 경로 패턴 | kind | 적용 validator |
|---|---|---|
| `.ai/agents/*.agent.md` | agent | metadata, agent references |
| `.ai/skills/**/*.skill.md` | skill | metadata, skill structure |
| `.ai/workflows/*.workflow.md` | workflow | metadata, workflow structure, validator references |
| `.ai/templates/*.md` | template | metadata optional, structure, references |
| `docs/**/*.md` | document | metadata optional, document structure, language policy warning |

### `aios validate --agent developer`

논리 에이전트 이름을 받아 `.ai/agents/developer.agent.md`를 찾고 관련 참조를 검증한다.

검증 범위:

- agent 파일 존재
- frontmatter 필수 필드
- `domain_rules`, `operation_rules`, `validators` 경로 존재
- agent 본문에서 참조하는 `.skill.md` 파일 존재
- agent별 skill validator가 존재하는지 확인

### `aios validate --workflow xxx`

워크플로우 이름 또는 파일명을 받아 `.ai/workflows/<name>.workflow.md`를 검증한다.

검증 범위:

- workflow 파일 존재
- 파일명 규칙
- 목적, 입력, 단계, 출력, 검증 관련 섹션 존재
- workflow 본문의 validator 링크가 `.ai/validators/`에 존재하는지 확인
- 관련 template 또는 skill 링크가 명백한 경우 존재 확인

## 4. 실행 경계

### v0에서 실행하는 것

| 영역 | 실행 조건 |
|---|---|
| 파일 존재 | 경로가 실제 파일인지 확인 |
| frontmatter | 필수 필드, 빈 값, 리스트 타입 일부 확인 |
| Markdown 구조 | 제목과 필수 섹션 존재 확인 |
| Obsidian 링크 | 명백한 상대 파일 링크 존재 확인 |
| validator index | 표 링크가 실제 validator 파일인지 확인 |
| skill 구조 | `.skill.md` 필수 블록과 종료 마커 확인 |
| agent 구조 | agent metadata와 rule/validator 참조 확인 |
| workflow 구조 | `.workflow.md` 기본 섹션과 참조 확인 |

### v0에서 실행하지 않는 것

| 제외 항목 | 이유 |
|---|---|
| sync | validate의 책임이 아님 |
| manifest 기록 | drift/sync 계층과 혼동됨 |
| adapter generation | runtime 호환 계층 작업 |
| worker execution | orchestration 범위 |
| skill execution | 실행 결과와 품질 평가가 필요 |
| L2 review 자동 판정 | 사람 판단이 필요한 품질 기준 |
| 비즈니스 임팩트 점수 | 도메인 맥락과 승인 필요 |
| YAML full schema validation | v0 이후에 단계적으로 도입 |

## 5. Validator Registry v0

v0 registry는 코드 내부 상수로 시작한다. `.ai` 파일을 새로 만들거나 manifest를 도입하지 않는다.

```text
src/aios/validate/
  __init__.py
  engine.py
  registry.py
  result.py
  targets.py
  validators/
    agent.py
    document.py
    metadata.py
    references.py
    skill.py
    workflow.py
```

초기 registry 항목:

| validator id | source document | target kind | v0 severity |
|---|---|---|---|
| `metadata` | `.ai/validators/meta_validator.md` | agent, skill, workflow, document | error |
| `structure` | `.ai/validators/structure_validator.md` | skill, workflow, document | error |
| `agent` | `.ai/rules/operations/agent.rules.md` | agent | error |
| `skill` | `.ai/validators/skill_validator.md` | skill | error |
| `skill-loading` | `.ai/validators/skill_loading_validator.md` | agent, skill | warning |
| `mapping` | `.ai/validators/_base/mapping_validator.md` | repository, workflow | warning |
| `workflow` | `.ai/workflows/_base/workflow_base.md` | workflow | warning |

## 6. 결과 모델

### Python 모델 초안

```python
@dataclass
class ValidationMessage:
    validator: str
    code: str
    severity: Literal["info", "warning", "error"]
    status: Literal["pass", "warn", "fail"]
    message: str
    path: str | None = None
    line: int | None = None
    recommendation: str | None = None

@dataclass
class ValidationRun:
    schema_version: str
    status: Literal["pass", "warn", "fail"]
    target: dict[str, str]
    summary: dict[str, int]
    results: list[ValidationMessage]
```

### JSON 출력 초안

```json
{
  "schema_version": "aios.validate.result.v0",
  "status": "warn",
  "target": {
    "kind": "agent",
    "path": ".ai/agents/developer.agent.md"
  },
  "summary": {
    "pass": 8,
    "warning": 1,
    "error": 0,
    "info": 0
  },
  "results": []
}
```

## 7. Severity 정책

| 조건 | severity | 이유 |
|---|---|---|
| 대상 파일 없음 | error | validate 대상 계약을 확인할 수 없음 |
| 필수 frontmatter 필드 없음 | error | agent/skill 계약 위반 |
| 참조 rule/validator 파일 없음 | error | 실행 시 로딩 실패 가능 |
| workflow 관련 validator 링크 없음 | warning | 오래된 문서일 수 있고 직접 실행 차단은 과함 |
| docs 언어 정책 의심 | warning | 자동 언어 판별 오판 가능 |
| 사람 검토 전용 validator 스킵 | info | 명시적 미실행 사유 |

Exit code:

- `0`: pass 또는 warning only
- `1`: error가 하나 이상 있음
- `2`: crash 또는 repository root 판별 실패

## 8. 구현 순서

### P0

1. `validate` 하위 패키지와 결과 모델 추가
2. 기존 `cli.py`에 `validate` 서브커맨드 연결
3. target resolver 구현
4. agent validator 구현
5. skill structure validator 구현
6. validator index 참조 검사 구현
7. human/json 출력과 exit code 연결
8. `python -m aios validate`, `python -m aios validate --agent developer`, `python -m aios validate --workflow l2_review` 수동 검증

### P1

1. workflow required section 검사 고도화
2. document type별 validator 추가
3. template validator 추가
4. `--json --summary-only` 지원
5. inspect 결과 재사용 옵션 검토

### P2

1. `.ai/validators/validator_registry.yaml` 도입 검토
2. full YAML schema validation 도입
3. human-review-only validator 결과를 별도 `skipped` 상태로 표현
4. run record 연계 검토
5. validator 문서와 실행 코드의 coverage 매핑 문서화

## 9. v0 테스트 계획

| 테스트 | 명령 | 기대 결과 |
|---|---|---|
| 기본 실행 | `python -m aios validate` | crash 없이 summary 출력 |
| JSON 출력 | `python -m aios validate --json` | `schema_version`, `status`, `summary`, `results` 포함 |
| agent 검증 | `python -m aios validate --agent developer` | developer agent와 참조 경로 검사 |
| workflow 검증 | `python -m aios validate --workflow l2_review` | workflow 구조와 validator 참조 검사 |
| path 검증 | `python -m aios validate .ai/skills/_shared/context_engineering.skill.md` | skill 구조 검사 |
| 실패 fixture | 임시 테스트 fixture에서 필수 필드 제거 | exit code 1 |
| 비파괴 확인 | `git diff --check` | 공백 오류 없음 |

## 10. 구현 시 주의사항

- `.ai` 콘텐츠 파일을 수정하지 않는다.
- validator 문서의 모든 품질 문장을 자동 fail 조건으로 해석하지 않는다.
- `aios inspect`가 이미 담당하는 저장소 전체 정책 검사를 validate에 중복 구현하지 않는다.
- agent/workflow 옵션은 이름과 파일명 모두 수용하되, 모호하면 후보를 출력하고 fail 처리한다.
- v0에서는 warning을 exit code 0으로 유지해 기존 문서 정리 작업을 막지 않는다.

## 11. 다음 Codex 작업 프롬프트

1. "`aios validate` v0를 계획 문서 기준으로 읽기 전용 구현하라. sync, manifest, adapter generation, worker execution은 구현하지 말라."
2. "기존 `aios inspect` 모듈을 재사용해 target resolver와 ValidationResult 모델을 추가하라."
3. "`python -m aios validate`, `python -m aios validate --json`, `python -m aios validate --agent developer`, `python -m aios validate --workflow l2_review`를 검증하고 한국어 구현 보고서를 작성하라."
