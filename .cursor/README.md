# Cursor IDE Configuration

이 디렉토리는 Cursor 에디터를 위한 프로젝트 로컬 설정 및 AI 프롬프트 룰 파일들을 포함합니다.

## 역할 및 구조
- Cursor 전용 프롬프트 및 `rules/` 파일을 보관하여, 개발자가 에디터 내에서 AI 기능을 사용할 때 참조할 수 있도록 합니다.
- 시스템 전체의 `.ai/` 공통 규칙과 Cursor 고유 기능(Context, RAG 기반 검색 등) 간의 연결 고리 역할을 수행합니다.

## 공통 규칙 연동
- 이 디렉토리 내의 규칙 파일들은 하드코딩된 규칙보다는 `.ai/rules/rules.md`를 참조(include/import 형태)하거나 포인터 역할만 하도록 구성하는 것을 권장합니다.
- AI 도구(Claude, Gemini 등) 통합 시, Cursor가 단독으로 튀지 않고 공통된 워크플로우를 유지하도록 확장성을 보장합니다.
