# ListFilterService - Dynamic Report Filtering

## Overview

The `ListFilterService` provides dynamic filtering capabilities for Django-based reports. It allows users to create complex filter conditions stored in the database and apply them to any report view.

## Table of Contents
- [Quick Start](#quick-start)
- [Integration Guide](#integration-guide)
- [Filter Condition Format](#filter-condition-format)
- [Supported Operators](#supported-operators)
- [Custom Filters](#custom-filters)
- [API Usage](#api-usage)
- [Examples](#examples)

## Quick Start

### Basic Usage in a Report View

```python
from apps.sales.partnercenter.models import List
from apps.sales.partnercenter.services import ListFilterService

class YourReportListView(BaseListMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter ID from query parameters
        filter_item_id = self.request.query_params.get('advance_filter_id')
        
        if filter_item_id:
            filter_item_obj = List.objects.filter(id=filter_item_id).first()
            if filter_item_obj:
                # Apply the filter
                queryset = ListFilterService.filter(filter_item_obj, queryset)
        
        return queryset
```

### API Request Example
```bash
GET /api/reports/revenue/?advance_filter_id=123e4567-e89b-12d3-a456-426614174000
```

## Integration Guide

### Step 1: Update Your Report View

Add filter support to your existing report view:

```python
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    serializer_list = ReportRevenueListSerializer
    
    def get_queryset(self):
        # Your existing queryset logic
        query_set = super().get_queryset().select_related(
            "sale_order",
            "lease_order",
            "quotation",
            "opportunity",
            "customer",
            "employee_inherit",
        ).filter(
            group_inherit__is_delete=False, 
            is_initial=False
        ).filter(
            Q(sale_order__system_status=3) | Q(lease_order__system_status=3)
        )
        
        # Add filter support
        filter_item_id = self.request.query_params.get('advance_filter_id')
        filter_item_obj = List.objects.filter(id=filter_item_id).first()
        
        if filter_item_obj:
            filtered_query_set = ListFilterService.filter(filter_item_obj, query_set)
            return filtered_query_set
            
        return query_set
```

### Step 2: Create Filter Configurations

Filter configurations are stored in the `List` model with the following structure:

```python
{
    "filter_condition": [
        [  # Group 1 (AND conditions within group)
            {
                "type": "1",  # Field type
                "left": {"code": "customer__name"},
                "operator": "icontains",
                "right": "Acme Corp"
            },
            {
                "type": "2",
                "left": {"code": "revenue"},
                "operator": "gte",
                "right": 10000
            }
        ],
        [  # Group 2 (OR between groups)
            {
                "type": "1",
                "left": {"code": "status"},
                "operator": "exact",
                "right": "active"
            }
        ]
    ]
}
```

## Filter Condition Format

### Basic Structure

```python
{
    "type": "1",  # Condition type (1-5)
    "left": {
        "code": "field_name"  # Django field lookup
    },
    "operator": "exact",  # Comparison operator
    "right": "value"  # Value to compare
}
```

### Condition Types

- **Type 1-4**: Standard field comparisons
- **Type 5**: Object/Foreign key comparisons (ID-based)

### Object Reference Example (Type 5)

```python
{
    "type": "5",
    "left": {"code": "owner_id"},
    "operator": "exact",
    "right": {
        "id": "123e4567-e89b-12d3-a456-426614174000"
    }
}
```

## Supported Operators

### Standard Operators
- `exact` - Exact match
- `notexact` - Not equal
- `icontains` - Case-insensitive contains
- `noticontains` - Does not contain (case-insensitive)
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `gt` - Greater than
- `lt` - Less than
- `exactnull` - Is NULL
- `notexactnull` - Is not NULL

### Operator Usage Examples

```python
# Text fields
{"operator": "icontains", "right": "search_term"}

# Numeric fields
{"operator": "gte", "right": 1000}

# Date fields
{"operator": "lte", "right": "2024-12-31"}

# Null checks
{"operator": "exactnull"}  # right value is ignored
```

## Custom Filters

The service supports programmatic filters for complex fields that require custom logic:

### Currently Supported Custom Filters

1. **revenue_ytd** - Year-to-date revenue calculation
2. **open_opp_num** - Number of open opportunities
3. **last_contacted_open_opp** - Days since last contact on open opportunities
4. **curr_opp_stage_id** - Current opportunity stage
5. **contact__owner__name** - Contact owner's full name
6. **manager** - Account manager (JSON field)
7. **num_sale_orders** - Number of sales orders
8. **gross_margin** - Gross margin percentage

### Custom Filter Examples

#### Revenue YTD Filter
```python
{
    "type": "1",
    "left": {"code": "revenue_ytd"},
    "operator": "gte",
    "right": 50000
}
```

#### Open Opportunities Count
```python
{
    "type": "1",
    "left": {"code": "open_opp_num"},
    "operator": "gt",
    "right": 5
}
```

#### Last Contact Days
```python
{
    "type": "1",
    "left": {"code": "last_contacted_open_opp"},
    "operator": "lte",
    "right": 30  # Contacted within last 30 days
}
```
## Examples

### Example 1: Filter High-Value Active Accounts

```python
{
    "filter_condition": [
        [
            {
                "type": "1",
                "left": {"code": "revenue_ytd"},
                "operator": "gte",
                "right": 100000
            },
            {
                "type": "1",
                "left": {"code": "account_type"},
                "operator": "exact",
                "right": "customer"
            }
        ]
    ]
}
```
## Adding Custom Filters

To add a new custom filter:

1. **Add the handler to programmatic_handlers** in `ListFilterService.filter()`:

```python
programmatic_handlers = {
    'revenue_ytd': CustomFilter.filter_revenue_ytd,
    'your_custom_field': CustomFilter.filter_your_custom_field,  # Add here
    # ... other handlers
}
```

2. **Implement the filter method** in `CustomFilter` class:

```python
@classmethod
def filter_your_custom_field(cls, obj, operator, right):
    # Your custom logic here
    # Must return a set of IDs
    
    # Example:
    model_class = apps.get_model(
        app_label=obj.data_object.application.app_label,
        model_name=obj.data_object.application.model_code,
    )
    
    # Apply your custom filtering logic
    filtered_objects = model_class.objects.filter(
        # your conditions
    )
    
    # Return set of IDs
    return set(filtered_objects.values_list('id', flat=True))
```