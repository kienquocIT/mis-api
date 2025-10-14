from drf_yasg.utils import swagger_auto_schema

from apps.hrm.payroll.serializers import (
    PayrollConfigListSerializer, PayrollConfigCreateSerializer,
    PayrollConfigDetailSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view
from apps.hrm.payroll.models import PayrollConfig


class PayrollConfigList(BaseListMixin, BaseCreateMixin):
    queryset = PayrollConfig.objects
    serializer_list = PayrollConfigListSerializer
    serializer_detail = PayrollConfigDetailSerializer
    serializer_create = PayrollConfigCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Payroll config list",
        operation_description="Payroll config list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Submit payroll config",
        operation_description="Submit payroll config",
        request_body=PayrollConfigCreateSerializer
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        request.data['company'] = str(request.user.company_current_id)
        return self.create(request, *args, **kwargs)
