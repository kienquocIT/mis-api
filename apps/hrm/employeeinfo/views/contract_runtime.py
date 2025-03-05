from drf_yasg.utils import swagger_auto_schema

from apps.hrm.employeeinfo.models import EmployeeContractRuntime
from apps.hrm.employeeinfo.serializers import EmployeeContractRuntimeCreateSerializers
from apps.hrm.employeeinfo.serializers.employee_contract import EmployeeContractRuntimeDetailSerializers, \
    EmployeeContractRuntimeUpdateSerializers
from apps.shared import BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class ContractRuntimeCreate(BaseCreateMixin):
    queryset = EmployeeContractRuntime.objects
    serializer_detail = EmployeeContractRuntimeDetailSerializers
    serializer_create = EmployeeContractRuntimeCreateSerializers
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created']

    @swagger_auto_schema(
        operation_summary="Create employee info",
        operation_description="Create employee info",
        request_body=EmployeeContractRuntimeCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user.employee_current
        }
        return self.create(request, *args, **kwargs)


class ContractRuntimeDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = EmployeeContractRuntime.objects
    serializer_detail = EmployeeContractRuntimeDetailSerializers
    serializer_update = EmployeeContractRuntimeUpdateSerializers
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created']
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Signing request runtime",
        operation_description="Signing request runtime detail"
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="User Signing submit",
        operation_description="Employee sign contract has assigned",
        request_body=EmployeeContractRuntimeUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user.employee_current,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.update(request, *args, pk, **kwargs)
