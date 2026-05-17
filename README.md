# AI Tool Template Project

이 저장소(Repository)는 다양한 AI 클라이언트(Claude, Cursor, Windsurf 등) 환경에서 **공통된 에이전트(Agent), 스킬(Skill), 워크플로우(Workflow)** 시스템을 일관성 있게 운영하기 위해 구축된 통합 템플릿입니다.

---

## 🚀 프로젝트의 핵심 목표
- **SSoT (Single Source of Truth)**: 모든 룰과 프롬프트는 `.ai/` 폴더 내에 마크다운 기반으로 정의되어 있으며, 어떤 IDE나 CLI 툴을 사용하더라도 동일한 에이전트 페르소나와 검증 체계(Validator)를 따릅니다.
- **다중 AI 지원**: `.claude/`, `.cursor/`, `.windsurf/`와 같은 개별 설정 폴더가 `.ai/`의 코어 룰을 래핑(Wrapping)하여 충돌 없는 확장이 가능합니다.
- **Workflow 기반 자동화**: 기획(PM), 개발(Developer), 재무(Finance), 인사(HR), 콘텐츠(Contents-Creator) 등 다중 에이전트가 협업하는 운영 루프(Roadmap -> Task -> Run Record)를 지원합니다.

---

## 📂 최상위 디렉토리 구조 및 안내

| 디렉토리/파일 | 역할 및 상세 안내 링크 |
|---------------|------------------------|
| `.ai/` | 통합 AI 시스템 코어 엔진 (Rules, Agents, Skills, Workflows 등). 전체 로직의 원천. ([자세히 보기](./.ai/README.md)) |
| `mcp-cli/` | Model Context Protocol 연동을 위한 전용 노드(Node.js) 기반 CLI 툴 패키지. ([자세히 보기](./mcp-cli/README.md)) |
| `.claude/` | Claude Code (CLI) 환경을 위한 로컬 설정. ([자세히 보기](./.claude/README.md)) |
| `.cursor/` | Cursor IDE 전용 환경 설정 및 룰 매핑. ([자세히 보기](./.cursor/README.md)) |
| `.windsurf/` | Windsurf 에디터 전용 환경 설정 및 룰 매핑. ([자세히 보기](./.windsurf/README.md)) |
| `.github/` | GitHub Copilot 명령어 연동 및 GitHub Actions 관련 설정. ([자세히 보기](./.github/README.md)) |
| `AI_System_Analysis_Report.md` | 전체 시스템 현황 분석 및 향후 Global/Project 단위 리팩토링 제안서. |

본 프로젝트의 확장 및 세부 모듈 변경 가이드는 [AI_System_Analysis_Report.md](./AI_System_Analysis_Report.md) 및 각 폴더 내부의 `README.md`를 참고해 주십시오.
