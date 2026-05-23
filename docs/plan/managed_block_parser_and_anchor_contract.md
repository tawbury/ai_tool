# Managed Block Parser and Anchor Contract

## 개요

이 문서는 future `aios sync --dry-run`의 managed block parser fixture 기대값과 insertion anchor 계약을 정의한다. Phase 7 구현 전 gate이며, runtime code를 변경하지 않는다.

현재 시스템은 read-only이다. 이 문서는 parser implementation, sync execution, manifest persistence, rollback execution, adapter generation, orchestration, worker execution, workflow execution, registry parser, `.ai/registry/`, auto-fix, force, decommission, source mutation을 구현하지 않는다.

## Canonical Managed Block Marker

Managed block marker는 begin marker와 end marker의 line-oriented pair이다.

필수 binding:

- begin marker와 end marker는 같은 `entry_id`를 가져야 한다.
- begin marker와 end marker는 같은 `marker_version`을 가져야 한다.
- marker `entry_id`는 manifest entry `entry_id`와 일치해야 한다.
- marker `marker_version`은 manifest marker metadata의 `marker_version`과 일치해야 한다.

기본 marker version:

```text
0
```

## Supported Marker Styles

### `markdown-html-comment`

Markdown과 HTML comment compatible target의 기본 marker style이다.

```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 generated_by=aios.sync.v0 -->
Managed content.
<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

### `hash-line-comment`

plain text 또는 line comment 기반 target의 후보 marker style이다.

```text
# AIOS:BEGIN managed-block entry_id=entry_plain_text_rules marker_version=0 generated_by=aios.sync.v0
Managed content.
# AIOS:END managed-block entry_id=entry_plain_text_rules marker_version=0
```

### `yaml-line-comment`

YAML target의 후보 marker style이다.

```yaml
# AIOS:BEGIN managed-block entry_id=entry_yaml_rules marker_version=0 generated_by=aios.sync.v0
generated:
  enabled: true
# AIOS:END managed-block entry_id=entry_yaml_rules marker_version=0
```

주의:

- `hash-line-comment`와 `yaml-line-comment`는 syntax는 같을 수 있지만 manifest metadata에서 style intent를 분리한다.
- YAML parser object model로 marker를 판단하면 안 된다. parser는 source text line을 기준으로 marker를 찾아야 한다.

## Parser Responsibilities

Parser는 read-only text analyzer이다.

책임:

- supported marker style별 begin/end marker detection
- marker attribute parsing
- begin/end marker pairing
- line number preservation
- same `entry_id` duplicate marker detection
- missing begin/end detection
- mismatched `entry_id` detection
- mismatched `marker_version` detection
- unsupported marker version detection
- nested marker rejection
- overlapping marker rejection
- malformed marker detection
- Markdown fenced code block exclusion
- orphan marker detection when marker exists without manifest entry

Parser output은 dry-run evaluator가 drift/conflict classification을 수행할 수 있을 만큼 충분해야 한다.

## Parser Non-responsibilities

Parser는 다음을 하지 않는다.

- marker insertion
- marker repair
- marker rewrite
- marker deletion
- sync apply
- file mutation
- manifest mutation
- adapter generation
- target content generation
- hash comparison
- rollback
- decommission

Parser는 marker facts만 보고한다. 어떤 action을 emit할지는 dry-run classifier의 책임이다.

## Canonical Parser Output Model

Parser output 후보:

```json
{
  "target_path": "AGENTS.md",
  "style": "markdown-html-comment",
  "detected_markers": [
    {
      "entry_id": "entry_codex_root_adapter_rules",
      "marker_version": "0",
      "begin_line": 4,
      "end_line": 12,
      "begin_raw": "<!-- AIOS:BEGIN managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->",
      "end_raw": "<!-- AIOS:END managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->",
      "content_line_start": 5,
      "content_line_end": 11,
      "integrity": "valid",
      "problems": [],
      "nested": false,
      "orphan": false
    }
  ],
  "summary": {
    "markers": 1,
    "valid": 1,
    "missing": 0,
    "duplicated": 0,
    "corrupted": 0,
    "orphaned": 0
  }
}
```

### Marker Integrity Values

Allowed `integrity` values:

- `valid`
- `missing`
- `duplicated`
- `corrupted`
- `unsupported-version`
- `not-expected`
- `unknown`

Recommended mapping:

- `valid`: exactly one valid begin/end pair.
- `missing`: expected marker is absent.
- `duplicated`: same `entry_id` has more than one begin/end pair or duplicate begin/end ambiguity.
- `corrupted`: malformed, mismatched, nested, overlapped, or reversed marker.
- `unsupported-version`: marker syntax is parseable but version is unsupported.
- `not-expected`: marker exists but no manifest entry expects it.
- `unknown`: parser could not classify safely.

### Problem Codes

Recommended problem codes:

- `begin-missing`
- `end-missing`
- `begin-duplicated`
- `end-duplicated`
- `entry-id-mismatch`
- `marker-version-mismatch`
- `marker-version-unsupported`
- `marker-malformed`
- `marker-nested`
- `marker-overlapped`
- `marker-reversed`
- `marker-in-code-fence`
- `orphaned-marker`

## Fixture Categories

Future fixture layout should include accept/reject cases. Each fixture should have:

- input file
- manifest entry metadata
- expected parser output JSON
- expected dry-run classification hint

Recommended path:

```text
tests/fixtures/sync/markers/
```

### Valid Marker Pair

Fixture:

```text
valid_markdown_pair.md
valid_hash_line_pair.txt
valid_yaml_line_pair.yaml
```

Expected:

- integrity: `valid`
- begin/end line preserved
- content line span preserved
- no problems
- dry-run may continue to hash comparison

### Missing End Marker

Fixture:

```text
missing_end_marker.md
```

Expected:

- integrity: `corrupted`
- problems: `end-missing`
- dry-run action: `conflict`
- stop reason: `marker-corrupted`

### Duplicate Begin Marker

Fixture:

```text
duplicate_begin_marker.md
```

Expected:

- integrity: `duplicated` or `corrupted`
- problems: `begin-duplicated`
- dry-run action: `conflict`
- stop reason: `marker-duplicated` when duplicate same `entry_id` is unambiguous, otherwise `marker-corrupted`

### Duplicate End Marker

Fixture:

```text
duplicate_end_marker.md
```

Expected:

- integrity: `duplicated` or `corrupted`
- problems: `end-duplicated`
- dry-run action: `conflict`

### Nested Marker

Fixture:

```text
nested_marker.md
```

Expected:

- integrity: `corrupted`
- nested: true
- problems: `marker-nested`
- dry-run action: `conflict`
- stop reason: `marker-corrupted`

### Malformed Marker

Fixture:

```text
malformed_marker.md
```

Expected:

- integrity: `corrupted`
- problems: `marker-malformed`
- dry-run action: `conflict`

### Mismatched `entry_id`

Fixture:

```text
mismatched_entry_id.md
```

Expected:

- integrity: `corrupted`
- problems: `entry-id-mismatch`
- dry-run action: `conflict`

### Unsupported Marker Version

Fixture:

```text
unsupported_marker_version.md
```

Expected:

- integrity: `unsupported-version`
- problems: `marker-version-unsupported`
- dry-run action: `conflict`
- stop reason: `marker-corrupted` or `marker-version-unsupported`

Recommendation:

- Use `marker-version-unsupported` as message code.
- Keep dry-run action as `conflict`.

### Fenced Code Block Marker-looking Text

Fixture:

```text
fenced_code_marker_ignored.md
```

Example:

````markdown
```markdown
<!-- AIOS:BEGIN managed-block entry_id=entry_example marker_version=0 -->
Example only.
<!-- AIOS:END managed-block entry_id=entry_example marker_version=0 -->
```
````

Expected:

- parser must not treat code-fence text as a real marker.
- if no real marker exists and manifest expects one, integrity: `missing`.
- problems may include `marker-in-code-fence` as informational detail.

### Multiple Independent Managed Blocks

Fixture:

```text
multiple_independent_blocks.md
```

Expected:

- different `entry_id` values may each have one valid pair.
- same `entry_id` repeated is duplicate.
- parser output should preserve deterministic order by begin line.

### Unmanaged File

Fixture:

```text
unmanaged_file.md
```

Expected:

- detected_markers: empty
- if manifest does not expect a marker, no parser conflict.
- if manifest expects a marker, integrity: `missing`.

## Insertion Anchor Contract

Insertion anchor is a future dry-run-only signal for first-create candidates. It does not authorize write by itself.

### Anchor Syntax

Recommended anchor syntax uses line-oriented comments and includes an `entry_id`.

Markdown style:

```markdown
<!-- AIOS:ANCHOR managed-block entry_id=entry_codex_root_adapter_rules marker_version=0 -->
```

Hash/YAML line style:

```text
# AIOS:ANCHOR managed-block entry_id=entry_plain_text_rules marker_version=0
```

Rules:

- anchor must be on a single line.
- anchor `entry_id` must match manifest entry `entry_id`.
- anchor `marker_version` must match manifest marker metadata.
- anchor style must be compatible with manifest `marker_style`.

### Allowed Anchor Locations

Allowed:

- outside Markdown fenced code blocks
- inside target file that has `mixed-boundary` ownership
- inside target file that manifest explicitly marks as first-create candidate
- at a location where inserting begin marker, generated content, and end marker would not alter marker-external content except by insertion at the anchor line

Disallowed:

- inside fenced code blocks
- inside an existing managed block
- inside another marker pair
- in a `user-owned` target
- in unmanaged target without manifest entry
- in files outside repository root

### Missing Anchor Behavior

If manifest entry is first-create candidate but target exists and no anchor is present:

- action: `conflict`
- severity: `blocking`
- stop reason: `anchor-missing`

If target is missing and ownership is `runtime-managed` with `whole-file` mode:

- anchor may not be required.
- create candidate may be allowed if manifest first-create policy permits it.

### Duplicate Anchor Behavior

If more than one anchor exists for the same `entry_id`:

- action: `conflict`
- severity: `blocking`
- stop reason: `anchor-duplicated`

If multiple anchors exist for different `entry_id` values:

- allowed only when each corresponds to a distinct manifest entry.
- parser must report them in deterministic line order.

### Unmanaged Target Restrictions

An unmanaged target must not become a create candidate merely because it contains an anchor-looking line.

Rules:

- manifest entry is required.
- ownership must not be `user-owned`.
- sync mode must be `managed-block` or `mixed-boundary`.
- first-create policy must explicitly allow insertion.

### First-create Candidate Boundary

First-create candidate requires all conditions:

- manifest entry exists.
- manifest schema is valid.
- target exists and is mixed-boundary, or target is missing and whole-file create is allowed.
- `target_hash` is null only because first-create policy allows it.
- marker is missing because this is initial creation, not accidental deletion.
- insertion anchor exists when target already exists.
- no duplicate anchor exists.
- no existing marker for the same `entry_id` exists.

If any condition is unclear, fail closed as `conflict`.

## Parser Conflict Classification

### Schema Error

Schema error belongs to manifest validation, not parser runtime facts.

Examples:

- unsupported `marker_style`
- missing marker metadata when sync mode requires it
- marker metadata `entry_id` mismatch
- invalid marker version format in manifest

### Parser Conflict

Parser conflict means target text is ambiguous or unsafe.

Examples:

- marker missing when expected existing block
- duplicated marker
- malformed marker
- mismatched begin/end marker
- nested marker
- unsupported marker version observed in target
- duplicate insertion anchor
- anchor inside code fence

### Orphan-warning

Orphan-warning means parser finds an AIOS marker for an entry that manifest does not contain.

Expected:

- action: `orphan-warning`
- severity: `warning`
- stop reason: `orphaned-managed-block`
- no auto-removal

### Drift-stop Interaction Boundary

Parser does not decide drift-stop from content hash.

Boundary:

- parser structural failure -> `conflict`
- parser valid marker -> hash layer may produce `drift-stop`
- marker valid but managed content hash mismatch -> `drift-stop`
- marker invalid -> no hash-based update candidate

## Future Fixture Layout

Recommended layout:

```text
tests/fixtures/sync/markers/
  valid/
    valid_markdown_pair.md
    valid_hash_line_pair.txt
    valid_yaml_line_pair.yaml
    multiple_independent_blocks.md
  invalid/
    missing_end_marker.md
    duplicate_begin_marker.md
    duplicate_end_marker.md
    nested_marker.md
    malformed_marker.md
    mismatched_entry_id.md
    unsupported_marker_version.md
  ignored/
    fenced_code_marker_ignored.md
    unmanaged_file.md
  anchors/
    valid_anchor.md
    missing_anchor.md
    duplicate_anchor.md
    anchor_inside_code_fence.md
```

Recommended expected files:

```text
tests/fixtures/sync/markers/expected/
  valid_markdown_pair.json
  missing_end_marker.json
  duplicate_anchor.json
```

## Future Validation Commands

Future implementation validation candidates:

```bash
python -m pytest tests/test_sync_markers.py
python -m pytest tests/test_sync_dry_run.py
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/valid.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/marker_conflict.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/anchor_missing.json --json
python -m aios sync --dry-run --manifest tests/fixtures/sync/manifests/orphan_marker.json --json --envelope-v2
python -m compileall -q src/aios aios
git diff --check
```

Expected outcomes:

- valid marker fixture produces parser integrity `valid`.
- malformed marker fixture produces `conflict`.
- fenced marker-looking text is ignored.
- duplicate same `entry_id` marker produces `conflict`.
- orphan marker produces warning, not removal.
- missing anchor for first-create produces blocking conflict.

## Explicit Non-goals

This contract does not implement:

- parser implementation
- parser auto-repair
- marker rewrite
- marker insertion
- marker deletion
- sync apply
- mutation
- manifest persistence
- transaction log persistence
- rollback execution
- adapter generation
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix
- force
- decommission
- source mutation

## Phase 7 Gate Decision

This document satisfies the managed block parser fixture and insertion anchor planning gate.

Runtime implementation should still wait until implementation task breakdown confirms:

- manifest schema validation contract
- parser fixture coverage
- hash normalization fixture behavior
- dry-run result mapping
- envelope v2 mapping
