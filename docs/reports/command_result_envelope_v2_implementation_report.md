# 명령 결과 엔벌로프 v2 구현 보고서

## 개요

AIOS 런타임 명령에 opt-in JSON 엔벌로프 v2 출력을 추가했다. 기존 JSON 출력은 기본값으로 유지하고, 사용자가 `--json --envelope-v2`를 함께 지정한 경우에만 통합 결과 형식으로 감싼다.

## 구현 범위

- `src/aios/envelope.py`를 추가해 공통 엔벌로프 생성 로직을 분리했다.
- 엔벌로프 스키마 버전은 `aios.command_result.v2`로 고정했다.
- `warning` 상태는 v2 표준 상태인 `warn`으로 정규화했다.
- 공통 필드는 `schema_version`, `command`, `status`, `root`, `target`, `summary`, `messages`, `payload`, `meta`로 구성했다.
- `inspect`, `inventory`, `validate`, `activation`, `load-context` 명령에 `--envelope-v2` 옵션을 추가했다.
- `--envelope-v2`는 `--json`과 함께 사용할 때만 허용하며, 단독 사용 시 명확한 오류를 출력하고 종료 코드 `2`를 반환한다.

## 메시지 및 페이로드 매핑

- `inspect`는 기존 `checks`를 `messages`와 `payload.checks`로 매핑한다.
- `inventory`는 메시지를 비워 두고 `payload.items`에 인벤토리 항목을 둔다.
- `validate`는 기존 `results`, 또는 summary-only 출력의 `errors`, `warnings`, `info` 항목을 `messages`로 정규화하고 `payload.results`를 유지한다.
- `activation`은 `issues`를 `messages`로 정규화하고 `payload.activation`, `payload.references`를 제공한다.
- `load-context`는 `warnings`를 `messages`로 정규화하고 `payload.chunks`, `payload.excluded`, `payload.budget`을 제공한다.

## 호환성

`--envelope-v2`를 지정하지 않은 JSON 출력은 기존 스키마를 그대로 유지한다. `--summary-only`, `--no-content`, `--include-pass` 옵션의 기존 동작도 변경하지 않았다.

엔벌로프의 `meta`에는 기존 스키마와의 연결을 위해 `legacy_schema_version`, `legacy_status`, `summary_only`를 포함했다. `load-context`에는 `include_content`를 추가하고, summary-only로 생략된 페이로드가 있을 경우 `omitted_payload`에 생략 개수를 기록한다.

## 비목표

이번 변경은 출력 형식의 opt-in 래핑만 구현한다. 기존 명령의 기본 JSON 스키마 전환, 동기화, 매니페스트 생성, 어댑터 생성, 오케스트레이션, 워커 실행, 워크플로 실행, 레지스트리 파서, `.ai/registry/`, 자동 수정, 소스 파일 변형은 구현하지 않았다.

## 검증

다음 명령으로 구현을 검증했다.

- `python -m aios inspect --json --envelope-v2`
- `python -m aios inventory --json --envelope-v2`
- `python -m aios validate --json --envelope-v2`
- `python -m aios activation .ai/templates/activation.v1.template.yaml --json --envelope-v2`
- `python -m aios load-context .ai/rules/rules.md --json --envelope-v2`
- `python -m aios validate --envelope-v2`
- `python -m aios inspect --json`
- `python -m aios validate --json --summary-only`
- `python -m aios load-context .ai/rules/rules.md --json --summary-only`

`python -m aios validate --envelope-v2`는 `$LASTEXITCODE` 기준 종료 코드 `2`를 반환하는 것을 확인했다.
