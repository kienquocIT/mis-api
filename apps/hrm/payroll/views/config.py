from drf_yasg.utils import swagger_auto_schema

from apps.hrm.payroll.models import PayrollConfig
from apps.hrm.payroll.serializers import PayrollConfigDetailSerializer, PayrollConfigUpdateSerializer
from apps.shared import BaseRetrieveMixin, BaseUpdateMixin, mask_view


class PayrollConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PayrollConfig.objects
    serializer_detail = PayrollConfigDetailSerializer
    serializer_update = PayrollConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Payroll Config Detail",
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
        operation_summary="Payroll Config Update",
        request_body=PayrollConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
