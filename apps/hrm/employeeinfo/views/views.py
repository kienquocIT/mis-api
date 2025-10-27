from drf_yasg.utils import swagger_auto_schema

from apps.hrm.employeeinfo.models import EmployeeInfo, EmployeeHRNotMapEmployeeHRM, EmployeeContract
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseUpdateMixin, BaseRetrieveMixin

from ..serializers import EmployeeInfoListSerializers, EmployeeInfoCreateSerializers, \
    EmployeeInfoUpdateSerializers, EmployeeHRNotMapHRMListSerializers, EmployeeInfoDetailSerializers, \
    EmployeeContractListSerializers, EmployeeContractDetailSerializers, EmployeeSignatureAttachmentListSerializers, \
    EmployeeSignatureUpdateAttachmentSerializers


class EmployeeInfoList(BaseListMixin, BaseCreateMixin):
    queryset = EmployeeInfo.objects
    serializer_list = EmployeeInfoListSerializers
    serializer_detail = EmployeeInfoDetailSerializers
    serializer_create = EmployeeInfoCreateSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related('employee', 'employee__user')

    @swagger_auto_schema(
        operation_summary="Employee Info list",
        operation_description="get employee info list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create employee info",
        operation_description="Create employee info",
        request_body=EmployeeInfoCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.create(request, *args, **kwargs)


class EmployeeInfoDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = EmployeeInfo.objects
    serializer_detail = EmployeeInfoDetailSerializers
    serializer_update = EmployeeInfoUpdateSerializers
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('nationality', 'place_birth', 'place_origin')

    @swagger_auto_schema(
        operation_summary="Employee Info detail",
        operation_description="get employee info detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee info",
        operation_description="Update employee info",
        request_body=EmployeeInfoUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='edit'
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.update(request, *args, pk, **kwargs)


class EmployeeNotMapHRMList(BaseListMixin):
    queryset = EmployeeHRNotMapEmployeeHRM.objects
    serializer_list = EmployeeHRNotMapHRMListSerializers
    list_hidden_field = ['company_id']
    filterset_fields = {
        "is_mapped": ["exact"],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'company', 'employee', 'employee__user'
        )

    @swagger_auto_schema(
        operation_summary="Employee not map HRM list",
        operation_description="get Employee not map HRM list",
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EmployeeContractList(BaseListMixin):
    queryset = EmployeeContract.objects
    serializer_list = EmployeeContractListSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'employee_info': ['exact']
    }

    @swagger_auto_schema(
        operation_summary="Employee Contract list",
        operation_description="get employee contract list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EmployeeContractDetail(BaseRetrieveMixin):
    queryset = EmployeeContract.objects
    serializer_detail = EmployeeContractDetailSerializers
    # serializer_update = EmployeeInfoUpdateSerializers
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('represent')

    @swagger_auto_schema(
        operation_summary="Employee Contract detail",
        operation_description="get employee contract detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class EmployeeInfoSignatureList(BaseListMixin):
    queryset = EmployeeInfo.objects
    serializer_list = EmployeeSignatureAttachmentListSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'id': ["exact"]
    }

    @swagger_auto_schema(
        operation_summary="Employee info attachment list",
        operation_description="get employee info attachment list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='create',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AttachmentSignatureUpdate(BaseUpdateMixin):
    queryset = EmployeeInfo.objects
    serializer_update = EmployeeSignatureUpdateAttachmentSerializers
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update employee info attachment signature",
        operation_description="Update employee info attachment signature",
        request_body=EmployeeSignatureUpdateAttachmentSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='edit'
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)
