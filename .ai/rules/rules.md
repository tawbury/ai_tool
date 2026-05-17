---
description: "Master system rules for multi-agent orchestration (Cursor, GitHub Copilot, Claude Code, Windsurf)"
globs: "**/*"
alwaysApply: true
---

# System Rules v2.1
*Last Updated: 2026-01-26*
*Version: 2.1.0*

## 1. Language & Content Rules

### Language & Encoding Requirements
- **docs/ Folder**: All documents in `docs/` folder MUST be written in Korean
- **.ai/ Folder**: All documents in `.ai/` folder MUST be written in English
- **Encoding Rule**: ALL files (especially those containing Korean) MUST be created and saved in **UTF-8 without BOM** encoding format. When using shell scripts (like PowerShell), explicitly define `-Encoding UTF8` to prevent text corruption.
- **Mixed Language Prohibition**: Never mix languages within the same document
- **Language Consistency**: Maintain consistent language usage throughout each document
- **Communication Language**: All user interactions (chat, responses) must be in Korean. Technical terms and code explanations may include English.

### Content Creation Rules
- **docs/tasks/**: Task documents must be created in Korean using Korean templates
- **docs/reports/**: Report documents must be generated in Korean
- **docs/dev/**: Development documentation must be written in Korean
- **AI System**: `.ai/agents/`, `.ai/skills/`, `.ai/workflows/` must be in English

### Language Validation
- **Language Detection**: Automatically detect document language before processing
- **Language Enforcement**: Reject or correct documents that violate language rules
- **Template Language**: Use language-appropriate templates for each folder
- **Template Translation**: When using English templates for docs/ folder, automatically translate content to Korean
- **Template Language Mapping**: 
  - docs/tasks/ ??Use Korean templates or translate English templates to Korean
  - docs/reports/ ??Use Korean templates or translate English templates to Korean
  - docs/dev/ ??Use Korean templates or translate English templates to Korean
  - .ai/ ??Use English templates (no translation needed)

### Template Processing Rules
- **Template Source**: Templates can be stored in either language, but output must match folder language requirements
- **Auto-Translation**: When generating docs/ folder documents from English templates, automatically translate content to Korean
- **Template Variables**: Template variables ({{CURRENT_DATE}}, {{USER}}) remain in original format
- **Structure Preservation**: Maintain template structure while translating content only
- **Meta Section Handling**: Meta section fields can remain in English, but content sections must be in Korean for docs/ folder
- **Content Translation**: Translate content sections to match folder language requirements
- **Template Validation**: Validate templates for language consistency and structure integrity

## 2. Directory & Path Mapping

### HR Evaluation
- **Role Definition Input**: `docs/tasks/task_<role>_<dept>.md`.
- **Evaluation Output**: `docs/reports/report_<role>_<dept>_<YYYYMMDD>.md`.

### Development Documentation
- **Architecture Docs**: `docs/dev/archi/`
- **Specifications**: `docs/dev/spec/`
- **PRD**: `docs/dev/PRD/`
- **Decision Records**: `docs/dev/decision/`

### AI System Structure
- **Agent Definitions**: `.ai/agents/`
- **Skill Definitions**: `.ai/skills/`
- **Templates**: `.ai/templates/`
- **Validators**: `.ai/validators/`
- **Workflows**: `.ai/workflows/`

### Excluded Folders (MCP-cli Only)
- **export/**: MCP-cli export functionality (not AI system)
- **install/**: MCP-cli installation management (not AI system)
- **spec/**: MCP-cli specification documents (not AI system)

## 3. Workflow System v2 Rules

### Metadata-First Linking (Enforced)
- All document relationships MUST be declared in the document metadata.
- If a relationship is not present in metadata fields (e.g., Parent Document, Related Reference), it is considered non-existent for operational purposes.
- Body text may explain context, but must not be the only place where relationships are defined.
- Use Obsidian internal links for relationships: [[filename.md]].

### Operational Loop Rules (Enforced)
- Core loop: Roadmap -> Task -> Run Record -> Roadmap update
- Roadmap drives work selection and phase/session status.
- Task is the smallest executable unit; Task must reference its Roadmap via metadata (Parent Document).
- Run Record is execution evidence; it must reference the executed Task (Parent Document) and relevant Roadmap (Related Reference).
- Roadmap updates MUST cite Run Records as evidence (in change history or related links).
- Wildcard links are forbidden in Obsidian links (no patterns like task_*.md). Use real filenames only.

### Operational Loop Templates
- [[roadmap_template.md]]
- [[run_record_template.md]]
- [[task_template.md]]

## 4. Agent System

### Available Agents
- **hr**: HR evaluation and management
- **developer**: Technical development and implementation
- **contents-creator**: content creation and management
- **finance**: Financial analysis and management
- **pm**: Project management and coordination

### Agent Context
- **HR Agent**: Refer to `.ai/agents/hr.agent.md` for overall execution flow
- **Developer Agent**: Refer to `.ai/agents/developer.agent.md`
- **Contents Creator Agent**: Refer to `.ai/agents/contents-creator.agent.md`
- **Finance Agent**: Refer to `.ai/agents/finance.agent.md`
- **PM Agent**: Refer to `.ai/agents/pm.agent.md`

**System Rules SSoT**: `.ai/rules/rules.md` is the single source of truth for system rules. All tool-specific configurations (Cursor `.cursorrules`, Copilot instructions, Claude project file, Windsurf rules) MUST be physically synchronized via mcp-cli. **Symbolic links (symlinks) are STRICTLY PROHIBITED** due to cross-platform compatibility and AI native parsing issues.

## 5. L1/L2 Agent System

### Junior Agents (L1)
- **Role**: Task execution, basic implementation, standard procedures
- **Responsibility**: Document creation, template compliance, basic quality assurance
- **Authority**: Create documents, execute defined tasks, self-review
- **Limitations**: Cannot approve final work, requires senior review for critical decisions

### Senior Agents (L2)
- **Role**: Strategic planning, architecture design, leadership, review
- **Responsibility**: Technical excellence, final approval, mentorship, certification
- **Authority**: Review and validate L1 work, make strategic decisions, override L1
- **Requirements**: Must provide detailed rationale for all decisions

### L1/L2 Collaboration Protocol
1. **Document Creation**: L1 creates ??L2 reviews ??L2 approves/rejects with feedback
2. **Task Assignment**: L2 plans ??L1 executes ??L2 validates
3. **Quality Gates**: L2 must review all critical documents before finalization
4. **Escalation**: L1 can escalate complex issues to L2 with proper justification

## 6. Constraint Enforcement

### System Constraints
- **File Integrity**: Do not manually edit generated rule files at the project root (e.g., `.cursorrules`, `.github/copilot-instructions.md`, `.claude/project.md`, `.windsurfrules`). Always edit `.ai/rules/rules.md` and use the MCP sync command to physically distribute updates. Do not use symlinks to connect these files.
- **Agent Boundaries**: Each agent operates within defined scope and constraints
- **Language Compliance**: Enforce language rules for all document creation and modification

### HR Evaluation Constraints
- **Meta Isolation**: Never use Meta section data (like Expected Level) to influence the final Evaluation Result.
- **Pending Protocol**: If criteria are insufficient, Status must be `PENDING` and the `Feedback for Improvement` section must be detailed.
- **No Natural Language**: Reports should be structured and deterministic for other agents to consume.

### Development Documentation Constraints
- **Template Consistency**: All development documents must follow standardized templates
- **Version Control**: Maintain version history for all architecture and specification documents
- **Cross-Reference**: Ensure proper linking between related documents

## 7. Validation System

### Document Validation
- **Task Validator**: Use `.ai/validators/task_validator.md` for task document validation
- **Template Compliance**: Ensure all documents follow their respective templates
- **Meta Data Integrity**: Validate required meta fields are present and correctly formatted
- **Execution Validation**: After code or document modification, validation MUST follow the rules defined in `.ai/validators/` (e.g., `task_validator.md`). If executable validation scripts are provided for this project, they SHOULD be run and MUST pass before work is considered complete.

### Validation Process
1. **Structure Check**: Verify document structure matches template
2. **Meta Validation**: Ensure all required meta fields exist
3. **content Validation**: Verify content sections are properly formatted
4. **Link Validation**: Check internal and external references are valid

## 8. Document Templates

### Template References
- **Task Template**: `.ai/templates/task_template.md`
- **Report Template**: `.ai/templates/report_template.md`
- **Architecture Template**: `.ai/templates/architecture_template.md`
- **Specification Template**: `.ai/templates/spec_template.md`
- **PRD Template**: `.ai/templates/prd_template.md`
- **Decision Template**: `.ai/templates/decision_template.md`

### Template Usage Guidelines
- **docs/tasks/**: Use Task Template for HR evaluation role definitions
- **docs/reports/**: Use Report Template for HR evaluation results
- **docs/dev/archi/**: Use Architecture Template for system architecture
- **docs/dev/spec/**: Use Specification Template for technical specifications
- **docs/dev/PRD/**: Use PRD Template for product requirements
- **docs/dev/decision/**: Use Decision Template for technical decisions

### Template Variables
- **{{CURRENT_DATE}}**: Current date in YYYY-MM-DD HH:MM format
- **{{USER}}**: Current user name
- **{{REVIEWER}}**: Senior agent designation for L2 validation
- All templates support standardized meta section with content separator `---`

### Template Compliance
- All documents must follow their respective templates
- Meta section fields must not be empty
- Content sections must use proper header format (##)
- Language rules apply: docs/ in Korean, .ai/ in English

## 9. Workflow Systems

### HR Evaluation Workflow
Whenever a user requests to "create a new role" or "evaluate a position":
1. **Generate Task**: Create a file in `docs/tasks/` using the **Task Template**.
2. **Validate Structure**: Run `HR_Onboarding_Init` logic to ensure all Meta and content sections exist (implemented in `.ai/validators/task_validator.md` and `.ai/skills/hr/hr_onboarding.skill.md`).
3. **Level Judgment**: Apply `HR_Level_Check` using department-specific keywords (Dev/content).
4. **Emit Report**: Produce the final evaluation in `docs/reports/`.

### Development Documentation Workflow
1. **Architecture Design**: Create architecture docs using Architecture Template
2. **Specification**: Define functional specs with API interfaces
3. **PRD Creation**: Define product requirements
4. **Decision Records**: Document key technical decisions

## 10. Error Handling & Recovery

### Document Creation Errors
- **Template Validation Failure**: Reject creation, provide specific error message
- **Language Policy Violation**: Auto-correct if possible, otherwise reject with guidance
- **Metadata Incomplete**: Block creation, list missing required fields

### System Recovery Protocol
1. **Session Interruption**: Resume from last valid Roadmap + Run Records
2. **Corrupted Documents**: Restore from last known good state, log incident
3. **Validation Failures**: Isolate affected documents, continue with valid ones
4. **Agent Failure**: Switch to backup agent, log error for analysis
5. **Infrastructure Error**: On Docker build or image conflicts, agents must stop infinite retries, analyze error logs, and provide solutions to users.

### Error Reporting
- All errors must be logged with timestamp, context, and resolution
- Critical errors require immediate notification and escalation
- Pattern analysis for recurring issues and systemic improvements

## 11. Performance & Optimization

### Context Management
- **Loading Optimization**: Load only relevant templates and skills per task
- **Memory Limits**: Monitor context usage, implement cleanup protocols
- **Cache Strategy**: Cache frequently used templates, invalidate on changes

### Workflow Efficiency
- **Parallel Processing**: Execute independent tasks simultaneously when possible
- **Batch Operations**: Group similar operations for efficiency
- **Resource Allocation**: Optimize agent assignment based on workload and expertise

## 12. Additional Rules

### Rule 1: Metadata Integrity
- **Description**: All documents must maintain complete and accurate metadata
- **Enforcement**: Automatic validation on document creation and modification
- **Compliance**: Required for all document operations

### Rule 2: Link Validation
- **Description**: All internal links must reference existing documents
- **Enforcement**: Automatic link checking on document save
- **Recovery**: Broken links trigger automatic documentation update

## 13. Enforcement & Compliance

### Rule Enforcement Protocol
- **Automatic Validation**: All rules automatically enforced on document creation/modification
- **Real-time Monitoring**: Continuous compliance checking during agent operations
- **Violation Handling**: Automatic correction when possible, manual review required for critical violations

### Compliance Metrics
- **Language Compliance**: 100% enforcement for folder-specific language requirements
- **Template Compliance**: 100% validation for required meta fields and structure
- **Link Integrity**: 99.9% target for valid internal references
- **Metadata Completeness**: 100% requirement for all mandatory fields

### Update Protocol
- **Version Control**: Semantic versioning (Major.Minor.Patch)
- **Change Log**: Document all changes with date, reason, and impact
- **Backward Compatibility**: Maintain compatibility for at least one previous version
- **Rollback Procedure**: Emergency rollback capability for critical issues

## Project Guidelines (CLAUDE.md)

## 🛠 Operations
- **Environment:** This project is based on the Docker container environment.
- **Build/Run:** If the project provides 'docker-compose.yml' or 'Makefile', scan them to identify the correct context before executing a specific command.
- **Execution:** Agents do not rely on their local environment, and if necessary, perform commands through the inner shell of the container.

## 📌 Key Rules (Key Rules)
- **Rules Sync:** All operations follow the detailed guidelines of '.ai/rules/' as a top priority.
- **Languages:** Strictly adhere to the rules for 'docs/' in Korean and '.ai/' in English.
- **Encoding:** Always use UTF-8 encoding to avoid Korean text corruption.
- **Name:** Variables use 'CamelCase' and 'UPPER_SNAKE_CASE' for constants.

## 🔄 Agent Workflow
1. **Explore:** Before modifying, analyze the verification script and project structure of '.ai/validators/' first.
2. **Validate:** After completing the task, run a project-specific verification loop, not a simple test command.
3. **Report:** Record execution results and changes in Korean in 'docs/reports/'

---
*End of System Rules v2.1*