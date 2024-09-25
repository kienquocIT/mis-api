from drf_yasg.utils import swagger_auto_schema

from apps.sales.production.models import ProductionReport
from apps.sales.production.serializers.production_report import ProductionReportListSerializer, \
    ProductionReportCreateSerializer, ProductionReportDetailSerializer, ProductionReportUpdateSerializer, \
    ProductionReportGRSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ProductionReportList(BaseListMixin, BaseCreateMixin):
    queryset = ProductionReport.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'production_order_id': ['exact'],
        'product_id': ['exact'],
        'employee_inherit_id': ['exact'],
    }
    serializer_list = ProductionReportListSerializer
    serializer_create = ProductionReportCreateSerializer
    serializer_detail = ProductionReportListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Report List",
        operation_description="Get Production Report List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionreport', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Production Report",
        operation_description="Create New Production Report",
        request_body=ProductionReportCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionreport', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductionReportDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = ProductionReport.objects
    serializer_detail = ProductionReportDetailSerializer
    serializer_update = ProductionReportUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Report Detail",
        operation_description="Get Production Report Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionreport', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Production Report",
        operation_description="Update Production Report By ID",
        request_body=ProductionReportUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionreport', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class ProductionReportDDList(BaseListMixin, BaseCreateMixin):
    queryset = ProductionReport.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'production_order_id': ['exact'],
        'product_id': ['exact'],
        'employee_inherit_id': ['exact'],
    }
    serializer_list = ProductionReportDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Report DD List",
        operation_description="Get Production Report DD List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionreport', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductionReportGRList(BaseListMixin, BaseCreateMixin):
    queryset = ProductionReport.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'production_order_id': ['exact'],
        'work_order_id': ['exact'],
        'product_id': ['exact'],
        'employee_inherit_id': ['exact'],
        'id': ['exact', 'in'],
    }
    serializer_list = ProductionReportGRSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Report GR List",
        operation_description="Get Production Report GR List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
