---
name: Code Quality and Technical Debt Analysis
type: skill
id: SKILL-DEV-CODE-QUALITY-v1
version: 2.2.0
updated: 2026-04-14
scope: developer
used_by: [developer]
tools: [claude-code, codex, gemini-cli]
---

# Code Quality and Technical Debt Analysis Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Code quality assessment & measurement and technical debt identification & management
- Quality and debt improvement strategy development
- Code review optimization and architecture health evaluation
- Data-driven quality and technical decision making

## Scope Boundaries
This consolidated skill covers two complementary concerns:
- **Code Quality Analysis**: Current state of code quality (metrics, standards, review efficiency)
- **Technical Debt Analysis**: Accumulated technical debt and architectural health

Use this skill to:
1. Assess current code quality status (quality metrics, standards compliance)
2. Identify and measure technical debt (debt quantification, prioritization)
3. Develop quality improvement and debt reduction strategies
4. Monitor quality trends and debt evolution over time
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
- Source code & repository data
- Code review records & feedback
- Test coverage & quality metrics
- Development process & workflow data
- System performance data & logs
- Architecture documentation & diagrams

### Output
- Code quality assessment reports
- Quality improvement recommendations
- Code review optimization strategies
- Quality monitoring frameworks
- Technical debt assessment reports
- Code quality analysis results
- Refactoring recommendations
- Technical improvement roadmaps
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic
### Junior Developer (L1)
1. Basic code quality assessment
2. Simple quality metric analysis
3. Simple technical debt identification
4. Basic improvement recommendations
5. Simple quality reporting

### Senior Developer (L2)
1. Advanced code quality methodology
2. Complex quality modeling
3. Advanced technical debt analysis
4. Complex code quality modeling
5. Strategic quality and technical insights
6. Quality and architecture optimization strategies

## Skill Components (Part 1: Code Quality Analysis)

### Quality Assessment
#### Code Quality Metrics
- Code complexity analysis (cyclomatic complexity, cognitive complexity)
- Code duplication detection
- Code maintainability assessment
- Code readability evaluation
- **Hard coding detection** (absolute paths, magic numbers, hardcoded values)
- **Path configuration analysis** (relative vs absolute path usage)

#### Quality Standards
- Coding standards compliance
- Best practices adherence
- Design pattern usage
- Documentation quality
- **Path management standards** (no absolute paths, configuration-based approach)
- **Environment-specific configuration** (development/staging/production)

### Quality Improvement
#### Junior Level (L1)
- Basic refactoring recommendations
- Simple code improvement suggestions
- Basic test coverage improvement
- Simple documentation enhancement

#### Senior Level (L2)
- Advanced quality improvement strategies
- Complex refactoring planning
- Quality architecture optimization
- Strategic quality frameworks

### Code Review Optimization
#### Review Process
- Review efficiency analysis
- Review quality assessment
- Review bottleneck identification
- Review workflow optimization

#### Review Quality
- Review effectiveness measurement
- Review consistency analysis
- Review coverage optimization
- Review feedback quality

## Skill Components (Part 2: Technical Debt Analysis)

### Technical Debt Assessment
#### Debt Identification
- Code complexity analysis
- Code duplication detection
- Architecture violation identification
- Performance bottleneck analysis
- **Hard coding technical debt** (absolute paths, environment-specific values)
- **Configuration management debt** (missing environment variables, hardcoded settings)

#### Debt Measurement
- Technical debt quantification
- Debt impact assessment
- Debt prioritization
- Debt trend analysis

### Code Quality Analysis (Debt Perspective)
#### Junior Level (L1)
- Basic code quality metrics (from debt assessment view)
- Simple code review analysis
- Basic test coverage analysis
- Simple documentation quality

#### Senior Level (L2)
- Advanced code quality modeling
- Complex quality metrics analysis
- Quality trend analysis
- Quality improvement strategies

### Architecture Analysis
#### System Architecture
- Architecture complexity assessment
- Design pattern analysis
- Coupling & cohesion analysis
- Scalability assessment

#### Technical Health
- System performance analysis
- Security vulnerability assessment
- Maintainability analysis
- Technical risk assessment

## Analytical Methods

### Static Analysis
- Code complexity metrics
- Code duplication analysis
- Code smell detection
- Security vulnerability scanning
- **Hard coding pattern detection** (absolute paths, magic strings/numbers)
- **Path dependency analysis** (cross-platform compatibility)

### Dynamic Analysis
- Test coverage analysis
- Performance profiling
- Memory usage analysis
- Execution time analysis

### Quality Modeling
- Quality trend analysis
- Quality prediction models
- Quality risk assessment
- Quality improvement forecasting

### Architectural Analysis
- Dependency analysis
- Coupling analysis
- Modularity assessment
- Design pattern compliance

## Data Sources

### Code Data
- Source code repositories
- Code review records
- Test coverage data
- Build & deployment data
- Issue tracking data

### Quality & Performance Tools
- Static analysis tools
- Code quality platforms
- Test automation tools
- Performance monitoring tools

## Performance Metrics

### Junior Developer Metrics
- Quality assessment accuracy
- Debt identification accuracy
- Basic recommendation relevance
- Analysis timeliness
- Report usefulness

### Senior Developer Metrics
- Advanced quality modeling accuracy
- Advanced debt modeling accuracy
- Strategic insight quality
- Quality improvement impact
- Architecture optimization impact
- Technical improvement effectiveness

## Analysis Tools

### Platforms & Tools
- SonarQube
- CodeClimate
- Coverity
- Veracode

### Visualization Tools
- Code quality visualization
- Technical debt dashboards
- Architecture visualization tools
- Dependency graph tools

### Quality Metrics
- Cyclomatic complexity
- Cognitive complexity
- Code duplication
- Test coverage
- **Hard coding violations count**
- **Absolute path usage metrics**
- **Configuration externalization score**

## Integration
- Connect to dev_code_review for review-informed analysis
- Integrate with dev_testing for test-quality analysis
- Enable dev_documentation for documentation quality
- Integrate with dev_performance_optimization for performance correlation
- Support dev_system_architecture for architecture analysis
- Enable dev_security for security-informed debt analysis

## Quality Standards
- Analysis methodology rigor
- Quality measurement accuracy
- Debt measurement accuracy
- Recommendation relevance
- Technical feasibility validation
- **Hard coding prevention standards**
- **Path configuration best practices**
- **Environment-specific configuration guidelines**

## Hard Coding Prevention Guidelines

### Prohibited Patterns
- **Absolute file paths** (e.g., `C:\Users\admin\config.json`, `/home/user/data`)
- **Hardcoded URLs** (e.g., `http://localhost:8080/api`)
- **Environment-specific values** (e.g., database passwords, API keys)
- **Magic numbers/strings** without constants

### Allowed Exceptions (with justification)
1. **System-critical paths** (OS-level dependencies, kernel modules)
2. **Build-time constants** (compile-time configuration, embedded resources)
3. **Security-critical hardcoded values** (with proper encryption/access control)
4. **Development-only debugging paths** (with compile-time guards)

### Implementation Requirements
- Use environment variables for configuration
- Implement configuration files (JSON/YAML/ENV)
- Provide fallback mechanisms
- Document all exceptions with security review
- Cross-platform path handling (path.join, pathlib)

<!-- END_BLOCK -->

<!-- BLOCK:CONSOLIDATION_NOTE -->
## Consolidation Note (2026-01-17)
This file consolidates two previously separate skills:
Original Part 1: code_quality_analysis.skill.md (archived at backup/phase2/skills/developer/code_quality_analysis.skill.md.bak_20260117)
Original Part 2: technical_debt_analysis.skill.md (archived at backup/phase2/skills/developer/technical_debt_analysis.skill.md.bak_20260117)

Reason: Both skills use identical analysis tools (SonarQube, CodeClimate, etc.), identical data sources (code repository data, metrics), and produce complementary outputs. Consolidation reduces redundancy while preserving all functionality.

Deprecated stubs have been moved to: backup/phase2/skills/deprecated/

For rollback instructions, see .ai/docs/manifests/PHASE2_DEPRECATED_SKILLS_MANIFEST.md.
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICAL_REQUIREMENTS -->
## Technical Requirements
- Source code analysis tools (SonarQube, CodeClimate, Coverity)
- Git repository access & metadata
- Build & deployment data
- Performance monitoring data
- Architecture documentation tools
- Code review platforms
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints
### OUT of Scope
- Direct code modification ❌
- Permanent architecture redesign ❌
- Project timeline management ❌
- Personnel evaluation ❌

### Analysis Constraints
- Objective metrics focus
- Tool-based analysis (not opinion-based)
- Feasibility validation required
- Technical improvement focus only
<!-- END_BLOCK -->
