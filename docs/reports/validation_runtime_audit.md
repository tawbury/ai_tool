# aios validate 런타임 감사 보고서

## 1. 요약

현재 `.ai/validators/`는 실행 가능한 validator 모듈이 아니라 마크다운 기반 검증 기준서 모음이다. `aios inspect` v1이 이미 저장소 구조, 참조 무결성, 런타임 정책 위반을 읽기 전용으로 검사하고 있으므로, `aios validate` v0는 이를 재구현하지 말고 대상별 계약 검증 계층으로 시작하는 것이 적절하다.

v0에서 바로 실행 가능한 영역은 메타데이터, 필수 섹션, 파일 참조, 에이전트 frontmatter, 스킬 블록, 워크플로우 기본 구조처럼 텍스트와 경로만으로 판정 가능한 규칙이다. 반대로 L2 리뷰 품질, 의사결정 타당성, 멘토링 효과, 비즈니스 임팩트, 스킬 실행 품질은 현재 범위에서 자동 실행하면 허위 양성 또는 과잉 판정 위험이 크므로 사람 검토 전용으로 유지해야 한다.

## 2. 현재 Validator 구조

### 파일 구성

| 영역 | 파일 | 현재 성격 |
|---|---|---|
| 인덱스 | `.ai/validators/validator_index.md`, `README.md` | validator 탐색 및 분류 문서 |
| 베이스 | `_base/document_base_validator.md`, `_base/agent_skill_base_validator.md`, `_base/mapping_validator.md`, `_base/skill_self_validator.md` | 공통 기준과 향후 실행 모델의 원형 |
| 기반 validator | `meta_validator.md`, `structure_validator.md`, `skill_validator.md` | v0 실행화 후보 |
| 문서 validator | `task_validator.md`, `report_validator.md`, `anchor_validator.md`, `architecture_validator.md`, `spec_validator.md`, `prd_validator.md`, `decision_validator.md` | 일부 구조 검증 가능, 의미 품질은 사람 검토 |
| 스킬 validator | `skill_loading_validator.md`, `skill_execution_validator.md`, agent별 `*_skill_validator.md` | 참조/구조 일부 가능, 실행 품질은 v0 제외 |
| 고급 validator | `l2_review_validator.md`, `senior_decision_validator.md`, `mentorship_validator.md`, `cross_agent_validator.md` | 대부분 사람 검토 전용 |

### 운영 규칙과의 관계

`.ai/rules/operations/validation.rules.md`는 validator 발견 위치, 공통 검증 순서, 실패 처리 방식을 정의한다. 핵심 절차는 구조, 메타데이터, 언어 정책, 링크/참조, 실행 스크립트, 결과 보고 순서다. 아직 실제 실행 스크립트가 없으므로 `aios validate` v0가 첫 실행 계층이 된다.

### 참조 위치

| 위치 | 참조 형태 | 진단 |
|---|---|---|
| `.ai/agents/*.agent.md` | frontmatter `validators` 필드 | 에이전트 단위 validate 진입점으로 사용 가능 |
| `.ai/rules/operations/agent.rules.md` | `agent-routing` YAML 블록의 validator 경로 | registry 후보이나 v0에서는 읽기 검증만 권장 |
| `.ai/workflows/*.workflow.md` | 관련 validator 링크와 본문 언급 | 워크플로우 validate 후보이나 일부 링크는 상대 경로가 모호함 |
| `.ai/templates/*.md` | 템플릿 검증 안내, validator 링크 | 템플릿 자체 구조 검증 후보 |
| `.ai/commands/implement-design.command.md` | 변경 후 검증 요구 | validate 명령을 호출할 수 있는 향후 소비자 |

## 3. Validator 분류

| Validator | 분류 | 실행 가능성 | v0 권장 처리 |
|---|---|---|---|
| `meta_validator.md` | 구조 | 높음 | frontmatter 또는 `# Meta` 필수 필드 검사 |
| `structure_validator.md` | 구조 | 높음 | 제목, 섹션, 헤더 계층, 빈 섹션 검사 |
| `skill_validator.md` | 구조/의미 일부 | 높음 | `.skill.md` 블록, 파일명, 필수 앵커 검사 |
| `_base/document_base_validator.md` | 구조 | 높음 | 문서 공통 검증 구현 기준으로 사용 |
| `_base/agent_skill_base_validator.md` | 구조/의미 일부 | 중간 | 스킬 블록과 agent별 매트릭스 검사 기준으로 사용 |
| `_base/mapping_validator.md` | 구조/참조 | 높음 | inspect 참조 엔진 재사용, validate에서는 대상 스코프 제한 |
| `_base/skill_self_validator.md` | 런타임 정책/개념 | 낮음 | v0 제외, 실행 후 자체 검증 개념으로 유지 |
| `task_validator.md` | 문서 구조 | 중간 | 필수 섹션 존재 검사만 실행화 |
| `report_validator.md` | 문서 구조 | 중간 | 필수 섹션 존재 검사만 실행화 |
| `anchor_validator.md` | 문서 의미 | 낮음 | 전략 품질은 사람 검토, 필수 섹션만 후보 |
| `architecture_validator.md` | 문서 의미 | 중간 | 구조 검사 가능, 설계 품질은 사람 검토 |
| `spec_validator.md` | 문서 의미 | 중간 | 구조/API 섹션 검사 가능, 기술 타당성은 사람 검토 |
| `prd_validator.md` | 문서 의미 | 중간 | 요구사항/사용자 스토리 섹션 검사 가능 |
| `decision_validator.md` | 문서 의미 | 중간 | 대안/근거 섹션 검사 가능, 결정 품질은 사람 검토 |
| `skill_loading_validator.md` | 런타임 정책/구조 | 중간 | 실제 로딩 성능 제외, 참조와 활성화 기준만 검사 |
| `skill_execution_validator.md` | 워크플로우/런타임 | 낮음 | 스킬 실행을 하지 않으므로 v0 제외 |
| `pm_skill_validator.md` | 스킬 구조 | 중간 | PM 스킬 파일 존재/구조 검사 가능 |
| `developer_skill_validator.md` | 스킬 구조 | 중간 | Developer 스킬 파일 존재/구조 검사 가능 |
| `finance_skill_validator.md` | 스킬 구조 | 중간 | Finance 스킬 파일 존재/구조 검사 가능 |
| `hr_skill_validator.md` | 스킬 구조 | 중간 | HR 스킬 파일 존재/구조 검사 가능 |
| `contents_creator_skill_validator.md` | 스킬 구조 | 중간 | Contents 스킬 파일 존재/구조 검사 가능 |
| `l2_review_validator.md` | 워크플로우/의미 | 낮음 | 사람 검토 전용 |
| `senior_decision_validator.md` | 의미 | 낮음 | 사람 검토 전용 |
| `mentorship_validator.md` | 의미/워크플로우 | 낮음 | 사람 검토 전용 |
| `cross_agent_validator.md` | 워크플로우/정책 | 낮음 | 참조 검사만 후보, 협업 품질은 사람 검토 |

## 4. 실행 가능한 Validator 후보

| 우선순위 | 후보 | 자동 판정 가능한 조건 |
|---|---|---|
| P0 | repository validation bootstrap | repo root 판별, `.ai/validators/validator_index.md` 존재, validator 문서 참조 무결성 |
| P0 | metadata validator | frontmatter 파싱, 필수 필드, 빈 값, 날짜 형식 |
| P0 | structure validator | 제목 존재, 필수 섹션 존재, 헤더 계층, 비어 있는 주요 섹션 |
| P0 | skill structure validator | `.skill.md` 파일명, 필수 블록, `END_BLOCK` 유사 종료 마커, 내부 참조 |
| P0 | agent validator | `.agent.md` frontmatter 필드와 참조 경로 존재 |
| P1 | workflow validator | `.workflow.md` 이름 규칙, 목적/단계/입력/출력/검증 섹션 |
| P1 | document type validator | task/report/prd/spec/architecture/decision별 필수 섹션 |
| P1 | policy validator | 공식 CLI runtime 용어, legacy `.cursorrules` 금지, docs 한국어 정책 일부 |

## 5. 사람 검토 전용 경계

다음 항목은 v0에서 실행하면 자동화 품질보다 오판 비용이 크다.

| 영역 | 제외 이유 | 유지 위치 |
|---|---|---|
| L2 리뷰 완성도 | 문맥, 설계 의도, 품질 판단 필요 | `l2_review_validator.md` |
| senior decision 품질 | 대안 비교와 리스크 판단 필요 | `senior_decision_validator.md` |
| mentorship 효과 | 실제 지식 전달 결과가 필요 | `mentorship_validator.md` |
| cross-agent synergy | 오케스트레이션 실행 로그가 필요 | `cross_agent_validator.md` |
| skill execution quality | 스킬 실행과 산출물 평가가 필요 | `skill_execution_validator.md` |
| 비즈니스 임팩트 점수 | 도메인 기준과 사람 승인 필요 | 각 고급 validator |
| 성능 수치 | 실제 런타임 측정 인프라 필요 | 향후 telemetry 또는 run record |

## 6. 구조적 문제와 리스크

| 심각도 | 리스크 | 설명 | 권장 대응 |
|---|---|---|---|
| 높음 | validator 문서와 실행 기준 혼재 | 같은 파일에 자동 검사 조건과 사람 판단 기준이 함께 있음 | v0 registry에서 실행 가능 rule만 명시 |
| 높음 | agent별 skill validator의 stale 가능성 | validator 문서의 스킬 매트릭스가 실제 `.ai/skills`와 어긋날 수 있음 | v0에서 참조 존재만 warning/fail로 검사 |
| 중간 | `validator_index.md` 인코딩 깨짐 흔적 | dependency map에 깨진 문자가 있어 자동 파싱 신뢰도가 낮음 | v0에서는 표 링크만 추출하고 다이어그램은 무시 |
| 중간 | workflow validator 참조 경로 모호성 | `[[meta_validator.md]]`처럼 현재 파일 기준으로는 경로가 불명확함 | validator 이름은 `.ai/validators/`에서 보정 |
| 중간 | validate와 inspect 책임 중복 | 참조 무결성을 양쪽에서 중복 구현할 수 있음 | validate는 inspect 모듈을 재사용 |
| 낮음 | 과도한 fail 정책 | 초기 문서들이 오래되어 엄격 적용 시 사용성이 낮음 | v0는 새 실행 계층 안정화 전 warning 위주 |

## 7. 권장 실행 모델

`aios validate`는 읽기 전용으로 동작하고, target resolver가 대상 파일 또는 논리 대상을 찾은 뒤 registry에서 validator를 선택한다. validator는 파일을 수정하지 않고 `ValidationResult`만 반환한다.

```text
CLI
  -> target resolver
  -> validator registry
  -> validator engine
  -> result aggregator
  -> human or JSON renderer
```

실행 순서는 다음처럼 단순해야 한다.

1. 저장소 root와 `.ai` SSoT 확인
2. 대상 결정
3. 대상 kind 판별
4. registry에서 적용 validator 선택
5. 각 validator 실행
6. 결과 집계
7. exit code 반환

## 8. 결과 스키마 제안

```json
{
  "schema_version": "aios.validate.result.v0",
  "command": "validate",
  "status": "pass",
  "target": {
    "kind": "repository",
    "path": "."
  },
  "summary": {
    "pass": 12,
    "warning": 0,
    "error": 0,
    "info": 3
  },
  "results": [
    {
      "validator": "structure",
      "code": "missing_required_section",
      "severity": "error",
      "status": "fail",
      "message": "Required section is missing.",
      "path": ".ai/workflows/example.workflow.md",
      "line": 12,
      "recommendation": "Add the required section or update the validator registry."
    }
  ]
}
```

## 9. Severity와 종료 정책

| Severity | 의미 | 기본 상태 |
|---|---|---|
| `info` | 참고 정보 또는 스킵 사유 | pass |
| `warning` | 정리 필요, v0에서 차단하지 않음 | warn |
| `error` | 계약 위반, 대상이 validate 실패 | fail |

집계 상태는 `error`가 하나라도 있으면 `fail`, `warning`만 있으면 `warn`, 그 외는 `pass`다. exit code는 `aios inspect`와 맞춰 `pass`와 `warn`은 0, `fail`은 1, crash 또는 root 판별 실패는 2를 권장한다.

## 10. Registry 구조 제안

v0에서는 별도 manifest를 만들지 않는다. sync/manifest와 혼동을 피하기 위해 코드 내부 registry로 시작한다.

```python
VALIDATORS = {
    "metadata": {
        "targets": ["agent", "skill", "workflow", "document"],
        "source": ".ai/validators/meta_validator.md",
        "severity": "error"
    },
    "structure": {
        "targets": ["skill", "workflow", "document"],
        "source": ".ai/validators/structure_validator.md",
        "severity": "error"
    }
}
```

향후 `.ai/validators/validator_registry.yaml`을 추가할 수 있지만, v0에서는 `.ai` 내용 변경 없이 실행 안정성을 먼저 확인하는 편이 낫다.

## 11. 권장 결론

`aios validate` v0는 inspect보다 좁고 깊은 대상별 계약 검사로 시작해야 한다. 첫 구현은 repository, path, agent, workflow 네 가지 진입점을 제공하되, 실제 worker 실행이나 sync, adapter 생성, manifest 기록은 포함하지 않는다. validator 문서는 실행 근거로 참조하되, 모든 문장과 품질 지표를 자동화 대상으로 보지 않는 것이 안전하다.
