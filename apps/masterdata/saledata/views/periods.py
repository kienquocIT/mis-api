from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Periods
from apps.masterdata.saledata.serializers import (
    PeriodsListSerializer, PeriodsCreateSerializer,
    PeriodsDetailSerializer, PeriodsUpdateSerializer
)
from apps.shared import (
    mask_view, ResponseController,
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
)


# Create your views here.
class PeriodsList(BaseListMixin, BaseCreateMixin):
    queryset = Periods.objects
    search_fields = ['title']
    serializer_list = PeriodsListSerializer
    serializer_create = PeriodsCreateSerializer
    serializer_detail = PeriodsDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('company').prefetch_related('sub_periods_period_mapped')

    @swagger_auto_schema(
        operation_summary="Periods list",
        operation_description="Periods list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        if 'get_current' in request.query_params:
            this_period = Periods.get_current_period(request.user.tenant_current_id, request.user.company_current_id)
            if this_period:
                self.kwargs['fiscal_year'] = this_period.fiscal_year
        self.ser_context = {
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Periods",
        operation_description="Create new Periods",
        request_body=PeriodsCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current': request.user.company_current
        }
        return self.create(request, *args, **kwargs)


class PeriodsDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = Periods.objects
    serializer_list = PeriodsListSerializer
    serializer_create = PeriodsCreateSerializer
    serializer_detail = PeriodsDetailSerializer
    serializer_update = PeriodsUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Periods')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update Periods", request_body=PeriodsUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'employee_current': request.user.employee_current,
            'company_current': request.user.company_current,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove member from opp'
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, **kwargs):
        this_period = Periods.get_current_period(request.user.tenant_current_id, request.user.company_current_id)
        instance = self.get_object()
        if str(instance.id) == str(this_period.id):
            return ResponseController.internal_server_error_500(msg="Cannot delete this Period.")
        instance.delete()
        return ResponseController.success_200({}, key_data='result')
