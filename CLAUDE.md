# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
- **Project Name**: MIS ERP System with Bflow Workflow Engine
- **Description**: Enterprise Resource Planning system with multi-tenant architecture, advanced workflow management (Bflow), and comprehensive business modules
- **Environment**: Django REST Framework API
- **Current Sprint**: Sprint 1 - Project Foundation (as of 2025-07-25)
- **Future Vision**: AI-First Transformation planned (see `/docs/bflow/ai-transformation/`)
- **Documentation**: Comprehensive docs available in `/docs/bflow/`

## Directory Structure
- **`/apps`**: All Django applications
  - **`/core`**: Authentication, company management, HR, workflows, attachments, notifications
  - **`/sales`**: CRM, sales processes, invoicing, contracts
  - **`/eoffice`**: Office management, leave requests, business trips
  - **`/kms`**: Knowledge management system
  - **`/hrm`**: Human resources management
  - **`/masterdata`**: Master data management
  - **`/accounting`**: Accounting and financial operations
  - **`/shared`**: Common utilities, extensions, permissions, translations
- **`/builder`**: Docker configurations
- **`/docs`**: Project documentation
- **`/media`**: Uploaded files (not in git)
- **`/static`**: Static assets

## Tech Stack
### Backend
- **Framework**: Django 4.2.8 + Django REST Framework 3.14.0
- **Database**: MySQL 8.0
- **Cache**: Redis
- **Queue**: Celery + RabbitMQ
- **Authentication**: JWT (djangorestframework-simplejwt)

### Infrastructure
- **Container**: Docker + Docker Compose
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Monitoring**: OpenTelemetry with Jaeger tracing

## Development Commands

### Server Management
- Start development server: `python manage.py runserver 8000`
- Create Django superuser: `python manage.py createsuperuser`

### Database Operations
- Run migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- Database shell: `python manage.py dbshell`

### Celery (Background Tasks)
- Start Celery worker: `celery -A misapi worker --loglevel=INFO`
- For Windows: `celery -A misapi worker --loglevel=INFO --pool=solo`
- Stop Celery: Use Ctrl+C (tasks don't auto-reload on code changes)

### Docker Setup
- Development environment: `docker-compose up --build` (run from `builder/dev/`)
- Services included: MySQL (port 3307), RabbitMQ (port 15673)
- Start existing containers: `docker start db` and `docker start queue`

### Code Quality
- Run pylint: `pylint` (using pylint-django plugin as configured in req.txt)
- Run Black formatter: `black .`
- Run Flake8 linter: `flake8`
- Run Bandit security scanner: `bandit -r apps/`

### Testing
- Run Django tests: `python manage.py test --keepdb`
- Run with coverage: `coverage run --source='.' manage.py test && coverage report`

## Coding Standards & Conventions

### Python Standards
- **C-1**: Use type hints for all functions
- **C-2**: Follow existing naming conventions (snake_case for functions/variables, PascalCase for classes)
- **C-3**: Prefer functions over classes when simple
- **C-4**: Use environment variables for configuration
- **C-5**: No hardcoded secrets or credentials

### Django Patterns
- **D-1**: All apps must be placed in the `apps/` folder
- **D-2**: Shared functionality goes in `apps/shared/` and must be imported via `__init__`
- **D-3**: Use UUID4 for all model primary keys
- **D-4**: Implement proper tenant isolation for multi-tenancy
- **D-5**: All new features should include workflow support where appropriate

### API Design
- **API-1**: Follow REST conventions (GET/POST `/api/resource`, GET/PUT/DELETE `/api/resource/{id}`)
- **API-2**: Use separate serializers for list, detail, create, and update operations
- **API-3**: Use `@mask_view` decorator for login/permission checks
- **API-4**: Use `@swagger_auto_schema` for API documentation
- **API-5**: Return consistent response format with success/error structure

### Model Architecture
All models inherit from abstract base classes in `apps.shared.models`:
- `DataAbstractModel`: Main models with tenant, company, workflow fields
- `MasterDataAbstractModel`: Master data models with tenant, company fields  
- `BastionFieldAbstractModel`: Models with opportunity/project permissions
- `SimpleAbstractModel`: Basic models for many-to-many relationships
- `M2MFilesAbstractModel`: File attachment relationships

### Testing Standards
- **T-1**: Write tests before implementation (TDD approach)
- **T-2**: Separate unit tests from integration tests
- **T-3**: Use pytest fixtures for test data
- **T-4**: Include security test cases
- **T-5**: Maintain test coverage ≥ 70%

### Security Requirements
- **S-1**: Run Bandit scanner: `bandit -r apps/`
- **S-2**: Validate all user inputs
- **S-3**: Use encryption service for sensitive data
- **S-4**: Implement proper authentication and authorization
- **S-5**: Never commit .env files or credentials

### Git Workflow
- **Branching Strategy**: GitFlow
- **Commit Messages**: Use Conventional Commits format
  - Types: feat, fix, docs, style, refactor, test, chore
  - Example: `feat(auth): add OAuth2 support`
- **Pull Requests**: Must pass all tests and security scans

## Core System Features

### Workflow System
The project includes a comprehensive workflow engine:
- Workflow configuration in `apps/core/workflow/`
- Runtime execution and stage management
- Email notifications and approvals
- Document state management
- Zone-based permissions

### Permission System
Multi-level permission system:
- Tenant-level admin permissions
- Company-level admin permissions  
- Role-based permissions with conditions
- Employee-level data isolation

### File Management
Integrated file/attachment system:
- Media Cloud API integration for file storage
- Many-to-many relationships between documents and files
- File approval workflows
- Folder-based organization with permissions

## Quality Gates
Before committing code, ensure:
- [ ] All tests pass: `python manage.py test --keepdb`
- [ ] Code is formatted: `black .`
- [ ] Linting passes: `flake8` and `pylint`
- [ ] Security scan passes: `bandit -r apps/`
- [ ] API documentation is updated
- [ ] No hardcoded secrets or credentials

## Key Configuration Files
- `misapi/settings.py`: Main Django settings
- `misapi/local_settings.py`: Local development overrides
- Environment variables for production database, queue, and cache settings
- Docker configuration in `builder/` directory

## Development Workflow Shortcuts

### QNEW
Follow all best practices including security guidelines when creating new features.

### QPLAN
Analyze codebase for consistency before implementing changes.

### QCODE
Implement with tests, run black, flake8, and bandit before finalizing.

### QCHECK
Review as skeptical senior developer:
1. Check best practices compliance
2. Verify Python idioms usage
3. Run all linting tools
4. Ensure security standards

### QSEC
Security review checklist:
1. Check OWASP Top 10 vulnerabilities
2. Run Bandit scanner
3. Review authentication logic
4. Verify input validation

### QGIT
Prepare and commit workflow:
1. Clean temporary artifacts
2. Format code with Black
3. Run all quality checks
4. Commit with conventional format

## Recent Updates (2025-07-25)

### Infrastructure & Environment Setup
- **Kubernetes Configurations**: Created complete K8s manifests for development environment
  - MySQL, Redis, RabbitMQ deployments: `/builder/k8s/development/`
  - Django application deployment with auto-scaling
  - Celery worker and beat deployments
  - Health check endpoint implementation: `/apps/core/health/`
- **Docker Optimization**: Updated Dockerfile with multi-stage build
- **Setup Scripts**: Created automated setup scripts (`setup-dev.sh`, `setup-dev.bat`)
- **Documentation**: Added comprehensive K8s deployment guide: `/builder/k8s/README.md`

### Sprint Progress
- **Sprint 1 Status**: 80% complete (34/42 story points)
  - Infrastructure issues resolved ✅
  - Development environment ready ✅
  - CI/CD pipeline 60% complete
- **Sprint 2 Planning**: Created detailed planning document: `/docs/bflow/01-planning-analysis/sprint-planning/Sprint-2-Planning.md`
- **Assessment Report Updated**: Sprint 1 near completion with improved metrics

### Documentation Created
- **Business Requirements Document (BRD)**: `/docs/bflow/01-planning-analysis/brd/BRD-Bflow-v1.0.md`
- **Product Roadmap**: `/docs/bflow/01-planning-analysis/product-roadmap/Product-Roadmap-Bflow-v1.0.md`
- **Feature List**: `/docs/bflow/01-planning-analysis/product-roadmap/Feature-List-Bflow-v1.0.md`
- **Technical Architecture**: `/docs/bflow/02-design/technical-architecture/TechArch-Bflow-v1.0.md`
- **System Design**: `/docs/bflow/02-design/system-design/SystemDesign-Bflow-v1.0.md`
- **API Documentation**: `/docs/bflow/03-development/api-docs/API-Documentation-Bflow-v1.0.md`
- **User Stories**: `/docs/bflow/01-planning-analysis/user-stories/UserStories-Bflow-v1.0.md`
- **Test Plan**: `/docs/bflow/04-testing/test-plan/TestPlan-Bflow-v1.0.md`
- **Deployment Guide**: `/docs/bflow/05-deployment/deployment-guide/DeploymentGuide-Bflow-v1.0.md`
- **Sprint Planning**: `/docs/bflow/01-planning-analysis/sprint-planning/Sprint-Plan-Bflow-v1.0.md`
- **Sprint Assessment**: `/docs/bflow/01-planning-analysis/sprint-planning/Sprint-Assessment-Report-v1.0.md`

### Module Documentation
- **Quotation Module README**: `/apps/sales/quotation/README.md` - Comprehensive guide for sales quotation management