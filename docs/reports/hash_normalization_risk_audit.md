# Hash Normalization Risk Audit

## 개요

이 문서는 future `aios sync --dry-run` hash normalization 정책의 위험을 감사한다. 목적은 Phase 7 구현 전에 drift detection의 byte boundary를 명확히 하여 구현 중 임의 normalization이 safety contract를 약화하지 않도록 하는 것이다.

현재 시스템은 read-only이다. 이 감사는 hash implementation, sync execution, manifest persistence, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## 감사 범위

감사 대상:

- observed bytes vs decoded text 선택
- CRLF/LF normalization 위험
- trailing newline normalization 위험
- marker line inclusion 위험
- UTF-8 BOM 처리 위험
- hash string format drift
- fixture coverage 부족
- manifest/dry-run/envelope hash policy 손실

## Risk Matrix

| Risk | 영향 | 완화 |
|---|---|---|
| implicit line ending normalization | 실제 drift를 clean으로 오판 | v0는 line ending preserve |
| trailing newline 무시 | content 차이를 숨김 | v0는 trailing newline preserve |
| marker lines hash 포함 | metadata 변경이 content drift로 오판 | marker lines excluded |
| marker inner content normalization | managed block drift 숨김 | inner content observed bytes hash |
| BOM 자동 제거 | 실제 bytes 변경 숨김 | BOM 포함 hash, validation warning |
| uppercase hash 허용 | consumer 비교 불안정 | lowercase hex required |
| fixture 부족 | OS별 drift 결과 흔들림 | LF/CRLF/trailing/BOM/Korean fixtures |

## Observed Bytes vs Decoded Text Risk

### Risk

Decoded text 기반 hash는 implementation 언어와 decoder 설정에 따라 newline, BOM, invalid sequence 처리가 달라질 수 있다.

### Decision

v0는 observed UTF-8 bytes를 기준으로 한다.

### Residual Risk

텍스트 의미가 같아도 bytes가 다르면 drift로 감지된다. 이는 v0에서 의도한 보수적 behavior이다.

## CRLF/LF Normalization Risk

### Risk

CRLF/LF를 자동 normalize하면 Windows와 Unix 간 편의성은 높아지지만, 실제 file content 변경을 숨길 수 있다.

### Decision

v0는 CRLF/LF normalization을 하지 않는다.

Expected:

- LF hash != CRLF hash.
- line ending change is drift.

### Mitigation

- fixture에 same semantic content with LF/CRLF를 포함한다.
- future v1 normalization mode는 별도 schema/hash policy version으로만 허용한다.

## Trailing Newline Risk

### Risk

trailing newline을 무시하면 file content 차이가 clean으로 보일 수 있다.

### Decision

v0는 trailing newline과 trailing whitespace를 그대로 hash에 포함한다.

Expected:

- file with final newline != file without final newline.

## Marker Line Inclusion Risk

### Risk

begin/end marker lines를 managed block hash에 포함하면 marker metadata 변경이 content drift로 오판된다.

예:

- `generated_by` 변경
- marker formatting 변경
- marker version metadata migration

### Decision

managed block hash는 begin/end marker lines를 제외한다.

### Boundary

Marker line이 identity나 syntax를 깨뜨리면 hash mismatch가 아니라 parser conflict이다.

## Inner Content Normalization Risk

### Risk

marker inner content를 trim하거나 newline normalize하면 managed content 변경이 숨겨질 수 있다.

### Decision

inner content는 observed bytes 그대로 hash한다.

Expected:

- inner content whitespace change is drift.
- inner content line ending change is drift.
- empty inner content hashes empty bytes.

## BOM Risk

### Risk

UTF-8 BOM을 자동 제거하면 actual bytes drift가 숨겨진다. 반대로 BOM을 포함하면 user에게 불편할 수 있다.

### Decision

v0 hash는 BOM bytes를 포함한다.

Validation recommendation:

- UTF-8 BOM in text targets should produce warning at minimum.
- Future managed targets may elevate BOM to validation error.

## Hash Format Risk

### Risk

hash field format이 느슨하면 string comparison과 schema validation이 흔들린다.

### Decision

v0 format:

```text
sha256:<lowercase-hex>
```

Rules:

- algorithm prefix required.
- only `sha256` supported.
- lowercase hex required.
- missing prefix is schema error.
- unsupported algorithm is schema error.

## Fixture Coverage Risk

### Risk

fixture가 happy path만 다루면 hash policy가 implementation 또는 OS에 따라 달라질 수 있다.

### Required Fixtures

- LF file
- CRLF file
- same semantic content different line endings
- trailing newline present/absent
- marker metadata changed but inner content same
- marker inner content changed
- UTF-8 Korean text
- UTF-8 without BOM
- UTF-8 with BOM

Expected:

- LF/CRLF differ.
- trailing newline differs.
- metadata-only marker changes do not change inner content hash.
- inner content changes do change managed block hash.
- Korean UTF-8 bytes hash deterministically.
- BOM is included in hash and reported.

## Manifest Interaction Risk

### Risk

Manifest may not state which hash policy produced stored hashes.

### Mitigation

- v0 default policy is implicit and documented.
- future `meta.hash_policy` can make the policy explicit.
- v0 implementation should not silently support multiple policies.

## Dry-run Result Risk

### Risk

Dry-run result may show only "hash mismatch" without enough context to debug line ending or marker boundary issues.

### Mitigation

- dry-run `hashes` should include expected and actual values.
- result `details` may include hash policy summary.
- envelope v2 meta may include `hash_policy`.

## Drift-stop Risk

### Risk

Hash mismatch can be reported before schema or marker validation, producing misleading drift-stop instead of conflict.

### Mitigation

Evaluation order:

1. manifest schema validation
2. marker parser validation
3. hash calculation
4. drift-stop classification

Invalid marker is conflict, not drift-stop.

## Future Normalization Risk

### Risk

Future v1 may introduce normalization and accidentally change v0 semantics.

### Mitigation

- v0 behavior must remain stable.
- normalization requires explicit `meta.hash_policy` or new schema version.
- fixtures must cover v0 and v1 separately.
- no silent default change.

## Non-goal Risk

Hash policy may be misread as permission to rewrite files into normalized form.

Mitigation:

- automatic normalization is non-goal.
- line ending conversion is non-goal.
- BOM removal is non-goal.
- auto-fix is non-goal.

## 감사 결론

v0 hash policy should prefer safety over convenience.

Decision:

- observed UTF-8 bytes.
- no CRLF/LF normalization.
- preserve trailing newline and whitespace.
- exclude marker begin/end lines.
- include marker inner content exactly.
- include BOM bytes if present, while reporting BOM as validation warning candidate.

This creates conservative drift detection. It may produce more drift-stop results across platforms, but it avoids silently treating changed bytes as clean.
