# Activation Validate 통합 보고서

## 개요

`aios validate`가 activation contract YAML 파일을 독립적인 런타임 검증 대상으로 처리하도록 통합했다.

## 변경 사항

- `src/aios/validate/validators/activation.py`를 추가했다.
- `python -m aios validate <activation.yaml>` 경로 입력 시 activation 대상으로 인식하도록 했다.
- 저장소 전체 검증 시 `.ai/**/*.yaml`, `.ai/**/*.yml` 중 activation contract 형태의 파일을 검증 대상으로 포함하도록 했다.
- 기존 activation 런타임 로직을 재사용해 스키마, 인벤토리 참조, semantic loader profile을 검증하도록 했다.
- validate 전용 검증으로 중복 activation reference 경고와 빈 category activation list 정보를 추가했다.
- 검증은 읽기 전용으로 유지했으며 semantic loading, workflow 실행, worker dispatch, auto-fix는 수행하지 않는다.

## Severity 정책

- 잘못된 activation schema: `error`
- 알 수 없는 inventory reference: `error`
- 알 수 없는 semantic loader profile: `error`
- 중복 activation reference: `warning`
- 빈 category activation list: `info`

## 검증 결과

다음 명령을 실행했고 모두 통과했다.

```powershell
python -m aios validate .ai/templates/activation.template.yaml
python -m aios validate .ai/templates/activation.template.yaml --json
python -m aios validate --json --summary-only
python -m aios activation .ai/templates/activation.template.yaml
python -m aios inspect
python -m compileall -q src/aios aios
git diff --check
```

## 비고

이번 변경은 activation contract 검증을 `aios validate`에 연결하는 범위로 제한했다. Sync, manifest, adapter generation, orchestration, worker execution, workflow execution, auto-fix 기능은 구현하지 않았다.
