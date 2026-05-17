---
name: Developer Database Optimization Unified
type: skill
id: SKILL-DEV-DB-OPT-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: developer
used_by: [developer]
tools: [claude-code, codex, gemini-cli]
---

# Dev Database Optimization Unified Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified database optimization with intelligent technology switching
- NoSQL strategy implementation and query performance optimization
- Single entry point for all database optimization needs with automatic technology detection
- **Scope**: Comprehensive database optimization engine that replaces 2 specialized database skills with intelligent routing
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Database schemas & query patterns
- Performance issues & bottleneck analysis
- Access patterns & load requirements
- Scalability & consistency requirements

### Output
**Unified Output Schema**:
- NoSQL database designs & data models
- Optimized queries & performance analysis reports
- Indexing strategies & optimization recommendations
- Database structure improvement proposals
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| NOSQL_STRATEGY | nosql, document, key-value, graph, column |
| QUERY_OPTIMIZATION | query, optimization, performance, tuning, index |
| QUERY_OPTIMIZATION | query, optimization, performance, tuning, index |
| (default) | (no specific keywords matched) |

### Unified Database Optimization Pipeline

#### Phase 1: Database Analysis & Assessment
1. Database schema & structure analysis
2. Query pattern & access pattern review
3. Performance bottleneck identification
4. Scalability & consistency requirements assessment

#### Phase 2: Mode-Specific Optimization

**NOSQL_STRATEGY Mode**:
- NoSQL database design & implementation
- Unstructured data modeling & schema design
- Scalable data architecture construction
- NoSQL-specific optimization strategies

**QUERY_OPTIMIZATION Mode**:
- Database query optimization & performance tuning
- Performance bottleneck resolution & analysis
- Scalable query strategy establishment
- Index design & query execution plan optimization

**UNIFIED_DATABASE Mode**:
- Comprehensive database optimization approach
- Integrated NoSQL strategy + query optimization
- End-to-end database performance enhancement
- Full-stack database architecture optimization

#### Phase 3: Implementation & Optimization
1. NoSQL database design & data modeling
2. Query optimization & indexing strategy
3. Performance analysis & bottleneck resolution
4. Database structure improvement implementation

#### Phase 4: Testing & Validation
1. Performance testing & benchmarking
2. Query execution plan analysis
3. Scalability testing & load testing
4. Optimization validation & monitoring

### Level-Specific Execution

#### Junior Database Developer (L1)
- Basic NoSQL database implementation
- Simple query optimization & indexing
- Standard performance analysis
- Basic database monitoring

#### Senior Database Developer (L2)
- Advanced NoSQL architecture & data modeling
- Complex query optimization & performance tuning
- Database scaling & strategy development
- Database architecture leadership & optimization
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- NoSQL databases (MongoDB, Cassandra, DynamoDB, Redis)
- Database management systems (PostgreSQL, MySQL)
- Query optimization tools & performance analyzers
- Database monitoring & profiling tools
- Data modeling & schema design tools
- Performance testing & benchmarking frameworks
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Scope Protection

**Purpose**: Physical isolation of application logic in database optimization

**Scope Validation**: Validate scope before processing. Reject if forbidden patterns are detected.

### OUT Scope (Universal)
- Application development & business logic ❌
- Frontend/backend implementation ❌
- API development & endpoint creation ❌
- User interface & user experience ❌
- Infrastructure & deployment management ❌

### Database Optimization Constraints
- Database-only optimization & performance tuning
- Data modeling & schema design
- Query optimization & indexing strategies
- Performance analysis & bottleneck resolution
- Modern database best practices & patterns

### Mode-Specific Constraints
**NOSQL_STRATEGY**: NoSQL databases only, no SQL systems
**QUERY_OPTIMIZATION**: Query performance only, no schema design
**UNIFIED_DATABASE**: Combined constraints with enhanced scope protection

### Quality & Standards Constraints
- Database standards compliance & best practices
- Performance optimization & scalability
- Data integrity & consistency
- Security & data protection
- Modern database architecture patterns
<!-- END_BLOCK -->
