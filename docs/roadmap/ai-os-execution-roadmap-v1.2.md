# AI Operating System (.ai OS) Execution Roadmap v1.2

> Status: Active
> Supersedes: `docs/roadmap/ai-os-execution-roadmap-v1.1.md`
> Runtime policy: CLI-first AI workforce OS
> Current supported runtimes: Codex CLI, Gemini CLI, Claude Code CLI
> Legacy/deprecated runtimes: Cursor, Windsurf, editor-centric AI integrations
> Implementation boundary: read-only integrity, validation, inventory, and context tooling before sync or adapter generation

## 1. Executive Summary

이 문서는 `.ai OS`의 현재 canonical 실행 로드맵이다.

v1.2는 v1.1의 물리 동기화 중심 순서를 대체한다. 현재 전략은 CLI-first AI workforce OS를 구축하는 것이며, `.ai/`를 runtime source of truth로 둔다. 구현 순서는 파일을 수정하지 않는 읽기 전용 무결성 검사, executable contract validation, repository inventory, semantic context loading을 먼저 안정화한 뒤 sync, manifest, adapter generation, orchestration으로 확장한다.

현재 구현은 다음 기준선을 갖는다.

- `aios inspect`는 구현되어 있고 `0 fail, 0 warning` 기준선을 유지한다.
- `aios load-context` v1은 구현되어 있다.
- `aios validate` v1 출력 사용성 개선은 구현되어 있다.
- `aios inventory` v0는 구현되어 있다.
- `frontmatter.py`, `references.py`, `status.py`, `contracts.py`, `inventory.py` 공유 primitive가 존재한다.
- documentation governance runtime-facing rule이 존재한다.

v1.2의 핵심 원칙은 다음과 같다.

- `.ai/`가 runtime source of truth다.
- `docs/`는 감사, 계획, ADR, 상세 spec을 담지만 runtime contract로 자동 소비되지 않는다.
- Codex CLI, Gemini CLI, Claude Code CLI만 current supported runtime이다.
- Cursor, Windsurf, editor-centric integration은 legacy/deprecated다.
- semantic loading과 validation이 physical sync보다 먼저다.
- sync, manifest, adapter generation, orchestration, worker execution은 현재 단계의 non-goal이다.

## 2. Phase Structure

## Phase 0: Runtime Policy and Documentation Governance Baseline

### Goal

runtime 정책과 문서 권한 경계를 명확히 하여 이후 구현이 잘못된 문서를 runtime contract로 소비하지 않도록 한다.

### Scope

- 공식 runtime은 Codex CLI, Gemini CLI, Claude Code CLI로 제한한다.
- Cursor, Windsurf, editor-centric AI integration은 legacy/deprecated로 둔다.
- `.ai/`를 runtime source of truth로 정의한다.
- `docs/plan`, `docs/reports`, `docs/adr`은 runtime contract가 아님을 명확히 한다.
- `docs/specs`는 상세 human-readable spec이며 always-load context가 아님을 명확히 한다.
- UTF-8 without BOM 정책을 유지한다.
- symlink 기반 rules/agents/commands 관리를 금지한다.
- root adapter는 thin compatibility layer로 유지한다.

### Current Status

부분 구현됨.

- `.ai/rules/rules.md`에 source-of-truth, thin adapter, UTF-8 without BOM, symlink policy가 존재한다.
- `.ai/rules/operations/documentation-governance.rules.md`가 runtime-facing documentation governance rule로 존재한다.

### Next

- runtime policy 관련 규칙을 `aios validate` 대상 contract로 점진 승격한다.
- legacy runtime 용어가 active target으로 다시 유입되지 않도록 inspect 또는 validate rule을 설계한다.

## Phase 1: Read-only Repository Integrity Layer

### Goal

파일을 수정하지 않고 repository structure와 reference integrity를 검사한다.

### Scope

- `aios inspect`
- required directory 검사
- root adapter existence 검사
- `.ai/rules/rules.md` existence 검사
- skill inventory 검사
- skill reference integrity 검사
- workflow reference integrity 검사
- stale `.ai/.cursorrules` reference 검사
- UTF-8 BOM 검사
- symlink 검사
- Markdown/Obsidian obvious link 검사
- agent-routing anchor와 fenced YAML block 존재 검사

### Current Status

구현됨.

- `python -m aios inspect`는 `0 fail, 0 warning` 기준선을 유지한다.
- 출력은 human-readable summary와 JSON을 지원한다.
- `--summary-only` JSON 옵션을 지원한다.

### Next

- inspect 내부 inventory 계산을 Phase 2의 inventory primitive로 점진 이전한다.
- inspect result schema v2 계획을 별도 문서화한다.

## Phase 2: Shared Runtime Primitives and Inventory

### Goal

runtime command들이 같은 parsing, reference, status, contract, inventory primitive를 공유하도록 한다.

### Scope

- `frontmatter.py`
- `references.py`
- `status.py`
- `contracts.py`
- `inventory.py`
- `aios inventory`
- normalized repository item model
- single-runtime in-memory cache

### Current Status

구현됨.

- `frontmatter.py`는 lightweight frontmatter extraction/parser를 제공한다.
- `references.py`는 Markdown/Obsidian file link, `.ai/...` path, relative path resolve primitive를 제공한다.
- `status.py`는 공통 status/severity/exit code 상수를 제공한다.
- `contracts.py`는 agent required field와 reference field contract를 제공한다.
- `inventory.py`는 agent, skill, workflow, validator, rule, command inventory를 제공한다.
- `python -m aios inventory`가 구현되어 있다.

### Next

- inspect의 agent/skill/workflow discovery를 inventory layer로 이전한다.
- validate target discovery를 inventory layer 기반으로 점진 이전한다.
- inventory metadata 포함 여부를 제어하는 옵션을 검토한다.

## Phase 3: Executable Contract Validation Layer

### Goal

`.ai/`의 runtime-relevant 문서가 최소 executable contract를 만족하는지 검증한다.

### Scope

- `aios validate`
- agent frontmatter required field validation
- agent rule/validator reference validation
- skill basic structure validation
- workflow filename and required section validation
- validator index reference integrity
- missing target error
- weak/legacy structure warning
- skipped human-review-only checks as info
- JSON `--summary-only`
- JSON `--include-pass`

### Current Status

구현됨.

- `aios validate` v0 검증 계층이 존재한다.
- v1 출력 사용성 개선으로 `--summary-only`와 `--include-pass`가 추가되었다.
- 현재 result model은 explicit pass item을 기록하지 않는다.

### Next

- validate v1/v2에서 explicit pass result 필요성을 검토한다.
- validator registry를 실제 dispatch table로 정리한다.
- human-review-only validator boundary를 더 명확히 문서화한다.
- runtime policy validator를 추가할지 검토한다.

## Phase 4: Semantic Loading and Context Budget Layer

### Goal

worker runtime 이전에 semantic context extraction과 loading profile을 안정화한다.

### Scope

- `aios load-context`
- governance annotation boundary parser
- inline annotation parser
- standard heading fallback
- legacy section fallback
- profile include/exclude layer policy
- examples, philosophy, performance metrics 기본 제외
- trace/provenance output

### Current Status

구현됨.

- `aios load-context` v1이 존재한다.
- `minimal-worker`, `reviewer`, `strategist`, `validation-runtime` profile을 지원한다.
- `--include-layer`, `--exclude-layer`, `--no-content`, `--summary-only`를 지원한다.

### Next

- token budget handling을 추가 설계한다.
- activation profile과 semantic loading profile의 관계를 정의한다.
- context provenance를 runtime trace schema와 연결한다.

## Phase 5: Runtime Contract and Activation Planning

### Goal

physical sync 전에 runtime activation, registry, precedence contract를 설계한다.

### Scope

- `activation.yaml` design
- semantic loading profile extension
- agent registry
- validator registry
- workflow registry
- project/global rule precedence
- runtime consumption boundary
- docs-to-runtime promotion policy

### Current Status

계획 단계.

- governance annotation standard와 semantic loader architecture 문서가 존재한다.
- agent-routing YAML block은 `.ai/rules/operations/agent.rules.md`에 존재한다.
- 아직 `activation.yaml` 구현은 없다.

### Next

- `activation.yaml` 최소 schema를 설계한다.
- agent-routing embedded YAML을 장기적으로 `agent-registry.yaml` 또는 activation registry로 분리할지 결정한다.
- validate에서 registry reference integrity를 검사할 수 있도록 contract를 정의한다.

## Phase 6: Sync/Manifest Safety Design

### Goal

physical sync 구현 전에 safety contract를 먼저 확정한다.

### Scope

- manifest schema
- source hash / target hash model
- drift detection
- dry-run contract
- managed block contract
- atomic update design
- transaction log design
- rollback design

### Current Status

설계 전 단계.

sync, manifest, managed block insertion, adapter generation은 아직 구현하지 않는다.

### Next

- `sync-manifest.json` schema draft 작성
- drift detection policy 작성
- managed block marker format 확정
- dry-run output schema 작성

## Phase 7: Physical Sync Implementation

### Goal

Phase 6 safety design이 검증된 뒤 `.ai/` source of truth를 target files로 안전하게 물리 반영한다.

### Scope

- `aios sync --dry-run`
- one-way SSoT propagation
- drift stop policy
- managed block insertion
- atomic update
- transaction log
- rollback

### Current Status

미구현.

현재 단계의 구현 대상이 아니다.

### Entry Criteria

- `aios inspect` clean baseline 유지
- `aios validate` contract baseline 유지
- inventory layer가 inspect/validate target discovery에 충분히 통합됨
- sync/manifest safety design 승인

## Phase 8: Thin Runtime Adapter Generation

### Goal

공식 CLI runtime용 thin adapter를 생성하거나 검증한다.

### Scope

- Codex CLI adapter
- Gemini CLI adapter
- Claude Code CLI adapter
- root adapter regeneration policy
- no duplicated rule bodies
- adapter verification

### Non-scope

- active Cursor support
- active Windsurf support
- editor-centric path generation
- broad client expansion

### Current Status

미구현.

root adapter files는 존재하지만 adapter generation은 구현하지 않는다.

## Phase 9: Export and External Integration

### Goal

semantic loader 기반으로 외부 web/chat 환경에 안전한 context export를 제공한다.

### Scope

- `aios export`
- token budget filtering
- secret exclusion
- profile-specific export
- context trace
- export template library

### Current Status

미구현.

`aios load-context`가 전제 계층이다.

## Phase 10: Orchestration and Worker Execution

### Goal

validation, loading, sync, adapter layer가 안정화된 뒤 worker execution을 검토한다.

### Possible Scope

- worker profiles
- task dispatch
- runtime execution trace
- reviewer/strategist/worker context profiles
- validation-gated task execution

### Non-scope

- v1.2 초기 구현
- tmux-first architecture
- unmanaged worker execution
- sync 이전 orchestration

## 3. Current Implementation Mapping

| 구현 항목 | 대응 Phase | 상태 |
|---|---|---|
| `.ai/rules/rules.md` source-of-truth policy | Phase 0 | 구현됨 |
| documentation governance runtime-facing rule | Phase 0 | 구현됨 |
| `aios inspect` | Phase 1 | 구현됨, clean baseline |
| `frontmatter.py` | Phase 2 | 구현됨 |
| `references.py` | Phase 2 | 구현됨 |
| `status.py` | Phase 2 | 구현됨 |
| `contracts.py` | Phase 2 | 구현됨 |
| `inventory.py` | Phase 2 | 구현됨 |
| `aios inventory` | Phase 2 | 구현됨 |
| `aios validate` | Phase 3 | 구현됨 |
| validate `--summary-only`, `--include-pass` | Phase 3 | 구현됨 |
| `aios load-context` | Phase 4 | 구현됨 |
| `activation.yaml` | Phase 5 | 미구현 |
| sync manifest | Phase 6 | 미구현, 설계 예정 |
| `aios sync` | Phase 7 | 미구현 |
| adapter generation | Phase 8 | 미구현 |
| `aios export` | Phase 9 | 미구현 |
| orchestration / worker execution | Phase 10 | 미구현 |

## 4. Next Implementation Priorities

### P0

- inspect target discovery를 inventory primitive로 점진 이전
- validate target discovery를 inventory primitive로 점진 이전
- validate registry dispatch 정리
- runtime policy validator 설계
- activation.yaml 최소 schema 계획 작성

### P1

- semantic loader token budget policy 설계
- activation profile과 loading profile 연결
- command result envelope v2 설계
- pass item recording 필요성 검토
- registry reference integrity validation 추가

### P2

- sync manifest safety design
- managed block contract 설계
- adapter generation contract 설계
- export context trace 설계
- orchestration preconditions 정의

## 5. Deferred Phases

다음 항목은 현재 구현하지 않는다.

- global install
- physical sync
- persistent manifest
- managed block insertion
- adapter generation
- web export
- orchestration
- worker execution
- tmux runtime
- Cursor/Windsurf active support

## 6. Explicit Non-goals

v1.2 현재 단계의 non-goal:

- sync 구현
- manifest 구현
- adapter generation 구현
- runtime worker execution 구현
- orchestration 구현
- tmux-first design
- auto-fix
- editor-centric integration
- Cursor/Windsurf를 current runtime target으로 복원
- root adapter에 shared rule body 복사

## 7. Validation Strategy

각 phase는 다음 validation command로 회귀 확인한다.

```bash
python -m aios inspect
python -m aios validate
python -m aios validate --json --summary-only
python -m aios inventory --type skill --summary-only
python -m aios load-context .ai/rules/rules.md --json --summary-only
python -m compileall -q src/aios aios
git diff --check
```

Sync 이후 phase가 시작되기 전까지 모든 runtime command는 read-only여야 한다.

## 8. Risk and Rollback Strategy

| Risk | Severity | Mitigation | Rollback |
|---|---|---|---|
| roadmap이 sync를 너무 일찍 유도 | High | sync를 Phase 6/7로 명확히 deferred | v1.2 phase gate로 회귀 |
| Cursor/Windsurf가 active target으로 재유입 | High | legacy/deprecated로 명시 | active adapter 목록에서 제거 |
| docs/reports가 runtime contract로 오인 | Medium | documentation governance rule 유지 | `.ai` runtime-facing rule로 promotion 전까지 비활성 |
| inspect/validate 중복 재증가 | Medium | shared primitives와 inventory layer 사용 | 중복 모듈 제거 리팩터 |
| semantic context bloat | Medium | profile include/exclude와 token budget 정책 | minimal-worker profile로 축소 |
| sync 구현 중 data loss | High | dry-run, drift stop, managed block, atomic update 설계 선행 | transaction rollback design 적용 |

## Appendix A: Future Sync Manifest Schema

이 schema는 Phase 6 설계 후보이며 현재 구현 대상이 아니다.

```json
{
  "schema_version": "aios.sync_manifest.v0",
  "source_path": ".ai/rules/rules.md",
  "target_path": "AGENTS.md",
  "source_hash": "sha256:<source>",
  "target_hash": "sha256:<target>",
  "last_synced_at": "2026-04-29T10:00:00Z",
  "adapter": "codex-cli",
  "sync_transaction_id": "tx-000000000"
}
```

## Appendix B: Future activation.yaml Sketch

이 schema는 Phase 5 설계 후보이며 현재 구현 대상이 아니다.

```yaml
schema_version: aios.activation.v0
active_set:
  agents:
    - developer
    - pm
  skills:
    - requirements_analysis
    - system_design
  workflows:
    - l2_review
  validators:
    - developer_skill_validator
profiles:
  default_loader: minimal-worker
```

## Appendix C: Future Managed Block Contract

managed block은 Phase 6/7 이후에만 사용한다. 현재는 삽입하지 않는다.

```markdown
<!-- BEGIN AIOS MANAGED: v0 [HASH:sha256:...] -->
Generated adapter content goes here.
<!-- END AIOS MANAGED -->
```

규칙:

- managed block 밖의 사용자 작성 내용은 보존한다.
- managed block update는 dry-run diff를 먼저 제공한다.
- drift가 감지되면 기본적으로 중단한다.
- force update는 명시적 사용자 승인 후에만 허용한다.

## Appendix D: Legacy Runtime Note

Cursor, Windsurf, editor-centric AI integration은 v1.2의 active implementation target이 아니다.

legacy 문서나 historical reference에는 남을 수 있지만, 다음 항목으로 취급하지 않는다.

- current supported runtime
- adapter generation target
- validation target
- sync target
- implementation priority
