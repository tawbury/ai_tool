# AI Operating System (.ai OS) Execution Roadmap (v1.1)

## Executive Summary

본 로드맵은 심볼릭 링크(Symlink)의 플랫폼 종속성 문제를 제거하고 물리적 동기화(Physical Sync) 기반으로 작동하는 다중 AI 클라이언트용 **AI Operating System (.ai OS)** 구축을 위한 단계별 실행 계획입니다. v1.1에서는 시스템 안정성, 데이터 정합성, 그리고 사용자 설정 보호를 위한 **Sync Manifest 및 Drift 감지 체계**를 추가하여 실전 배포 수준의 안전성을 확보하였습니다.

---

## Phase 0: 환경 및 정책 표준화 (Environment Standardization & Policy Definition)

### Goal
물리적 동기화 메커니즘을 지원하기 위한 기본적인 경로, 권한, 인코딩 및 관리 정책을 확립합니다.

### Sub-Phases
* **0-1 path definition:** 글로벌(`~/.ai/`) 및 프로젝트별(`.ai/project/`) 경로 매핑.
* **0-2 permission model:** OS별 읽기/쓰기 권한 보장 및 보안 가이드라인.
* **0-3 encoding policy:** UTF-8 without BOM 강제화 및 검증 스크립트.

---

## Phase 1: 글로벌 설치 및 SSoT 규칙 관리 시스템 (Global Install & SSoT Framework)

### Goal
사용자 홈 디렉토리에 글로벌 룰을 설치하고, 기존 설정을 파괴하지 않으면서 새로운 `.ai OS` 규칙을 삽입하는 SSoT 프레임워크와 **상태 추적 기반**을 구축합니다.

### Sub-Phases
* **1-1 global-install script:** 초기화 CLI 및 디렉토리 셋업.
* **1-2 SSoT repository definition:** Rule, Agent, Skill, Workflow 템플릿 구조화.
* **1-3 managed block insertion:** `BEGIN/END AIOS MANAGED` 블록 기반 안전 주입 로직.
* **1-4 sync manifest definition (NEW):** 동기화 상태 추적을 위한 `sync-manifest.json` 스키마 정의 (Hash, Version, Timestamp).

### Deliverables
* Global Install Command, Managed Block Updater, **Sync Manifest Schema Spec**.

---

## Phase 2: 프로젝트 초기화 및 규칙 분리 (Project Init & Rule Separation)

### Goal
개별 프로젝트 환경을 초기화하고, 글로벌 룰과 프로젝트 전용 룰을 분리하며 **필요한 기능만 선별적으로 도입**하는 구조를 구축합니다.

### Sub-Phases
* **2-1 init-project:** `.ai/` 프로젝트 폴더 및 초기 템플릿 배치.
* **2-2 rule precedence logic:** 프로젝트 룰(Override) > 글로벌 룰(Base) 우선순위 병합 로직.
* **2-3 agent/skill restructuring:** 물리적 파일 구조로의 모듈 재배치.
* **2-4 selective activation (NEW):** `activation.yaml`을 통한 프로젝트별 에이전트/스킬 구독 모델 구현.

### Deliverables
* Project Init Command, **Activation Config Template (`activation.yaml`)**.

---

## Phase 3: 물리적 동기화 및 안전 엔진 (Physical Sync & Safety Engine)

### Goal
심볼릭 링크 없이 데이터 정합성을 유지하며, 사용자의 로컬 수동 수정을 보호하는 **안전한 동기화 아키텍처**를 완성합니다.

### Sub-Phases
* **3-1 physical sync core:** 단방향(SSoT -> Project) 물리 복사 및 병합 엔진.
* **3-2 adapters logic design:** 다중 클라이언트(Cursor, Claude 등) 대응 변환 인터페이스.
* **3-3 mapping rules contract (NEW):** `mapping_rules.yaml`을 통한 필드 변환 및 검증 규약 확립.
* **3-4 drift detection & atomic sync (NEW):** 로컬 수동 수정 감지(Drift) 및 임시 파일을 활용한 원자적 업데이트(Atomic Update).
* **3-5 dry-run & preview (NEW):** 실행 전 변경 사항을 시각적으로 확인하는 Diff 미리보기 기능.

### Deliverables
* Sync Core Utility, **Drift Checker, Mapping Rules Spec, Dry-run Interface**.

---

## Phase 4: 웹 환경 지원 및 최종 통합 (Web Export & Integration)

### Goal
로컬을 넘어 웹/채팅 환경까지 일관된 컨텍스트를 전파하며 전체 시스템을 통합합니다.

### Sub-Phases
* **4-1 export-chat prompt bundling:** Markdown 기반 One-shot Prompt 생성.
* **4-2 layered export strategy:** 토큰 리밋 대응을 위한 중요도 기반 레이어드 컨텍스트 구성.
* **4-3 web environment templates:** ChatGPT, Claude Web 전용 최적화 템플릿.

---

## [Appendix] Safety & Integrity Architecture

### 1. Sync Manifest (`sync-manifest.json`)
모든 동기화된 파일의 메타데이터를 관리하여 시스템의 투명성을 보장합니다.
*   **Version:** 파일이 파생된 SSoT의 버전.
*   **Source Hash:** 동기화 시점의 원본 Hash.
*   **Target Hash:** 현재 프로젝트 내 파일의 Hash (Drift 감지용).

### 2. Drift 감지 로직
`aios sync` 실행 시 다음 단계를 거칩니다.
1.  **Check:** Manifest의 Source Hash와 현재 로컬 파일의 Hash 비교.
2.  **Detect:** Hash가 다를 경우 사용자가 수동 수정한 것으로 판단 (Drift 발생).
3.  **Action:** 사용자에게 덮어쓰기 여부 확인 또는 `diff` 제공 (무단 삭제 방지).

### 3. 구독 기반 동기화 (Selective Sync)
`activation.yaml`에 정의된 에이전트만 복사하여 프로젝트를 가볍게 유지하고 AI 컨텍스트 노이즈를 최소화합니다.

### 4. 원자적 업데이트 (Atomic Update)
업데이트 중 오류 발생 시 시스템 불능 상태를 막기 위해 `.tmp` 파일을 생성 후 최종 교체하는 방식을 채택합니다.

---

## Final Roadmap Summary
v1.1 고도화안은 **"물리적 동기화는 위험하다"**는 인식을 불식시키기 위해 **상태 기록(Manifest)**과 **수정 감지(Drift Check)**를 핵심 코어로 통합하였습니다. 이를 통해 대규모 팀에서도 안심하고 AI 규칙을 관리할 수 있는 엔터프라이즈급 AI OS 환경을 제공합니다.
