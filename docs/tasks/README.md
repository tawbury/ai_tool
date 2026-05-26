# `.ai OS` 남은 작업 태스크 인덱스

> 이 폴더는 `docs/roadmap/static_validation_and_execution_readiness_roadmap.md`를 실행 가능한 순차 작업으로 분리한 human context이다. 런타임 계약이 아니며 `.ai/rules/`를 대체하지 않는다.

## 목적

남은 작업을 micro prompt가 아니라 phase별 task bundle로 진행하기 위해 작업 단위를 분리한다. 각 task 문서는 독립 실행 요청으로 사용할 수 있도록 목적, 선행 조건, 허용 범위, 금지 범위, 산출물, 검증 명령을 포함한다.

## 진행 순서

1. `phase-08-static-validation-completion/01-sandbox-trace-validate-integration.md`
2. `phase-08-static-validation-completion/02-sandbox-trace-output-stabilization.md`
3. `phase-08-static-validation-completion/03-sandbox-trace-rule-promotion-audit.md`
4. `phase-08-static-validation-completion/04-sandbox-trace-rule-promotion.md`
5. `phase-08-static-validation-completion/05-static-validation-surface-completion-audit.md`
6. `phase-09-execution-readiness/01-execution-readiness-audit.md`
7. `phase-09-execution-readiness/02-execution-architecture-approval.md`
8. `phase-10-execution-prototype-planning/01-execution-prototype-planning.md`

## 공통 차단 범위

아래 작업은 모든 task에서 명시적으로 차단된다. 단, 후속 phase에서 별도 승인 문서와 명시 요청이 생기기 전까지 구현하지 않는다.

- sandbox launcher
- subprocess execution
- provider execution
- replay execution
- generated content
- snapshot update
- sync apply/mutation
- rollback execution
- dynamic loading
- registry/discovery
- adapter execution
- manifest persistence
- transaction log persistence
- marker insertion, repair, delete
- source mutation
- target mutation

## 운영 원칙

- 각 task는 순서대로 진행한다.
- validate integration은 output stabilization보다 먼저 진행한다.
- output stabilization은 rule promotion audit보다 먼저 진행한다.
- rule promotion audit가 명시적으로 권장한 경우에만 rule promotion을 진행한다.
- static validation surface completion audit 전에는 execution readiness audit로 넘어가지 않는다.
- execution readiness audit와 architecture approval 전에는 execution prototype planning을 시작하지 않는다.
