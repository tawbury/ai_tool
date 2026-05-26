# Task 05: Static validation surface completion audit

## 목적

sync, replay, provider, sandbox 계층의 static validation surface가 완료 상태인지 감사한다. 이 task는 execution readiness audit로 넘어갈 수 있는지 판단하는 gate이다.

## 선행 조건

- Task 04 완료 또는 Task 03에서 rule promotion 불필요 판단
- sandbox trace validation governance 상태가 명확해야 함

## 허용 범위

- static validation surface 전체 감사
- 지원 명령과 schema 정리
- output contract 안정화 상태 확인
- rule promotion 상태 확인
- remaining static gaps 식별
- execution readiness audit 진입 가능 여부 결정
- docs index 간결한 갱신

## 금지 범위

- runtime code 변경
- `.ai/rules` 수정
- sandbox/provider/replay execution 설계 승인
- execution implementation

## 산출물

- `docs/reports/static_validation_surface_completion_audit.md`

## 검증 명령

```powershell
git diff --check
git diff --cached --check
```

## 요청 문구

```text
Audit static validation surface completion for `.ai OS` and commit the result.

Scope:
- Determine whether sync/replay/provider/sandbox static validation is complete enough to close the static validation surface phase.
- Identify remaining static gaps, if any.
- Decide whether execution readiness audit can begin.
- Write `docs/reports/static_validation_surface_completion_audit.md`.

Do not implement runtime code, modify `.ai/rules`, or authorize execution behavior.
```

## 다음 task

`../phase-09-execution-readiness/01-execution-readiness-audit.md`
