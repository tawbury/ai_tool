# MCP CLI 설정 및 사용 가이드

## 📌 핵심 개념

### 1. **경로 이해하기 (가장 중요!)**

```
mcp-cli/         ← CLI 도구 (어디에 설치해도 됨)
  └─ 명령어: mcp init, mcp install, mcp sync

.ai/             ← SSoT (Single Source of Truth)
  └─ 프로젝트마다 필요 (또는 공유 저장소에 한 번)

my-project/      ← 실제 작업 폴더
  ├─ .ai/        ← 이 프로젝트의 설정
  ├─ docs/       ← 생성된 문서
  └─ [mcp install 실행 후]
     ├─ .cursorrules           ← 생성됨
     ├─ .claude/project.md     ← 생성됨
     └─ .github/...            ← 생성됨
```

### 2. **중요한 경로 규칙**

| 명령어 | 실행 위치 | 생성 위치 | 설명 |
|---|---|---|---|
| `mcp init my-project` | **프로젝트 루트** (mcp-cli 외부) | `./my-project/.ai/` | 새 프로젝트 초기화 |
| `mcp install --all-tools` | **프로젝트 루트** | `./` (현재 디렉토리) | 생성 파일 생성 |
| `mcp sync` | **프로젝트 루트** | `./` (현재 디렉토리) | 생성 파일 갱신 |

**🚨 가장 흔한 실수:**

```bash
# ❌ mcp-cli 폴더 안에서 mcp init 실행
cd mcp-cli
mcp init my-project    # ← mcp-cli/.ai/ 생성됨 (틀림!)

# ✅ mcp-cli 밖에서 실행
cd ../                 # mcp-cli를 벗어남
mcp init my-project    # ← my-project/.ai/ 생성됨 (맞음!)
```

---

## 🚀 빠른 시작 (3단계)

### Step 1: mcp-cli 설치 (한 번만)

```bash
# Option A: 글로벌 설치 (권장 - 어디서나 mcp 사용 가능)
cd mcp-cli
npm install && npm run build && npm link

# Option B: 로컬 설치 (권한 문제가 있다면)
cd mcp-cli
npm install && npm run build
# 이후 사용할 때: node /path/to/mcp-cli/lib/cli.js 또는 alias 생성
```

**설치 확인:**

```bash
mcp --version
# 출력: MCP CLI version 0.1.0
```

### Step 2: 새 프로젝트 생성 (선택사항)

```bash
# Option A: mcp init으로 자동 생성
mcp init my-awesome-project
cd my-awesome-project

# Option B: 기존 프로젝트에 설정 추가
cd /path/to/existing-project

# Option C: 템플릿 복사
cp -r /path/to/templates/ai_tool/* my-new-project/
cd my-new-project
```

### Step 3: IDE 설정 생성

```bash
# 프로젝트 루트에서 실행 (중요!)
cd my-awesome-project

# 모든 IDE용 설정 생성
mcp install --all-tools

# 생성 확인
ls -la | grep -E '^\.'
# .cursorrules           ← Cursor 규칙
# .claude/               ← Claude Code 컨텍스트
# .github/               ← GitHub Copilot 설정
```

**완료! 이제 IDE에서 프로젝트를 열 수 있습니다.**

---

## 📁 프로젝트 구조 이해하기

```
my-awesome-project/
│
├── .ai/                              ← SSoT (Single Source of Truth)
│   ├── spec/                         ← 운영 스펙
│   ├── agents/                       ← 에이전트 정의 (5개)
│   ├── skills/                       ← 스킬 구현 (90+개)
│   ├── validators/                   ← 검증 규칙 (24+개)
│   ├── workflows/                    ← 워크플로우 (8+개)
│   ├── templates/                    ← 문서 템플릿 (15+개)
│   ├── install/                      ← 설정 매핑
│   │   ├── mapping_rules.yaml        ← 어떤 파일을 생성할지 정의
│   │   ├── adapters/                 ← IDE별 설정
│   │   └── templates/                ← 생성 템플릿
│   ├── export/                       ← 외부 도구 설정
│   ├── .cursorrules                  ← Cursor 규칙 소스
│   └── README.md
│
├── .cursorrules                      ← 생성됨 (mcp install)
├── .claude/
│   └── project.md                    ← 생성됨 (mcp install)
├── .github/
│   └── copilot-instructions.md       ← 생성됨 (mcp install)
│
├── docs/                             ← 프로젝트 문서
│   ├── decisions/
│   ├── tasks/
│   ├── dev/
│   │   ├── archi/
│   │   ├── spec/
│   │   └── PRD/
│   └── ...
│
├── vault/                            ← AI 작업 공간
│   ├── drafts/
│   ├── pending/
│   └── ...
│
├── ops/                              ← 운영 기록
│   ├── run_records/
│   ├── approvals/
│   └── ...
│
├── backup/                           ← 백업
│
├── mcp-cli/                          ← CLI 도구 (선택사항)
│   ├── src/
│   ├── lib/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

### 파일별 역할

| 파일/폴더 | 누가 생성 | 언제 | Git 커밋 | 설명 |
|---|---|---|---|---|
| `.ai/` | 사용자/템플릿 | 프로젝트 시작 시 | ✅ YES | SSoT - 모든 설정 |
| `.cursorrules` | `mcp install` | IDE 설정 생성 시 | ❌ NO | .ai/.cursorrules에서 자동 생성 |
| `.claude/project.md` | `mcp install` | IDE 설정 생성 시 | ❌ NO | 템플릿에서 자동 생성 |
| `.github/copilot-instructions.md` | `mcp install` | IDE 설정 생성 시 | ❌ NO | 템플릿에서 자동 생성 |
| `mcp-cli/` | 사용자/템플릿 | 프로젝트 시작 시 | ✅ YES (선택) | CLI 도구 |
| `docs/`, `vault/`, `ops/` | 사용자/AI | 작업 진행 중 | ✅ YES | 실제 작업 산물 |

---

## 🔄 일상적인 작업 흐름

### 시나리오 1: .ai/ 파일 수정 후 IDE에 반영

```bash
# 1. .ai/ 폴더의 파일 수정
vi .ai/.cursorrules
vi .ai/spec/MCP_OS_Operational_Spec_v0_1.md
vi .ai/agents/developer.agent.md

# 2. IDE 설정 파일 재생성
mcp sync

# 3. IDE 재시작 (자동 로드)
# Claude Code, Cursor 등 다시 열기

# 4. 변경사항 확인
git diff .cursorrules
git diff .claude/project.md
```

### 시나리오 2: 팀 협업

```bash
# 사용자 A: 스펙 수정
vi .ai/spec/MCP_OS_Operational_Spec_v0_1.md
mpc sync
git add .ai/
git commit -m "스펙 업데이트"
git push

# 사용자 B: 변경사항 받기
git pull
mcp sync              # ← 반드시 실행! 로컬 파일 재생성
# 이제 새로운 스펙이 IDE에 적용됨
```

### 시나리오 3: 새 프로젝트 복제 후 설정

```bash
# 팀 저장소 클론
git clone <repo>
cd <repo>

# mcp-cli 설정 (처음 한 번)
cd mcp-cli && npm install && npm run build && npm link && cd ..

# 또는 이미 글로벌로 설치된 경우 스킵

# 프로젝트 설정 생성
mcp install --all-tools

# 완료!
```

---

## ⚠️ 흔한 실수와 해결책

### 문제 1: ".ai/ 폴더가 mcp-cli 안에 생겼어요"

**원인:** mcp-cli 폴더 안에서 `mcp init`을 실행했음

**해결:**

```bash
# 1. 잘못된 폴더 삭제
cd mcp-cli
rm -rf .ai

# 2. 올바른 위치로 이동
cd ..

# 3. 다시 실행
mcp init my-project
cd my-project
mcp install --all-tools
```

### 문제 2: "mcp: command not found"

**원인:** mcp-cli를 설치하지 않았거나 링크하지 않음

**해결:**

```bash
# 옵션 A: npm link 사용
cd mcp-cli
npm install && npm run build && npm link

# 옵션 B: alias 사용 (권한 문제 있을 때)
# ~/.bashrc 또는 ~/.zshrc에 추가
alias mcp="node /path/to/mcp-cli/lib/cli.js"
source ~/.bashrc

# 옵션 C: 직접 실행
node /path/to/mcp-cli/lib/cli.js --version
```

### 문제 3: "생성된 파일이 계속 되돌아가요"

**원인:** 생성된 파일(.cursorrules, .claude/project.md)을 수정하고 있음

**해결:**

```bash
# ❌ 이렇게 하지 마세요:
vi .cursorrules          # 수정하면 mcp sync 때 덮어써짐

# ✅ 이렇게 하세요:
vi .ai/.cursorrules      # 소스 파일 수정
mcp sync                 # 재생성
```

### 문제 4: "IDE에서 에이전트/스킬을 모르네요"

**원인:** `.claude/project.md`가 없거나 자동 로드되지 않음

**해결:**

```bash
# 1. project.md 생성 확인
ls -lh .claude/project.md

# 없으면 생성:
mcp install --all-tools

# 2. IDE 재시작
# Claude Code를 완전히 종료 후 다시 열기

# 3. 설정 확인
cat .claude/settings.json | grep project_context_file
```

---

## 📊 의존성 관리

### node_modules는 어디에 필요한가?

```
mcp-cli/node_modules/       ← 필수 (mpc 명령어 실행용)
project/node_modules/       ← 선택 (프로젝트가 Node 기반일 때)

.ai/ 폴더의 파일들          ← node_modules 불필요!
docs/, vault/ 등            ← node_modules 불필요!
```

### .gitignore에 포함할 파일

```bash
# ✅ 무시할 파일들 (자동 생성됨)
.cursorrules
.claude/project.md
.github/copilot-instructions.md
.windsurfrules
node_modules/

# ✅ 커밋할 파일들
.ai/              # 모든 설정 파일
mcp-cli/          # CLI 도구 (선택)
docs/             # 문서
vault/            # 작업 산물
```

---

## 🛠️ 고급 설정

### 특정 IDE만 설정하기

```bash
# Cursor만
mcp install --tools cursor

# Claude Code만
mcp install --tools claude_code

# 여러 개
mpc install --tools cursor claude_code

# 전체
mpc install --all-tools
```

### 변경사항 확인만 하기 (적용 안 함)

```bash
mcp sync --check
```

### 모든 파일 강제 재생성

```bash
mcp sync --force
```

### 상세 출력 보기

```bash
mcp install --all-tools --verbose
mcp sync --verbose
```

---

## 📚 참고 자료

- **전체 스펙**: `.ai/spec/MCP_OS_Operational_Spec_v0_1.md`
- **CLI 매뉴얼**: `mcp-cli/README.md`
- **시스템 개요**: `.ai/README.md`
- **문제 해결**: `mcp-cli/README.md` → "문제 해결" 섹션

---

## 🎯 핵심 체크리스트

### 초기 설정

- [ ] mcp-cli 설치: `npm install && npm run build && npm link`
- [ ] 설치 확인: `mcp --version`
- [ ] 프로젝트 생성: `mpc init my-project` (mpc-cli 밖에서!)
- [ ] IDE 설정 생성: `mcp install --all-tools`
- [ ] 파일 생성 확인: `.cursorrules`, `.claude/project.md` 존재?

### 일상 작업

- [ ] `.ai/` 파일 수정
- [ ] `mcp sync` 실행
- [ ] IDE 재시작
- [ ] 변경사항 확인
- [ ] Git 커밋 (`.ai/` 폴더만)

### 팀 협업

- [ ] `.ai/` 폴더 커밋
- [ ] `mpc-cli/` 폴더 커밋 (선택)
- [ ] `.cursorrules` 등은 `.gitignore` 확인
- [ ] Pull 후 `mcp sync` 실행
- [ ] IDE 재시작

---

**버전**: 0.1.0
**마지막 업데이트**: 2026-01-25
