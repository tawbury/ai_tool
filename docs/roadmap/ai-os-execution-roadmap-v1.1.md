# AI Operating System (.ai OS) Execution Roadmap v1.1

## Executive Summary
본 문서는 다중 AI 클라이언트(Codex, Claude, Gemini, Cursor 등) 환경에서 일관된 규칙과 컨텍스트를 안전하게 관리하기 위한 **AI Operating System (.ai OS)**의 공식 실행 로드맵입니다. v1.1에서는 심볼릭 링크를 배제한 물리적 동기화 아키텍처를 기반으로, 데이터 정합성 보장을 위한 **Sync Manifest**, 사용자 설정 보호를 위한 **Drift Detection**, 그리고 효율적인 자원 관리를 위한 **Selective Activation** 체계를 핵심 코어로 통합하였습니다.

---

## Phase 0: Environment Standardization & Policy Definition

### Goal
물리적 동기화 및 다중 OS 환경 지원을 위한 기반 인프라와 표준 정책을 확립합니다.

### Sub-Phases
*   **0-1 path definition:** 글로벌(`~/.ai/`, `~/.claude/` 등) 및 프로젝트별(`.ai/project/`) 경로의 절대/상대 매핑 테이블 정의.
*   **0-2 permission model:** OS별(POSIX, NTFS) 파일 접근 권한 및 복사 시 권한 유지/변경 정책 수립.
*   **0-3 encoding policy:** 모든 생성/수정 파일에 대해 **UTF-8 without BOM** 인코딩 강제 적용 로직 구현.

### Deliverables
*   Environment Standard Spec Document
*   Encoding Enforcement Script (`ensure-encoding.sh/ps1`)

### Validation
*   Windows/macOS/Linux 환경에서 경로 인식 및 파일 생성 테스트.
*   BOM 유무 및 권한 상속 여부 검증.

### Risks
*   **Permissions:** 특정 OS(Windows)의 권한 제한으로 인한 물리적 복사 실패.
*   **Pathing:** 사용자 홈 디렉토리 경로 환경 변수의 일관성 결여.

### Rollback
*   수동 파일 복원 가이드 제공 및 기존 설정 파일 백업본 원복.

---

## Phase 1: Global Install & SSoT Framework

### Goal
사용자 홈 디렉토리에 단일 진실 공급원(SSoT)을 구축하고, 상태 추적을 위한 데이터 구조를 초기화합니다.

### Sub-Phases
*   **1-1 install-global:** 글로벌 CLI 홈 디렉토리(`~/.ai`) 및 툴별 경로(`~/.codex`, `~/.claude`, `~/.gemini`) 셋업.
*   **1-2 managed block strategy:** 기존 사용자 설정을 보호하며 특정 영역만 업데이트하는 주입 엔진 개발.
*   **1-3 sync manifest schema:** 동기화 이력을 관리할 `sync-manifest.json` 스키마 확립.
*   **1-4 version tracking:** Rule/Agent/Skill 단위의 시맨틱 버저닝 시스템 적용.
*   **1-5 backup policy:** 업데이트 직전 자동 스냅샷 백업 및 보관 주기 설정.

### Deliverables
*   `aios install-global` CLI Command
*   Global SSoT Directory Structure
*   Sync Manifest Initial Schema

### Validation
*   설치 후 글로벌 디렉토리 구조 정합성 확인.
*   Managed Block 주입 시 외부 텍스트 보존 여부 테스트.

### Risks
*   **Config Overwrite:** 기존에 사용자가 직접 수정하던 설정 파일과의 충돌.
*   **Version Drift:** 글로벌 룰 버전 관리 실패로 인한 프로젝트 간 불일치.

### Rollback
*   `aios uninstall-global` 명령어를 통한 설치 이전 상태 복구 및 백업본 복원.

---

## Phase 2: Project Init & Rule Separation

### Goal
프로젝트별 고유 환경을 초기화하고, 필요한 기능만 선택적으로 동기화하는 구독 모델을 활성화합니다.

### Sub-Phases
*   **2-1 init-project:** 프로젝트 루트 내 `.ai/` 폴더 및 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 초기화.
*   **2-2 project rule bootstrap:** 프로젝트 전용 로컬 규칙 템플릿 배포.
*   **2-3 global vs project precedence:** 프로젝트 룰(Override)이 글로벌 룰(Base)을 덮어쓰는 병합 엔진 구현.
*   **2-4 activation.yaml:** 프로젝트에서 사용할 Agent/Skill/Workflow를 명시적으로 선택하는 설정 파일 도입.
*   **2-5 selective activation:** 구독 모델에 기반한 타겟팅 물리 동기화(Selective Sync) 로직.

### Deliverables
*   `aios init-project` CLI Command
*   `activation.yaml` Template
*   Rule Merging Logic Module

### Validation
*   `activation.yaml` 수정 후 동기화 대상 파일 변경 여부 확인.
*   프로젝트 전용 룰이 글로벌 룰보다 우선 적용되는지 결과 검증.

### Risks
*   **Missing Dependency:** 구독하지 않은 에이전트가 다른 규칙에서 참조될 때의 런타임 오류.
*   **Redundancy:** 물리적 복사로 인한 프로젝트 폴더 용량 증가.

### Rollback
*   `.ai/` 폴더 삭제 및 `aios restore-project`를 통한 초기 상태 복구.

---

## Phase 3: Physical Sync & Safety Engine

### Goal
안전하고 원자적인 동기화 엔진을 구축하여 데이터 파괴를 방지하고 상태 정합성을 보장합니다.

### Sub-Phases
*   **3-1 one-way SSoT to Project sync:** 상향식 자동 동기화를 금지하고 하향식(SSoT -> Project) 전파만 허용.
*   **3-2 upstream request model:** 프로젝트 수정을 SSoT로 반영할 때 수동 승인 과정을 거치는 Upstream 프로세스 구축.
*   **3-3 drift detection:** Manifest의 Hash와 로컬 파일 Hash 비교를 통한 무단 수정 감지.
*   **3-4 dry-run / preview / diff:** 실제 파일 쓰기 전 변경 내역(Diff)을 사용자에게 시각적으로 제시.
*   **3-5 atomic update:** 임시 파일(`*.tmp`) 생성 후 최종 교체(Swap) 방식을 통한 쓰기 실패 방지.
*   **3-6 sync transaction:** 동기화 과정을 트랜잭션 ID 단위로 기록하여 부분 실패 방지.
*   **3-7 rollback by transaction id:** 특정 시점의 동기화 상태로 전체 롤백 기능.

### Deliverables
*   `aios sync` CLI Engine
*   Drift Detection Module
*   Diff Viewer Utility

### Validation
*   동기화 도중 프로세스 강제 종료 시 파일 정합성 유지 테스트.
*   사용자 수정분(Drift) 발생 시 경고 및 중단 여부 확인.

### Risks
*   **Split-brain:** 수동 수정이 빈번할 경우 글로벌 룰과의 괴리 발생.
*   **Race Condition:** 여러 프로세스가 동시에 동기화를 시도할 때의 파일 잠금 문제.

### Rollback
*   `aios sync --undo [TransactionID]` 명령어를 통한 원상 복구.

---

## Phase 4: Adapter & Multi-Client Expansion

### Goal
다양한 AI 클라이언트의 특수한 파일 포맷과 경로에 맞게 규칙을 변환하여 주입하는 어댑터 시스템을 구축합니다.

### Sub-Phases
*   **4-1 adapter contract:** 어댑터 구현을 위한 표준 인터페이스(Contract) 정의.
*   **4-2 mapping_rules.yaml:** 소스 룰과 클라이언트 타겟 룰 간의 필드 매핑 및 변환 규칙 정의.
*   **4-3 client-specific target paths:** `.cursor/rules/`, `.claude/config/` 등 클라이언트별 전용 경로 자동 탐색.
*   **4-4 encoding enforcement:** 변환된 결과물에 대해서도 UTF-8 without BOM 정책 강제 적용.
*   **4-5 adapter validation:** 주입된 결과물이 해당 AI 클라이언트에서 정상 파싱되는지 검증 로직.

### Deliverables
*   Adapter Transformation Engine
*   `mapping_rules.yaml` Parser
*   Client Adapters (Codex, Claude, Cursor, Gemini)

### Validation
*   Cursor Rules 폴더에 생성된 규칙이 IDE 상에서 정상 작동하는지 확인.
*   복잡한 JSON/YAML 구조의 설정값이 어댑터 통과 후 유효한지 검증.

### Risks
*   **Breaking Changes:** AI 클라이언트의 업데이트로 인한 설정 파일 스키마 변경.
*   **Incompatibility:** 클라이언트마다 지원하는 마크다운 문법이나 주석 형태의 차이.

### Rollback
*   클라이언트별 백업 폴더에서 원본 설정 복구.

---

## Phase 5: Web Export & Integration

### Goal
로컬 환경을 넘어 웹 기반 AI 채팅 환경으로 컨텍스트를 안전하게 전파합니다.

### Sub-Phases
*   **5-1 export modes:** Global-only, Project-only, Full, Agent-specific 등 다양한 범위의 내보내기 옵션.
*   **5-2 token-limit strategy:** 모델의 컨텍스트 제한에 맞춰 가중치 기반으로 텍스트를 압축하거나 필터링하는 전략.
*   **5-3 secret exclusion policy:** `.env`나 민감 키워드가 포함된 파일을 내보내기 대상에서 강제 제외하는 보안 필터링.

### Deliverables
*   `aios export` CLI Utility
*   Export Template Library

### Validation
*   생성된 익스포트 파일 내 민감 정보 포함 여부 스캔.
*   웹 UI(Claude.ai 등)에 복사 시 토큰 초과 여부 체크.

### Risks
*   **Data Leak:** 보안 필터 우회로 인한 민감 정보 외부 유출.
*   **Context Loss:** 지나친 압축으로 인한 AI의 지시 이행 능력 하락.

### Rollback
*   생성된 익스포트 파일 즉시 삭제 및 필터링 정책 강화.

---

## Appendix A: Sync Manifest Schema
```json
{
  "version": "1.2.3",
  "source_path": "~/.ai/rules/global_rule.md",
  "target_path": "./.ai/project/global_rule.md",
  "source_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "target_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "last_synced_at": "2026-04-29T10:00:00Z",
  "adapter": "default",
  "sync_transaction_id": "tx-987654321"
}
```

## Appendix B: activation.yaml Example
```yaml
# .ai/activation.yaml
active_set:
  agents:
    - developer
    - architect
    - security-expert
  skills:
    - code-review
    - testing-framework
    - deployment-pipeline
  workflows:
    - release-flow
  validators:
    - l2-review-validator
```

## Appendix C: mapping_rules.yaml Example
```yaml
# ~/.ai/install/mapping_rules.yaml
- client: cursor
  source: ~/.ai/rules/coding_style.md
  target: .cursor/rules/style.md
  format: markdown
  merge_strategy: overwrite_block
  encoding: utf-8-no-bom
  managed_block:
    begin: "<!-- BEGIN AIOS -->"
    end: "<!-- END AIOS -->"
  validation: schema_check
```

## Appendix D: Managed Block Format
모든 동기화 대상 파일은 다음 형식을 준수해야 합니다.
```markdown
<!-- BEGIN AIOS MANAGED: v1.1.0 [HASH:sha256:...] -->
## AIOS Managed Rules
(이 영역은 aios sync에 의해 자동으로 업데이트됩니다.)
...
<!-- END AIOS MANAGED -->
```
*   **Begin/End Marker:** 파서가 동기화 영역을 식별하는 기준점.
*   **Metadata Header:** 버전 및 해시 정보를 포함하여 빠른 비교 지원.
*   **Replacement Rule:** 블록 외부의 사용자 작성 내용은 100% 보존됨.

## Appendix E: Sync Safety Policy
1.  **Dry-run Default:** 모든 `aios sync`는 `--yes` 옵션이 없는 한 미리보기를 기본으로 실행함.
2.  **Force Option:** Drift가 발생했을 때 사용자가 명시적으로 `--force`를 사용해야만 덮어쓰기 허용.
3.  **Backup Behavior:** 파일 수정 전 `~/.ai/backups/`에 원본 파일의 복사본을 타임스탬프와 함께 저장.
4.  **Atomic Update:** 원자적 교체가 불가능한 파일 시스템의 경우 트랜잭션 로그를 통해 수동 복구 지원.
5.  **Rollback Behavior:** 롤백 시 Manifest 이력을 역순으로 추적하여 관련 파일을 일괄 복원.
