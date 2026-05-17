# Templates: Base Directory

이 디렉토리는 AI 시스템이 참조하는 모든 마크다운 문서 및 산출물 템플릿(`.md`)의 **근간(Base)**이 되는 스키마 및 매핑 규칙 파일들을 보관합니다.

---

## 📂 파일 구성

| 파일명 | 역할 및 목적 |
|--------|--------------|
| `base_schema.md` / `base_meta.md` | 문서 메타데이터 영역(Meta Block)의 필수 필드와 타입 정의 스키마 |
| `base_mapping.md` | 구체적인 템플릿(Task, Report 등)이 생성될 때 상속받아야 하는 필드 매핑 룰 |
| `base_rules.md` / `base_template.md` | 모든 템플릿에 공통으로 적용되는 기본 레이아웃 가이드라인 |
| `planning_base.md` | 기획 단계 산출물(Roadmap, Spec 등)을 위한 베이스 템플릿 |
| `execution_base.md` | 실행 단계 산출물(Run Record 등)을 위한 베이스 템플릿 |
| `management_base.md` | 관리 및 평가 문서(Decision, Report 등)를 위한 베이스 템플릿 |
