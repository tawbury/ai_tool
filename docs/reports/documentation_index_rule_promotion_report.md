# Documentation index 규칙 승격 보고서

## 개요

Phase 6-8 문서 색인이 생성된 이후, future plan/report 작성 시 색인 유지보수를 고려하도록 runtime-facing documentation governance rule에 짧은 규칙을 승격했다.

이번 작업은 문서 거버넌스 규칙과 보고서만 변경했다. 런타임 코드, 자동 색인 로직, 자동 docs loading은 추가하지 않았다.

## 변경 사항

### `.ai/rules/operations/documentation-governance.rules.md`

다음 내용을 추가했다.

- `docs/index/`는 summary-first human context이며 runtime contract가 아님.
- `.ai/rules/`가 canonical runtime authority임.
- 새 `docs/plan/*` 또는 `docs/reports/*` 산출물은 `docs/index/document_status_registry.md` entry 필요 여부를 고려해야 함.
- phase-level 또는 runtime-impacting work는 `docs/index/phase_6_8_summary.md` 또는 future phase summary 갱신 필요 여부를 고려해야 함.
- runtime-facing behavior change는 `docs/index/current_runtime_context.md` 갱신 필요 여부를 고려해야 함.
- index maintenance는 docs index를 always-load runtime contract로 만들면 안 됨.
- index maintenance는 automatic docs loading을 추가하면 안 됨.

### `.ai/rules/rules.md`

Documentation governance section에 `docs/index/`의 역할을 짧게 추가했다.

- `docs/index/`는 summary-first navigation과 document status context임.
- Indexes are not runtime contracts.

### `.ai/rules/operations/README.md`

`documentation-governance.rules.md` 설명에 summary index maintenance와 runtime consumption limits를 추가했다.

## 유지한 경계

다음 경계를 유지했다.

- `.ai/rules/`가 canonical runtime authority다.
- `docs/index/`는 human context다.
- Index는 always-load runtime contract가 아니다.
- Runtime loader나 validator가 docs index를 자동 소비하도록 바꾸지 않았다.
- 계획서/보고서 자동 색인 생성 로직을 추가하지 않았다.

## 변경하지 않은 항목

이번 작업은 다음을 수행하지 않았다.

- runtime code 변경
- 파일 이동
- 파일 삭제
- automatic indexing logic 구현
- automatic docs loading 구현
- semantic loader behavior 변경
- activation behavior 변경

## 검증

요청된 검증:

- `python -m aios inspect`
- `python -m aios validate`
- `git diff --check`
- `git diff --cached --check`

## 결론

문서 색인은 계속 human context로 유지된다. 다만 앞으로 새로운 계획서와 보고서를 만들 때 색인 갱신 여부를 명시적으로 고려해야 하므로, Phase 6-8 이후 문서 sprawl과 stale index 위험을 줄일 수 있다.
