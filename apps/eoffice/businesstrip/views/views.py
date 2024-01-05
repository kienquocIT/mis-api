from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.businesstrip.models import BusinessRequest, ExpenseItemMapBusinessRequest
from apps.eoffice.businesstrip.serializers import BusinessRequestListSerializer, BusinessRequestDetailSerializer, \
    BusinessRequestCreateSerializer, BusinessRequestUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin
from ..filters import BusinessTripListFilters

__all__ = ['BusinessTripRequestList', 'BusinessTripRequestDetail']


class BusinessTripRequestList(BaseListMixin, BaseCreateMixin):
    queryset = BusinessRequest.objects
    serializer_list = BusinessRequestListSerializer
    serializer_detail = BusinessRequestDetailSerializer
    serializer_create = BusinessRequestCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    search_fields = ('code', 'title')
    filterset_class = BusinessTripListFilters

    def get_queryset(self):
        return super().get_queryset().select_related('destination', 'employee_inherit').prefetch_related(
            'employee_on_trip_list',
        )

    @swagger_auto_schema(
        operation_summary="Business trip request list",
        operation_description="get business trip request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='businesstrip', model_code='businessrequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create business trip request",
        operation_description="Create business trip request",
        request_body=BusinessRequestCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='businesstrip', model_code='businessRequest', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        return self.create(request, *args, **kwargs)


class BusinessTripRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = BusinessRequest.objects
    serializer_detail = BusinessRequestDetailSerializer
    serializer_update = BusinessRequestUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit', 'departure', 'destination').prefetch_related(
            Prefetch(
                'expense_item_map_business_request',
                queryset=ExpenseItemMapBusinessRequest.objects.select_related(
                    'expense_item',
                    'tax',
                )
            )

        )

    @swagger_auto_schema(
        operation_summary="Business trip request list",
        operation_description="get business trip request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='businesstrip', model_code='businessRequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Business trip request update",
        operation_description="Business trip request update by ID",
        request_body=BusinessRequestUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='businesstrip', model_code='businessRequest', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
