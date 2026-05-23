# Command Result Schema 감사 보고서

## 개요

AIOS runtime command의 현재 JSON result shape를 감사했다. 대상 명령은 `inspect`, `inventory`, `validate`, `activation`, `load-context`이다.

이번 감사는 unified command result envelope v2 설계를 위한 문서 작업이며 runtime code는 수정하지 않았다.

## 감사 명령

```powershell
python -m aios inspect --json --summary-only
python -m aios inventory --json --summary-only
python -m aios validate --json --summary-only
python -m aios activation .ai/templates/activation.v1.template.yaml --json --summary-only
python -m aios load-context .ai/rules/rules.md --json --summary-only
```

## 현재 Shape 요약

| Command | schema_version | command | status | root | target/path | summary | message 계열 | payload 계열 |
|---|---|---|---|---|---|---|---|---|
| `inspect` | 없음 | 없음 | 있음 | 있음 | 없음 | 있음 | `checks` | `checks` |
| `inventory` | `aios.inventory.v0` | 없음 | 있음 | 있음 | 없음 | 있음 | 없음 | `items` |
| `validate` | `aios.validate.result.v0` | 없음 | 있음 | 없음 | `target` | 있음 | `errors`, `warnings`, `info` 또는 `results` | `results` |
| `activation` | `aios.activation.result.v0` | 없음 | 있음 | 있음 | `path` | 있음 | `issues` | `activation`, `references` |
| `load-context` | `aios.semantic_loader.bundle.v0` | 없음 | 있음 | 있음 | `target` | 있음 | `warnings` | `chunks`, `excluded`, `budget` |

## 상세 비교

### `schema_version`

- `inspect`에는 없다.
- `inventory`, `validate`, `activation`, `load-context`에는 있다.
- schema naming convention이 command별로 다르다.

예:

- `aios.inventory.v0`
- `aios.validate.result.v0`
- `aios.activation.result.v0`
- `aios.semantic_loader.bundle.v0`

### `command`

모든 현재 JSON output에 명시적인 `command` field가 없다.

Consumer는 schema version 또는 호출 context로 command를 추론해야 한다.

### `status`

현재 status 값은 통일되어 있지 않다.

- `inspect`: `pass`, `warning`, `fail` 계열을 내부 check에 사용한다.
- `validate`: top-level은 `pass`, `warn`, `fail` convention을 사용한다.
- `load-context`: warning이 있으면 top-level `warning`을 사용한다.
- `inventory`: 현재 항상 `pass`이다.
- `activation`: 현재 `pass`, `warn`, `fail` convention과 가까운 구조이다.

### `root`

- `inspect`, `inventory`, `activation`, `load-context`에는 있다.
- `validate`에는 top-level `root`가 없다.

### `target` 또는 `path`

- `validate`: `target` object를 사용한다.
- `load-context`: `target` string을 사용한다.
- `activation`: `path` string을 사용한다.
- `inspect`, `inventory`: repository 자체를 대상으로 하지만 target field가 없다.

### `summary`

모든 command에 summary가 있지만 내용과 naming이 다르다.

- `inspect`: `files_scanned`, `skills_found`, `workflows_found`, `errors`, `warnings`, `info`, `passes`
- `inventory`: `total`, `counts`
- `validate`: `errors`, `warnings`, `info`, `results`
- `activation`: `errors`, `warnings`, `info`, reference counts, inactive counts
- `load-context`: `chunks`, `excluded`, `warnings`, `chars`

### Messages, Issues, Warnings, Results

Message-like output이 command마다 다르다.

- `inspect`: `checks`
- `validate`: `results`, 또는 summary-only에서 severity group `errors`, `warnings`, `info`
- `activation`: `issues`
- `load-context`: `warnings`
- `inventory`: 현재 message list 없음

Message object field도 통일되어 있지 않다.

- `inspect` check는 `id`, `status`, `message`, `source`, optional details를 사용한다.
- `validate` result는 `validator`, `code`, `severity`, `status`, `message`, optional `path`, `line`, `recommendation`, `details`를 사용한다.
- `activation` issue는 `code`, `severity`, `status`, `message`, optional `field`, `reference`를 사용한다.
- `load-context` warning은 `code`, `message`, `path`만 가진다.

### Payload

Payload성 데이터도 top-level field로 분산되어 있다.

- `inventory.items`
- `activation.activation`
- `activation.references`
- `load-context.chunks`
- `load-context.excluded`
- `load-context.budget`
- `inspect.checks`
- `validate.results`

## 주요 문제

1. Consumer가 command별 parser를 따로 가져야 한다.
2. `warning`과 `warn` status 차이가 있다.
3. message list 이름과 object field가 다르다.
4. `root`, `target`, `path` 위치가 다르다.
5. `summary-only`에서 command별 payload 생략 방식이 다르다.
6. budget처럼 새 공통성 후보 field가 top-level에 직접 추가되고 있다.

## 감사 결론

현재 public JSON shape는 각 command의 발전 단계에 맞춰 안정적으로 동작한다. 따라서 즉시 변경하지 않고 backward compatibility를 유지해야 한다.

다만 future command schema version에서는 공통 envelope가 필요하다. v2 envelope는 top-level에 `schema_version`, `command`, `status`, `root`, `target`, `summary`, `messages`, `payload`, `meta`를 두고, 기존 command-specific data를 payload로 이동하는 방향이 적절하다.
