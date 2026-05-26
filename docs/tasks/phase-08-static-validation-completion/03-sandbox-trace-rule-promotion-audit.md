# Task 03: Sandbox trace rule promotion audit

## 목적

sandbox trace validation behavior가 runtime governance rules로 승격될 만큼 안정적인지 감사한다. 이 task는 감사만 수행하며 `.ai/rules`를 수정하지 않는다.

## 선행 조건

- Task 02 완료
- sandbox trace output contract report 존재
- native JSON/envelope v2 output contract tests 안정화

## 허용 범위

- `.ai/rules/operations/validation.rules.md` 검토
- `.ai/rules/operations/sync.rules.md` 검토
- sandbox trace validate reports 검토
- promotion target 결정
- 승격할 내용과 human-context-only 내용을 구분
- 병렬화/묶음 진행 가능성 평가
- audit report 작성
- 필요한 docs index의 간결한 갱신

## 금지 범위

- `.ai/rules` 수정
- runtime code 수정
- tests/fixtures 수정
- execution behavior 구현

## 산출물

- `docs/reports/sandbox_trace_rule_promotion_audit.md`

## 검증 명령

```powershell
git diff --check
git diff --cached --check
```

## 요청 문구

```text
Audit sandbox trace validation rule promotion for `.ai OS` and commit the result.

Scope:
- Decide whether `aios validate <sandbox-trace.json>` should be promoted into runtime governance rules.
- Recommend promotion targets and exact minimal rule changes if promotion is appropriate.
- Write `docs/reports/sandbox_trace_rule_promotion_audit.md`.

Do not modify `.ai/rules`, runtime code, fixtures, or tests in this task.
```

## 다음 task

`04-sandbox-trace-rule-promotion.md`
