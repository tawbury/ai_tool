# Real preview provider contract

## 개요

이 문서는 `.ai OS`의 future real preview provider 계약을 정의한다. Phase 8 fixture provider는 provider interface와 dry-run integration을 검증했지만, 실제 source material에서 비교용 preview output을 만드는 provider는 아직 없다.

이번 문서는 계약 설계만 수행한다. 런타임 코드, adapter 실행, generated content 생성, sync apply, mutation, manifest persistence는 구현하지 않는다.

## 목적

Real preview provider의 목적은 dry-run evaluator가 비교할 수 있는 deterministic read-only preview output을 만드는 것이다.

Provider는 다음을 수행해야 한다.

- manifest entry와 승인된 source/context 입력에서 비교 가능한 output을 만든다.
- whole-file, managed-block, mixed-boundary 비교에 필요한 generated hash를 제공한다.
- output provenance와 provider identity를 보존한다.
- 동일 입력에 대해 동일 generated hash를 반환한다.
- dry-run의 read-only update candidate 판단을 보조한다.

Provider는 쓰기 권한을 만들지 않는다. `action: update`는 informational candidate이며 sync apply 승인이 아니다.

## 비목표

Real preview provider는 다음이 아니다.

- sync apply
- target mutation
- rollback
- manifest persistence
- transaction log writer
- marker insertion, repair, deletion
- adapter execution authorization
- unrestricted model execution
- workflow execution
- worker dispatch
- activation-driven sync selection
- source of truth replacement

## Provider identity model

Provider는 명시적 identity를 가져야 한다.

```json
{
  "provider_id": "aios.preview.example",
  "provider_version": "0.1.0",
  "deterministic_capable": true,
  "supported_sync_modes": ["whole-file", "managed-block"],
  "hash_policy": "aios.hash_policy.v0"
}
```

필드 규칙:

- `provider_id`는 stable identifier여야 한다.
- `provider_version`은 output 결정성에 영향을 주는 변경마다 증가해야 한다.
- `deterministic_capable`이 `true`가 아니면 update candidate를 만들 수 없다.
- `supported_sync_modes`는 provider가 preview를 만들 수 있는 sync mode만 포함한다.
- `hash_policy`는 dry-run evaluator의 hash policy와 일치해야 한다.

## Provider input contract

Provider input은 manifest entry, source evidence, optional context reference, provider identity를 포함해야 한다.

```json
{
  "schema_version": "aios.real_preview.input.v0",
  "entry_id": "entry_example",
  "manifest_entry": {
    "source_path": ".ai/rules/operations/sync.rules.md",
    "source_paths": null,
    "source_hash": "sha256:<source>",
    "target_path": "AGENTS.md",
    "ownership": "mixed-boundary",
    "sync_mode": "managed-block",
    "marker": {
      "marker_version": "0",
      "marker_style": "markdown-html-comment",
      "entry_id": "entry_example"
    }
  },
  "source_evidence": {
    "source_paths": [".ai/rules/operations/sync.rules.md"],
    "source_hashes": {
      ".ai/rules/operations/sync.rules.md": "sha256:<source>"
    }
  },
  "context": {
    "activation_reference": null,
    "rule_context_reference": null
  },
  "provider": {
    "provider_id": "aios.preview.example",
    "provider_version": "0.1.0"
  },
  "hash_policy": {
    "version": "aios.hash_policy.v0",
    "algorithm": "sha256",
    "encoding": "observed-utf8-bytes",
    "line_endings": "preserve",
    "trailing_newline": "preserve",
    "managed_block_marker_lines": "exclude"
  }
}
```

Required input fields:

- `schema_version`
- `entry_id`
- `manifest_entry`
- `manifest_entry.source_path` or `manifest_entry.source_paths`
- `manifest_entry.source_hash`
- `manifest_entry.target_path`
- `manifest_entry.ownership`
- `manifest_entry.sync_mode`
- `manifest_entry.marker`
- `source_evidence.source_paths`
- `source_evidence.source_hashes`
- `provider.provider_id`
- `provider.provider_version`
- `hash_policy`

Optional context fields:

- `context.activation_reference`
- `context.rule_context_reference`

Context references are references only. They do not authorize broad context loading, activation-driven sync selection, or adapter execution.

## Provider output contract

Provider output must use an explicit schema.

```json
{
  "schema_version": "aios.real_preview.output.v0",
  "entry_id": "entry_example",
  "preview_available": true,
  "generated_content_kind": "managed-block",
  "generated_bytes_hash": "sha256:<generated-bytes>",
  "generated_target_hash": null,
  "generated_managed_block_hash": "sha256:<generated-managed-block>",
  "deterministic": true,
  "provider_metadata": {
    "provider_id": "aios.preview.example",
    "provider_version": "0.1.0",
    "hash_policy": "aios.hash_policy.v0",
    "supported_sync_mode": "managed-block"
  },
  "provenance": {
    "source_paths": [".ai/rules/operations/sync.rules.md"],
    "source_hashes": {
      ".ai/rules/operations/sync.rules.md": "sha256:<source>"
    },
    "activation_reference": null,
    "rule_context_reference": null,
    "generated_by": "aios.real_preview_provider.v0"
  },
  "unavailable_reason": null
}
```

When preview is unavailable:

```json
{
  "schema_version": "aios.real_preview.output.v0",
  "entry_id": "entry_example",
  "preview_available": false,
  "generated_content_kind": null,
  "generated_bytes_hash": null,
  "generated_target_hash": null,
  "generated_managed_block_hash": null,
  "deterministic": false,
  "provider_metadata": {
    "provider_id": "aios.preview.example",
    "provider_version": "0.1.0"
  },
  "provenance": {
    "source_paths": [],
    "source_hashes": {},
    "activation_reference": null,
    "rule_context_reference": null,
    "generated_by": "aios.real_preview_provider.v0"
  },
  "unavailable_reason": "adapter-unavailable"
}
```

Output rules:

- Available output requires `preview_available: true`.
- Available output requires `deterministic: true`.
- Available output requires at least one generated hash appropriate to the sync mode.
- Unavailable output must set all generated hash fields to `null`.
- `unavailable_reason` must be `null` for available output.
- `unavailable_reason` must be present for unavailable output.
- Provider metadata and provenance must be preserved for both available and unavailable output.

## Deterministic requirements

Real provider output must be deterministic.

Requirements:

- Identical input must produce identical generated bytes hash.
- Identical input means the same manifest entry, source hashes, context references, provider id, provider version, and hash policy.
- Provider output must not depend on wall-clock time, environment-specific absolute paths, random ordering, network state, non-pinned model behavior, or mutable external state.
- If deterministic output cannot be guaranteed, the provider must return unavailable output with `unavailable_reason: nondeterministic-output`.
- Provider version must change when output logic changes.
- Output ordering must be stable.
- Source file ordering must be stable and explicit.

Normalization policy:

- Use `aios.hash_policy.v0`.
- Use observed UTF-8 bytes.
- Do not normalize CRLF/LF.
- Preserve trailing newline and whitespace.
- Include BOM bytes if present.
- Exclude marker begin/end lines from managed block hashes.
- Do not introduce line ending normalization unless a future hash policy version explicitly allows it.

## Unavailable and failure semantics

Provider failures must be represented as unavailable output, not as write actions.

Supported unavailable reasons:

- `adapter-unavailable`
- `source-missing`
- `unsupported-sync-mode`
- `activation-unresolved`
- `nondeterministic-output`
- `provider-timeout`
- `generation-disabled`
- `marker-invalid`

Guidance:

- `source-missing` should normally be superseded by dry-run source conflict before provider execution.
- `marker-invalid` should normally be superseded by marker conflict before provider comparison.
- `provider-timeout` must not create update candidate.
- `nondeterministic-output` must not create update candidate.
- `generation-disabled` is an intentional no-preview state.
- `activation-unresolved` must not trigger implicit activation loading.

## Provider safety boundary

Provider must not bypass existing safety checks.

Rules:

- Provider cannot bypass drift-stop.
- Provider cannot repair markers.
- Provider cannot infer ownership.
- Provider cannot mutate files.
- Provider cannot write manifests.
- Provider cannot write transaction logs.
- Provider cannot invoke sync apply.
- Provider cannot insert, repair, or delete markers.
- Provider cannot expand source scope beyond explicit input.
- Provider cannot treat context references as unrestricted runtime context.
- Provider cannot authorize writes through `update` candidate output.

Dry-run must run manifest, source, target, marker, and drift checks before preview comparison. Provider output is only useful after the target is known clean.

## Adapter boundary

An adapter may become one provider implementation later, but adapter execution is not approved by this contract.

Boundary:

- Provider contract must exist before adapter runtime exists.
- Adapter execution policy must be separately approved.
- Adapter identity may be recorded as provider metadata.
- Adapter output must satisfy deterministic requirements.
- Adapter output must use the same hash policy.
- Adapter execution must not write files unless a future mutation gate separately authorizes it.

This contract does not approve adapter generation, adapter execution, root adapter rewrite, or adapter-specific sync apply.

## Future dry-run integration expectations

Real provider output may extend dry-run comparison only.

Expected behavior:

- Clean target plus generated hash differs -> read-only `update` candidate.
- Clean target plus generated hash matches -> `skip`.
- Preview unavailable -> preserve existing dry-run result and record reason.
- Drift-stop remains fail even if generated hash exists.
- Marker conflict remains fail even if generated hash exists.
- Source-missing remains conflict even if provider output exists.
- `update` remains informational and non-mutating.
- `meta.mutation_performed` remains `false`.

## Future validation expectations

Future validation should check provider capability before dry-run uses a real provider.

Validation targets:

- provider identity shape
- provider version presence
- deterministic capability declaration
- supported sync mode compatibility
- hash policy compatibility
- unavailable reason enum
- output schema shape
- non-null generated hash format
- provenance source hash preservation

Validation must not execute sync apply or mutate files.

## Future test strategy

Recommended tests:

- provider contract fixture schema tests
- deterministic replay tests with identical inputs
- hash stability tests for LF/CRLF/trailing newline cases
- provider unavailable reason classification tests
- unsupported sync mode tests
- nondeterministic output rejection tests
- provider timeout classification tests
- envelope v2 preservation tests
- dry-run precedence tests with real provider output mocked or fixture-backed

Test fixtures should include:

- whole-file available output
- managed-block available output
- mixed-boundary available output
- unsupported sync mode unavailable output
- nondeterministic unavailable output
- provider-timeout unavailable output
- activation-unresolved unavailable output
- generation-disabled unavailable output

## Explicit non-goals

This contract does not implement or authorize:

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

Real preview provider는 fixture provider 다음 단계로 적절하지만, 구현 전에 deterministic input/output, provider identity, failure semantics, adapter boundary를 고정해야 한다. 이 계약은 real provider가 dry-run에 정보를 제공하는 경계를 정의하며, mutation이나 sync apply 권한은 계속 차단한다.
