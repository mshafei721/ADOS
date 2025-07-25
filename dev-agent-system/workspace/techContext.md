# Technical Context - Agent Workspace

## Overview
This file maintains the technical context for agent crews, inherited from main planning and adapted for agent execution.

---

## Current Technical Environment

### Technology Stack
**Source**: Inherited from `config/tech_stack.json`
**Scope**: Agent-specific technical decisions and constraints

#### Backend Technology
- **Language**: Python 3.11+
- **Framework**: FastAPI (primary)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Testing**: pytest framework

#### Frontend Technology
- **Framework**: React 18+ with TypeScript
- **Styling**: TailwindCSS
- **Build Tool**: Vite
- **State Management**: Redux Toolkit

#### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Cloud**: AWS (primary)
- **IaC**: Terraform

#### CI/CD
- **Pipeline**: GitHub Actions
- **Code Quality**: black, ruff, mypy, eslint, prettier
- **Security**: bandit, safety, snyk
- **Deployment**: Blue-Green strategy

### Development Constraints
**Source**: Inherited from crew configurations and system settings

#### Code Quality Standards
- **Coverage**: 80% minimum test coverage
- **Linting**: All code must pass linting rules
- **Style**: Follow project style guides
- **Documentation**: API documentation with OpenAPI/Swagger

#### Security Requirements
- **Authentication**: JWT/OAuth2 standards
- **Guidelines**: OWASP security guidelines
- **Scanning**: Regular security scanning required
- **Architecture**: Zero-trust principles

#### Performance Requirements
- **API Response**: < 200ms average response time
- **Database**: Optimized queries with proper indexing
- **Frontend**: < 3s initial load time
- **Scalability**: Support horizontal scaling

### Tool Configuration
**Source**: Inherited from agent tool assignments

#### Development Tools
- **Code Generation**: Boilerplate generators for FastAPI, React, Docker
- **Search Tools**: Documentation search for Python, React, Docker, K8s
- **Testing Tools**: pytest runner, coverage reporter, security scanner
- **Deployment Tools**: Docker builder, K8s deployer, pipeline runner

### Memory and Communication
**Source**: Inherited from system settings

#### Memory Configuration
- **Vector DB**: ChromaDB for knowledge base
- **Crew Memory**: JSON-based local memory per crew
- **Session Memory**: 1000 entries maximum
- **Persistence**: `./memory/` directory structure

#### Communication Protocol
- **Protocol**: File-based communication
- **Task Queue**: `workspace/todo.md`
- **Progress Tracking**: `workspace/progress.md`
- **Context Sharing**: `workspace/activeContext.md`
- **Update Interval**: 10 seconds

---

## Technical Inheritance
- **Master Plan**: `.devdocs/memory-bank/PLAN.md` (read-only reference)
- **Main Tech Context**: `.devdocs/memory-bank/techContext.md` (inherited)
- **Configuration**: `config/` directory (authoritative)
- **Crew Specifications**: `config/crews.yaml` and `config/agents.yaml`

## Agent-Specific Technical Notes
- Each crew operates within defined technical constraints
- Technology choices are consistent across crews
- Tool usage is standardized per agent role
- Integration patterns follow established protocols

### Logging Infrastructure Implementation (Phase 2 - Task 2.4) ✅
**Status**: Complete
**Integration**: Full JSON logging with performance monitoring
**Components**:
- JSON formatters with structured data support
- Central logging service with configuration management
- Log rotation handlers (10MB/5 files) with compression
- Performance monitoring with metrics collection
- Crew-specific logging utilities
- Comprehensive test suite

**Technical Details**:
- All logs formatted in JSON structure per `system_settings.json`
- Log rotation working with 10MB file limit and 5 file retention
- Performance monitoring hooks operational
- Crew-specific logging capabilities enabled
- Zero disruption to existing functionality maintained

### Security Crew Implementation (Phase 3.3) ✅
**Status**: Complete
**Integration**: Full security crew with authentication and vulnerability assessment
**Components**:
- SecurityTools class with JWT/OAuth2 authentication systems
- SecurityCrew class following backend crew patterns
- AuthAgent for authentication system generation
- VulnAgent for vulnerability scanning and threat modeling
- Comprehensive testing suite (30 tests)

**Technical Details**:
- JWT authentication with HS256/RS256 algorithms
- OAuth2 flows (authorization code, PKCE) for multiple providers
- Password hashing with bcrypt/argon2
- Vulnerability scanning (dependencies, code, OWASP Top 10)
- Threat modeling using STRIDE methodology
- Security configuration management with environment variables
- Performance monitoring and health checking
- Workspace integration with runtime context management

## Next Technical Steps
- Initialize crew-specific technical environments
- Establish development tool chains per crew
- Configure communication and memory systems
- Begin technical implementation following constraints