# Current runtime context map

> 이 문서는 summary-first human context이다. 런타임 계약이 아니며, `.ai/rules/`가 canonical runtime authority다.

## 목적

현재 `.ai OS`의 runtime source of truth, 지원 명령, 지원 schema, active runtime rules, read-only boundary, deferred capability를 빠르게 확인하기 위한 색인이다.

## Runtime source of truth

권한 순서:

1. 최신 사용자 요청
2. active system/developer instructions
3. `.ai/rules/rules.md`
4. task-relevant `.ai/rules/domains/*.rules.md`
5. task-relevant `.ai/rules/operations/*.rules.md`
6. executable contract sections under `.ai/commands`, `.ai/agents`, `.ai/skills`, `.ai/workflows`, `.ai/validators`
7. explicitly relevant active specs under `docs/specs`
8. `docs/plan`, `docs/reports`, `docs/adr` as human context only

Important boundary:

- `docs/plan/`은 runtime contract가 아니다.
- `docs/reports/`는 runtime contract가 아니다.
- Durable runtime behavior는 `.ai/`로 승격되어야 효력을 가진다.
- 이 index 문서도 runtime contract가 아니다.

## Active runtime rules

| Rule | Runtime area | Load when |
| --- | --- | --- |
| `.ai/rules/rules.md` | global authority, selective loading, docs boundary | always minimum |
| `.ai/rules/operations/documentation-governance.rules.md` | document taxonomy and promotion boundary | docs governance task |
| `.ai/rules/operations/context-loading.rules.md` | semantic loader profiles and budget behavior | context loading task |
| `.ai/rules/operations/activation.rules.md` | activation v0/v1 contract | activation task |
| `.ai/rules/operations/sync.rules.md` | sync dry-run, manifest validation, replay validation, marker, preview, mutation block | sync/manifest/preview/replay task |
| `.ai/rules/operations/validation.rules.md` | validation behavior | validate task |
| `.ai/rules/operations/observability.rules.md` | future event/trace model | observability task |
| `.ai/rules/operations/registry.rules.md` | future registry relationship layer | registry task |

## Supported commands

Current runtime supports:

- `python -m aios inspect`
- `python -m aios inspect --json`
- `python -m aios inventory`
- `python -m aios inventory --summary-only`
- `python -m aios validate`
- `python -m aios validate --json`
- `python -m aios validate <activation.yaml>`
- `python -m aios validate <sync-manifest.json>`
- `python -m aios validate <replay-manifest.json>`
- `python -m aios validate <replay-manifest.json> --replay-compare fixture`
- `python -m aios validate <provider-capability.json>`
- `python -m aios validate <provider-trace.json>`
- `python -m aios validate <sandbox-policy.json>`
- `python -m aios validate <sandbox-result.json>`
- `python -m aios validate <sandbox-trace.json>`
- `python -m aios activation <path>`
- `python -m aios activation <path> --json`
- `python -m aios load-context <path>`
- `python -m aios load-context <path> --max-chars <int>`
- `python -m aios sync --dry-run --manifest <path>`
- `python -m aios sync --dry-run --manifest <path> --json`
- `python -m aios sync --dry-run --manifest <path> --json --envelope-v2`
- `python -m aios sync --dry-run --manifest <path> --json --preview-provider fixture --preview-fixtures <path>`

Envelope v2 is opt-in and requires `--json`.

## Supported schemas

| Schema | Use |
| --- | --- |
| `aios.activation.v0` | activation v0 contract |
| `aios.activation.v1` | activation v1 contract with runtime mode, rules, loader overrides |
| `aios.sync_manifest.v0` | sync manifest validation and dry-run input |
| `aios.sync_dry_run.v0` | native sync dry-run output |
| `aios.command_result.v2` | opt-in unified JSON envelope |
| `aios.generated_preview.input.v0` | fixture preview input contract |
| `aios.generated_preview.output.v0` | fixture preview output contract |
| `aios.real_preview.input.v0` | planned real preview provider input contract |
| `aios.real_preview.output.v0` | planned real preview provider output contract |
| `aios.preview_replay_manifest.v0` | deterministic replay fixture manifest statically validated by `aios validate <replay-manifest.json>` |
| `aios.preview_provider_snapshot.v0` | replay provider snapshot fixture statically validated from replay manifests |
| `aios.provider_capability.v0` | provider capability declaration statically validated by `aios validate <provider-capability.json>` |
| `aios.provider_execution_trace.v0` | provider execution trace statically validated by `aios validate <provider-trace.json>` |
| `aios.sandbox_policy.v0` | sandbox policy statically validated by `aios validate <sandbox-policy.json>` |
| `aios.sandbox_execution_result.v0` | sandbox execution result statically validated by `aios validate <sandbox-result.json>` |
| `aios.sandbox_trace.v0` | sandbox trace statically validated by `aios validate <sandbox-trace.json>` |

The real preview provider schemas are planning artifacts only until implemented and promoted. Replay manifest and provider snapshot schemas currently exist as fixture/test contracts with static validation integration, not provider execution contracts.

## Read-only boundary

Current runtime is read-only.

Allowed:

- inspect repository structure
- inventory `.ai` assets
- validate agents, skills, workflows, activation files, validator index, sync manifests, replay manifests
- validate provider capability declarations, provider execution traces, and sandbox policies statically
- validate sandbox execution results statically
- validate sandbox traces statically
- perform fixture-backed replay comparison when explicitly configured
- load semantic context from `.ai` files with profile/budget filtering
- evaluate sync dry-run against an explicit manifest
- parse managed markers
- compare hashes
- classify dry-run results
- perform fixture-backed preview comparison when explicitly configured

Forbidden:

- sync apply
- target mutation
- source mutation
- manifest write
- transaction log write
- rollback execution
- marker insertion, repair, deletion
- generated content persistence
- adapter execution
- real preview provider execution
- repository-wide unmanaged/orphan scan
- activation-driven sync selection
- force
- decommission
- orchestration
- worker execution
- workflow execution
- registry parser
- `.ai/registry/`
- auto-fix

## Current sync/preview behavior

`aios sync --dry-run --manifest <path>` is read-only.

Supported result actions:

- `create`
- `update`
- `skip`
- `conflict`
- `drift-stop`
- `orphan-warning`

Preview behavior:

- no default preview provider
- only fixture provider is supported
- preview requires `--preview-provider fixture --preview-fixtures <path>`
- preview comparison only applies to clean targets
- `action: update` is informational and non-mutating
- source-missing beats preview
- marker conflict beats preview
- drift-stop beats preview
- preview unavailable means no update candidate

## Do-not-load-by-default guidance

Do not load these by default:

- completed implementation reports
- risk audits
- completion audits
- historical Phase 6/7 planning documents
- old readiness reports
- low-level fixture reports

Load them only when:

- the user names them
- a current task needs evidence
- a regression or policy conflict must be investigated
- a report must cite prior work

## Summary-first loading guidance

Recommended order:

1. `.ai/rules/rules.md`
2. relevant operation rule
3. `docs/index/current_runtime_context.md`
4. `docs/roadmap/static_validation_and_execution_readiness_roadmap.md` when planning remaining work or bundles
5. `docs/index/phase_6_8_summary.md`
6. `docs/index/document_status_registry.md` when document authority/status is needed
7. detailed plans/reports only if needed

If more than five docs appear necessary, first check whether this index or `phase_6_8_summary.md` can answer the question.

## Current next safe direction

The next safe direction is still read-only:

- use `docs/roadmap/static_validation_and_execution_readiness_roadmap.md` to group remaining work into roadmap-driven bundles
- define execution architecture approval boundaries as the next design-only gate
- keep sandbox policy validation static-only under promoted validation/sync rules
- keep deterministic mock provider fixtures fixture-only until a helper boundary is separately approved
- keep provider capability and provider trace validation static-only
- maintain fixture-only replay schema tests
- keep sync apply and mutation blocked

Do not start sync apply, mutation design, sandbox launcher, subprocess execution, provider execution, or replay execution until architecture approval and later prototype planning explicitly allow the next step.
