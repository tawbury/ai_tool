# MCP CLI - MCP OS 커맨드라인 인터페이스

MCP OS (Multi-Agent AI Operating System)를 위한 CLI 도구로, IDE AI 도구 설정의 초기화, 설치 및 동기화를 처리합니다.

## 주요 기능

- **`mcp init`** - 완전한 디렉토리 구조로 새로운 MCP OS 프로젝트 초기화
- **`mcp install --all-tools`** - 모든 IDE AI 도구의 설정 파일 생성
- **`mcp sync`** - .ai/ 변경사항을 생성 파일에 동기화

---

## 📋 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [패키징 구조 이해하기](#패키징-구조-이해하기)
4. [사용 방법](#사용-방법)
5. [실전 예제](#실전-예제)
6. [프로젝트 구조](#프로젝트-구조)
7. [의존성 패키지](#의존성-패키지)
8. [문제 해결](#문제-해결)
9. [개발 가이드](#개발-가이드)

---

## 시스템 요구사항

mcp-cli를 설치하기 전에 다음 요구사항을 확인하세요:

| 항목 | 최소 버전 | 권장 버전 | 확인 명령어 |
|---|---|---|---|
| **Node.js** | 14.0.0 | 18.0.0+ | `node --version` |
| **npm** | 6.0.0 | 8.0.0+ | `npm --version` |
| **OS** | Windows, macOS, Linux | Windows 11+, macOS 12+, Ubuntu 20.04+ | - |
| **RAM** | 512 MB | 2 GB+ | - |
| **디스크 공간** | 200 MB | 500 MB+ | - |

### 버전 확인 방법

```bash
# Node.js 및 npm 버전 확인
node --version    # v14.0.0 이상 출력되어야 함
npm --version     # 6.0.0 이상 출력되어야 함

# npm 글로벌 설정 확인
npm config get prefix  # 글로벌 패키지 설치 위치 확인
```

---

## 설치 방법

### 옵션 1: 소스에서 설치 (개발용, 권장)

개발이나 커스터마이징에 가장 적합한 방법:

```bash
# mcp-cli 디렉토리로 이동 또는 클론
cd mcp-cli

# 의존성 패키지 설치
npm install

# TypeScript를 JavaScript로 빌드
npm run build

# 글로벌 명령어로 링크 (npm 글로벌 설정 필요)
npm link
```

링크 후, 어디서나 `mcp` 명령어 사용 가능:
```bash
mcp init my-project
mcp install --all-tools
```

### 옵션 2: 직접 실행 (글로벌 설치 없이)

클론한 디렉토리에서 직접 실행:

```bash
cd mcp-cli
npm install
npm run build

# 빌드된 CLI 직접 사용
node lib/cli.js init my-project
node lib/cli.js install --all-tools
```

### 옵션 3: Shell Alias 생성

글로벌 설치 없이 편리하게 사용:

```bash
# Shell 프로필에 추가 (.bashrc, .zshrc, .bash_profile 등)
alias mcp="node /path/to/mcp-cli/lib/cli.js"

# Shell 재로드
source ~/.bashrc  # 또는 .zshrc, .bash_profile 등

# 일반 명령어처럼 사용
mcp init my-project
```

### 설치 후 확인

설치가 제대로 되었는지 확인:

```bash
# 옵션 1 사용 시 (글로벌 링크)
mcp --version

# 옵션 2 또는 3 사용 시
node lib/cli.js --version
# 또는 (alias 사용 시)
mcp --version
```

---

## 패키징 구조 이해하기

### ❓ "mcp-cli만 가져가면 되나요?"

**❌ 아니요** - **두 가지 모두 필요합니다**:

#### 1. **mcp-cli** (도구)
- 파일: `src/`, `lib/`, `package.json`, `tsconfig.json`
- 크기: ~5 MB (node_modules 포함)
- 설치: 시스템/팀당 한 번만

#### 2. **.ai/ 폴더** (설정)
- 파일: `install/`, `spec/`, `agents/`, `skills/`, `templates/` 등
- 크기: 프로젝트당 ~2-5 MB
- 설치: 프로젝트마다 필요, 또는 공유 저장소에 한 번

### 시스템 작동 방식

```
┌─────────────────────────────────────────────────────────────────┐
│                         mcp-cli 도구                             │
│           (글로벌 또는 npm 패키지로 설치 - 한 번만)              │
├─────────────────────────────────────────────────────────────────┤
│  npm install → npm run build → npm link (또는 npm install -g)    │
│  결과: 어디서나 'mcp' 명령어 사용 가능                            │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ mcp init my-project
              │ (디렉토리 구조 생성)
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    새 프로젝트 생성됨                             │
│  my-project/                                                    │
│  ├── .ai/          ← SSoT (Single Source of Truth)              │
│  │   ├── spec/                                                  │
│  │   ├── agents/                                                │
│  │   ├── install/                                               │
│  │   │   ├── mapping_rules.yaml  ← 설정 중심                    │
│  │   │   ├── adapters/*.yaml                                    │
│  │   │   └── templates/*                                        │
│  │   └── .cursorrules            ← 소스 규칙                     │
│  ├── .cursorrules     (여기 없음 - mcp install 후에만)           │
│  └── docs/, vault/, ops/                                        │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ mcp install --all-tools
              │ (.ai/install/mapping_rules.yaml 읽음)
              ▼
┌─────────────────────────────────────────────────────────────────┐
│            생성된 파일들 (.gitignore에 포함)                      │
├─────────────────────────────────────────────────────────────────┤
│  ✓ .cursorrules             ← .ai/.cursorrules에서               │
│  ✓ .claude/project.md       ← claude_template.md에서            │
│  ✓ .github/copilot-instructions.md ← copilot_template.md에서    │
│  ✓ .windsurfrules           ← windsurf_template.txt에서         │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ .ai/.cursorrules, .ai/spec/ 등 수정
              ▼
              │ mcp sync
              │ (업데이트된 소스에서 재생성)
              ▼
┌─────────────────────────────────────────────────────────────────┐
│          업데이트된 생성 파일들                                    │
├─────────────────────────────────────────────────────────────────┤
│  ✓ 모든 IDE 도구 설정 새로고침                                   │
│  ✓ 연결된 모든 IDE 도구에 변경사항 전파                          │
│  ✓ 다음 IDE 세션 준비 완료                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 필수 파일 경로

`mcp install`과 `mcp sync` 명령어는 다음 파일들이 필요합니다:

```
필수 파일 (mcp install/sync 작동에 필요):
┌─ .ai/install/mapping_rules.yaml (모든 도구 정의)
│  ├─ Cursor 활성화?
│  │  └─ 필요: .ai/install/templates/cursor_template.txt
│  │          + .ai/install/adapters/cursor.yaml
│  │          + .ai/.cursorrules (소스 콘텐츠)
│  │
│  ├─ Claude 활성화?
│  │  └─ 필요: .ai/install/templates/claude_template.md
│  │          + .ai/install/adapters/claude_code.yaml
│  │
│  ├─ Copilot 활성화?
│  │  └─ 필요: .ai/install/templates/copilot_template.md
│  │          + .ai/install/adapters/github_copilot.yaml
│  │
│  └─ Windsurf 활성화?
│     └─ 필요: .ai/install/templates/windsurf_template.txt
│             + .ai/install/adapters/windsurf.yaml
└─ 모든 경로는 프로젝트 루트 기준 상대 경로
```

### 배포 시나리오

#### 시나리오 A: 개인 사용
```
설정: npm install mcp-cli (글로벌로) 한 번
배포: mcp init (프로젝트마다)
결과: 각 프로젝트가 독립적인 .ai/ 폴더를 가짐
이동할 파일: mcp-cli만 글로벌, .ai/는 로컬에서 생성됨
```

#### 시나리오 B: 팀 저장소
```
설정: mcp-cli/와 .ai/ 둘 다 포함한 저장소 클론
결과: 팀 멤버들이 mcp-cli npm link 한 번 실행
업데이트: git pull로 .ai/ 변경사항 자동으로 가져옴
이동할 파일: mcp-cli/와 .ai/ 둘 다 같은 저장소에
```

#### 시나리오 C: 배포 패키지
```
패키징: npm pack mcp-cli → mcp-cli-0.1.0.tgz
설정: npm install -g mcp-cli-0.1.0.tgz
배포: mcp init my-project
생성: .ai/ 폴더가 로컬에서 생성됨
이동할 파일: mcp-cli 패키지만, .ai/는 템플릿에서 생성
```

#### 시나리오 D: 템플릿 폴더 사용 (권장)
```
목적: mcp-cli와 .ai/를 함께 유지하는 마스터 템플릿
설정: mcp-cli/ + .ai/ 폴더를 템플릿으로 보관
배포: 새 프로젝트마다 mcp-cli/과 .ai/를 복사
결과: 각 프로젝트가 독립적인 환경
이동할 파일: mcp-cli/와 .ai/ 전체를 복사

예시:
  templates/ai_tool/
  ├── mcp-cli/        ← CLI 도구
  ├── .ai/            ← 시스템 정의 (SSoT)
  └── README.md

  새 프로젝트:
  cp -r templates/ai_tool/* my-new-project/
  cd my-new-project
  mcp install --all-tools
```

### 파일 생성 위치

| 명령어 | 생성 대상 | 위치 | Git 커밋 여부 |
|---|---|---|---|
| `npm install mcp-cli` | 도구 코드 | global 또는 local | ✅ mcp-cli 저장소 |
| `mcp init` | 디렉토리 구조 | ./.ai/ | ✅ 프로젝트 저장소 |
| `mcp init` | README 파일들 | .ai/, root | ✅ 프로젝트 저장소 |
| `mcp init` | .gitignore | root | ✅ 프로젝트 저장소 |
| `mcp install --all-tools` | .cursorrules | root | ❌ .gitignore에 포함 |
| `mcp install --all-tools` | .claude/project.md | root | ❌ .gitignore에 포함 |
| `mcp install --all-tools` | .github/copilot-instructions.md | root | ❌ .gitignore에 포함 |
| `mcp sync` | (위 파일들 재생성) | root | ❌ .gitignore에 포함 |

### .gitignore 설정

```bash
# 프로젝트 루트의 .gitignore

# 생성된 IDE 파일들 (mcp sync로 재생성되므로 커밋 불필요)
.cursorrules                          # Cursor IDE 규칙
.claude/project.md                    # Claude Code 컨텍스트
.github/copilot-instructions.md       # GitHub Copilot 설정
.windsurfrules                        # Windsurf IDE 규칙

# 의존성 (각 팀원이 npm install로 설치함)
node_modules/
mcp-cli/node_modules/

# OS 파일
.DS_Store
Thumbs.db
*.lock

# 로그
*.log
npm-debug.log*

# 임시 파일
.env.local
.env.*.local
backup/
```

**반드시 커밋해야 할 파일들:**

```bash
# ✅ SSoT (Single Source of Truth) - 모두 커밋!
.ai/                                  # 전체 폴더 및 파일
  ├── install/                        # 설정 매핑
  ├── spec/                           # 운영 스펙
  ├── agents/                         # 에이전트 정의
  ├── skills/                         # 스킬 구현
  ├── workflows/                      # 워크플로우
  ├── validators/                     # 검증 규칙
  ├── templates/                      # 문서 템플릿
  ├── .cursorrules                    # Cursor 규칙 소스
  └── export/                         # 외부 도구 내보내기

# ✅ CLI 도구 (프로젝트와 함께 배포하는 경우)
mcp-cli/                              # src/, lib/, package.json 등
  ├── src/                            # TypeScript 소스
  ├── package.json                    # 의존성 명시
  ├── package-lock.json              # 버전 잠금
  └── README.md                       # CLI 문서

# ✅ 프로젝트 파일
docs/                                 # 프로젝트 문서
vault/                                # AI 작업 공간
ops/                                  # 운영 기록
.gitignore                            # Git 설정
README.md                             # 프로젝트 설명
```

**팀 협업 시 주의사항:**

```bash
# 사용자 A: .ai/ 수정 및 커밋
git add .ai/
git commit -m "AI 에이전트 정의 업데이트"
git push

# 사용자 B: 풀 후 프로젝트 설정 재생성
git pull
mcp install --all-tools              # 로컬 .cursorrules, .claude/ 재생성

# ❌ 다음은 하지 마세요:
# git add .cursorrules              # .gitignore에 이미 포함됨
# git add .claude/project.md        # 각자 로컬에서만 생성
```

---

## 사용 방법

### 1️⃣ 새 프로젝트 초기화

```bash
mcp init [directory] --force --verbose
```

**옵션:**
- `[directory]` - 프로젝트 디렉토리 (기본값: 현재 디렉토리)
- `--force` - 디렉토리가 이미 존재해도 강제로 초기화
- `--verbose` - 상세 출력 표시

### 2️⃣ IDE 도구 설정 설치

```bash
mcp install --all-tools --verbose
# 또는 특정 도구만:
mcp install --tools copilot claude cursor --verbose
```

**옵션:**
- `--all-tools` - 모든 설정된 도구 설치
- `--tools <도구1> <도구2> ...` - 특정 도구만 설치
- `--verbose` - 상세 출력 표시

### 3️⃣ 변경사항 동기화

```bash
mcp sync --force --verbose
# 또는 변경사항 확인만:
mcp sync --check --verbose
```

**옵션:**
- `--force` - 모든 파일 강제 재생성
- `--check` - 변경사항만 확인, 적용하지 않음
- `--verbose` - 상세 출력 표시

---

## 실전 예제

### 예제 1: 새로 시작하기 (신규 프로젝트)

```bash
# 1단계: CLI 설정 (한 번만, 아직 설치 안 했다면)
cd mcp-cli
npm install && npm run build && npm link
cd ..

# 2단계: 모든 파일과 함께 새 프로젝트 생성
mcp init my-awesome-project
cd my-awesome-project

# 3단계: IDE 설정 생성
mcp install --all-tools

# 4단계: 생성된 파일 확인
ls -la | grep -E '^\.'  # 생성된 파일 보기
cat .cursorrules        # Cursor 규칙 보기

# 5단계: 변경사항 적용 및 동기화
echo "# 업데이트된 규칙" >> .ai/.cursorrules
mcp sync                # .cursorrules 재생성
```

### 예제 2: 팀 저장소에서 작업

```bash
# 팀 저장소 클론 (mcp-cli와 .ai/ 둘 다 포함)
git clone team-repo
cd team-repo

# CLI 설치 및 설정
npm install --prefix mcp-cli
npm run build --prefix mcp-cli
cd mcp-cli && npm link && cd ..

# 프로젝트 설정 생성
mcp install --all-tools

# 변경사항 만들기
vi .ai/.cursorrules

# 동기화 및 커밋
mcp sync
git add .
git commit -m "AI 도구 설정 업데이트"
git push
```

### 예제 3: npm 글로벌 설치 사용

```bash
# npm 레지스트리에서 설치
npm install -g @your-org/mcp-cli

# 어디서나 mcp 명령어 사용
cd ~/projects/project1
mcp init .                    # 현재 디렉토리 초기화
mcp install --all-tools
mcp sync --check

cd ~/projects/project2
mcp init .
mcp install --all-tools
```

### 예제 4: 기계 간 프로젝트 이동

**소스 기계:**
```bash
# 생성된 파일 제외하고 모두 커밋
git add .ai/ mcp-cli/ .gitignore README.md
git commit -m "mcp-cli 및 .ai/ 설정 추가"
git push
```

**타겟 기계:**
```bash
# 클론하면 mcp-cli와 .ai/ 둘 다 가져옴
git clone <repo>
cd <repo>

# mcp-cli 설정
npm install --prefix mcp-cli
npm run build --prefix mcp-cli
cd mcp-cli && npm link && cd ..

# IDE 설정 재생성
mcp install --all-tools

# 준비 완료!
```

---

## 프로젝트 구조

### mcp-cli 도구 구조

```
mcp-cli/
├── src/
│   ├── cli.ts              # 메인 CLI 진입점
│   ├── index.ts            # 내보내기
│   ├── commands/           # 명령어 구현
│   │   ├── init.ts         # mcp init 명령어
│   │   ├── install.ts      # mcp install 명령어
│   │   ├── sync.ts         # mcp sync 명령어
│   │   └── index.ts        # 명령어 내보내기
│   └── utils/              # 유틸리티 함수
│       ├── file.ts         # 파일 작업
│       ├── yaml.ts         # YAML 파싱
│       └── index.ts        # 유틸리티 내보내기
├── lib/                    # 컴파일된 JavaScript (생성됨)
├── package.json
├── tsconfig.json
└── README.md
```

### 프로젝트 .ai/ 디렉토리 구조

```
.ai/
├── .cursorrules                 ← SSoT (Source of Truth)
├── install/
│   ├── mapping_rules.yaml       ← 설정 중심
│   ├── adapters/
│   │   ├── github_copilot.yaml
│   │   ├── claude_code.yaml
│   │   ├── cursor.yaml
│   │   └── windsurf.yaml
│   └── templates/
│       ├── copilot_template.md
│       ├── claude_template.md
│       └── cursor_template.txt
├── spec/                        ← 운영 스펙
├── agents/                      ← 에이전트 정의
├── skills/                      ← 스킬 구현
├── workflows/                   ← 워크플로우 정의
├── templates/                   ← 문서 템플릿
├── validators/                  ← 검증 규칙
└── export/                      ← 외부 도구용 내보내기
```

### 생성되는 파일 위치

**프로젝트 루트:**
```
project-root/
├── .cursorrules                 ← 생성됨, .gitignore에 포함
├── .claude/project.md           ← 생성됨, .gitignore에 포함
├── .github/copilot-instructions.md  ← 생성됨, .gitignore에 포함
├── .gitignore
└── README.md
```

### 핵심 함수

| 함수 | 파일 | 목적 |
|---|---|---|
| `getMappingRulesPath()` | `utils/file.ts` | `.ai/install/mapping_rules.yaml` 찾기 |
| `getToolConfig()` | `utils/yaml.ts` | YAML에서 도구 설정 읽기 |
| `renderTemplate()` | `utils/file.ts` | 템플릿에 변수 치환 |
| `initCommand()` | `commands/init.ts` | `.ai/` 디렉토리 구조 생성 |
| `installCommand()` | `commands/install.ts` | 설정 파일 생성 |
| `syncCommand()` | `commands/sync.ts` | 소스 변경 시 재생성 |

---

## 의존성 패키지

### 프로덕션 의존성

mcp-cli 실행에 필요한 패키지:

| 패키지 | 버전 | 목적 | 크기 |
|---|---|---|---|
| **chalk** | ^5.0.0 | 터미널 텍스트 스타일 및 색상 | ~10 KB |
| **fs-extra** | ^11.0.0 | 확장 파일 시스템 작업 (copy, ensure, remove) | ~100 KB |
| **js-yaml** | ^4.1.0 | YAML 파일 파싱 및 검증 | ~250 KB |
| **ora** | ^7.0.0 | 우아한 터미널 진행 스피너 | ~30 KB |
| **yargs** | ^17.0.0 | CLI 인자 파싱 및 검증 | ~200 KB |

**전체 프로덕션 크기**: ~600 KB

**상세 설명:**
- **chalk**: 색상 콘솔 출력 (성공 ✓, 오류 ✗, 경고 ⚠)
- **fs-extra**: 크로스 플랫폼 파일 작업 `copy()`, `ensureDir()`, `readFile()`
- **js-yaml**: `.ai/install/mapping_rules.yaml` 및 어댑터 설정 파일 파싱
- **ora**: 긴 작업 중 스피너 애니메이션 (install, sync, init)
- **yargs**: 명령줄 인자 파싱 `--force`, `--verbose`, `--all-tools`

### 개발 의존성

개발 및 테스트에만 필요한 패키지:

| 패키지 | 버전 | 목적 |
|---|---|---|
| **@types/node** | ^20.0.0 | Node.js TypeScript 타입 정의 |
| **@types/fs-extra** | ^11.0.0 | fs-extra TypeScript 타입 |
| **@types/js-yaml** | ^4.0.0 | js-yaml TypeScript 타입 |
| **typescript** | ^5.0.0 | TypeScript 컴파일러 |
| **ts-node** | ^10.0.0 | 컴파일 없이 TypeScript 직접 실행 |
| **eslint** | ^8.0.0 | 코드 린팅 및 품질 검사 |
| **jest** | ^29.0.0 | 유닛 테스트 프레임워크 |
| **@types/jest** | ^29.0.0 | Jest TypeScript 타입 |

**전체 개발 크기**: ~500 MB (컴파일러 및 도구용 node_modules 포함)

### 의존성 설치 명령어

```bash
# 모든 의존성 설치 (프로덕션 + 개발)
npm install

# 프로덕션 의존성만 설치 (배포용)
npm install --production

# 최신 호환 버전으로 업데이트
npm update

# 의존성 취약점 확인
npm audit

# 취약점 자동 수정
npm audit fix
```

### npm 명령어 참조

```bash
# 설치 및 의존성 관리
npm install                 # 모든 의존성 설치
npm install --production    # 프로덕션만 설치
npm update                  # 최신 버전으로 업데이트
npm audit                   # 취약점 확인
npm audit fix              # 취약점 수정

# 빌드 및 개발
npm run build              # TypeScript를 JavaScript로 컴파일
npm run dev                # 개발 모드 실행
npm run dev -- init        # 개발 모드에서 특정 명령어 실행

# 테스트 및 코드 품질
npm test                   # 테스트 스위트 실행
npm run lint               # 코드 품질 검사

# 정리
npm run clean              # 컴파일된 lib/ 디렉토리 제거
npm cache clean --force    # npm 캐시 삭제 (필요시)

# 문제 해결
npm list                   # 설치된 의존성 트리 표시
npm list --depth=0         # 최상위 의존성만 표시
npm ls -g                  # 글로벌 패키지 표시
```

---

## 문제 해결

### 문제: "mcp: command not found"

**원인**: CLI가 링크되지 않았거나 글로벌로 설치되지 않음

**해결 방법:**
```bash
# 로컬 설치한 경우
cd mcp-cli
npm install
npm run build
npm link

# npm에서 설치한 경우
npm install -g mcp-cli
mcp --version
```

### 문제: 설치 중 "Tool config not found"

**원인**: `.ai/install/mapping_rules.yaml` 또는 필수 어댑터/템플릿 파일 누락

**해결 방법:**
```bash
# 필수 파일 존재 확인
ls -la .ai/install/
ls -la .ai/install/adapters/
ls -la .ai/install/templates/

# 누락된 경우, 재초기화
mcp init . --force

# 도구 활성화 확인
cat .ai/install/mapping_rules.yaml | grep -A 5 "cursor:"
```

### 문제: "Could not read source file" 경고

**원인**: 템플릿이 소스 파일(`.ai/.cursorrules` 등)을 참조하지만 누락됨

**해결 방법:**
```bash
# 소스 파일 존재 확인
ls -la .ai/.cursorrules

# 누락된 경우, 기본값으로 생성
echo "# Cursor IDE Rules" > .ai/.cursorrules

# 동기화 재실행
mcp sync
```

### 문제: 생성된 파일이 계속 되돌아감

**원인**: 소스 파일 대신 생성된 파일을 직접 수정

**해결 방법:**
```bash
# ✅ 이렇게 하세요: 소스 파일 수정
vi .ai/.cursorrules
vi .ai/spec/...

# 그 다음 동기화
mcp sync

# ❌ 하지 마세요: 생성된 파일 수정
# vi .cursorrules          # 덮어써짐!
# vi .github/copilot-instructions.md  # 덮어써짐!
```

### 문제: TypeScript 컴파일 오류

**원인**: 구버전 의존성 또는 Node.js 버전 불일치

**해결 방법:**
```bash
# Node.js 버전 확인
node --version  # 14.0.0+ 이어야 함

# 정리 및 재빌드
npm run clean
npm install
npm run build

# 개발 모드로 실행하여 오류 확인
npm run dev
```

### 문제: npm link 시 "EACCES: permission denied"

**원인**: npm 글로벌 디렉토리에 sudo 필요

**해결 방법 1** - sudo 사용 (권장하지 않음):
```bash
sudo npm link
```

**해결 방법 2** - npm 권한 수정:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
npm link
```

**해결 방법 3** - alias 사용:
```bash
# ~/.bashrc, ~/.zshrc 또는 ~/.bash_profile에 추가
alias mcp="node /path/to/mcp-cli/lib/cli.js"
source ~/.bashrc
```

### 문제 해결 체크리스트

```bash
# 1. mcp 명령어 사용 가능 확인
which mcp  # 경로가 표시되어야 함

# 2. 현재 프로젝트에 .ai/install/ 파일 확인
ls -la .ai/install/
# 포함되어야 함: mapping_rules.yaml, adapters/, templates/

# 3. 특정 도구 설정 확인
cat .ai/install/mapping_rules.yaml | grep -A 3 "cursor:"

# 4. 소스 파일 존재 확인
ls -la .ai/.cursorrules
ls -la .ai/install/templates/cursor_template.txt

# 5. 상세 출력으로 설치 실행
mcp install --all-tools --verbose

# 6. 생성된 파일 내용 확인
head -20 .cursorrules  # 처음 20줄
```

---

## 개발 가이드

### 개발 환경 설정

```bash
# mcp-cli 디렉토리로 이동 또는 클론
cd mcp-cli

# 의존성 설치
npm install

# 개발 모드 시작
npm run dev init my-test-project
npm run dev install --all-tools

# 테스트 실행
npm test

# 린터 실행
npm run lint
```

### 빌드

```bash
npm run build
```

`lib/` 디렉토리에 TypeScript를 JavaScript로 컴파일합니다.

### 개발 모드

```bash
npm run dev
```

ts-node로 TypeScript를 직접 실행합니다.

### 테스트

```bash
npm test
```

Jest 테스트 스위트를 실행합니다.

### 린팅

```bash
npm run lint
```

ESLint로 TypeScript 코드를 검사합니다.

---

## 빠른 설정 치트시트

### 최초 설정 (처음 설치)

```bash
# 1. mcp-cli 클론 또는 다운로드
git clone <mcp-cli-repo> mcp-cli
cd mcp-cli

# 2. 의존성 설치
npm install

# 3. TypeScript 빌드
npm run build

# 4. 글로벌 링크 (권한 문제 시 alias 사용)
npm link

# 5. 설치 테스트
mcp --version
# 출력: MCP CLI version 0.1.0

# 완료! 이제 어디서나 'mcp' 사용 가능
cd ..
```

### 프로젝트별 설정

⚠️ **중요**: `mcp init` 명령어는 **현재 작업 디렉토리**에 `.ai/` 폴더를 생성합니다. 반드시 프로젝트 폴더에서 실행하세요!

```bash
# ✅ 올바른 방법 1: mcp-cli 밖의 위치에서 실행
cd ~/projects  # mcp-cli가 아닌 다른 위치
mcp init my-project
cd my-project
mcp install --all-tools

# ✅ 올바른 방법 2: 기존 프로젝트 폴더에서 실행
cd /path/to/existing-project
mcp install --all-tools

# ❌ 틀린 방법: mcp-cli 폴더 안에서 실행하면 안 됨!
cd mcp-cli                    # ✗ 이 위치에서 실행하면
mcp init my-project           # ✗ mcp-cli/.ai/ 생성됨 (원치 않음)
```

**올바른 흐름:**

```bash
# 1단계: 프로젝트 루트로 이동 (mcp-cli 안이 아님!)
cd ~/my-awesome-project       # 프로젝트 폴더

# 2단계: 모든 IDE 도구 설정 설치
mcp install --all-tools

# 3단계: 생성된 파일 확인
ls -la | grep -E '^\..*'
# 표시되어야 함:
#   .cursorrules                    ← 생성됨 (Cursor IDE용)
#   .claude/project.md              ← 생성됨 (Claude Code용)
#   .github/copilot-instructions.md ← 생성됨 (GitHub Copilot용)

# 4단계: IDE 도구와 함께 사용 시작
# (Cursor, Claude, VS Code with Copilot 등에서 프로젝트 폴더 열기)
```

**경로가 꼬인 경우 (mcp-cli/.ai/ 생성됨):**

```bash
# mcp-cli 폴더에서 실수로 mcp init을 실행했다면:

# 1. 잘못된 .ai/ 폴더 삭제
cd mcp-cli
rm -rf .ai

# 2. 올바른 위치에서 다시 실행
cd ../my-project  # 또는 다른 프로젝트 폴더
mcp install --all-tools
```

### 일상 워크플로우

```bash
# 1. 규칙 및 스펙 수정
vi .ai/.cursorrules
vi .ai/spec/MCP_OS_Operational_Spec_v0_1.md

# 2. 생성된 파일에 변경사항 동기화
mcp sync

# 3. IDE 도구가 자동으로 변경사항 적용

# 4. 적용하지 않고 변경사항만 확인
mcp sync --check

# 5. 모든 것 강제 재생성
mcp sync --force
```

---

## 지원

### 주요 문서

- **전체 스펙**: `.ai/spec/MCP_OS_Operational_Spec_v0_1.md`
- **시스템 개요**: `.ai/README.md`
- **MCP 설정 가이드**: `MCP_SETUP_GUIDE.md`
- **Claude Code 설정**: `CLAUDE_CODE_SETTINGS.md` ← `.claude/` 폴더 이해하기
- **설치 문제 해결**: 위의 "문제 해결" 섹션 참조

### `.claude/` 폴더 설정에 대해 알아보기

MCP는 다음 파일들을 자동으로 생성하고 관리합니다:

| 파일 | 생성자 | 역할 | Git 관리 |
|---|---|---|---|
| `.claude/settings.json` | MPC (자동) | Claude Code 공식 설정 | ✅ 커밋 |
| `.claude/project.md` | MCP (자동) | 프로젝트 컨텍스트 (에이전트, 스킬 등) | ❌ 생성됨 |
| `.claude/settings.local.json` | 사용자 (수동) | 로컬 환경별 오버라이드 | ❌ 개인용 |

자세한 내용은 **`CLAUDE_CODE_SETTINGS.md`** 참조

---

## 라이선스

MIT

---

**버전**: 0.1.0
**MCP OS 버전**: 0.1
**최종 업데이트**: 2026-01-21
