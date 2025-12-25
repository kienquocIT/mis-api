from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.sales.servicequotation.models import (
    ServiceQuotation, ServiceQuotationServiceDetail, ServiceQuotationWorkOrder
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.servicequotation.serializers import (
    ServiceQuotationListSerializer, ServiceQuotationDetailSerializer,
    ServiceQuotationCreateSerializer, ServiceQuotationUpdateSerializer,
)


__all__ = [
    'ServiceQuotationList',
    'ServiceQuotationDetail',
]


class ServiceQuotationList(BaseListMixin, BaseCreateMixin):
    queryset = ServiceQuotation.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'system_status': ['exact'],
    }
    serializer_list = ServiceQuotationListSerializer
    serializer_create = ServiceQuotationCreateSerializer
    serializer_detail = ServiceQuotationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("employee_created__group")

    @swagger_auto_schema(
        operation_summary="ServiceQuotation list",
        operation_description="ServiceQuotation list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='servicequotation', model_code='servicequotation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ServiceQuotation",
        operation_description="Create new ServiceQuotation",
        request_body=ServiceQuotationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='servicequotation', model_code='servicequotation', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class ServiceQuotationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ServiceQuotation.objects  # noqa
    serializer_list = ServiceQuotationListSerializer
    serializer_detail = ServiceQuotationDetailSerializer
    serializer_update = ServiceQuotationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee_inherit",
        ).prefetch_related(
            Prefetch(
                'service_details',
                queryset=ServiceQuotationServiceDetail.objects.select_related('product'),
            ),
            Prefetch(
                'work_orders',
                queryset=ServiceQuotationWorkOrder.objects.select_related(
                    'product',
                ).prefetch_related(
                    'work_order_costs',
                    'work_order_contributions',
                ),
            ),
            "service_quotation_shipment_service_quotation",
            "attachment_m2m",
            "payments",
            "service_quotation_expense_service_quotation"
        )

    @swagger_auto_schema(operation_summary='Detail ServiceQuotation')
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='servicequotation', model_code='servicequotation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ServiceQuotation", request_body=ServiceQuotationUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='servicequotation', model_code='servicequotation', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
