# Runtime Normalization Audit

## 1. 개요

이 문서는 `.ai OS` 저장소를 CLI-first AI 운영체제 구조로 정리하기 위한 runtime terminology 및 legacy reference 감사 보고서다.

현재 공식 지원 runtime은 다음 세 가지로 한정한다.

- Codex CLI
- Gemini CLI
- Claude Code CLI

legacy 또는 deprecated runtime으로 분류할 대상은 다음이다.

- Cursor
- Windsurf
- editor-centric AI integrations
- `.cursorrules` style legacy patterns

이번 작업은 audit only 범위로 수행했다. 파일 자동 수정, sync, manifest, adapter generation은 수행하지 않았다.

## 2. 검색 범위와 기준

검색 키워드:

- `.cursorrules`
- `cursor`
- `windsurf`
- `editor`
- `IDE`
- `Cursor`
- `Windsurf`

검색 범위:

- 전체 저장소
- 제외: `.git`, `node_modules`, `dist`, `build`

현재 `aios inspect v1`도 `.ai/**/*.md` 내 stale `.cursorrules`와 일부 상대 링크 문제를 warning으로 보고하고 있다.

## 3. Executive Summary

현재 저장소에는 Cursor/Windsurf를 실제 active runtime으로 사용하는 실행 코드나 설정 디렉터리는 보이지 않는다. 그러나 문서와 workflow/skill 설명에는 과거 editor-centric 또는 multi-client 관점의 표현이 남아 있다.

가장 먼저 정리할 대상은 `.ai/templates`, `.ai/validators`, `.ai/workflows/hr_evaluation.workflow.md`에 남아 있는 `.ai/.cursorrules` 참조다. 이 참조는 현재 SSoT인 `.ai/rules/rules.md` 정책과 직접 충돌한다.

Cursor/Windsurf 관련 문서는 대부분 historical note 또는 과거 refactoring design/report에 해당한다. 이 문서들은 삭제보다 보존하되, 현재 아키텍처 문서에서는 legacy/deprecated로 명시하는 것이 좋다.

IDE/editor 표현은 두 종류로 나뉜다.

- architecture assumption: “IDE AI가 저장소를 읽고 재개한다” 같은 런타임 가정
- 일반 문맥: text editor, image editor, editorial 등 AI runtime과 무관한 표현

architecture assumption에 해당하는 문장은 CLI-first 용어로 rewrite하는 것이 안전하다.

## 4. Findings Classification

### 4.1 Active Runtime Dependency

| 파일 | 참조 | 분류 | 판단 |
|---|---|---|---|
| 없음 | Cursor/Windsurf active config | active runtime dependency 없음 | 현재 `.cursor/`, `.windsurf/` 디렉터리나 실행 경로는 검색 결과에 없음 |
| `.gemini/settings.json`, `.gemini/policies/*` | Gemini | active runtime dependency | 공식 지원 runtime |
| `.claude/*` | Claude Code | active runtime dependency | 공식 지원 runtime |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | Codex/Claude/Gemini adapters | active adapter | 공식 지원 runtime adapter |

### 4.2 Stale Legacy Wording: `.cursorrules`

| 파일 | 참조 | 분류 | 권장 |
|---|---|---|---|
| `.ai/templates/anchor_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/architecture_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/decision_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/prd_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/README.md` | `[[../.cursorrules]]` | stale legacy wording | rewrite |
| `.ai/templates/report_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/spec_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/templates/task_template.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/anchor_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/architecture_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/decision_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/prd_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/report_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/spec_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/validators/task_validator.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |
| `.ai/workflows/hr_evaluation.workflow.md` | `.ai/.cursorrules` | stale legacy wording | rewrite |

권장 replacement:

| 기존 | 권장 |
|---|---|
| `.ai/.cursorrules` | `.ai/rules/rules.md` |
| `[[../.cursorrules]]` in `.ai/templates/README.md` | `[[../rules/rules.md]]` |

### 4.3 Cursor / Windsurf Historical Notes

| 파일 | 참조 | 분류 | 권장 |
|---|---|---|---|
| `docs/plan/multi_ai_cli_rules_refactoring_design.md` | `.cursor/rules`, `.windsurf/rules`, Cursor/Windsurf adapters | historical note | keep-as-legacy, 상단에 deprecated context 표시 권장 |
| `docs/reports/multi_ai_cli_rules_refactoring_report.md` | `.cursor/rules`, `.windsurf/rules` 생성/검증 결과 | historical note | keep-as-legacy |
| `docs/roadmap/ai-os-execution-roadmap-v1.1.md` | Cursor 포함 client adapters, `.cursor/rules/` | stale roadmap wording | rewrite 또는 supersede |
| `docs/plan/ai_os_roadmap.md` | “다중 클라이언트(Cursor, Claude 등)” | stale roadmap wording | rewrite |

이 문서들은 과거 설계/보고 이력을 담고 있으므로 삭제하지 않는 것이 좋다. 다만 현재 공식 runtime 정책과 충돌하지 않도록 “legacy design note” 또는 “superseded by CLI-first runtime policy” 문구를 붙이는 전략이 적절하다.

### 4.4 Editor / IDE Architecture Assumptions

| 파일 | 참조 | 분류 | 권장 |
|---|---|---|---|
| `.ai/workflows/_base/workflow_base.md` | “IDE-based AI”, “IDE AI” | editor-centric architecture assumption | should-rewrite |
| `.ai/workflows/workflow_index.md` | “IDE AI”, “compatible editors” | editor-centric architecture assumption | should-rewrite |
| `.ai/workflows/deploy_automation.workflow.md` | “IDE AI” | editor-centric architecture assumption | should-rewrite |
| `.ai/templates/workflow_template.md` | “IDE AI can resume...” | editor-centric architecture assumption | should-rewrite |
| `.ai/skills/_shared/operational_run_record_creation.skill.md` | “IDE-based AI”, “IDE Paste Safety”, Cursor mention | editor-centric wording mixed with usability note | partial rewrite |
| `.ai/skills/_shared/operational_roadmap_management.skill.md` | “IDE-based AI”, “IDE AI” | editor-centric architecture assumption | should-rewrite |
| `.ai/workflows/code_quality_validation.workflow.md` | “IDE Integration”, “IDE real-time feedback” | editor-centric workflow assumption | should-rewrite 또는 archive |

권장 replacement:

| 기존 표현 | 권장 표현 |
|---|---|
| IDE AI | AI CLI runtime |
| IDE-based AI | CLI runtime agent |
| IDE Integration | Runtime integration 또는 Developer tooling integration |
| IDE real-time feedback | Runtime feedback 또는 validation feedback |
| compatible editors | compatible Markdown tools 또는 local authoring tools |
| VS Code, Cursor, or other IDEs | local text editors or CLI runtime surfaces |

### 4.5 Documentation-only / False Positive

| 파일 | 참조 | 분류 | 권장 |
|---|---|---|---|
| `.gitignore` | `# IDEs and Editors` | documentation-only | keep |
| `docs/cc/slash-commands.md` | `/ide` Claude command 설명 | documentation-only external docs | keep |
| `docs/cc/sub-agent.md` | “edit ... in your own editor” | documentation-only | keep |
| `.claude/skills/subagent-creator/references/available-tools.md` | “IDE Tools (when available)” | Claude skill reference | keep-as-legacy 또는 leave |
| `.ai/skills/_shared/ai_cli/subagent-creator/references/available-tools.md` | “IDE Tools (when available)” | migrated Claude reference | keep-as-legacy |
| `.claude/skills/skill-creator/SKILL.md` | image-editor, pdf-editor examples | false positive | keep |
| `.claude/skills/skill-creator/LICENSE.txt` | editorial revisions | false positive | keep |
| `.ai/skills/_shared/ai_cli/skill-creator/LICENSE.txt` | editorial revisions | false positive | keep |
| `.ai/skills/contents-creator/text/ebook_editing.skill.md` | editorial decisions | false positive | keep |
| `.ai/skills/contents-creator/video/video_storyboarding.skill.md` | editor's shot selection | non-runtime domain language | keep |

## 5. Architecture Assumptions Tied to Editor-centric Workflows

현재 일부 workflow/skill 문서는 다음 전제를 암묵적으로 둔다.

1. AI가 IDE 안에서 항상 저장소와 문서를 직접 읽는다.
2. 작업 재개 주체를 “IDE AI”로 부른다.
3. 실시간 feedback 또는 code completion 중심의 개발 흐름을 AI OS runtime 흐름으로 본다.
4. Cursor/Windsurf/Copilot이 workflow stage의 협업 도구로 들어간다.
5. `.cursorrules`가 system rules entrypoint라는 과거 경로를 참조한다.

CLI-first AI OS에서는 이 전제를 다음처럼 바꿔야 한다.

1. AI 실행 주체는 `CLI runtime`이다.
2. 저장소 상태를 읽고 작업을 재개하는 주체는 `runtime worker` 또는 `AI CLI runtime`이다.
3. IDE/editor는 authoring surface 또는 local text editor일 뿐 runtime source of truth가 아니다.
4. adapter는 runtime별 discovery/config layer이며 canonical rule source가 아니다.
5. system rules entrypoint는 `.ai/rules/rules.md`이다.

## 6. Canonical Terminology Proposal

| 용어 | 정의 | 사용 예 |
|---|---|---|
| AI OS | `.ai/`를 source of truth로 삼아 rules, agents, skills, workflows, validators, adapters를 관리하는 운영 계층 | `.ai OS` manages CLI runtime context. |
| runtime | AI 작업을 실제로 수행하는 실행 환경 | Codex CLI runtime, Gemini CLI runtime, Claude Code CLI runtime |
| CLI runtime | 터미널/CLI 기반 AI 실행 환경 | Codex CLI, Gemini CLI, Claude Code CLI |
| adapter | runtime이 `.ai` SSoT를 발견하거나 로드하도록 돕는 얇은 호환 파일 | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` |
| worker | 특정 runtime 안에서 task를 수행하는 실행 주체 | developer worker, validation worker |
| agent definition | worker의 역할, scope, skill routing을 정의하는 `.ai/agents/*.agent.md` 파일 | `developer.agent.md` |
| source of truth | canonical rule/content source | `.ai/rules/rules.md`, `.ai/skills/` |
| authoring surface | 사람이 문서를 편집하는 도구 | VS Code, text editor, Obsidian |
| legacy runtime | 현재 공식 지원에서 제외된 과거 runtime/integration | Cursor, Windsurf |

금지 또는 축소 권장 표현:

| 기존 표현 | 문제 | 대체 |
|---|---|---|
| IDE AI | editor-centric | AI CLI runtime |
| IDE-based AI | editor-centric | CLI runtime worker |
| client-specific target paths | 너무 광범위 | runtime adapter target paths |
| Cursor adapter | legacy runtime | legacy Cursor adapter |
| Windsurf adapter | legacy runtime | legacy Windsurf adapter |
| `.cursorrules` | deprecated rule entrypoint | `.ai/rules/rules.md` |

## 7. Files Safe to Rewrite Immediately

다음 파일은 현재 SSoT 정책과 직접 충돌하는 stale path 또는 용어만 포함하므로 즉시 rewrite가 안전하다.

| 파일 | 권장 변경 |
|---|---|
| `.ai/templates/anchor_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/architecture_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/decision_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/prd_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/report_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/spec_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/task_template.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/templates/README.md` | `[[../.cursorrules]]` -> `[[../rules/rules.md]]` |
| `.ai/validators/*_validator.md` listed in section 4.2 | `.ai/.cursorrules` -> `.ai/rules/rules.md` |
| `.ai/workflows/hr_evaluation.workflow.md` | `.ai/.cursorrules` -> `.ai/rules/rules.md` |

## 8. Files Risky to Rewrite

다음 파일은 단순 치환보다 문맥 재설계가 필요하다.

| 파일 | 위험 이유 | 권장 |
|---|---|---|
| `.ai/workflows/stock_trading_system.workflow.md` | Windsurf/Copilot/Claude 등이 workflow stage collaboration role로 들어가 있음 | CLI runtime vocabulary로 stage role 재설계 |
| `.ai/workflows/code_quality_validation.workflow.md` | IDE integration 자체가 workflow section으로 존재 | validation runtime 중심으로 rewrite |
| `.ai/workflows/_base/workflow_base.md` | 운영 루프의 continuity 설명이 IDE AI 전제에 묶임 | AI CLI runtime/worker 중심으로 rewrite |
| `.ai/workflows/workflow_index.md` | 전체 workflow index에 IDE AI parsing assumption이 반복됨 | canonical terminology 적용 후 재검증 |
| `.ai/templates/workflow_template.md` | 새 workflow 생성 template이 IDE AI 표현을 전파함 | template update 필요 |
| `.ai/skills/_shared/operational_run_record_creation.skill.md` | IDE paste safety는 일부 유효하지만 Cursor/IDE 표현이 섞임 | authoring surface와 runtime을 분리해서 rewrite |
| `.ai/skills/_shared/operational_roadmap_management.skill.md` | continuity 설명이 IDE AI 중심 | CLI runtime worker 중심으로 rewrite |
| `docs/roadmap/ai-os-execution-roadmap-v1.1.md` | roadmap phase에 Cursor adapter target이 포함됨 | 새 CLI-first roadmap으로 supersede |
| `docs/plan/ai_os_roadmap.md` | Cursor 등 다중 클라이언트 표현 포함 | 현재 공식 runtime 기준으로 개정 |

## 9. Recommended Actions

### Remove

| 대상 | 이유 |
|---|---|
| 새로운 `.cursor/`, `.windsurf/` target 생성 계획 | 현재 공식 runtime이 아니므로 구현 대상에서 제외 |
| `.cursorrules`를 system rules로 설명하는 문장 | 현재 SSoT와 충돌 |

### Rewrite

| 대상 | 방향 |
|---|---|
| `.ai/.cursorrules` 참조 | `.ai/rules/rules.md`로 교체 |
| IDE AI continuity 문장 | CLI runtime worker continuity로 교체 |
| Windsurf/Copilot stage collaboration | 공식 runtime 또는 generic worker 역할로 교체 |
| `client-specific` 용어 | `runtime adapter` 용어로 교체 |

### Keep as Legacy

| 대상 | 이유 |
|---|---|
| `docs/reports/multi_ai_cli_rules_refactoring_report.md` | 과거 refactoring 기록 |
| `docs/plan/multi_ai_cli_rules_refactoring_design.md` | 과거 설계 근거 |
| `.claude/skills/*` 내 IDE tools reference | Claude skill 원본/참조 성격 |

### Archive

| 대상 | 권장 |
|---|---|
| Cursor/Windsurf adapter 설계가 포함된 roadmap/design 문서 | 삭제하지 말고 `legacy/superseded` 표시 또는 docs archive 정책 수립 후 이동 |
| stock trading workflow의 Windsurf/Copilot-heavy collaboration 설명 | 현재 workflow가 실제 운영에 쓰이지 않으면 archive 후보 |

## 10. Suggested Deprecation Strategy

1. **Policy 선언**
   - `.ai/rules/rules.md` 또는 별도 planning 문서에 “official runtimes: Codex CLI, Gemini CLI, Claude Code CLI”를 명시한다.

2. **Stale path cleanup**
   - `.ai/.cursorrules` 참조를 전부 `.ai/rules/rules.md`로 교체한다.
   - `aios inspect` warning을 0으로 낮춘다.

3. **Terminology cleanup**
   - IDE AI, IDE-based AI를 CLI runtime worker로 교체한다.
   - editor는 authoring surface 의미일 때만 유지한다.

4. **Legacy docs labeling**
   - Cursor/Windsurf가 포함된 과거 plan/report 상단에 “Legacy / superseded by CLI-first runtime policy” 메모를 추가한다.

5. **Runtime adapter boundary**
   - adapters는 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` 같은 얇은 discovery layer로 제한한다.
   - Cursor/Windsurf adapter는 “legacy candidate”로만 문서화한다.

6. **Future compatibility**
   - Cursor/Windsurf 지원이 다시 필요해질 경우 “legacy runtime adapter plugin”으로 별도 설계한다.
   - canonical `.ai` content에는 Cursor/Windsurf-specific behavior를 넣지 않는다.

## 11. Recommended Runtime Architecture Vocabulary

권장 기본 문장:

```text
The .ai OS supports Codex CLI, Gemini CLI, and Claude Code CLI as official CLI runtimes.
Root files such as AGENTS.md, CLAUDE.md, and GEMINI.md are runtime adapters.
The canonical rule source is .ai/rules/rules.md.
Runtime workers load only the minimum required rules, agents, skills, workflows, and validators for the task.
Editor or IDE tools are authoring surfaces, not canonical runtimes.
Cursor and Windsurf references are legacy compatibility notes unless explicitly reintroduced as supported runtime adapters.
```

권장 한국어 정책 문장:

```text
.ai OS의 공식 실행 환경은 Codex CLI, Gemini CLI, Claude Code CLI이다.
루트 adapter 파일은 각 CLI runtime이 `.ai/rules/rules.md`를 발견하도록 돕는 얇은 호환 계층이다.
IDE/editor는 문서 편집 표면일 뿐 canonical runtime이 아니다.
Cursor와 Windsurf는 legacy runtime으로 분류하며, 현재 구현 대상에서 제외한다.
```

## 12. 우선순위

### P0

- `.ai/.cursorrules` 참조 제거
- `.ai/templates/README.md`의 `[[../.cursorrules]]` 교체
- `.ai/validators/*_validator.md` stale rule path 교체
- `.ai/workflows/hr_evaluation.workflow.md` stale rule path 교체

### P1

- `workflow_base.md`, `workflow_index.md`, `workflow_template.md`의 IDE AI 표현 rewrite
- operational roadmap/run record skill의 IDE-based AI 표현 rewrite
- code quality workflow의 IDE integration section 재정의

### P2

- Cursor/Windsurf 포함 과거 docs에 legacy/superseded label 추가
- CLI-first roadmap v1.2 작성
- legacy runtime adapter plugin 정책 설계

## 13. 결론

현재 저장소는 이미 Codex CLI, Gemini CLI, Claude Code CLI 중심으로 상당 부분 정리되어 있다. 그러나 `.cursorrules`, Cursor/Windsurf, IDE AI 표현이 일부 template, validator, workflow, 과거 plan/report에 남아 있어 CLI-first AI OS 아키텍처를 흐리게 만든다.

가장 실용적인 다음 단계는 `.ai/.cursorrules` 참조를 먼저 제거해 `aios inspect v1` warning을 줄이는 것이다. 그 다음 workflow와 operational skill의 “IDE AI” 표현을 “AI CLI runtime worker”로 바꾸면 runtime vocabulary가 안정된다.

