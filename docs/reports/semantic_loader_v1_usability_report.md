# 시맨틱 로더 v1 사용성 개선 보고서

## 1. 작업 요약

read-only `aios load-context` v1 사용성 개선을 구현했다.

이번 작업은 semantic layer 선택과 JSON 출력 제어를 개선한 것이며, orchestration, worker execution, sync, manifest, adapter generation, auto-fix는 구현하지 않았다.

## 2. 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `src/aios/semantic_loader/models.py` | `LoaderInput.excluded_layers` 기본값을 empty set으로 수정, profile include/exclude defaults 추가, JSON `summary_only` 지원 |
| `src/aios/semantic_loader/sections.py` | inline annotation parser 추가 |
| `src/aios/semantic_loader/loader.py` | profile include/exclude와 CLI include/exclude 조합 적용 |
| `src/aios/cli.py` | `--include-layer`, `--exclude-layer`, `--no-content`, `--summary-only`, profile validation 추가 |
| `docs/reports/semantic_loader_v1_usability_report.md` | 구현 보고서 추가 |

## 3. 구현 내용

### LoaderInput 기본값 수정

- `LoaderInput.excluded_layers`는 이제 empty set이 기본값이다.
- 기본 제외 레이어는 `PROFILE_EXCLUDED_LAYERS`에서만 온다.
- CLI의 `--exclude-layer`는 profile 기본 제외에 추가된다.
- CLI의 `--include-layer`는 profile 기본 include에 추가되며, 같은 레이어가 profile exclude에 있으면 명시 include가 우선한다.

### CLI 옵션 추가

추가된 옵션:

```powershell
--include-layer <layer>
--exclude-layer <layer>
--no-content
--summary-only
```

`--include-layer`와 `--exclude-layer`는 반복 가능하다.

### Profile 지원

지원 profile:

- `minimal-worker`
- `reviewer`
- `strategist`
- `validation-runtime`

현재 profile 차이는 include/exclude layer defaults에만 있다.

### Profile validation

알 수 없는 profile은 명확한 오류 메시지를 출력하고 exit code 2로 종료한다.

확인 명령:

```powershell
python -m aios load-context .ai/rules/rules.md --profile nope
```

결과:

```text
aios load-context: unknown profile 'nope'. Valid profiles: minimal-worker, reviewer, strategist, validation-runtime
EXIT:2
```

### Inline annotation 지원

지원 형식:

```markdown
<!-- ai-governance:<layer> -->
```

보수적 동작:

- 다음 paragraph, list, table, code block 하나에만 적용한다.
- boundary annotation이 있으면 boundary가 우선한다.
- inline annotation은 `inline-annotation` method와 high confidence로 기록된다.

## 4. 유지된 동작

- annotation boundary는 최우선으로 추출된다.
- standard heading fallback은 medium confidence를 유지한다.
- legacy heading fallback은 low confidence를 유지한다.
- `.ai/rules/*.md`에 대한 rules-file fallback은 유지된다.
- loader는 read-only로 동작한다.

## 5. 검증 결과

### `python -m aios load-context .ai/rules/rules.md`

```text
AIOS Semantic Loader v1
Status: warning
Summary: 1 chunks, 0 excluded, 1 warnings
```

warning은 rules file fallback provenance이며, 현재 `.ai/rules/rules.md`에 governance annotation이 아직 없기 때문에 예상된 결과다.

### `python -m aios load-context .ai/rules/operations/documentation-governance.rules.md --json --no-content`

```text
status: warning
chunks: 1
content: omitted
```

### `python -m aios load-context .ai/rules/operations/documentation-governance.rules.md --json --summary-only`

```text
status: warning
summary only output includes summary and warnings
```

### `python -m aios load-context .ai/rules/operations/documentation-governance.rules.md --profile validation-runtime --json --no-content`

```text
profile: validation-runtime
chunks: 1
semantic_layer: runtime_policy
```

### Inline annotation smoke test

Python inline smoke test로 다음 annotation이 list block 하나를 `review_criteria`로 추출하는 것을 확인했다.

```markdown
<!-- ai-governance:review-criteria -->
- Check one
- Check two
```

### `python -m aios inspect`

```text
Status: pass
Summary: 0 fail, 0 warning, 2 info, 308 pass
```

### `python -m compileall -q src/aios aios`

```text
통과
```

### `git diff --check`

```text
통과
```

LF/CRLF 관련 Git warning이 출력되었지만 `git diff --check` exit code는 0이다.

## 6. 알려진 제한

- token budget handling은 아직 구현하지 않았다.
- activation.yaml 입력은 아직 지원하지 않는다.
- inline annotation은 다음 block 하나만 보수적으로 추출한다.
- profile은 아직 include/exclude defaults만 다르다.
- summary-only는 JSON 출력에서 chunks/excluded를 생략하고 warnings는 유지한다.

## 7. 권장 다음 작업

1. token budget 근사 처리 추가
2. profile별 max chars 정책 추가
3. activation.yaml 입력 지원
4. annotation adoption 이후 rules-file fallback warning 감소
5. `aios validate`에서 semantic loader 선택 사용 검토
