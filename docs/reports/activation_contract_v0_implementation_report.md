# Activation Contract v0 구현 보고서

## 1. 작업 요약

`.ai OS`의 첫 번째 최소 runtime activation contract 계층을 구현했다.

구현 범위:

- `src/aios/activation.py`
- `python -m aios activation <path>`
- `python -m aios activation <path> --json`
- `python -m aios activation <path> --summary-only`
- `.ai/templates/activation.template.yaml`

유지한 제약:

- read-only only
- sync 없음
- manifest 없음
- adapter generation 없음
- orchestration 없음
- worker execution 없음
- workflow execution 없음
- auto-fix 없음

## 2. Activation Model

지원하는 최소 schema:

```yaml
schema_version: aios.activation.v0
active_set:
  agents:
    - developer
  skills:
    - requirements_analysis
  workflows:
    - l2_review
  validators:
    - developer_skill_validator
profiles:
  default_loader: minimal-worker
```

필드:

- `schema_version`
- `active_set.agents`
- `active_set.skills`
- `active_set.workflows`
- `active_set.validators`
- `profiles.default_loader`

## 3. YAML 처리 범위

외부 YAML dependency는 추가하지 않았다.

지원하는 lightweight YAML subset:

- top-level scalar
- top-level section
- section 내부 scalar
- section 내부 list
- inline list 일부
- `#` comment 제거

지원하지 않는 범위:

- anchor/alias
- nested object list
- multiline string
- complex YAML typing
- full YAML schema validation

## 4. Inventory 통합

activation reference는 inventory와 대조한다.

지원하는 reference 방식:

- inventory item `name`
- inventory item `canonical_path`
- inventory item `relative_path`
- frontmatter `name`

대상 type mapping:

| activation field | inventory type |
|---|---|
| `active_set.agents` | `agent` |
| `active_set.skills` | `skill` |
| `active_set.workflows` | `workflow` |
| `active_set.validators` | `validator` |

알 수 없는 reference는 `unknown_activation_reference` error로 보고한다.

## 5. Semantic Loader Profile과의 관계

`profiles.default_loader`는 semantic loader profile 이름을 참조한다.

현재 허용되는 값은 `aios load-context`가 지원하는 profile과 같다.

- `minimal-worker`
- `reviewer`
- `strategist`
- `validation-runtime`

activation v0는 profile을 실제로 load하지 않는다. 단지 activation contract가 어떤 semantic loader profile을 기본값으로 요구하는지 검증한다.

## 6. Future Sync Selection과의 차이

activation은 runtime selection contract다.

activation이 하는 일:

- 어떤 agent/skill/workflow/validator가 활성 set에 포함되는지 선언
- 선언된 reference가 현재 `.ai/` inventory에 존재하는지 검증
- 기본 semantic loader profile이 유효한지 검증

activation이 하지 않는 일:

- 파일 복사
- sync target 선택
- manifest 작성
- adapter 생성
- managed block 삽입
- drift detection
- workflow 실행
- worker dispatch

따라서 activation은 future sync selection의 입력 후보가 될 수 있지만, 그 자체가 physical sync 정책은 아니다.

## 7. CLI 출력

Human summary 예시:

```text
AIOS Activation v0
Status: pass
Summary: 0 error, 0 warning, 0 info, 6/6 references resolved
Inactive Counts:
- agent: 4
- skill: 99
- workflow: 8
- validator: 27
```

JSON schema:

```json
{
  "schema_version": "aios.activation.result.v0",
  "status": "pass|warn|fail",
  "root": "...",
  "path": "...",
  "summary": {},
  "issues": [],
  "activation": {},
  "references": []
}
```

`--summary-only`는 `activation`과 `references`를 생략한다.

## 8. 검증 결과

### `python -m aios activation .ai/templates/activation.template.yaml`

결과:

- 종료 코드: `0`
- 상태: `pass`
- references: `6/6 resolved`
- missing references: `0`

### `python -m aios activation .ai/templates/activation.template.yaml --json`

결과:

- 종료 코드: `0`
- 상태: `pass`
- schema_version: `aios.activation.result.v0`
- activation body와 resolved references 포함

### `python -m aios inventory --summary-only`

결과:

- 종료 코드: `0`
- 상태: `pass`
- total: `156`
- skill: `101`

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
- `src/aios/cli.py`의 LF/CRLF 경고는 출력되었으나 diff check 실패는 아님

## 9. 의도적으로 미룬 항목

- activation file 자동 생성
- activation file auto-fix
- activation 기반 semantic context loading
- activation 기반 sync target selection
- manifest generation
- adapter generation
- orchestration
- worker dispatch
- workflow execution
- full YAML parser dependency

## 10. 권장 다음 작업

- `aios validate`에서 activation file 검증 target을 추가할지 검토
- activation schema를 `.ai/rules/operations` runtime-facing rule로 승격할지 검토
- activation과 semantic loader profile의 상세 contract 문서화
- agent registry / validator registry와 activation의 관계 설계
