from drf_yasg.utils import swagger_auto_schema

from apps.hrm.employeeinfo.models import EmployeeContractRuntime
from apps.hrm.employeeinfo.serializers import EmployeeContractRuntimeCreateSerializers
from apps.shared import BaseCreateMixin, mask_view, BaseRetrieveMixin


class ContractRuntimeCreate(BaseCreateMixin):
    queryset = EmployeeContractRuntime.objects
    serializer_detail = EmployeeContractRuntimeCreateSerializers
    serializer_create = EmployeeContractRuntimeCreateSerializers
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created']

    @swagger_auto_schema(
        operation_summary="Create employee info",
        operation_description="Create employee info",
        request_body=EmployeeContractRuntimeCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContractRuntimeDetail(BaseRetrieveMixin):
    queryset = EmployeeContractRuntime.objects
    serializer_detail = EmployeeContractRuntimeCreateSerializers
    serializer_create = EmployeeContractRuntimeCreateSerializers
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created']

    @swagger_auto_schema(
        operation_summary="Create employee info",
        operation_description="Create employee info",
        request_body=EmployeeContractRuntimeCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

# , BaseUpdateMixin
