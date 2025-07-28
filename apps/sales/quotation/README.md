# Quotation Management Module

## Overview

The Quotation module (`apps.sales.quotation`) is a comprehensive sales quotation management system within the MIS ERP platform. It provides full lifecycle management of sales quotations with configurable business rules, multi-currency support, and deep integration with other ERP modules.

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Models](#models)
- [API Reference](#api-reference)
- [Business Logic](#business-logic)
- [Configuration](#configuration)
- [Integration Points](#integration-points)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Performance Considerations](#performance-considerations)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Architecture

### Directory Structure

```
apps/sales/quotation/
├── migrations/              # Database migrations (25 files)
├── models/
│   ├── __init__.py         # Model exports
│   ├── quotation.py        # Core quotation models
│   └── indicator.py        # Business indicator models
├── serializers/
│   ├── __init__.py         # Serializer exports
│   ├── quotation_config.py # Configuration serializers
│   ├── quotation_indicator.py # Indicator serializers
│   ├── quotation_serializers.py # Main quotation serializers
│   └── quotation_sub.py    # Sub-model serializers
├── utils/
│   ├── logical.py          # Business logic utilities
│   └── logical_finish.py   # Quotation completion logic
├── views.py                # API views
├── urls.py                 # URL routing
├── tests.py                # Test cases
├── apps.py                 # Django app configuration
└── admin.py                # Django admin (empty)
```

### Design Patterns

- **Model-View-Serializer (MVS)**: Standard Django REST Framework pattern
- **Abstract Base Classes**: Inherits from shared abstract models for consistency
- **Service Layer**: Business logic encapsulated in utils modules
- **Repository Pattern**: Data access through Django ORM
- **Factory Pattern**: Automatic code generation for quotations

## Features

### Core Features

1. **Two Sales Modes**
   - **Short Sale**: Direct quotation creation without opportunities
   - **Long Sale**: Quotations linked to sales opportunities

2. **Multi-Currency Support**
   - Exchange rate management
   - Currency conversion for reporting

3. **Flexible Pricing**
   - Product-level pricing with discounts
   - Total-level discounts
   - Tax calculations (VAT, WHT)
   - Multiple price list support

4. **Business Indicators (KPIs)**
   - Pre-configured indicators (Revenue, Cost, Gross Profit, etc.)
   - Formula-based calculations
   - Customizable per company

5. **Workflow Integration**
   - Approval workflows
   - Status management
   - Process tracking

6. **Document Management**
   - File attachments
   - Version control
   - Change order tracking

### Configuration Options

- Company-level settings for sales modes
- Role-based feature access
- Customizable business indicators
- Approval workflow configuration

## Models

### QuotationAppConfig

Company-specific configuration for the quotation module.

```python
class QuotationAppConfig(MasterDataAbstractModel):
    company = models.OneToOneField('base.Company')
    is_short_sale = models.BooleanField(default=True)
    is_long_sale = models.BooleanField(default=True)
    # Configuration for various features...
```

### Quotation

Main quotation model with comprehensive business data.

```python
class Quotation(DataAbstractModel, BastionFieldAbstractModel, CurrencyAbstractModel):
    # Key fields
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICES)
    
    # Relationships
    opportunity = models.ForeignKey('opportunity.Opportunity', null=True)
    customer = models.ForeignKey('account.Account')
    contact = models.ForeignKey('contact.Contact', null=True)
    sale_person = models.ForeignKey('hr.Employee')
    
    # Financial data
    quotation_products = models.JSONField(default=list)
    quotation_logistics = models.JSONField(default=list)
    quotation_costs = models.JSONField(default=list)
    quotation_expenses = models.JSONField(default=list)
    
    # Calculated totals
    total_product_amount = models.DecimalField(max_digits=20, decimal_places=2)
    total_discount = models.DecimalField(max_digits=20, decimal_places=2)
    grand_total = models.DecimalField(max_digits=20, decimal_places=2)
```

### QuotationIndicator

Business indicators for performance tracking.

```python
class QuotationIndicator(SimpleAbstractModel):
    quotation = models.ForeignKey(Quotation)
    config = models.ForeignKey(QuotationIndicatorConfig)
    value = models.DecimalField(max_digits=20, decimal_places=2)
```

### QuotationIndicatorConfig

Configuration for business indicators with formula support.

```python
class QuotationIndicatorConfig(MasterDataAbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    formula = models.TextField()  # Calculation formula
    is_active = models.BooleanField(default=True)
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quotation/list` | List quotations with pagination |
| POST | `/api/quotation/list` | Create new quotation |
| GET | `/api/quotation/{id}` | Get quotation details |
| PUT | `/api/quotation/{id}` | Update quotation |
| DELETE | `/api/quotation/{id}` | Delete quotation |
| GET | `/api/quotation/config` | Get company configuration |
| PUT | `/api/quotation/config` | Update configuration |
| GET | `/api/quotation/indicators` | List indicator configs |
| POST | `/api/quotation/indicators` | Create indicator config |
| PUT | `/api/quotation/indicator/{id}` | Update indicator config |
| PUT | `/api/quotation/indicator-restore/{id}` | Restore default indicators |

### Request/Response Examples

#### Create Quotation

```http
POST /api/quotation/list
Content-Type: application/json
Authorization: Bearer {token}

{
    "name": "Q-2024-001 - ABC Company",
    "customer": "550e8400-e29b-41d4-a716-446655440000",
    "sale_person": "660e8400-e29b-41d4-a716-446655440000",
    "quotation_products": [
        {
            "product": "770e8400-e29b-41d4-a716-446655440000",
            "quantity": 10,
            "unit_price": 1000,
            "discount_percent": 10
        }
    ],
    "payment_term": "net30",
    "valid_until": "2024-12-31"
}
```

#### Response

```json
{
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "code": "QT-2024-00001",
    "name": "Q-2024-001 - ABC Company",
    "status": 1,
    "grand_total": "9000.00",
    "created_at": "2024-01-15T10:00:00Z"
}
```

### Serializers

- `QuotationListSerializer`: List view with summary data
- `QuotationDetailSerializer`: Full quotation details
- `QuotationCreateSerializer`: Creation with validation
- `QuotationUpdateSerializer`: Update operations
- `QuotationProductSerializer`: Product line items
- `QuotationIndicatorSerializer`: Business indicators

## Business Logic

### Quotation Creation Rules

1. **Opportunity Validation**
   - Only one active quotation per opportunity
   - Cannot create quotations for closed opportunities
   - Opportunities with sales orders are restricted

2. **Auto-Code Generation**
   - Format: `QT-YYYY-NNNNN`
   - Sequential numbering per company
   - Configurable prefix

3. **Status Workflow**
   ```
   Draft (0) → Created (1) → Finished (2)
                    ↓
                Canceled (3)
   ```

4. **Financial Calculations**
   - Product Total = Σ(Quantity × Unit Price × (1 - Discount%))
   - Grand Total = Product Total - Total Discount + VAT - WHT

### Indicator Calculations

Default indicators with formulas:

1. **Revenue (DT)**: `product_amount + total_expense`
2. **Cost (CP)**: `total_cost + total_expense_is_labor`
3. **Gross Profit (LNG)**: `revenue - cost`
4. **Gross Profit Margin (BLNG)**: `(gross_profit / revenue) × 100`
5. **Net Profit (LNR)**: `gross_profit - other_expenses`
6. **Net Profit Margin (BLNR)**: `(net_profit / revenue) × 100`

### Workflow Integration

```python
# Quotation approval workflow
if quotation.status == STATUS_CREATED:
    # Trigger workflow
    process_definition = quotation.get_process_definition()
    if process_definition:
        runtime = create_runtime(quotation, process_definition)
        quotation.runtime = runtime
        quotation.save()
```

## Configuration

### Company Configuration

```python
# Enable/disable features
config = QuotationAppConfig.objects.get(company=company)
config.is_short_sale = True  # Enable direct quotations
config.is_long_sale = True   # Enable opportunity-linked quotations
config.save()
```

### Role-Based Access

```python
# Configure role permissions
config.role_config_sps = role_sales_person
config.role_receive_lead = role_sales_manager
config.save()
```

### Indicator Configuration

```python
# Create custom indicator
indicator_config = QuotationIndicatorConfig.objects.create(
    company=company,
    name="Custom Margin",
    code="CUSTOM_MARGIN",
    formula="(grand_total - total_cost) / grand_total * 100",
    is_active=True
)
```

## Integration Points

### 1. Opportunity Management
- Links quotations to sales opportunities
- Updates opportunity status and logs
- Validates opportunity lifecycle rules

### 2. Customer (Account) Management
- References customer master data
- Updates customer activity logs
- Manages customer contacts

### 3. Product Management
- Uses product master data
- Applies price lists
- Manages inventory reservations

### 4. Financial Integration
- Posts to revenue reports
- Integrates with payment terms
- Supports multi-currency transactions

### 5. Workflow Engine
- Approval process integration
- Status transition management
- Notification system

### 6. Document Management
- File attachment support
- Version control
- Change tracking

## Usage Examples

### Creating a Simple Quotation

```python
from apps.sales.quotation.models import Quotation
from apps.sales.quotation.utils.logical import create_quotation

# Create quotation data
quotation_data = {
    'name': 'Quotation for ABC Corp',
    'customer': customer_instance,
    'sale_person': employee_instance,
    'quotation_products': [
        {
            'product': product_instance,
            'quantity': 10,
            'unit_price': 1000,
            'discount_percent': 10,
            'tax': tax_instance
        }
    ],
    'payment_term': payment_term_instance,
    'valid_until': '2024-12-31'
}

# Create quotation
quotation = create_quotation(quotation_data, user=request.user)
```

### Calculating Indicators

```python
from apps.sales.quotation.utils.logical import calculate_indicators

# Calculate all active indicators for a quotation
indicators = calculate_indicators(quotation)

# Access specific indicator
revenue_indicator = indicators.filter(config__code='DT').first()
print(f"Revenue: {revenue_indicator.value}")
```

### Workflow Processing

```python
from apps.sales.quotation.utils.logical_finish import process_quotation_approval

# Submit quotation for approval
if quotation.status == Quotation.STATUS_CREATED:
    runtime = process_quotation_approval(quotation, user=request.user)
    print(f"Workflow started: {runtime.id}")
```

## Testing

### Running Tests

```bash
# Run quotation app tests
python manage.py test apps.sales.quotation

# Run with coverage
coverage run --source='apps.sales.quotation' manage.py test apps.sales.quotation
coverage report
```

### Test Categories

1. **Unit Tests**
   - Model validation
   - Calculation accuracy
   - Business rule enforcement

2. **Integration Tests**
   - API endpoint testing
   - Cross-module integration
   - Workflow integration

3. **Performance Tests**
   - Large dataset handling
   - Calculation performance
   - Query optimization

### Example Test Case

```python
class QuotationTestCase(TestCase):
    def test_create_quotation_with_opportunity(self):
        # Setup test data
        opportunity = create_test_opportunity()
        customer = create_test_customer()
        
        # Create quotation
        quotation_data = {
            'opportunity': opportunity,
            'customer': customer,
            'name': 'Test Quotation'
        }
        
        response = self.client.post('/api/quotation/list', quotation_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quotation.objects.count(), 1)
```

## Performance Considerations

### Query Optimization

1. **Use select_related() for foreign keys**
   ```python
   quotations = Quotation.objects.select_related(
       'customer', 'sale_person', 'opportunity'
   ).filter(company=company)
   ```

2. **Prefetch related data**
   ```python
   quotations = Quotation.objects.prefetch_related(
       'quotationindicator_set__config'
   ).filter(status=Quotation.STATUS_CREATED)
   ```

3. **Index key fields**
   - `code` (unique index)
   - `status`, `company` (composite index)
   - `opportunity` (foreign key index)

### Caching Strategy

```python
from django.core.cache import cache

# Cache quotation calculations
cache_key = f'quotation_total_{quotation.id}'
total = cache.get(cache_key)
if not total:
    total = calculate_quotation_total(quotation)
    cache.set(cache_key, total, timeout=3600)
```

### Bulk Operations

```python
# Bulk create quotation products
QuotationProduct.objects.bulk_create([
    QuotationProduct(quotation=quotation, **product_data)
    for product_data in products_data
])
```

## Security

### Permission Requirements

1. **View Quotations**
   - Permission: `quotation.view_quotation`
   - Check: Company and data access

2. **Create/Edit Quotations**
   - Permission: `quotation.change_quotation`
   - Additional: Role-based configuration

3. **Delete Quotations**
   - Permission: `quotation.delete_quotation`
   - Restriction: Only draft status

### Data Access Control

```python
# Tenant isolation
quotations = Quotation.objects.filter(
    company=request.user.employee.company,
    tenant=request.user.tenant
)

# Department/team access
if not request.user.is_company_admin:
    quotations = quotations.filter(
        sale_person__department=request.user.employee.department
    )
```

### Sensitive Data Protection

- Customer information encryption
- Price data access control
- Audit logging for all changes

## Troubleshooting

### Common Issues

1. **"Cannot create quotation for opportunity"**
   - Check opportunity status (must be open)
   - Verify no existing active quotation
   - Ensure no linked sales orders

2. **"Invalid product configuration"**
   - Verify product is active
   - Check price list assignment
   - Validate tax configuration

3. **"Workflow not starting"**
   - Check process definition exists
   - Verify user permissions
   - Review workflow configuration

### Debugging Tips

```python
# Enable SQL logging
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        }
    }
}

# Check quotation calculation details
from apps.sales.quotation.utils.logical import debug_calculation
debug_info = debug_calculation(quotation)
print(debug_info)
```

### Health Checks

```python
# Verify configuration
from django.core.management import call_command
call_command('check_quotation_config')

# Validate indicators
from apps.sales.quotation.utils.logical import validate_indicators
issues = validate_indicators(company)
```

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters
- Document complex business logic
- Write comprehensive tests

### Submitting Changes

1. Create feature branch: `feature/quotation-enhancement`
2. Write tests for new functionality
3. Update documentation
4. Submit pull request with clear description

### Review Checklist

- [ ] Tests pass and coverage maintained
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Backward compatibility maintained

---

**Last Updated**: 2025-07-25  
**Maintained By**: Sales Team  
**Version**: 1.0.0