from drf_yasg.utils import swagger_auto_schema

from apps.sales.leaseorder.models import LeaseOrder
from apps.sales.leaseorder.serializers import (
    LeaseOrderListSerializer, LeaseOrderCreateSerializer, LeaseOrderDetailSerializer, LeaseOrderUpdateSerializer,
    LeaseOrderMinimalListSerializer,
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class LeaseOrderList(BaseListMixin, BaseCreateMixin):
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

        main_queryset = super().get_queryset().select_related(
            "customer",
            "opportunity",
            "quotation",
            "employee_inherit",
        )
        return self.get_queryset_custom_direct_page(main_queryset)

    @swagger_auto_schema(
        operation_summary="Lease Order List",
        operation_description="Get Lease Order List",
    )
    @mask_view(
        login_require=True, auth_require=False,
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
        login_require=True, auth_require=False,
        employee_require=True,
        label_code='leaseorder', model_code='leaseorder', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
        login_require=True, auth_require=False,
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
        login_require=True, auth_require=False,
        label_code='leaseorder', model_code='leaseorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
