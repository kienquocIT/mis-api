from apps.sales.opportunity.models import Opportunity
from apps.shared import BastionFieldAbstractListFilter


class OpportunityListFilters(BastionFieldAbstractListFilter):
    class Meta:
        model = Opportunity
        fields = {
            'employee_inherit': ['exact'],
            'quotation': ['exact', 'isnull'],
            'sale_order': ['exact', 'isnull'],
            'is_close_lost': ['exact'],
            'is_deal_close': ['exact'],
            'id': ['in'],
        }
