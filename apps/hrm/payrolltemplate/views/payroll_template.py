from drf_yasg.utils import swagger_auto_schema

from apps.hrm.payrolltemplate.models import PayrollTemplate
from apps.hrm.payrolltemplate.serializers import PayrollTemplateListSerializers, PayrollTemplateDetailSerializers, \
    PayrollTemplateCreateSerializers, PayrollTemplateUpdateSerializers
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, mask_view


class PayrollTemplateList(BaseListMixin, BaseCreateMixin):
    queryset = PayrollTemplate.objects
    serializer_list = PayrollTemplateListSerializers
    serializer_detail = PayrollTemplateDetailSerializers
    serializer_create = PayrollTemplateCreateSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    search_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary="Payroll Template list",
        operation_description="get payroll template list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create payroll template request",
        operation_description="Create payroll template request",
        request_body=PayrollTemplateCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PayrollTemplateDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PayrollTemplate.objects
    serializer_detail = PayrollTemplateDetailSerializers
    serializer_update = PayrollTemplateUpdateSerializers
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    # def get_queryset(self):
    #     return super().get_queryset().select_related('shift')

    @swagger_auto_schema(
        operation_summary="Payroll template request detail",
        operation_description="get payroll template request detail by id",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Payroll template request update",
        operation_description="Payroll template request update by ID",
        request_body=PayrollTemplateUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code="edit",
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
