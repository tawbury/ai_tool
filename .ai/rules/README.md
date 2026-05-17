# Rules Directory

이 디렉토리는 통합 AI 시스템(Multi-Agent Orchestration)이 준수해야 할 핵심 시스템 규칙과 컨벤션을 정의합니다.

---

## 📄 주요 파일 구성

| 파일명 | 역할 및 내용 |
|--------|--------------|
| `rules.md` | **시스템 통합 규칙 (SSoT)** <br>언어 정책, 디렉토리 제약, L1/L2 협업 프로토콜, 워크플로우 룰 등을 모두 포함하는 마스터 파일 |

---

## 🚀 향후 분리 및 개선 계획 (리팩토링)

현재 통합된 `rules.md`는 재사용성과 프로젝트별 유연성을 높이기 위해 향후 아래와 같이 계층화된 디렉토리 구조로 분리될 예정입니다.

| 제안된 디렉토리 | 설명 및 포함 예정 내용 |
|-----------------|------------------------|
| `global/` | **모든 프로젝트 공통 시스템 제약사항** <br>- `system_constraints.md`: 언어 정책, 파일 무결성<br>- `mcp_integration.md`: MCP 연동 규약<br>- `fallback_protocols.md`: 에러 복구 지침 |
| `project/` | **현 프로젝트 특화 규칙** <br>- `architecture.md`: 프로젝트 특화 기술 스택/아키텍처 규칙<br>- `code_conventions.md`: 코딩 스타일 가이드 |

이 구조는 Claude, Cursor, Windsurf 등 다양한 AI 클라이언트가 자신에게 필요한 룰만 조합(Include)하여 컨텍스트를 구성하도록 확장성을 제공합니다.
