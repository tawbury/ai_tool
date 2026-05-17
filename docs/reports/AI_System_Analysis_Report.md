# AI System 아키텍처 현황 및 구조 개선(Refactoring) 제안 보고서

**최초 작성일**: 2026-04-29  
**최근 업데이트**: 2026-04-29 (세션 업데이트 반영)  
**대상 프로젝트**: `_templates/ai_tool`

---

## 1. 개요 및 목적
본 보고서는 구축된 `.ai/` 통합 시스템 및 MCP 기반 CLI 툴의 심층적인 구조 현황을 분석합니다.
전수 조사를 통해 파악된 수십 개의 스킬(Skill)과 워크플로우(Workflow), 그리고 클라이언트 연동 어댑터(Adapter)의 역할을 명확히 규명하고, 이를 기반으로 다양한 멀티 AI 도구(Claude, Cursor, Windsurf, Gemini, Deepseek 등) 환경에서 시스템이 유연하게 확장될 수 있도록 **Global Rules**와 **Project Rules**의 분리 등 구조적 개선 방안을 제안합니다.

---

## 2. 시스템 아키텍처 및 디렉토리 현황 심층 분석

현재 시스템은 코어 엔진 역할을 하는 `.ai/` 디렉토리를 중심으로, 애플리케이션 실행을 돕는 `mcp-cli/`, 그리고 각 환경별 IDE 설정 파일들(`.claude/`, `.cursor/`, `.windsurf/`, `.github/`)이 모듈화되어 있습니다.

### 2.1 통합 AI 코어 엔진 (`.ai/` 하위 시스템)

#### A. Rules (`.ai/rules/`)
- **현황 (Update 반영)**: 기존 `rules.mdc` 확장자 체계에서 범용적인 `rules.md` 마스터 파일 체계로 전면 마이그레이션이 완료되었습니다.
- **인코딩 정책 신설**: 한글 텍스트 깨짐 현상을 방지하기 위해, 모든 파일은 **UTF-8(without BOM)** 포맷으로 강제 저장하고 관리하도록 룰이 업데이트 되었습니다.

#### B. Agents (`.ai/agents/`)
- **현황**: 도메인별 5대 핵심 에이전트(`pm.agent.md`, `developer.agent.md`, `contents-creator.agent.md`, `finance.agent.md`, `hr.agent.md`) 페르소나가 정의되어 있음.

#### C. Skills (`.ai/skills/`)
단일 과업 단위의 스킬들이 에이전트별로 엄격히 분리되어 방대한 생태계를 구성 중입니다.
- **`pm/` (9개)**: PRD 정의, 제품 수명 주기, 리스크 관리 등 전략/기획 포커스
- **`developer/` (18개)**: 백엔드/프론트 통합 스택, 시스템 아키텍처, 성능/DB 최적화, 카오스 엔지니어링 등 전문 엔지니어링 포커스
- **`finance/` (14개)**: 예산 관리, 수익성 모델링, 재무 리스크 검증, 투자 포트폴리오 관리 등
- **`hr/` (15개)**: L1/L2 레벨 체크, 퍼포먼스 리뷰, 에이전트 태스크 할당, 역량 개발 추적 등 조직 관리
- **`contents-creator/` (20개+)**: `business`, `interactive`, `text`, `video`, `visual` 의 5개 도메인으로 세분화되어 텍스트부터 3D 렌더링 가이드까지 커버
- **`_shared/`**: 로드맵, Run Record 작성 등 전 에이전트 공통 운영 루프(Operational Loop) 스킬과 콘텐츠 코어 프레임워크 보관

#### D. Workflows & Validators (`.ai/workflows/`, `.ai/validators/`)
- **현황**: 기획-실행-보고-피드백에 이르는 파이프라인. 각 단계별로 문서 구조와 메타데이터 규격을 강제하는 수십 개의 검증기(Validator) 스크립트 기반 구성.

#### E. Templates (`.ai/templates/`)
- **현황**: `_base/` 폴더를 통해 메타데이터 매핑 스키마와 기본 레이아웃을 상속받는 구조. Roadmap, Task, Run Record 등의 핵심 템플릿 포함.

### 2.2 MCP CLI 시스템 (`mcp-cli/`)
- **현황**: 노드 기반(TypeScript) 실행기. `src/` 내부에 `cli.ts`를 진입점으로 `commands/` (init, install, sync)와 `utils/` (파일/yaml 파싱)를 통해 AI 환경 초기화와 룰 동기화 담당. (내부에 중첩된 잉여 `src/src/` 폴더 존재, 추후 정리 권장)

### 2.3 통합 및 배포 관리 영역 (`.ai/install/`, `.ai/export/`)
- **`install/`**: `adapters/` 내에 `claude_code.yaml`, `cursor.yaml` 등 환경별 매핑 룰 보관. `templates/`에 배포될 설정 베이스 존재.
- **`export/`**: `chat/` 하위에 `chatgpt/`, `claude-web/`, `gemini/`를 두어 외부 웹 클라이언트로 스냅샷/프롬프트를 내보내는 브릿지 역할.

### 2.4 클라이언트 설정 환경 및 동기화
- **심볼릭 링크 정책 폐기 (Update 반영)**: 기존에는 `.claude`, `.cursor` 등에서 `.ai/rules`를 심볼릭 링크로 엮어 사용했으나, Windows 권한 문제 및 IDE 네이티브 인식 버그를 해결하기 위해 **심볼릭 링크 사용을 전면 금지**했습니다.
- **MCP 물리적 동기화 체제**: 현재는 `docs/plan/symlink_refactoring_plan.md`가 수립되어, 모든 룰은 `mcp-cli sync` 명령을 통해 물리적으로 덮어쓰고 동기화하는 체제로 전환 중입니다.

---

## 3. 리팩토링 및 구조 개선(Refactoring) 전략 제안

현재 시스템은 에이전트와 스킬의 분리가 훌륭하게 되어 있으나, **시스템 전체를 통제하는 제약사항(Rules)이 단일 파일에 의존하고 있어 확장이 제한적**입니다. 이를 다음과 같이 개선할 것을 제안합니다.

### 3.1 Global Rules와 Project Rules의 계층 분리

현재의 마스터 `rules.md`를 해체하여, AI가 절대적으로 지켜야 할 **"글로벌 시스템 제약"**과 현재 진행 중인 저장소의 **"프로젝트 도메인 제약"**으로 분할합니다.

```text
.ai/rules/
├── global/
│   ├── system_constraints.md       # 템플릿 양식 준수, 언어/인코딩 정책(UTF-8), 파일 무결성
│   ├── mcp_integration.md          # 물리적 동기화 규약 및 어댑터 매핑 규칙
│   ├── agent_protocol.md           # L1/L2 권한 및 Operational Loop(Roadmap->Task) 준수 규약
│   └── fallback_protocols.md       # Validation 실패 시 재시도/복구 프로토콜
└── project/
    ├── architecture.md             # 현 프로젝트의 기술 스택 (예: React, Next.js 등) 가이드라인
    ├── code_conventions.md         # 언어/프레임워크 특화 코딩 스타일, 린트 룰
    └── domain_dictionary.md        # 비즈니스 도메인 용어집
```

**효과**: 새로운 프로젝트를 시작할 때 `global/`은 그대로 재사용(Copy)하고, `project/` 규칙만 갈아 끼워 넣음으로써 일관성 유지 및 컨텍스트 비용 최적화 달성.

### 3.2 다중 AI 도구(Multi-AI Client) 지원 및 확장성 확보 (Deepseek 등)

각 클라이언트(Cursor, Claude 등)의 설정 파일에 직접 프롬프트를 하드코딩하지 않고, **레퍼런스(Pointer) 패턴**을 고도화합니다.

1. **설정 파일 역할 축소**: `.cursorrules`, `claude_code.yaml` 등은 오직 *"이 AI 모델의 Context에 `.ai/rules/global`과 `.ai/rules/project`를 로드하라"*는 명령만 수행하도록 축소.
2. **동기화 유틸리티(Sync) 고도화**: `mcp-cli/src/commands/sync.ts`의 로직을 개선하여, 새로운 AI 에디터(Deepseek, Roo Code 등)가 추가되더라도 `install/adapters/` 에 YAML 하나만 추가하면 곧바로 룰이 물리적으로 배포되도록 구성.
3. **Export 최적화**: 웹 전용 챗봇 환경(ChatGPT, Gemini)에서는 파일 시스템 직접 접근이 어려우므로, `mcp-cli export` 명령 시 분리된 Global/Project 룰을 하나로 압축된 프롬프트(One-shot Prompt) 텍스트로 합쳐 `.ai/export/chat/` 에 덤프하는 기능 강화.

---

## 4. 기대 효과 및 Next Action

### 기대 효과
- **완전한 SSoT 확보**: 어떤 에디터를 쓰든 분리된 계층형 룰(`.ai/rules/`)에서 동일한 페르소나와 검증(Validator) 기준을 가져옵니다.
- **컨텍스트 효율(Context Window Efficiency)**: 단일 거대 파일 대신, 글로벌 룰과 현재 작업 중인 스킬/템플릿만 조합(Include)하여 LLM 비용을 절약합니다.
- **안정성 향상**: 심볼릭 링크 및 인코딩 깨짐 문제를 원천 차단하여, 크로스 플랫폼에서도 100% 신뢰할 수 있는 개발 환경을 구축했습니다.

### Next Action Item (우선순위 순)
1. `.ai/rules/rules.md`를 `global/`과 `project/` 디렉토리로 물리적 분할 작업 진행.
2. `symlink_refactoring_plan.md` 에 명시된 대로 워크스페이스 내 잔존하는 모든 심볼릭 링크들을 완전히 제거하고 `mcp-cli` `sync` 로직 적용.
3. 잔재물로 판단되는 `mcp-cli/src/src/` 디렉토리의 안전성 검토 후 삭제 진행.
