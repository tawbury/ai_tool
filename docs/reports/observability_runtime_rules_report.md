# 관측성 런타임 규칙 승격 보고서

## 개요

런타임 이벤트 및 트레이스 모델 계획을 `.ai` 운영 규칙으로 승격했다. 이번 변경은 문서와 규칙 승격만 수행하며, 이벤트 출력이나 저장 기능은 구현하지 않는다.

## 변경 사항

- `.ai/rules/operations/observability.rules.md`를 새로 추가했다.
- `.ai/rules/rules.md`의 operation rule 목록, selective loading 예시, migration map에 observability 규칙을 추가했다.
- `.ai/rules/operations/README.md`에 observability operation rule 항목을 추가했다.

## 규칙에 반영한 내용

새 runtime-facing 규칙은 다음을 정의한다.

- observability의 목적
- envelope v2와 runtime events의 차이
- 미래 event taxonomy 범주
  - command lifecycle
  - phase lifecycle
  - inventory
  - validation
  - activation
  - context loading
- future event schema 기대 필드
  - `event_id`
  - `trace_id`
  - `parent_trace_id`
  - `timestamp`
  - `event_type`
  - `command`
  - `phase`
  - `status`
  - `severity`
  - `code`
  - `target`
  - `provenance`
  - `details`
- trace model 원칙
- provenance 보존 정책
- 미래 opt-in CLI 후보
  - `--trace`
  - `--emit-events`
  - `--event-format jsonl`
- read-only boundary
- 명시적 non-goals

## 비목표 유지

이번 변경은 다음을 구현하지 않았다.

- event emission
- event persistence
- telemetry 또는 networking
- sync
- manifest generation
- adapter generation
- orchestration
- worker execution 또는 dispatch
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- source mutation

## 검증 계획

요청된 검증 명령을 실행해 runtime-facing 규칙 추가가 기존 read-only 명령과 검증 흐름을 깨지 않는지 확인한다.
