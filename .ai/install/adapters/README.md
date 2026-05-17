# Adapters Directory

이 디렉토리는 다양한 AI 클라이언트와의 연동을 자동화하는 YAML 어댑터 파일들을 보관합니다.

---

## 📂 파일 구성

| 파일명 | 매핑 대상 및 목적 |
|--------|-------------------|
| `claude_code.yaml` | `.claude` 디렉토리를 위한 매핑 및 로컬 초기화 룰 정의 |
| `cursor.yaml` | `.cursor` 디렉토리(Cursor IDE)를 위한 룰 세팅 어댑터 |
| `github_copilot.yaml` | `.github` 디렉토리(Copilot)를 위한 커스텀 인스트럭션 어댑터 |
| `windsurf.yaml` | `.windsurf` 디렉토리 전용 설정 매핑 어댑터 |

MCP CLI가 `install` 명령어를 수행할 때 이 어댑터 설정값을 참조하여 타겟 환경의 룰을 동기화합니다.
