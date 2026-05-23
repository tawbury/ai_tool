# Hash Normalization and Fixture Policy

## 개요

이 문서는 future `aios sync --dry-run`의 hash normalization 정책과 fixture 기대값을 결정한다. Phase 7 구현 전 gate이며, runtime code를 변경하지 않는다.

현재 시스템은 read-only이다. 이 문서는 hash implementation, sync execution, manifest persistence, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Hash Scope

### Source File Hash

`source_hash`는 manifest entry가 참조하는 source file 또는 source bundle의 현재 content를 검증하기 위한 hash이다.

범위:

- single `source_path`: 해당 파일 전체 content
- future `source_paths`: ordered source bundle content

Phase 7 v0 dry-run에서는 single `source_path` hash를 우선한다.

### Whole Target Hash

`sync_mode: whole-file`에서는 target file 전체 content가 `target_hash` 범위이다.

용도:

- runtime-managed whole-file drift detection
- whole-file create/update candidate 판단

### Managed Block Inner Content Hash

`sync_mode: managed-block` 또는 `mixed-boundary`에서는 marker begin/end line 사이의 inner content만 `target_hash` 범위이다.

범위에서 제외:

- begin marker line
- end marker line

범위에 포함:

- begin/end marker 사이의 모든 content bytes
- inner content의 line endings
- inner content의 trailing newline
- inner content의 leading/trailing whitespace

### Generated Preview Hash

`generated_*_hash`는 future generated preview content의 hash이다.

Phase 7 dry-run planning에서는 preview hash의 shape만 정의한다. Adapter generation이나 content generation은 non-goal이다.

## v0 Hash Policy Decision

`aios.sync_manifest.v0`와 `aios.sync_dry_run.v0`의 hash policy는 다음으로 고정한다.

### Encoding

권장 v0 결정:

- Hash input은 observed UTF-8 bytes이다.
- UTF-8 decoding validation은 별도 validation concern이다.
- BOM이 있으면 bytes에 포함되지만, UTF-8 BOM은 validation warning 또는 error 후보로 보고해야 한다.

### CRLF/LF Normalization

권장 v0 결정:

- CRLF/LF normalization을 하지 않는다.
- LF와 CRLF는 서로 다른 hash를 만든다.
- 같은 semantic content라도 line ending이 다르면 drift로 감지한다.

### Trailing Newline Handling

권장 v0 결정:

- trailing newline을 보존한다.
- trailing newline 유무는 서로 다른 hash를 만든다.
- trailing spaces도 그대로 hash에 포함한다.

### Marker Line Exclusion

권장 v0 결정:

- managed block hash는 begin/end marker lines를 제외한다.
- marker inner content는 observed bytes 기준으로 그대로 hash한다.
- marker metadata 변경은 marker integrity나 metadata comparison concern이며 inner content drift가 아니다.

## Rationale

### Deterministic Drift Detection

Observed bytes 기반 hash는 가장 단순하고 결정적이다.

장점:

- current filesystem state를 정확히 반영한다.
- implicit normalization으로 실제 변경이 숨겨지지 않는다.
- manifest hash와 dry-run hash가 byte-for-byte 비교 가능하다.

### Cross-platform Tradeoff

CRLF/LF normalization을 하지 않으면 Windows와 Unix 간 line ending 차이가 drift로 나타날 수 있다.

그러나 v0에서는 safety를 우선한다.

이유:

- sync는 future mutation으로 이어질 수 있다.
- line ending 변경도 실제 file content drift이다.
- normalization은 편의성이 있지만, 사용자가 의도한 byte-level 변경을 숨길 수 있다.

### Safety over Convenience

v0는 false negative보다 false positive를 선호한다.

- drift가 아닌 것을 drift로 보는 것은 dry-run에서 멈출 수 있다.
- drift인 것을 clean으로 보는 것은 future overwrite 위험을 만든다.

따라서 v0는 automatic normalization을 적용하지 않는다.

## Hash String Format

Hash string format:

```text
sha256:<lowercase-hex>
```

Rules:

- algorithm prefix is required.
- only `sha256` is supported in v0.
- digest must be lowercase hex.
- uppercase hex is schema error or validation warning candidate; v0 recommendation is schema error.
- missing prefix is schema error.

Example:

```json
{
  "source_hash": "sha256:0123456789abcdef"
}
```

## Managed Block Hash Boundary

Given:

```markdown
before
<!-- AIOS:BEGIN managed-block entry_id=entry_example marker_version=0 -->
line 1
line 2
<!-- AIOS:END managed-block entry_id=entry_example marker_version=0 -->
after
```

Hash input for managed block:

```text
line 1
line 2
```

Boundary rules:

- begin marker line is excluded.
- end marker line is excluded.
- bytes between the marker line terminators are included.
- if inner content ends with a newline before the end marker, that newline is included.
- if inner content is empty, hash input is empty bytes.

Parser dependency:

- parser must provide byte span or line span sufficient to extract inner content.
- if marker boundary is invalid, no managed block hash should be used for update candidate.

## Fixture Categories

Future fixture root:

```text
tests/fixtures/sync/hash/
```

Each fixture should include:

- input file
- expected hash policy note
- expected hash string or relation
- expected dry-run effect

### LF File

Fixture:

```text
lf_file.txt
```

Expected:

- hash uses LF bytes exactly.
- status clean only if manifest hash was produced from same LF bytes.

### CRLF File

Fixture:

```text
crlf_file.txt
```

Expected:

- hash uses CRLF bytes exactly.
- hash differs from LF fixture with same semantic lines.

### Same Semantic Content Different Line Endings

Fixtures:

```text
same_content_lf.txt
same_content_crlf.txt
```

Expected:

- hashes differ.
- if manifest expects LF and target is CRLF, dry-run produces `drift-stop`.

### Trailing Newline Difference

Fixtures:

```text
trailing_newline_present.txt
trailing_newline_absent.txt
```

Expected:

- hashes differ.
- trailing newline difference is drift.

### Marker Metadata Changed but Inner Content Same

Fixtures:

```text
marker_metadata_changed_same_inner.md
```

Expected:

- managed block inner content hash is unchanged.
- marker metadata mismatch may be parser conflict if `entry_id` or `marker_version` binding is broken.
- generated_by change alone does not change inner content hash.

### Marker Inner Content Changed

Fixtures:

```text
marker_inner_content_changed.md
```

Expected:

- managed block inner content hash changes.
- if manifest target_hash expects old inner content, dry-run produces `drift-stop`.

### UTF-8 Korean Text

Fixture:

```text
utf8_korean_text.md
```

Expected:

- hash uses UTF-8 bytes.
- Korean text must be handled without lossy decoding.

### UTF-8 Without BOM

Fixture:

```text
utf8_without_bom.md
```

Expected:

- accepted as normal.
- hash uses file bytes.

### UTF-8 With BOM

Fixture:

```text
utf8_with_bom.md
```

Expected:

- v0 recommendation: validation warning for BOM in text target.
- hash includes BOM bytes if hash evaluation proceeds.
- future policy may elevate BOM to schema/runtime validation error for managed targets.

## Interaction with Manifest Schema

Manifest schema uses:

- `source_hash`
- `target_hash`
- future optional `meta.hash_policy`

v0 default hash policy is implicit:

```json
{
  "meta": {
    "hash_policy": {
      "algorithm": "sha256",
      "encoding": "observed-utf8-bytes",
      "line_endings": "preserve",
      "trailing_newline": "preserve",
      "managed_block_marker_lines": "exclude"
    }
  }
}
```

Rules:

- If `meta.hash_policy` is absent, v0 default applies.
- If `meta.hash_policy` conflicts with v0 default, validation should warn or fail depending on future schema revision.
- v0 implementation should not support multiple hash policies unless explicitly designed.

## Interaction with Marker Parser Output

Marker parser must provide a reliable managed block boundary.

Required for hashing:

- begin line
- end line
- content start
- content end
- marker integrity

Rules:

- If marker integrity is not `valid`, managed block hash must not produce update candidate.
- If marker is valid, hash layer extracts inner content according to v0 policy.
- Parser does not normalize content for hash.

## Interaction with Dry-run Result Hashes

Dry-run result hash fields should identify expected and actual values.

Recommended fields:

- `expected_source_hash`
- `actual_source_hash`
- `expected_target_hash`
- `actual_target_hash`
- `expected_managed_block_hash`
- `actual_managed_block_hash`
- `generated_target_hash`
- `generated_managed_block_hash`

Rules:

- actual hashes use v0 policy.
- expected hashes are read from manifest.
- generated hashes use v0 policy over preview bytes.
- hash policy mismatch should be visible in `details` or `meta`.

## Interaction with Drift-stop Policy

Hash mismatch drives drift-stop only after structural validation passes.

Rules:

- invalid manifest hash format -> schema error.
- invalid marker -> parser conflict.
- valid marker + managed block hash mismatch -> `drift-stop`.
- whole-file hash mismatch -> `drift-stop`.
- source hash changed may indicate update candidate only if target remains clean.

## Interaction with Envelope v2

Envelope v2 should preserve hash policy metadata.

Recommended mapping:

- `meta.hash_policy`: v0 hash policy summary
- `payload.results[].hashes`: expected/actual/generated hashes
- `messages[].details.hash_policy`: optional when warning or drift-stop is hash-related

Example message detail:

```json
{
  "code": "target-modified",
  "details": {
    "expected_target_hash": "sha256:<manifest>",
    "actual_target_hash": "sha256:<current>",
    "hash_policy": "observed-utf8-bytes/preserve-line-endings"
  }
}
```

## Future Extension

### `meta.hash_policy`

Future manifests may include explicit hash policy metadata.

Candidate:

```json
{
  "meta": {
    "hash_policy": {
      "version": "aios.hash_policy.v0",
      "algorithm": "sha256",
      "encoding": "observed-utf8-bytes",
      "line_endings": "preserve",
      "trailing_newline": "preserve",
      "managed_block_marker_lines": "exclude"
    }
  }
}
```

### Possible v1 Normalization Mode

Future v1 may introduce:

- normalized text mode
- CRLF/LF normalization
- trailing newline normalization
- explicit binary target handling

Requirements for v1:

- new schema version or explicit compatible hash policy version
- fixtures proving behavior
- migration guidance
- no silent default change from v0

## Explicit Non-goals

This policy does not implement:

- hash implementation
- automatic normalization
- automatic line ending conversion
- BOM removal
- auto-fix
- mutation
- sync apply
- manifest persistence
- transaction log persistence
- rollback execution
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- force
- decommission
- source mutation

## Phase 7 Gate Decision

This document satisfies the hash normalization planning gate.

v0 decision:

- use observed UTF-8 bytes.
- do not normalize CRLF/LF.
- preserve trailing newline and whitespace.
- exclude begin/end marker lines from managed block hash.
- include managed block inner content exactly as observed.

Runtime implementation should not begin until fixtures for these decisions are prepared or included in the Phase 7 implementation task breakdown.
