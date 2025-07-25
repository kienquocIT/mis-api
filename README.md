# MIS ERP System with Bflow Workflow Engine

## Overview

MIS (Management Information System) là một hệ thống ERP toàn diện với kiến trúc multi-tenant, tích hợp Bflow - một workflow engine mạnh mẽ cho phép tự động hóa quy trình kinh doanh phức tạp.

### Key Features
- 🏢 **Multi-tenant Architecture**: Hỗ trợ nhiều công ty độc lập
- 🔄 **Bflow Workflow Engine**: Quản lý quy trình linh hoạt với visual designer
- 📊 **Comprehensive Modules**: Sales, E-Office, KMS, HRM, Accounting, Inventory
- 🔐 **Advanced Security**: JWT authentication, role-based permissions
- 📱 **RESTful API**: Fully documented với Swagger/OpenAPI
- 🚀 **High Performance**: Celery + RabbitMQ cho async processing

## Technology Stack

### Backend
- **Framework**: Python 3.11 + Django 4.2.8 + Django REST Framework 3.14.0
- **Database**: MySQL 8.0
- **Cache**: Redis
- **Queue**: Celery + RabbitMQ
- **Authentication**: JWT (djangorestframework-simplejwt)

### Infrastructure
- **Container**: Docker + Docker Compose
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Monitoring**: OpenTelemetry with Jaeger tracing

## Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git

### Development Setup

1. **Clone repository**
```bash
git clone <repository-url>
cd mis_site/API/sit
```

2. **Setup Docker services**
```bash
cd builder/dev/
docker-compose up --build
```

Services will be available at:
- MySQL: `localhost:3307`
- RabbitMQ: `localhost:15673`

3. **Setup Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Configure local settings**
Create `misapi/local_settings.py`:
```python
DEBUG = True
SHOW_API_DOCS = True
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start development server**
```bash
python manage.py runserver 8000
```

8. **Start Celery worker** (in another terminal)
```bash
# Linux/Mac
celery -A misapi worker --loglevel=INFO

# Windows
celery -A misapi worker --loglevel=INFO --pool=solo
```

## Project Structure

```
mis_site/API/sit/
├── apps/                    # All Django applications
│   ├── core/               # Core modules (auth, company, HR, workflows)
│   │   └── workflow/       # Bflow workflow engine
│   ├── sales/              # Sales modules (CRM, quotation, orders)
│   ├── eoffice/            # E-Office modules
│   ├── kms/                # Knowledge Management System
│   ├── hrm/                # Human Resource Management
│   ├── accounting/         # Accounting modules
│   └── shared/             # Shared utilities and base classes
├── builder/                # Docker configurations
├── docs/                   # Project documentation
│   └── bflow/             # Bflow documentation
├── misapi/                # Django project settings
├── media/                 # Uploaded files
├── static/                # Static assets
└── CLAUDE.md              # AI assistant guidance
```

## Documentation

### Bflow Documentation
Comprehensive documentation for Bflow workflow engine:
- 📋 [Business Requirements](docs/bflow/01-planning-analysis/brd/BRD-Bflow-v1.0.md)
- 🗺️ [Product Roadmap](docs/bflow/01-planning-analysis/product-roadmap/Product-Roadmap-Bflow-v1.0.md)
- 🏗️ [Technical Architecture](docs/bflow/02-design/technical-architecture/TechArch-Bflow-v1.0.md)
- 🔧 [System Design](docs/bflow/02-design/system-design/SystemDesign-Bflow-v1.0.md)
- 📡 [API Documentation](docs/bflow/03-development/api-docs/API-Documentation-Bflow-v1.0.md)
- 🧪 [Test Plan](docs/bflow/04-testing/test-plan/TestPlan-Bflow-v1.0.md)
- 🚀 [Deployment Guide](docs/bflow/05-deployment/deployment-guide/DeploymentGuide-Bflow-v1.0.md)
- 📅 [Sprint Planning](docs/bflow/01-planning-analysis/sprint-planning/Sprint-Plan-Bflow-v1.0.md)

### Module Documentation
- 💰 [Quotation Module](apps/sales/quotation/README.md) - Sales quotation management

## Development Guidelines

### Coding Standards
- **Python**: Follow PEP8, use type hints
- **Django**: Follow Django best practices
- **API**: RESTful conventions
- **Git**: Conventional commits (feat, fix, docs, etc.)

### Code Quality Tools
```bash
# Format code
black .

# Lint code
flake8
pylint

# Security scan
bandit -r apps/

# Run tests
python manage.py test --keepdb

# Test coverage
coverage run --source='.' manage.py test
coverage report
```

### Model Architecture
All models inherit from abstract base classes:
- `DataAbstractModel`: Main models with workflow support
- `MasterDataAbstractModel`: Master data models
- `BastionFieldAbstractModel`: Models with opportunity/project permissions
- `SimpleAbstractModel`: Many-to-many relationship models
- `M2MFilesAbstractModel`: File attachment relationships

### API Patterns
- Use class-based views with mixins
- Implement `@swagger_auto_schema` for documentation
- Use `@mask_view` decorator for authentication/authorization
- Separate serializers for list, detail, create, update

## API Documentation

Access interactive API documentation at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

### Authentication
All API requests require JWT authentication:
```http
Authorization: Bearer <your-jwt-token>
```

### Example API Usage
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login', json={
    'username': 'your-username',
    'password': 'your-password'
})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
workflows = requests.get('http://localhost:8000/api/workflow/lists', headers=headers)
```

## Testing

### Run all tests
```bash
python manage.py test
```

### Run specific app tests
```bash
python manage.py test apps.sales.quotation
```

### Run with coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Deployment

### Production Environment Variables
```bash
# Database
DB_NAME='production_db'
DB_USER='prod_user'
DB_PASSWORD='secure_password'
DB_HOST='db.example.com'
DB_PORT='3306'

# Cache
CACHE_HOST='redis.example.com'
CACHE_PORT='6379'

# Message Queue
MSG_QUEUE_HOST='rabbitmq.example.com'
MSG_QUEUE_PORT='5672'
MSG_QUEUE_USER='rabbitmq_user'
MSG_QUEUE_PASSWORD='rabbitmq_password'

# Security
SECRET_KEY='your-secret-key'
ALLOWED_HOSTS='api.example.com,*.example.com'
```

See [Deployment Guide](docs/bflow/05-deployment/deployment-guide/DeploymentGuide-Bflow-v1.0.md) for detailed instructions.

## Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes following coding standards
3. Write/update tests
4. Run quality checks
5. Commit with conventional message: `git commit -m "feat: add new feature"`
6. Push and create pull request

### Quality Checklist
- [ ] All tests pass
- [ ] Code formatted with Black
- [ ] No linting errors
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] No hardcoded secrets

## Troubleshooting

### Common Issues

1. **Database connection error**
   - Check Docker containers: `docker ps`
   - Restart database: `docker start db`

2. **Celery not processing tasks**
   - Check RabbitMQ: `docker start queue`
   - Restart Celery worker

3. **Import errors**
   - Ensure virtual environment activated
   - Install requirements: `pip install -r requirements.txt`

### Useful Commands

```bash
# Docker management
docker start db queue  # Start services
docker logs db        # View database logs

# Django management
python manage.py showmigrations  # Check migration status
python manage.py shell           # Django shell
python manage.py dbshell        # Database shell

# Celery monitoring
celery -A misapi status         # Check worker status
celery -A misapi flower         # Start Flower monitoring
```

## Support

### Resources
- 📚 [Django Documentation](https://docs.djangoproject.com/)
- 📖 [DRF Documentation](https://www.django-rest-framework.org/)
- 🔧 [Project Wiki](docs/README.md)

### Contact
- Technical Lead: tech@example.com
- DevOps Team: devops@example.com
- Product Owner: po@example.com

## License

Proprietary - All rights reserved

---

**Last Updated**: 2025-07-25  
**Version**: 1.0.0  
**Status**: In Development (Sprint 1 - 80% Complete)