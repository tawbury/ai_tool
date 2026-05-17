---
name: Developer Cloud Architecture Unified
type: skill
id: SKILL-DEV-CLOUD-ARCH-UNIFIED-v1
version: 2.2.0
updated: 2026-04-14
scope: developer
used_by: [developer]
tools: [claude-code, codex, gemini-cli]
---

# Dev Cloud Architecture Unified Skill

<!-- BLOCK:CORE_LOGIC -->
## Core Logic
- Unified cloud architecture with intelligent service switching
- Microservices architecture, cloud infrastructure, and containerization integration
- Single entry point for all cloud architecture needs with automatic service detection
- **Scope**: Comprehensive cloud architecture engine that replaces 3 specialized cloud skills with intelligent routing
<!-- END_BLOCK -->

<!-- BLOCK:INPUT_OUTPUT -->
## Input/Output
### Input
**Universal Input Schema**:
- Application architecture & monolithic structures
- Business domain analysis & scalability requirements
- Inter-service communication requirements
- Security, compliance, and cost constraints

### Output
**Unified Output Schema**:
- Microservice design specifications & service separation strategies
- Cloud infrastructure designs & service architecture specifications
- Container orchestration setups & distributed data management strategies
- Cost optimization strategies & disaster recovery plans
<!-- END_BLOCK -->

<!-- BLOCK:EXECUTION_LOGIC -->
## Execution Logic

### Mode Detection Rules

Select the mode by matching keywords in the input:

| Mode | Keywords |
|------|----------|
| MICROSERVICES_ARCHITECTURE | microservice, service, domain, distributed, separation |
| CLOUD_INFRASTRUCTURE | cloud, infrastructure, aws, azure, gcp, cost |
| CONTAINERIZATION | container, docker, kubernetes, orchestration, deployment |
| CLOUD_INFRASTRUCTURE | cloud, infrastructure, aws, azure, gcp, cost |
| CONTAINERIZATION | container, docker, kubernetes, orchestration, deployment |
| (default) | (no specific keywords matched) |

### Unified Cloud Architecture Pipeline

#### Phase 1: Architecture Analysis & Planning
1. Application architecture analysis & monolithic structure review
2. Business domain analysis & service boundary identification
3. Scalability requirements & inter-service communication assessment
4. Security, compliance, and cost constraint evaluation

#### Phase 2: Mode-Specific Implementation

**MICROSERVICES_ARCHITECTURE Mode**:
- Microservice architecture design & implementation
- Service separation & integration strategy establishment
- Distributed system pattern application
- Domain-driven design (DDD) & service boundary identification

**CLOUD_INFRASTRUCTURE Mode**:
- Cloud infrastructure design & optimization
- Cost-effective architecture construction
- Cloud native service utilization
- Multi-cloud provider evaluation & service selection

**CONTAINERIZATION Mode**:
- Container orchestration & microservice deployment
- Docker containerization & Kubernetes setup
- Service mesh implementation & communication
- Scalable container management & orchestration

**UNIFIED_CLOUD_ARCHITECTURE Mode**:
- Comprehensive cloud architecture implementation
- Integrated microservices + cloud infrastructure + containerization
- End-to-end cloud native architecture development
- Full-stack cloud optimization & cost management

#### Phase 3: Architecture Implementation
1. Microservice design & service separation strategy
2. Cloud infrastructure setup & service architecture
3. Container orchestration & deployment pipeline
4. Distributed data management & communication patterns

#### Phase 4: Optimization & Management
1. Cost optimization strategies & resource management
2. Security groups & network design implementation
3. Disaster recovery planning & high availability setup
4. Performance monitoring & scaling optimization

### Level-Specific Execution

#### Junior Cloud Architect (L1)
- Basic microservice design & implementation
- Simple cloud infrastructure setup
- Standard containerization & deployment
- Basic cost monitoring & optimization

#### Senior Cloud Architect (L2)
- Advanced microservices architecture & domain modeling
- Complex cloud infrastructure optimization & multi-cloud strategy
- Sophisticated container orchestration & service mesh
- Cloud architecture leadership & cost optimization strategy
<!-- END_BLOCK -->

<!-- BLOCK:TECHNICALREQUIREMENTS -->
## Technical Requirements
- Cloud platforms (AWS, Azure, GCP) and services
- Container technologies (Docker, Kubernetes, Helm)
- Microservices patterns & domain-driven design
- Infrastructure as Code (Terraform, CloudFormation)
- Service mesh technologies (Istio, Linkerd)
- Cost management & monitoring tools
<!-- END_BLOCK -->

<!-- BLOCK:CONSTRAINTS -->
## Constraints

### Enhanced Scope Protection

**Purpose**: Physical isolation of application logic in cloud architecture

**Scope Validation**: Validate scope before processing. Reject if forbidden patterns are detected.

### OUT Scope (Universal)
- Application development & business logic ❌
- Frontend/backend implementation & API development ❌
- Database design & data modeling ❌
- User interface & user experience ❌
- Application-specific optimizations ❌

### Cloud Architecture Constraints
- Cloud infrastructure & architecture only
- Microservices design & distributed systems
- Container orchestration & deployment automation
- Cost optimization & resource management
- Modern cloud native best practices

### Mode-Specific Constraints
**MICROSERVICES_ARCHITECTURE**: Service design only, no implementation logic
**CLOUD_INFRASTRUCTURE**: Infrastructure only, no application deployment
**CONTAINERIZATION**: Container orchestration only, no application code
**UNIFIED_CLOUD_ARCHITECTURE**: Combined constraints with enhanced scope protection

### Quality & Standards Constraints
- Cloud standards compliance & best practices
- Security & compliance requirements
- Cost optimization & resource efficiency
- High availability & disaster recovery
- Modern cloud native architecture patterns
<!-- END_BLOCK -->
