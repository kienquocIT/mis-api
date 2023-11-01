from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.report.models import ReportRevenue
from apps.sales.report.serializers.report_sales import ReportRevenueListSerializer
from apps.sales.saleorder.models import SaleOrderIndicator
from apps.shared import mask_view, BaseListMixin


# Create your views here.
# REPORT
class ReportRevenueList(BaseListMixin):
    queryset = ReportRevenue.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'group_inherit': ['exact'],
    }
    serializer_list = ReportRevenueListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sale_order",
            "sale_order__customer",
            "sale_order__employee_inherit",
        ).prefetch_related(
            Prefetch(
                'sale_order__sale_order_indicator_sale_order',
                queryset=SaleOrderIndicator.objects.filter(
                    code__in=['IN0001', 'IN0003', 'IN0005']
                )
            )
        )

    @swagger_auto_schema(
        operation_summary="Report revenue List",
        operation_description="Get report revenue List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='report', model_code='reportrevenue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
