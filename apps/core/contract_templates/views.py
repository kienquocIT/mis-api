from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin
from .models import ContractTemplate
from .serializers import ContractTemplateListSerializers, ContractTemplateCreateSerializers, \
    ContractTemplateDetailSerializers


class ContractTemplateList(BaseListMixin, BaseCreateMixin):
    queryset = ContractTemplate.objects
    serializer_list = ContractTemplateListSerializers
    serializer_detail = ContractTemplateDetailSerializers
    serializer_create = ContractTemplateCreateSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id', 'employee_created_id'
    ]

    def get_queryset(self):
        return super().get_queryset().select_related('application', 'employee_created')

    @swagger_auto_schema(
        operation_summary="Contract template list",
        operation_description="get contract list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Contract template",
        operation_description="Create contract template",
        request_body=ContractTemplateCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user,
        }
        return self.create(request, *args, **kwargs)


class ContractTemplateDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ContractTemplate.objects
    serializer_detail = ContractTemplateDetailSerializers
    serializer_update = ContractTemplateDetailSerializers
    retrieve_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('application')

    @swagger_auto_schema(
        operation_summary="Contract template detail",
        operation_description="get contract template detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update contract template detail",
        operation_description="Update contract template detail",
        request_body=ContractTemplateDetailSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update contract template detail",
        operation_description="Update contract template detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True
    )
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)
