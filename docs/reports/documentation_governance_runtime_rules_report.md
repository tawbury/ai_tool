# 문서 거버넌스 런타임 규칙 반영 보고서

## 1. 작업 요약

문서 거버넌스 명세, ADR, 마이그레이션 계획의 durable runtime-facing 규칙을 `.ai/rules/` 아래에 반영했다.

이번 작업은 문서 거버넌스 규칙의 런타임 소비 경계를 명확히 하기 위한 규칙 추가 작업이며, runtime code, loader, sync, orchestration은 구현하지 않았다.

## 2. 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `.ai/rules/operations/documentation-governance.rules.md` | 문서 taxonomy, authority hierarchy, runtime consumption boundary, promotion rule을 담은 짧은 operation rule 추가 |
| `.ai/rules/rules.md` | Rule Layers, Selective Loading 예시, Documentation Governance 섹션, Migration Map에 operation rule 포인터 추가 |
| `docs/reports/documentation_governance_runtime_rules_report.md` | 작업 결과 보고서 추가 |

## 3. 반영된 런타임 규칙

추가된 operation rule은 다음 내용을 포함한다.

- `spec`, `adr`, `plan`, `audit`, `historical`, `reference` 문서 taxonomy 요약
- `.ai/`를 canonical runtime source of truth로 정의
- `docs/specs/`는 상세 human-readable spec이며 always-load context가 아님을 명시
- `docs/adr/`, `docs/plan/`, `docs/reports/`는 runtime contract가 아님을 명시
- runtime loader와 validator가 plans, reports, ADRs, examples, philosophy, human-review-only criteria를 자동 소비하지 않아야 함을 명시
- audit/plan insight는 `.ai` 또는 active normative spec으로 승격된 뒤에만 runtime rule로 유효하다는 promotion rule 명시

## 4. `.ai/rules/rules.md` 업데이트

글로벌 규칙에는 장문 명세를 복제하지 않고 다음 포인터만 추가했다.

- operations layer 목록에 `documentation-governance.rules.md` 추가
- selective loading 예시에 documentation governance task 추가
- 짧은 `Documentation Governance` 섹션 추가
- migration map에 documentation taxonomy/authority/promotion/runtime boundary 항목 추가

## 5. 검증 결과

### `python -m aios inspect`

결과:

```text
Status: warning
Summary: 0 fail, 2 warning, 2 info, 306 pass
Inventory: 321 files scanned, 101 skills, 13 workflow files
```

남은 경고:

- 기존 `.ai/.cursorrules` stale reference 경고
- 기존 obvious relative Markdown/Obsidian file link 경고

이번 작업으로 새 fail은 발생하지 않았다.

### `git diff --check`

결과:

```text
통과
```

PowerShell 출력에 `.ai/rules/rules.md`의 LF/CRLF 경고가 표시되었지만, `git diff --check` 자체는 exit code 0으로 통과했다.

## 6. 범위 확인

수행하지 않은 작업:

- 기존 docs 이동 없음
- 기존 docs rewrite 없음
- runtime implementation 없음
- loader implementation 없음
- sync/manifest/orchestration 작업 없음

## 7. 후속 권장 작업

1. 필요하면 `.ai/rules/operations/README.md`에 새 operation rule을 navigation 항목으로 추가한다.
2. 별도 작업에서 `aios inspect`의 남은 `.ai/.cursorrules` 및 relative link warning을 정리한다.
3. 향후 semantic loader 구현 시 `documentation-governance.rules.md`를 docs consumption boundary의 우선 source로 사용한다.
