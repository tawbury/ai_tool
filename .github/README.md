# GitHub Integrations Directory

이 디렉토리는 GitHub의 생태계 및 워크플로우와 관련된 특화 설정 및 AI 지침을 보관합니다.

---

## 📂 파일 구성

| 파일명 | 목적 및 사용 대상 |
|--------|-------------------|
| `copilot-instructions.md` | GitHub Copilot을 사용하는 에디터(VS Code 등) 환경에서 참조할 커스텀 인스트럭션. `.ai/rules/` 의 핵심 제약 조건을 Copilot 형식에 맞게 전달하기 위한 목적으로 사용됩니다. |

*(추후 GitHub Actions CI/CD 워크플로우 정의 파일 등도 이곳에 포함될 수 있습니다.)*

---

## 💡 운영 로직
- 다른 AI 클라이언트 설정(`.claude`, `.cursor` 등)과 마찬가지로, GitHub Copilot 역시 본 저장소의 코어 엔진인 `.ai/rules/rules.md`의 철학을 준수하도록 매핑하는 역할을 합니다.
- 시스템 전체 리팩토링 시, 가이드라인 일관성을 위해 다른 클라이언트 설정 파일과 함께 업데이트 관리 대상이 됩니다.
