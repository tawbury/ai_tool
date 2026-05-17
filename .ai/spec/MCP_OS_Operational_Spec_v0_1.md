# MCP OS Operational Specification v0.1

## 1. Introduction

This document defines the operational specification for the MCP OS (Model Context Protocol Operating System), a comprehensive multi-agent AI system designed for managing complex projects across development, content creation, finance, HR, and strategic planning.

## 2. Core Design Principles

### SSoT (Single Source of Truth)

The `.ai/` directory serves as the single source of truth for all system definitions:
- Agent specifications and capabilities
- Skill definitions and implementations
- Workflow execution patterns
- Validation rules and quality standards
- Document templates and structures
- System configuration and mapping rules

Generated files are auto-created from `.ai/` sources and must never be manually edited.

### Generated Files Policy

All IDE-specific configuration files are automatically generated:
- `.github/copilot-instructions.md` - GitHub Copilot project context
- `.claude/project.md` - Claude Code project context
- `.cursorrules` - Cursor IDE rules
- `.windsurfrules` - Windsurf IDE rules (optional)

**Critical Policy**: Manual edits to generated files will be lost when `mcp sync` is run. All changes must be made to source files in `.ai/` directory.

### Artifact Separation

The system enforces strict separation of artifacts by purpose and AI visibility:

**AI Visible Directories**:
- `docs/` - Official confirmed documents (authoritative project artifacts)
- `vault/` - AI drafts and experimental content (AI workspace)
- `.ai/` - System rules and definitions (source of truth)

**AI Not Visible Directories**:
- `ops/` - Operations logs, approvals, audit records (append-only, human-focused)
- `backup/` - Disaster recovery backups (read-only archive)

### Session Resilience

The system is designed for session-resilient operation:
- All state persisted in filesystem (ops/run_records/, roadmaps, task definitions)
- Conversation context is NOT a source of truth
- Previous session state can be recovered from files
- Metadata-first linking ensures document relationships survive session boundaries

### Metadata-First Linking

All document relationships are declared in metadata sections using [[Obsidian link]] syntax:
- Parent Document: [[parent_file.md]]
- Related Documents: [[doc1.md]], [[doc2.md]]
- Referenced By: [[referencing_file.md]]

This enables:
- Context recovery across sessions
- Automated dependency tracking
- Document graph visualization
- Workflow continuity

## 3. Directory and Path Standards

### Project Root Structure

```
project_root/
├── .ai/                          Single Source of Truth
│   ├── spec/                      Operational specifications
│   ├── agents/                    Agent definitions (5 agents)
│   ├── skills/                    Skills by agent (90+ skills)
│   ├── validators/                Validation rules (24+ validators)
│   ├── workflows/                 Workflow definitions (8 workflows)
│   ├── templates/                 Document templates (15 templates)
│   ├── install/                   Tool integration mapping
│   ├── export/chat/               Conversational AI configs
│   └── .cursorrules               Cursor rules source
│
├── docs/                          Project artifacts
│   ├── decisions/                 Decision records
│   ├── tasks/                     Task definitions
│   ├── reports/                   Evaluation reports
│   ├── dev/                       Development documents
│   │   ├── archi/                 Architecture documents
│   │   ├── spec/                  Technical specifications
│   │   └── PRD/                   Product requirements
│   └── index/                     Index documents
│
├── vault/                         AI workspace
│   ├── drafts/                    AI-generated drafts (AI visible)
│   ├── pending/                   Review-pending docs (AI visible)
│   ├── experiments/               Experimental content (AI restricted)
│   └── legacy/                    Legacy materials (AI restricted)
│
├── ops/                           Operations records
│   ├── run_records/               Workflow execution logs (JSON)
│   ├── approvals/                 Approval packets (Markdown)
│   ├── audit/                     Audit logs
│   └── notes/                     Manual operational notes
│
├── backup/                        Disaster recovery
│   ├── docs/                      docs/ backups
│   ├── vault/                     vault/ backups
│   └── .ai/                       .ai/ backups
│
├── .claude/                       Claude Code configuration
│   ├── settings.json              Claude settings
│   └── project.md                 Auto-generated project context
│
├── .github/                       GitHub integration
│   └── copilot-instructions.md    Auto-generated Copilot context
│
├── .cursorrules                   Auto-generated Cursor IDE rules
│
└── mcp-cli/                       MCP CLI tool
    ├── src/                       TypeScript source
    ├── lib/                       Compiled JavaScript
    └── node_modules/              Dependencies
```

### File Naming Conventions

**Task Documents**: `task_{role}_{dept}.md`
- Example: `task_backend_developer_dev.md`

**Decision Records**: `decision_{project}_{YYYYMMDD}.md`
- Example: `decision_auth_system_20250125.md`

**Reports**: `report_{role}_{dept}_{date}.md`
- Example: `report_hr_evaluation_20250125.md`

**Architecture Documents**: `architecture_{project}.md`
- Example: `architecture_trading_system.md`

**Specifications**: `spec_{module}.md`
- Example: `spec_api_authentication.md`

**PRDs**: `prd_{project}.md`
- Example: `prd_user_dashboard.md`

**Run Records**: `run_{workflow_id}_{run_id}.json`
- Example: `run_hr_eval_20250125_001.json`

**Approval Packets**: `approval_{context}_{timestamp}.md`
- Example: `approval_architecture_review_20250125.md`

## 4. Agent System

### Agent Definitions

The system includes 5 specialized agents:

1. **Developer Agent** - Software design, implementation, testing, deployment
2. **HR Agent** - Role assessment, task classification, performance evaluation
3. **PM Agent** - Product strategy, roadmap planning, requirements management
4. **Finance Agent** - Budget management, financial analysis, forecasting
5. **Contents-Creator Agent** - Multi-media content production (text, visual, video)

### Skill Levels

**L1 (Junior Level)**:
- Basic implementation tasks
- Standard procedure execution
- Foundational knowledge application
- Supervised work execution

**L2 (Senior Level)**:
- Strategic planning and architecture
- Leadership and mentorship
- Expert-level validation and review
- Independent decision-making

### Shared Operational Skills

All agents have access to shared operational frameworks:
- `operational_roadmap_management.skill.md` - Roadmap management
- `operational_run_record_creation.skill.md` - Evidence documentation
- `analytics_framework.skill.md` - Unified analytics patterns
- `optimization_framework.skill.md` - Optimization techniques
- `research_framework.skill.md` - Research methodologies

## 5. Workflow System v2.0

### Operational Loop

All workflows follow this pattern:

```
Roadmap (phase/session structure)
    ↓
Task (executable unit)
    ↓
Skill Execution (agent processes task)
    ↓
Run Record (evidence document)
    ↓
Roadmap Update (review record, plan next)
```

### 4-Stage Standard Workflow

1. **Stage 1: Planning** (PRD Template)
   - Define requirements and goals
   - Output: `docs/dev/PRD/prd_{project}.md`

2. **Stage 2: Design** (Architecture Template)
   - Design system architecture
   - Output: `docs/dev/archi/architecture_{project}.md`

3. **Stage 3: Specification** (Spec Template)
   - Write technical specifications
   - Output: `docs/dev/spec/spec_{module}.md`

4. **Stage 4: Decision** (Decision Template)
   - Record final decisions
   - Output: `docs/decisions/decision_{project}_{date}.md`

### Workflow Continuity

**Session Interruption Recovery**:
1. Read current Roadmap status
2. Review latest Run Records
3. Check Task definitions
4. Continue from last completion point

**Metadata-First Linking**:
- All relationships declared in document metadata
- No dependency on conversation history
- File system is source of truth

## 6. Document System

### Standard Document Structure

All documents follow this structure:

```markdown
---
Project Name: {project_name}
File Name: {filename}
Document ID: {unique_id}
Status: Draft | In Review | Approved | Archived
Created Date: YYYY-MM-DD
Last Updated: YYYY-MM-DD
Author: {author_name} (L1/L2)
Reviewer: {reviewer_name} (L2)
Parent Document: [[parent.md]]
Related Documents: [[doc1.md]], [[doc2.md]]
Version: {semver}
---

# Document Title

[Document content following template structure]
```

### Template Variables

Templates support these standard variables:
- `{{CURRENT_DATE}}` - Current date in YYYY-MM-DD format
- `{{USER}}` - Current user name
- `{{REVIEWER}}` - Assigned reviewer name
- `{{PROJECT}}` - Project name
- `{{VERSION}}` - Document version

### Language Compliance Rules

**Korean for User Documents** (`docs/` folder):
- All user-facing documents in Korean
- Technical terms may remain in English
- Code and configuration examples in English

**English for System Files** (`.ai/` folder):
- All system definitions in English
- Ensures compatibility across IDEs
- Maintains consistency with tooling

## 7. Validation System

### Validator Types

**Base Validators**:
- `meta_validator.md` - Metadata format validation
- `structure_validator.md` - Document structure validation

**Document Type Validators**:
- `task_validator.md` - Task document validation
- `spec_validator.md` - Specification validation
- `prd_validator.md` - PRD validation
- `architecture_validator.md` - Architecture validation
- `decision_validator.md` - Decision record validation
- `report_validator.md` - Report validation

**Skill Validators**:
- `skill_validator.md` - General skill validation
- `skill_loading_validator.md` - Skill loading optimization
- `skill_execution_validator.md` - Execution quality validation

**Agent-Specific Validators**:
- `developer_skill_validator.md`
- `finance_skill_validator.md`
- `hr_skill_validator.md`
- `pm_skill_validator.md`
- `contents_creator_skill_validator.md`

**Advanced Validators**:
- `l2_review_validator.md` - Senior-level work validation
- `mentorship_validator.md` - Knowledge transfer effectiveness
- `cross_agent_validator.md` - Multi-agent collaboration quality
- `senior_decision_validator.md` - Strategic decision validation

### Validation Workflow

1. Execute skill or generate document
2. Select appropriate validator(s)
3. Run validator with output
4. Address any failures
5. Generate validation report
6. Record in Run Record

## 8. MCP CLI Tool

### Commands

**init**: Initialize new project structure
```bash
mcp init [project-name]
```

**install**: Generate IDE-specific configurations
```bash
mcp install --all-tools
mcp install --tool claude_code
mcp install --tool cursor
```

**sync**: Synchronize changes from `.ai/` to generated files
```bash
mcp sync
mcp sync --force
mcp sync --check
```

### Mapping Rules

Defined in `.ai/install/mapping_rules.yaml`:
- Source sections from `.ai/` directory
- Output paths for each IDE tool
- Template files for generation
- Enabled/disabled tool configurations

### Adapter System

Each IDE has an adapter configuration:
- `claude_code.yaml` - Claude Code adapter
- `cursor.yaml` - Cursor IDE adapter
- `github_copilot.yaml` - GitHub Copilot adapter
- `windsurf.yaml` - Windsurf IDE adapter

Adapters define:
- Content sections to include
- Filtering and transformation rules
- Post-processing steps
- Output format specifications

## 9. Integration with IDEs

### Claude Code

**Configuration**: `.claude/settings.json`
**Context File**: `.claude/project.md` (auto-generated)
**Update Command**: `mcp install --all-tools` or `mcp sync`

### Cursor IDE

**Configuration**: `.cursorrules` (auto-generated)
**Source**: `.ai/.cursorrules`
**Update Command**: `mcp install --all-tools` or `mcp sync`

### GitHub Copilot

**Configuration**: `.github/copilot-instructions.md` (auto-generated)
**Update Command**: `mcp install --all-tools` or `mcp sync`

### Windsurf IDE

**Configuration**: `.windsurfrules` (auto-generated, optional)
**Status**: Disabled by default
**Update Command**: Enable in `mapping_rules.yaml`, then `mcp install --all-tools`

## 10. Operational Guidelines

### Do's ✅

- Modify files in `.ai/` to change system behavior
- Create/modify documents in `docs/` following templates
- Add entries to `ops/run_records/` and `ops/approvals/`
- Run `mcp sync` after structural changes
- Use metadata-first linking in documents
- Use [[filename.md]] Obsidian links for references
- Follow L1/L2 role guidelines
- Apply validators before finalizing work
- Maintain append-only policy for ops/ directory

### Don'ts ❌

- Manually edit Generated files (.github/, .claude/, .cursorrules)
- Modify `.ai/` files without understanding their purpose
- Delete or modify entries in `ops/` (append-only)
- Mix SSoT (.ai/) with Generated or Artifact files
- Use wildcard Obsidian links like [[task_*]]
- Skip metadata sections in documents
- Use conversation context as source of truth
- Bypass validation steps
- Violate language compliance rules

## 11. Troubleshooting

### Generated Files Out of Sync

**Issue**: Changes in `.ai/` not reflected in Generated files

**Solution**:
1. Edit files in `.ai/spec/` or `.ai/install/`
2. Run: `mcp sync`
3. Generated files will regenerate

### Missing Document

**Issue**: Can't find where to create a document

**Solution**:
1. Check document type
2. Use corresponding template from `.ai/templates/`
3. Place in appropriate `docs/` subdirectory
4. Follow naming convention

### Session Recovery

**Issue**: Session was interrupted, need to resume

**Solution**:
1. Review `ops/run_records/` for last execution state
2. Check current Roadmap status
3. Read relevant Task definitions
4. Continue from last completion point

### MCP CLI Not Working

**Issue**: MCP commands fail or not found

**Solution**:
1. Check `mcp-cli/node_modules/` exists
2. Run `npm install` in `mcp-cli/` directory
3. Verify compiled files in `mcp-cli/lib/`
4. Test with `node mcp-cli/lib/cli.js --help`

## 12. Version History

- **v0.1** (2025-01-25) - Initial specification release
  - Core design principles established
  - 5 agents, 90+ skills, 24+ validators, 8 workflows
  - MCP CLI tool implementation
  - Multi-IDE integration support
  - Metadata-first linking system
  - Session resilience patterns

---

**For implementation details, consult the source files in `.ai/` directory.**
