# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### Testing
- Run Django tests: `python manage.py test --keepdb`

## Architecture Overview

### Project Structure
This is a Django REST Framework (DRF) project with a modular app-based architecture:

- **Core Apps** (`apps/core/`): Authentication, company management, HR, workflows, attachments, notifications
- **Business Apps**: 
  - `apps/sales/`: CRM, sales processes, invoicing, contracts
  - `apps/eoffice/`: Office management, leave requests, business trips
  - `apps/kms/`: Knowledge management system
  - `apps/hrm/`: Human resources management
  - `apps/masterdata/`: Master data management
  - `apps/accounting/`: Accounting and financial operations
- **Shared Libraries** (`apps/shared/`): Common utilities, extensions, permissions, translations

### Key Technologies
- **Backend**: Django 4.2.8, Django REST Framework 3.14.0
- **Database**: MySQL 8.0 with Django ORM
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Queue System**: Celery with RabbitMQ
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Monitoring**: OpenTelemetry with Jaeger tracing

### Model Architecture
All models inherit from abstract base classes in `apps.shared.models`:
- `DataAbstractModel`: Main models with tenant, company, workflow fields
- `MasterDataAbstractModel`: Master data models with tenant, company fields  
- `BastionFieldAbstractModel`: Models with opportunity/project permissions
- `SimpleAbstractModel`: Basic models for many-to-many relationships
- `M2MFilesAbstractModel`: File attachment relationships

All models use UUID4 primary keys and include tenant isolation.

### API Patterns
- **RESTful URLs**: Follow REST conventions (GET/POST `/api/resource`, GET/PUT/DELETE `/api/resource/{id}`)
- **View Classes**: Inherit from shared mixins (`BaseListMixin`, `BaseCreateMixin`, etc.)
- **Serializers**: Separate serializers for list, detail, create, and update operations
- **Authentication**: Use `@mask_view` decorator for login/permission checks
- **Documentation**: Use `@swagger_auto_schema` for API documentation

### Workflow System
The project includes a comprehensive workflow engine:
- Workflow configuration in `apps/core/workflow/`
- Runtime execution and stage management
- Email notifications and approvals
- Document state management

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

### Key Configuration Files
- `misapi/settings.py`: Main Django settings
- `misapi/local_settings.py`: Local development overrides
- Environment variables for production database, queue, and cache settings
- Docker configuration in `builder/` directory

### Important Development Notes
- All apps must be placed in the `apps/` folder
- Shared functionality goes in `apps/shared/` and must be imported via `__init__`
- Follow PEP8 coding standards with pylint checking
- Use UUID4 for all model primary keys
- Implement proper tenant isolation for multi-tenancy
- All new features should include workflow support where appropriate