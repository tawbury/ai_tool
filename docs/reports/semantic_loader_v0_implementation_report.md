# 시맨틱 로더 v0 구현 보고서

## 1. 작업 요약

read-only `aios load-context` v0를 구현했다.

이번 구현은 Markdown 파일에서 시맨틱 레이어를 추출하고, 기본 제외 정책을 적용한 뒤 trace/provenance 정보를 출력하는 최소 기능만 포함한다.

구현하지 않은 것:

- orchestration
- worker execution
- sync
- manifest
- adapter generation
- auto-fix

## 2. 구현 파일

| 파일 | 내용 |
|---|---|
| `src/aios/semantic_loader/__init__.py` | 시맨틱 로더 패키지 export |
| `src/aios/semantic_loader/models.py` | `LoaderInput`, `ContextBundle`, chunk/excluded/warning 모델 |
| `src/aios/semantic_loader/sections.py` | governance annotation boundary, 표준 heading, legacy heading 추출 |
| `src/aios/semantic_loader/loader.py` | 파일 로딩, 레이어 필터링, trace/provenance bundle 생성 |
| `src/aios/cli.py` | `load-context` CLI 명령 추가 |

## 3. 구현 기능

### Annotation boundary parser

지원 형식:

```markdown
<!-- ai-governance:start <layer> v1 -->
...
<!-- ai-governance:end -->
```

추출된 boundary는 `confidence: high`, `extraction_method: annotation-boundary`로 기록된다.

### Standard heading fallback

지원 heading:

- `## Executable Contract`
- `## Structural Rules`
- `## Runtime Policy`
- `## Human Review Guidance`
- `## Review Criteria`
- `## Philosophy`
- `## Examples`

### Legacy section fallback

지원 legacy heading:

- `Validation Rules`
- `Input/Output`
- `Execution Logic`
- `Constraints`
- `Quality Standards`
- `Performance Metrics`

### Rules file fallback

현재 `.ai/rules/*.md`는 annotation standard가 아직 적용되지 않은 문서가 많다. v0에서는 recognized semantic section이 없고 대상이 `.ai/rules/` 파일이면 전체 문서를 `runtime_policy`로 추출한다.

이 fallback은 warning과 `rules-file-fallback` provenance로 표시된다.

### Exclusion policy

기본 profile인 `minimal-worker`는 다음 레이어를 제외한다.

- `examples`
- `philosophy`
- `performance_metrics`

제외된 레이어는 silent drop하지 않고 `excluded` 목록에 기록한다.

## 4. CLI

추가 명령:

```powershell
python -m aios load-context <path>
python -m aios load-context <path> --profile minimal-worker
python -m aios load-context <path> --json
```

human 출력은 summary, loaded chunks, excluded layers, warnings를 보여준다.

JSON 출력은 다음 최상위 필드를 포함한다.

- `schema_version`
- `status`
- `root`
- `profile`
- `target`
- `summary`
- `chunks`
- `excluded`
- `warnings`

## 5. 검증 결과

### `python -m aios load-context .ai/rules/rules.md`

결과 요약:

```text
AIOS Semantic Loader v0
Status: warning
Summary: 1 chunks, 0 excluded, 1 warnings
Loaded Chunks:
- runtime_policy [.ai/rules/rules.md:1-173] rules-file-fallback confidence=low
```

warning은 annotation이 아직 없는 rules 파일에 `rules-file-fallback`을 사용했다는 provenance 경고다.

### `python -m aios load-context .ai/rules/operations/documentation-governance.rules.md --json`

결과 요약:

```text
status: warning
chunks: 1
excluded: 0
warnings: 1
semantic_layer: runtime_policy
extraction_method: rules-file-fallback
```

### `python -m aios inspect`

결과:

```text
Status: pass
Summary: 0 fail, 0 warning, 2 info, 308 pass
```

### `git diff --check`

결과:

```text
통과
```

출력에 일부 LF/CRLF 경고가 표시되었지만 exit code는 0이다.

### `python -m compileall -q src/aios aios`

결과:

```text
통과
```

검증 중 생성된 `__pycache__`는 제거했다.

## 6. 알려진 제한

- YAML/frontmatter 기반 activation profile은 아직 지원하지 않는다.
- token budget 처리는 아직 구현하지 않았다.
- annotation이 없는 일반 문서의 fallback은 보수적이다.
- inline 단일 annotation은 아직 지원하지 않는다.
- section summarization은 구현하지 않았다.
- validate runtime과의 직접 연동은 아직 없다.

## 7. 권장 v1 작업

1. `--include-layer`와 `--exclude-layer` 옵션 추가
2. `--summary-only` 또는 `--no-content` JSON 옵션 추가
3. token budget 근사 처리 추가
4. inline annotation 지원
5. activation profile YAML 입력 지원
6. validate runtime에서 semantic loader를 선택적으로 사용
