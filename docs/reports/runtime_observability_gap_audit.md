# 런타임 관측성 격차 감사

## 개요

AIOS 런타임 명령의 현재 출력 구조를 기준으로 미래 이벤트 및 트레이스 모델에 필요한 관측성 격차를 감사했다. 대상 명령은 `inspect`, `inventory`, `validate`, `activation`, `load-context`이다.

이번 감사는 설계 문서 작업이다. 런타임 코드, 이벤트 저장, 네트워크 전송, 텔레메트리, 워크플로 실행, 워커 디스패치, 소스 파일 변형은 구현하지 않았다.

## 현재 관측 가능한 출력

### 공통 명령 결과

`--json --envelope-v2` 출력은 다음 공통 필드를 제공한다.

| 필드 | 현재 의미 |
|---|---|
| `schema_version` | `aios.command_result.v2` |
| `command` | 실행된 명령 이름 |
| `status` | `pass`, `warn`, `fail`의 정규화 상태 |
| `root` | 저장소 루트 |
| `target` | 명령 대상 |
| `summary` | 명령별 요약 |
| `messages` | 정규화된 메시지 목록 |
| `payload` | 명령별 상세 결과 |
| `meta` | 기존 스키마, summary-only 여부, 생략 payload 개수 |

이 구조는 미래 이벤트 모델의 기본 원천으로 사용할 수 있다.

### Inspect

`inspect`는 저장소 구조, 규칙 파일, 에이전트 frontmatter, skill/workflow/validator 참조, symlink, BOM, agent-routing YAML을 점검한다.

현재 관측 가능한 정보:

- 전체 상태
- 파일 스캔 수
- skill/workflow 발견 수
- check별 `id`, `status`, `message`, `source`, `line`, `details`
- summary-only 모드의 비통과 또는 info 메시지

격차:

- 개별 검사 phase의 시작/종료 시점이 없다.
- 전체 검사 순서와 소요 시간이 없다.
- 어떤 inventory primitive가 사용되었는지 trace로 남지 않는다.

### Inventory

`inventory`는 `.ai` 런타임 자산을 discovery layer로 수집한다.

현재 관측 가능한 정보:

- 전체 상태
- item 총량과 type별 count
- item별 type, name, path, canonical_path, relative_path, metadata

격차:

- discovery source별 이벤트가 없다.
- 제외되거나 스캔되지 않은 경로의 이유가 없다.
- inventory item과 이후 activation/validate 참조 사이의 causality가 없다.

### Validate

`validate`는 agent, skill, workflow, validator index, activation target을 검증한다.

현재 관측 가능한 정보:

- 전체 상태
- target kind, label, count
- error/warning/info/result count
- result별 validator, code, severity, status, message, path, line, details
- activation validation 결과가 validate result로 편입됨

격차:

- validator별 시작/완료/실패 이벤트가 없다.
- repository-wide validate에서 target별 처리 순서가 명시되지 않는다.
- warning이 어떤 상위 명령 phase에서 발생했는지 구분하기 어렵다.

### Activation

`activation`은 v0/v1 activation contract를 파싱하고 참조, schema, loader profile, runtime_mode를 검증한다.

현재 관측 가능한 정보:

- activation schema version
- reference 수, resolved/missing reference 수
- inactive_counts
- issue별 code, severity, status, message, field, reference
- reference별 type, reference, resolved, canonical_path

격차:

- missing reference를 별도 event type으로 분리하지 않는다.
- reference resolution이 inventory item과 어떻게 연결되었는지 trace id가 없다.
- schema parsing phase와 semantic validation phase가 구분되지 않는다.

### Load-context

`load-context`는 semantic loader profile을 적용해 context chunk를 추출하고 character budget을 적용한다.

현재 관측 가능한 정보:

- target path와 profile
- chunk 수, excluded 수, warning 수, char 수
- chunk별 path, semantic_layer, line_start, line_end, extraction_method, confidence, chars
- excluded별 path, semantic_layer, line_start, line_end, reason
- warning별 code, message, path
- budget profile, soft/hard/used/excluded chars, budget_excluded_chunks, truncated_chunks

격차:

- chunk 포함/제외 결정이 별도 이벤트로 표현되지 않는다.
- budget exclusion이 warning과 excluded payload로만 분리되어 있고 causal link가 없다.
- provenance는 path와 line 범위로 충분히 시작 가능하지만 trace relationship field가 없다.

## 공통 관측성 격차

| 격차 | 영향 |
|---|---|
| event_id 없음 | 개별 사건을 안정적으로 참조하기 어렵다. |
| timestamp 없음 | 순서와 소요 시간을 계산할 수 없다. |
| trace_id 없음 | 한 명령 안의 phase, message, payload 관계를 연결하기 어렵다. |
| parent_trace_id 없음 | 미래 명령 체인이나 orchestration에서 부모/자식 관계를 표현할 수 없다. |
| phase 없음 | validation, discovery, parsing, budget filtering 같은 처리 단계를 구분하기 어렵다. |
| severity/status/code는 있으나 이벤트 taxonomy가 없음 | 소비자가 command별 message 해석을 반복해야 한다. |
| provenance relationship 없음 | chunk, excluded item, activation reference, inventory item 사이의 관계를 기계적으로 추적하기 어렵다. |
| started/completed/failed 이벤트 없음 | 명령 실패 전후의 부분 진행 정보를 표현할 수 없다. |

## 이벤트 모델에 재사용 가능한 현재 자산

- envelope v2의 `command`, `status`, `root`, `target`, `summary`, `messages`, `payload`, `meta`
- validate result의 `validator`, `code`, `severity`, `status`, `path`, `line`, `details`
- activation reference의 `type`, `reference`, `resolved`, `canonical_path`
- semantic loader chunk/excluded의 `path`, `semantic_layer`, `line_start`, `line_end`, `reason`
- budget object의 `soft_chars`, `hard_chars`, `used_chars`, `excluded_chars`, `budget_excluded_chunks`
- inventory item의 `type`, `name`, `canonical_path`, `relative_path`, `metadata`

## 감사 결론

현재 출력은 최종 결과 관측에는 충분하지만, 처리 흐름 관측에는 부족하다. 미래 이벤트/트레이스 모델은 기존 envelope v2를 깨지 않고, opt-in 이벤트 스트림으로 명령 시작, phase 진행, warning, exclusion, reference resolution, 명령 완료를 표현하는 방향이 적절하다.

이벤트는 저장이나 전송을 전제로 하지 않아야 하며, 현재 read-only boundary를 유지해야 한다.
