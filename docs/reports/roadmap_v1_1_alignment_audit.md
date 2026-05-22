# Roadmap v1.1 정렬 감사 보고서

## 1. 감사 요약

대상 문서:

- `docs/roadmap/ai-os-execution-roadmap-v1.1.md`

현재 구현 상태:

- `aios inspect` 구현 및 `0 fail, 0 warning` 기준선 유지
- `aios load-context` v1 구현
- `aios validate` v1 출력 사용성 개선 구현
- `aios inventory` v0 구현
- 공유 primitive 구현
  - `frontmatter.py`
  - `references.py`
  - `status.py`
  - `contracts.py`
  - `inventory.py`
- 문서 governance runtime-facing rule 존재
- 공식 runtime은 Codex CLI, Gemini CLI, Claude Code CLI
- Cursor/Windsurf/editor-centric integration은 legacy/deprecated로 분류

결론:

로드맵 v1.1은 핵심 원칙 일부는 여전히 유효하지만, 현재 구현 방향과 단계 순서가 크게 달라졌다. 특히 v1.1은 sync manifest, global install, physical sync, adapter expansion을 너무 이른 단계에 배치한다. 현재 `.ai OS`는 읽기 전용 integrity/validation/context tooling을 먼저 안정화하는 방향으로 진행 중이므로, v1.1은 patch보다 v1.2로 supersede하는 것이 적절하다.

권고:

- v1.1은 historical/superseded roadmap으로 표시
- v1.2를 새 canonical execution roadmap으로 작성
- v1.2의 핵심 순서는 `inspect -> inventory -> validate -> semantic load-context -> governance/contracts -> sync planning -> physical sync -> adapter generation -> orchestration`이 되어야 한다.

## 2. Alignment Matrix

| v1.1 Phase | v1.1 의도 | 현재 구현과의 정렬 | 상태 | 판단 |
|---|---|---:|---|---|
| Phase 0: Environment Standardization & Policy Definition | 경로, 권한, encoding policy 표준화 | 중간 | 부분 유효 | UTF-8/BOM, symlink policy는 inspect에 반영됨. OS별 install/permission 표준화는 아직 이르다. |
| Phase 1: Global Install & SSoT Framework | `~/.ai`, global install, managed block, sync manifest | 낮음 | 미구현/조기 | `.ai/` SSoT 원칙은 유효하지만 global install, manifest, managed block은 현재 read-only 단계보다 앞서 있다. |
| Phase 2: Project Init & Rule Separation | project init, rule merge, activation.yaml, selective sync | 중간 | 일부 유효/순서 조정 필요 | rule separation과 activation 개념은 유효하나 project init과 selective physical sync는 아직 이르다. semantic loading profile과 validation이 먼저다. |
| Phase 3: Physical Sync & Safety Engine | one-way sync, drift detection, dry-run, atomic update, rollback | 낮음 | 방향 유효/시기 조기 | symlink 회피와 drift detection 방향은 유효하지만 현재는 sync 구현 전 단계다. validate/inventory/semantic loader 이후로 밀어야 한다. |
| Phase 4: Adapter & Multi-Client Expansion | adapter contract, client-specific target path, Cursor 포함 | 낮음 | outdated | 공식 runtime 정책과 충돌한다. Cursor/Windsurf/editor-centric target은 legacy로 내려야 한다. adapter generation도 sync 이후가 아니라 contract 안정화 이후 별도 단계여야 한다. |
| Phase 5: Web Export & Integration | web chat export, token-limit, secret exclusion | 중간 | 나중 단계 유효 | semantic loader와 context budget 기반으로 나중에 구현 가능하다. 현재는 export보다 loader/validator/inventory가 우선이다. |

## 3. Current Implementation Mapping

| 현재 구현 | v1.1에 대응되는 영역 | 비고 |
|---|---|---|
| `aios inspect` | Phase 0 validation, Phase 3 drift/safety의 전단계 | 실제 구현은 sync 이전 integrity baseline이다. v1.1에는 이 독립 단계가 없다. |
| `aios load-context` v1 | Phase 5 token-limit/export, Phase 2 selective activation과 관련 | 현재는 export가 아니라 semantic context extraction이다. v1.1에는 semantic loader 단계가 없다. |
| `aios validate` v1 output usability | Phase 0/2 validation과 관련 | 현재는 executable contract validation이다. v1.1에는 validate runtime 계층이 명시적으로 부족하다. |
| `aios inventory` v0 | Phase 1/2 SSoT structure와 관련 | sync 전에 필요한 read-only inventory layer다. v1.1에는 독립 inventory 단계가 없다. |
| `frontmatter.py` | Phase 0 standardization | lightweight parser primitive로 구현됨. |
| `references.py` | Phase 0/3 path/reference integrity | sync가 아니라 reference primitive로 구현됨. |
| `status.py` | Phase 0 command convention | command status/exit code convention의 내부 primitive. |
| `contracts.py` | Phase 2 rule/agent contract | agent contract field를 공유화. |
| Documentation governance runtime-facing rules | v1.1에 직접 대응 없음 | 현재 방향에서는 runtime consumption boundary가 핵심인데 v1.1에는 약함. |

## 4. 여전히 유효한 v1.1 요소

유효한 원칙:

- `.ai/`를 source of truth로 두는 방향
- symlink 기반 sync를 피하고 물리 파일 기반 관리로 가는 방향
- UTF-8 without BOM 정책
- drift detection 필요성
- dry-run/preview/diff 필요성
- managed block 개념
- adapter는 thin compatibility layer여야 한다는 방향
- context export에서 secret exclusion과 token limit을 고려해야 한다는 방향

단, 대부분은 지금 즉시 구현할 항목이 아니라 read-only validation/context tooling 이후 단계로 재배치해야 한다.

## 5. Outdated / Premature / Misordered Assumptions

### 5.1 Outdated assumptions

| 항목 | 문제 |
|---|---|
| Cursor를 current client로 취급 | 현재 공식 runtime 정책은 Codex CLI, Gemini CLI, Claude Code CLI다. Cursor는 legacy/deprecated다. |
| `.cursor/rules/` 같은 editor-specific path | CLI-first runtime architecture와 충돌한다. |
| “multi-client expansion”을 broad client support로 표현 | 현재 방향은 broad client가 아니라 thin runtime adapter다. |
| IDE 정상 작동 검증 | editor-centric validation이며 현재 runtime policy와 충돌한다. |

### 5.2 Premature assumptions

| 항목 | 문제 |
|---|---|
| `aios install-global` | local read-only runtime validation이 안정화되기 전에는 이르다. |
| `sync-manifest.json` | inventory, validate, semantic loader contract가 더 안정화된 뒤 설계해야 한다. |
| managed block insertion | adapter generation/sync가 아직 금지된 단계다. |
| atomic update/rollback transaction | sync safety에는 필요하지만 현재 구현 순서상 뒤로 가야 한다. |
| `aios export` | semantic loader와 context policy 안정화 이후가 적절하다. |

### 5.3 Misordered assumptions

| v1.1 순서 | 현재 권장 순서 |
|---|---|
| global install 후 SSoT framework | local `.ai` runtime source-of-truth 검사와 inventory 먼저 |
| activation.yaml 후 selective physical sync | semantic loading profile과 validation boundary 먼저 |
| sync manifest를 early core로 배치 | validate/inventory/load-context 후 sync planning으로 배치 |
| adapter expansion이 sync 직후 | runtime contract와 validation 안정화 후 adapter generation |
| web export가 adapter 다음 | semantic loader와 context budget 정책 이후 별도 단계 |

## 6. Runtime Policy Conflicts

| Reference / Assumption | Conflict | 권장 처리 |
|---|---|---|
| Cursor | legacy/deprecated runtime임에도 active target으로 서술 | v1.2에서는 legacy note로 이동 |
| Cursor Rules folder | editor-centric path | runtime adapter target에서 제거 |
| IDE validation | CLI-first 정책과 충돌 | historical note 또는 legacy appendix로 이동 |
| broad multi-client expansion | 현재는 공식 runtime 3개에 집중 | “supported CLI runtimes”로 축소 |
| client-specific target paths | adapter generation 이전에 premature | thin adapter contract 이후로 이동 |
| Sync manifest appendix | 현재 read-only phase와 충돌 | sync phase의 future appendix로 이동 |
| Managed block format | adapter/sync 구현 전 premature | v1.2 후반 phase로 이동 |

## 7. v1.1 처리 권고

판정:

- `patched as v1.1`: 비권장
- `superseded by v1.2`: 권장
- `archived as historical`: v1.2 작성 후 권장

이유:

v1.1은 단순 오탈자나 일부 표현 수정으로 해결될 수준이 아니다. 현재 구현은 이미 read-only inspect/validate/inventory/semantic-loader 중심으로 전개되었고, sync/manifest/adapter는 의도적으로 뒤로 밀렸다. 또한 Cursor/editor-centric 전제가 현재 runtime policy와 충돌한다. 따라서 v1.1을 patch하면 문서 내부 단계 구조가 어색해지고, 향후 구현자에게 잘못된 우선순위를 줄 위험이 있다.

권장 상태:

- v1.1 상단에 `Status: Superseded by v1.2` 표시
- v1.1은 `docs/roadmap/`에 historical roadmap으로 유지하거나 `docs/historical/` 정책이 생긴 뒤 이동
- v1.2를 새 canonical roadmap으로 작성

## 8. Recommended Roadmap v1.2 Phase Structure

### Phase 0: Runtime Policy and Documentation Governance Baseline

목표:

- 공식 runtime 범위 확정
- `.ai/` runtime source of truth 확정
- docs와 runtime contract boundary 확정

포함:

- Codex CLI, Gemini CLI, Claude Code CLI를 current supported runtime으로 명시
- Cursor/Windsurf/editor-centric integration은 legacy/deprecated로 명시
- `.ai/rules/operations/documentation-governance.rules.md`를 runtime-facing governance rule로 반영
- UTF-8 without BOM, symlink 금지, root adapter thin policy 유지

### Phase 1: Read-only Repository Integrity Layer

목표:

- 파일을 수정하지 않는 구조/참조 무결성 검사 안정화

포함:

- `aios inspect`
- stale reference detection
- BOM/symlink detection
- root adapter existence check
- agent frontmatter reference check
- Obsidian/Markdown obvious link check

현재 상태:

- 대부분 구현됨
- `0 fail, 0 warning` baseline 유지 중

### Phase 2: Shared Runtime Primitives and Inventory

목표:

- inspect/validate/load-context가 공유할 primitive 안정화

포함:

- `frontmatter.py`
- `references.py`
- `status.py`
- `contracts.py`
- `inventory.py`
- `aios inventory`
- repository item model

현재 상태:

- 구현됨
- 향후 inspect/validate target discovery와 통합 예정

### Phase 3: Executable Contract Validation Layer

목표:

- `.ai` 파일이 실행 가능한 contract를 만족하는지 검증

포함:

- `aios validate`
- agent contract validation
- skill basic structure validation
- workflow basic contract validation
- validator index integrity
- JSON summary usability
- human-review-only boundary 유지

현재 상태:

- v1 output usability까지 구현됨
- pass item model은 아직 없음

### Phase 4: Semantic Loading and Context Budget Layer

목표:

- runtime worker가 생기기 전 semantic context extraction 기준 확립

포함:

- `aios load-context`
- governance annotation parser
- heading fallback
- legacy section fallback
- profile별 include/exclude policy
- context provenance/trace
- context budget policy

현재 상태:

- v1 구현됨
- runtime orchestration과 분리된 read-only loader로 유지

### Phase 5: Runtime Contract and Activation Planning

목표:

- sync 전 activation/contract 설계를 명확히 함

포함:

- `activation.yaml` 설계
- semantic loading profile 확장
- agent registry 설계
- validator registry 설계
- runtime consumption boundary
- project/global rule precedence 문서화

현재 상태:

- 일부 감사/계획 문서 존재
- 아직 구현 단계 아님

### Phase 6: Sync/Manifest Safety Design

목표:

- physical sync 구현 전 safety contract 확정

포함:

- sync manifest schema
- source hash/target hash
- drift detection
- dry-run contract
- atomic update design
- managed block contract
- rollback design

현재 상태:

- 구현 금지 단계
- v1.1의 Phase 1/3 내용을 이 단계로 재배치

### Phase 7: Physical Sync Implementation

목표:

- validation과 manifest design이 안정화된 뒤 physical sync 구현

포함:

- `aios sync --dry-run`
- one-way SSoT propagation
- managed block insertion
- drift stop policy
- transaction log
- rollback

현재 상태:

- 미구현
- 아직 착수하지 않는 것이 맞음

### Phase 8: Thin Runtime Adapter Generation

목표:

- 공식 CLI runtime용 thin adapter 생성

포함:

- Codex CLI adapter
- Gemini CLI adapter
- Claude Code CLI adapter
- root adapter regeneration policy
- no duplicated rule bodies
- adapter verification

제외:

- Cursor/Windsurf active support
- IDE-centric path generation

### Phase 9: Export and External Integration

목표:

- semantic loader 기반으로 web/export 기능 구현

포함:

- `aios export`
- token budget filtering
- secret exclusion
- profile-specific export
- copied context trace

### Phase 10: Orchestration and Worker Execution

목표:

- 충분한 validation, loading, sync, adapter 안정화 이후 worker runtime 검토

포함 가능:

- worker profile
- task dispatch
- runtime execution trace
- reviewer/strategist/worker context profiles

제외:

- v1.2 초기 구현 범위
- tmux 선행 설계

## 9. Exact Suggested Changes if Rewrite Is Approved

v1.2 rewrite 승인 시 적용할 변경:

1. 문서 제목 변경
   - from: `AI Operating System (.ai OS) Execution Roadmap v1.1`
   - to: `AI Operating System (.ai OS) Execution Roadmap v1.2`

2. 상단 status block 추가

```markdown
Status: Active
Supersedes: ai-os-execution-roadmap-v1.1.md
Runtime policy: CLI-first
Current supported runtimes: Codex CLI, Gemini CLI, Claude Code CLI
Legacy/deprecated runtimes: Cursor, Windsurf, editor-centric AI integrations
Implementation boundary: read-only validation/context tooling before sync
```

3. Executive Summary 재작성
   - physical sync 중심 요약 제거
   - read-only inspect/validate/inventory/load-context 선행 원칙 추가
   - `.ai/` runtime source of truth 명시
   - sync/manifest는 later safety phase로 이동

4. Phase 0 재작성
   - environment standardization만이 아니라 runtime policy와 documentation governance 포함

5. Phase 1을 read-only integrity layer로 변경
   - `aios inspect`
   - reference integrity
   - encoding/symlink policy

6. Phase 2를 shared primitives/inventory로 변경
   - `frontmatter.py`
   - `references.py`
   - `status.py`
   - `contracts.py`
   - `inventory.py`
   - `aios inventory`

7. Phase 3을 validation layer로 변경
   - `aios validate`
   - executable contract validation
   - human-review-only boundary

8. Phase 4를 semantic loading layer로 변경
   - `aios load-context`
   - governance annotation layer
   - semantic profiles

9. 기존 sync manifest, managed block, atomic update, rollback은 후반 phase로 이동
   - 새 Phase 6/7

10. Adapter phase에서 Cursor 제거
    - active adapters: Codex CLI, Gemini CLI, Claude Code CLI
    - Cursor/Windsurf는 legacy appendix로 이동

11. Web export는 semantic loader 기반으로 재정의
    - export modes는 유지
    - token-limit strategy는 context budget policy와 연결

12. Appendix 정리
    - `sync-manifest.json`: future sync phase appendix
    - `activation.yaml`: activation planning appendix
    - managed block: future adapter/sync appendix
    - Cursor examples: 제거 또는 legacy appendix

## 10. Risks if v1.1 Remains Active

| Risk | Severity | 설명 |
|---|---|---|
| 잘못된 구현 우선순위 | High | sync/manifest/adapter가 validate/loader보다 먼저 구현되어 현재 안정화 방향을 깨뜨릴 수 있다. |
| runtime policy 혼선 | High | Cursor/editor-centric target이 active support로 오해될 수 있다. |
| source-of-truth 혼선 | Medium | global install과 project init이 현재 local `.ai` SSoT 안정화보다 먼저 보일 수 있다. |
| context architecture 누락 | Medium | semantic loader와 context budget이 roadmap 핵심 phase로 보이지 않는다. |
| validation layer 과소평가 | Medium | 현재 구현된 validate/inventory primitive가 임시 도구처럼 취급될 수 있다. |

## 11. Final Recommendation

v1.1은 patch하지 말고 v1.2로 supersede해야 한다.

v1.1에 남길 최소 변경은 다음 정도가 적절하다.

```markdown
> Status: Superseded
> Superseded by: ai-os-execution-roadmap-v1.2.md
> Note: This roadmap predates the current CLI-first read-only inspect/validate/load-context/inventory implementation sequence.
```

그 다음 v1.2에서 현재 구현 현실을 기준으로 phase 구조를 재작성해야 한다. 특히 sync/manifest/adapter/orchestration은 지금 구현할 대상이 아니라, read-only runtime integrity와 semantic validation 계층이 안정화된 이후의 후속 단계로 내려야 한다.
