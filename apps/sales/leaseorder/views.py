from drf_yasg.utils import swagger_auto_schema

from apps.sales.leaseorder.models import LeaseOrder, LeaseOrderAppConfig
from apps.sales.leaseorder.serializers import (
    LeaseOrderListSerializer, LeaseOrderCreateSerializer, LeaseOrderDetailSerializer, LeaseOrderUpdateSerializer,
    LeaseOrderMinimalListSerializer, LORecurrenceListSerializer,
)
from apps.sales.leaseorder.serializers.lease_order_config import LeaseOrderConfigDetailSerializer, \
    LeaseOrderConfigUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class LeaseOrderList(BaseListMixin, BaseCreateMixin):
    queryset = LeaseOrder.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'id': ['exact', 'in'],
        'delivery_call': ['exact'],
        'system_status': ['exact', 'in'],
        'quotation_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
        'opportunity__is_deal_close': ['exact'],
        'customer_id': ['exact', 'in'],
        'indicator_revenue': ['exact', 'gt', 'lt', 'gte', 'lte'],
        'date_approved': ['lte', 'gte'],
        'has_regis': ['exact'],
        'is_recurring': ['exact'],
        'document_root_id': ['exact'],
    }
    serializer_list = LeaseOrderListSerializer
    serializer_list_minimal = LeaseOrderMinimalListSerializer
    serializer_create = LeaseOrderCreateSerializer
    serializer_detail = LeaseOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    # create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        is_minimal = self.get_param(key='is_minimal')
        if is_minimal:
            return super().get_queryset()

        return super().get_queryset().select_related(
            "customer",
            "opportunity",
            "quotation",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Lease Order List",
        operation_description="Get Lease Order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leaseorder', model_code='leaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Lease Order",
        operation_description="Create new Lease Order",
        request_body=LeaseOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='leaseorder', model_code='leaseorder', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class LeaseOrderDDList(BaseListMixin):
    queryset = LeaseOrder.objects
    search_fields = ['title', 'code', 'customer__name']
    filterset_fields = {
        'delivery_call': ['exact'],
        'system_status': ['exact', 'in'],
        'quotation_id': ['exact'],
        'customer_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
        'opportunity__is_deal_close': ['exact'],
        'has_regis': ['exact'],
        'is_recurring': ['exact'],
    }
    serializer_list = LeaseOrderMinimalListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Lease Order DD List",
        operation_description="Get Lease Order DD List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LeaseOrderDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = LeaseOrder.objects
    serializer_detail = LeaseOrderDetailSerializer
    serializer_update = LeaseOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "opportunity",
            "opportunity__customer",
            "employee_inherit",
            "process",
        )

    @swagger_auto_schema(
        operation_summary="Lease Order detail",
        operation_description="Get Lease Order detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leaseorder', model_code='leaseorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Lease Order",
        operation_description="Update Lease Order by ID",
        request_body=LeaseOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leaseorder', model_code='leaseorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


# Config
class LeaseOrderConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = LeaseOrderAppConfig.objects
    serializer_detail = LeaseOrderConfigDetailSerializer
    serializer_update = LeaseOrderConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Lease order Config Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Lease order Config Update",
        request_body=LeaseOrderConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class LORecurrenceList(BaseListMixin, BaseCreateMixin):
    queryset = LeaseOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'is_recurrence_template': ['exact'],
        'employee_inherit_id': ['exact'],
    }
    serializer_list = LORecurrenceListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="LO Recurrence List",
        operation_description="Get LO Recurrence List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
