# Claude IDE Configuration

이 디렉토리는 Claude Code(CLI) 및 관련 Anthropic AI 에이전트를 위한 프로젝트 로컬 설정 파일들을 포함합니다.

## 역할 및 구조
- `.ai/rules` 및 `.ai/` 구조 내의 공통 워크플로우(SSoT)를 참조하여 Claude 모델이 이 프로젝트를 분석하고 코드를 생성할 때 필요한 제약 조건(Constraints)을 반영합니다.
- `settings.json`, `settings.local.json` 등은 Claude 환경에 종속적인 설정(예: 단축키, 프롬프트 파일 경로 등)을 관리합니다.

## 공통 규칙 연동
- Claude는 초기 로드 시 이 폴더의 설정을 거쳐 최종적으로 글로벌 시스템 규칙(`.ai/rules/rules.md`)에 바인딩됩니다.
- 향후 규칙들이 `global` / `project` 로 분리될 경우, Claude 설정에서 이 두 경로를 순차적으로 로드하도록 스크립트 또는 프롬프트를 조정할 수 있습니다.
