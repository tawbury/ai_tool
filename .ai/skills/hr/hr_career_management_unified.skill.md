---
name: HR Career Management Unified
type: skill
id: SKILL-HR-CAREER-MGMT-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: hr
used_by: [hr]
tools: [claude-code, codex, gemini-cli]
---

# HR Career Management Unified Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified career management with intelligent mode switching
- Career path design, growth planning, and opportunity management
- Single entry point for all career-related needs with automatic domain detection
- **Scope**: Comprehensive career management engine that replaces 2 specialized career skills with intelligent routing between strategic management and tactical pathing
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Employee career data (objectives, performance, capabilities, interests)
- Opportunity information (internal roles, promotions, transfers)
- Development requirements (skills, experiences, timeline)
- Context parameters (timeframe, scope, constraints)

### Output
**Unified Output Schema**:
- Comprehensive career roadmaps & development plans
- Promotion & transfer opportunity recommendations
- Growth strategies & capability development plans
- Career coaching guides & progress tracking
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the career mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| STRATEGIC_MANAGEMENT | strategy, management, overall, comprehensive, long-term |
| CAREER_PATHING | path, roadmap, specific, detailed, step-by-step |
| UNIFIED | (default — no specific keywords matched) |

### Unified Career Management Pipeline

#### Phase 1: Career Assessment & Analysis
1. Current capabilities & performance evaluation
2. Career objectives & aspirations clarification
3. Strengths & growth potential identification
4. Internal opportunity landscape analysis

#### Phase 2: Mode-Specific Processing

**STRATEGIC_MANAGEMENT Mode**:
- Long-term career strategy development
- Organizational needs vs personal objectives alignment
- Promotion timing & pathway prediction
- Career coaching framework establishment

**CAREER_PATHING Mode**:
- Detailed career path design & mapping
- Step-by-step development roadmap creation
- Specific skill acquisition planning
- Timeline & milestone establishment

**UNIFIED Mode**:
- Comprehensive career management approach
- Strategic oversight with tactical pathing
- Integrated opportunity analysis
- Holistic development planning

#### Phase 3: Opportunity Analysis & Matching
1. Internal job opportunity exploration
2. Promotion path & timing analysis
3. Horizontal transfer possibility assessment
4. New role development opportunities

#### Phase 4: Development Planning
1. Required capability development plans
2. Education & training program recommendations
3. Project assignment proposals
4. Mentoring & networking strategies

#### Phase 5: Implementation & Progress Management
1. Regular career review schedules
2. Goal achievement evaluation metrics
3. Plan adjustment & modification protocols
4. Success case documentation & sharing

### Level-Specific Execution

#### Junior Career Manager (L1)
- Basic career path template application
- Simple opportunity identification
- Standard development plan creation
- Basic progress tracking

#### Senior Career Manager (L2)
- Advanced career strategy development
- Complex opportunity analysis
- Customized roadmap design
- Strategic career coaching
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Career management system integration
- Job database & opportunity matching systems
- Performance evaluation system connection
- Career mapping & visualization tools
- Progress tracking & analytics platforms
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Meta Information Protection

**Forbidden Patterns** (must not appear in task content):
- Individual evaluation, personal rating, specific person references
- Confidential career, private development, secret promotion references

**Scope Validation**: Career management scope must be validated before processing. Reject if personal career meta information is detected.

### OUT Scope (Universal)
- Actual promotion decisions & salary management ❌
- Individual evaluation execution & personal counseling ❌
- Actual transfer/deployment execution ❌
- Legal personnel management & compensation decisions ❌

### Career Management Constraints
- Analysis-based proposals & recommendations only
- Fair opportunity provision & equal consideration
- Organizational needs & personal objectives balance
- Sustainable career growth & development support
- Personal information protection & confidentiality

### Mode-Specific Constraints
**STRATEGIC_MANAGEMENT**: No individual career decisions, strategic level only
**CAREER_PATHING**: No actual deployment decisions, path design only
**UNIFIED**: Combined constraints with enhanced privacy protection
<!-- END_BLOCK -->
