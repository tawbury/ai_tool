# Deterministic replay test architecture

## 개요

이 문서는 future real preview provider를 구현하기 전에 필요한 deterministic replay test architecture를 정의한다. Real preview provider는 dry-run update 후보 판단에 영향을 주므로, 동일 입력이 동일 output hash와 metadata를 재현한다는 점을 provider 구현 전에 검증 체계로 고정해야 한다.

이번 문서는 설계만 수행한다. Provider 구현, adapter runtime, generated content generation, sync apply, mutation은 포함하지 않는다.

## 목적

Replay testing의 목적은 다음과 같다.

- Provider output stability를 증명한다.
- Provider identity drift를 감지한다.
- Generated hash instability를 감지한다.
- Provenance와 provider metadata 보존을 검증한다.
- False update candidate를 예방한다.
- Nondeterministic provider를 update 후보 생성 경로에서 제외한다.

Replay test는 provider가 안전한 preview comparison input을 만들 수 있는지 검증하는 장치이며, sync apply나 mutation readiness를 의미하지 않는다.

## Replay unit boundaries

Replay unit은 하나의 provider input과 하나의 expected output snapshot을 비교하는 최소 단위다.

Replay unit 구성:

- provider input fixture
- expected provider output fixture
- generated hash comparison
- provenance comparison
- provider metadata comparison
- deterministic flag comparison
- unavailable reason comparison

Replay unit은 target file mutation, manifest write, adapter execution, sync apply를 수행하지 않는다.

## Deterministic replay rules

Replay 규칙:

- 동일 input은 동일 generated hash를 만들어야 한다.
- 동일 input은 동일 provenance를 보존해야 한다.
- 동일 input은 동일 provider metadata를 보존해야 한다.
- 동일 input은 동일 `preview_available` 값을 가져야 한다.
- 동일 input은 동일 `deterministic` 값을 가져야 한다.
- 동일 input은 동일 unavailable reason을 가져야 한다.
- Replay mismatch는 validation failure로 처리해야 한다.

동일 input의 정의:

- 동일 manifest entry
- 동일 source paths
- 동일 source hashes
- 동일 marker metadata
- 동일 sync mode
- 동일 optional activation/rule context reference
- 동일 provider id
- 동일 provider version
- 동일 hash policy

## Replay dimensions

Replay suite는 최소한 다음 차원을 포함해야 한다.

| 차원 | 목적 | 기대 |
| --- | --- | --- |
| whole-file | full target hash 비교 검증 | `generated_target_hash` 안정성 |
| managed-block | marker inner content hash 비교 검증 | `generated_managed_block_hash` 안정성 |
| mixed-boundary | user-owned 외부 content 배제 검증 | managed inner block만 비교 |
| LF | observed bytes policy 검증 | LF hash 안정성 |
| CRLF | line ending 보존 검증 | CRLF hash가 LF와 필요 시 다름 |
| trailing newline | trailing newline 보존 검증 | newline 유무가 hash에 반영 |
| BOM | BOM byte 보존 검증 | BOM 포함 hash가 별도 안정성 유지 |
| unavailable output | 실패/비가용 상태 재현성 검증 | unavailable reason과 null hashes 유지 |

## Provider version replay policy

Provider version은 replay 판단의 핵심 축이다.

Rules:

- 동일 provider version에서는 동일 input이 동일 output을 만들어야 한다.
- Provider version이 바뀌면 output drift는 허용될 수 있다.
- Provider version 변경으로 인한 output drift는 명시적 snapshot 갱신 또는 migration note가 필요하다.
- Provider output logic이 바뀌었는데 version이 유지되면 replay failure로 보아야 한다.
- Provider metadata의 `provider_id`와 `provider_version`은 replay snapshot에 포함되어야 한다.

Version change policy:

- Output-affecting change: version bump required.
- Metadata-only non-output change: version bump 권장, 최소한 audit note 필요.
- Hash policy change: provider version과 hash policy version 모두 명시적으로 변경해야 한다.

## Nondeterministic detection policy

Replay mismatch는 nondeterminism의 신호로 취급한다.

Classification:

- generated hash mismatch -> `replay-hash-mismatch`
- provenance mismatch -> `replay-provenance-mismatch`
- provider metadata mismatch -> `replay-provider-metadata-mismatch`
- unavailable reason mismatch -> `replay-unavailable-reason-mismatch`
- deterministic flag mismatch -> `replay-deterministic-flag-mismatch`

Nondeterministic output semantics:

- Provider가 deterministic output을 보장할 수 없으면 `preview_available: false`를 반환해야 한다.
- Unavailable reason은 `nondeterministic-output`이어야 한다.
- Nondeterministic output은 update candidate를 만들 수 없다.

Retry policy:

- Replay mismatch에 대한 automatic retry는 금지한다.
- Retry는 nondeterminism을 숨길 수 있다.
- Timeout이나 external-state dependency는 `provider-timeout` 또는 `nondeterministic-output`으로 분류해야 한다.

## Replay fixture structure

권장 fixture layout:

```text
tests/fixtures/sync/real_previews/replay/
  inputs/
    whole_file_lf_input.json
    whole_file_crlf_input.json
    whole_file_trailing_newline_input.json
    whole_file_bom_input.json
    managed_block_lf_input.json
    managed_block_crlf_input.json
    mixed_boundary_input.json
    unavailable_adapter_input.json
    unavailable_nondeterministic_input.json
    unavailable_timeout_input.json

  outputs/
    whole_file_lf_output.json
    whole_file_crlf_output.json
    whole_file_trailing_newline_output.json
    whole_file_bom_output.json
    managed_block_lf_output.json
    managed_block_crlf_output.json
    mixed_boundary_output.json
    unavailable_adapter_output.json
    unavailable_nondeterministic_output.json
    unavailable_timeout_output.json

  manifests/
    replay_manifest.json

  provider_snapshots/
    aios_preview_example_0_1_0.json
```

`replay_manifest.json` should include:

```json
{
  "schema_version": "aios.preview_replay_manifest.v0",
  "provider": {
    "provider_id": "aios.preview.example",
    "provider_version": "0.1.0",
    "hash_policy": "aios.hash_policy.v0"
  },
  "cases": [
    {
      "case_id": "whole_file_lf",
      "input_fixture": "inputs/whole_file_lf_input.json",
      "expected_output_fixture": "outputs/whole_file_lf_output.json",
      "replay_dimensions": ["whole-file", "LF"]
    }
  ]
}
```

Provider metadata snapshot should include:

- provider id
- provider version
- deterministic capability
- supported sync modes
- hash policy
- output-affecting configuration

## Replay validation expectations

Replay validation must compare:

- `schema_version`
- `entry_id`
- `preview_available`
- `generated_content_kind`
- `generated_bytes_hash`
- `generated_target_hash`
- `generated_managed_block_hash`
- `deterministic`
- `provider_metadata`
- `provenance`
- `unavailable_reason`

Hash expectations:

- All non-null hashes must use `sha256:<lowercase-hex>`.
- Generated hash equality is exact string equality.
- Hashes must not be normalized during comparison.

Provenance expectations:

- Source path order must be stable.
- Source hash values must match exactly.
- Activation reference must match exactly.
- Rule context reference must match exactly.
- `generated_by` must match exactly.

Provider metadata expectations:

- Provider id must match exactly.
- Provider version must match exactly.
- Hash policy must match exactly.
- Supported sync mode metadata must match exactly.
- Deterministic flag must match exactly.

Unavailable expectations:

- `preview_available: false`
- all generated hash fields are `null`
- `unavailable_reason` matches exactly
- provider metadata remains present
- provenance remains present where available

## Replay CLI and testing expectations

Future CLI/testing modes may include:

- replay-only validation mode
- fixture-backed replay mode
- future provider validation integration

Possible future commands:

```bash
python -m pytest tests/test_real_preview_replay.py
python -m aios validate tests/fixtures/sync/real_previews/replay/manifests/replay_manifest.json
python -m aios sync --dry-run --manifest <path> --preview-provider real --preview-replay <replay-manifest>
```

The command examples are planning targets only. They do not authorize implementation in this task.

Replay-only validation should:

- load replay manifest
- load provider input fixture
- load expected output fixture
- execute provider only in explicitly approved future provider validation mode
- compare output to snapshot
- report replay mismatch as validation failure

Fixture-backed replay mode should:

- use expected output fixtures without executing real provider
- validate output contract and dry-run mapping
- preserve read-only behavior

Future provider validation integration should:

- require explicit provider selection
- require explicit replay manifest
- fail closed on mismatch
- avoid writing updated snapshots automatically

## False update candidate prevention

Replay tests must reduce false update candidates by proving that generated hashes are stable. However, replay success alone must not create update candidates.

Dry-run must still enforce:

- manifest validation first
- source hash check before preview
- marker integrity before preview
- target drift check before preview
- clean target only comparison
- preview unavailable no-update policy

Replay tests validate provider stability; they do not replace dry-run safety checks.

## Explicit non-goals

This architecture does not implement or authorize:

- provider implementation
- adapter runtime
- generated content generation
- sync apply
- target mutation
- manifest persistence
- transaction persistence
- rollback
- marker insertion, repair, or deletion
- repository-wide scan
- activation-driven preview selection
- force
- decommission
- orchestration
- workflow execution
- worker execution
- `.ai/registry/`
- auto-fix
- source mutation

## 결론

Deterministic replay architecture는 real preview provider 구현 전 필수 gate다. 동일 provider version과 동일 input에서 hash, provenance, metadata가 정확히 재현되어야 하며, mismatch는 retry로 숨기지 않고 validation failure로 처리해야 한다. 이 구조는 read-only preview 신뢰성을 높이지만 sync apply나 mutation을 승인하지 않는다.
