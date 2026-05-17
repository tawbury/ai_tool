# Chat Export Directory

이 디렉토리는 터미널 환경이 아닌 웹 기반의 AI 클라이언트(ChatGPT, Claude Web, Gemini 등)에서 활용하기 위해 대화 내용이나 프롬프트 구조를 내보내기(Export)할 때 사용되는 중간 저장소 역할을 합니다.

---

## 📂 하위 디렉토리 구성

각 웹 클라이언트의 특성에 맞춰 최적화된 포맷으로 관리됩니다.

| 디렉토리명 | 목적 및 사용 대상 |
|------------|-------------------|
| `chatgpt/` | ChatGPT (Web) 환경에서 사용하기 적합한 형태의 프롬프트 및 대화 스냅샷 데이터 |
| `claude-web/` | Claude Web (Project/Artifact) 환경에서 사용하기 적합한 형태의 컨텍스트 스냅샷 |
| `gemini/` | Gemini (Web/Advanced) 환경을 위한 대화 컨텍스트 데이터 보관 |
