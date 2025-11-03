from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from apps.shared.extends.response import cus_response
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, \
    BaseDestroyMixin, HttpMsg
from ..models import AttributeComponent
from ..serializers import PayrollComponentListSerializers, PayrollComponentCreateSerializers


def check_has_perm():
    # disper_obj = DisperseModel(app_model='')
    # if
    return True


class PayrollComponentList(BaseListMixin, BaseCreateMixin):
    queryset = AttributeComponent.objects
    serializer_list = PayrollComponentListSerializers
    serializer_detail = PayrollComponentListSerializers
    serializer_create = PayrollComponentCreateSerializers
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']
    search_fields = ('code', 'title')

    @swagger_auto_schema(
        operation_summary="Payroll component list",
        operation_description="get payroll component list",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create payroll component",
        operation_description="Create payroll component",
        request_body=PayrollComponentCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PayrollComponentDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = AttributeComponent.objects
    serializer_detail = PayrollComponentListSerializers
    serializer_update = PayrollComponentListSerializers
    retrieve_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Payroll component detail",
        operation_description="get payroll component detail by id",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Payroll component update",
        operation_description="Payroll component update by ID",
        request_body=PayrollComponentCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code="edit",
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Payroll component destroy",
        operation_description="Payroll component destroy by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='payrolltemplate', model_code='payrolltemplate', perm_code="delete",
    )
    def delete(self, request, *args, pk, **kwargs):
        if not AttributeComponent.objects.filter(id=pk, is_system=False).exists():
            return cus_response(
                data={
                    "status": status.HTTP_403_FORBIDDEN,
                    "detail": HttpMsg.FORBIDDEN,
                }, status=status.HTTP_403_FORBIDDEN, is_errors=True
            )
        return self.destroy(request, *args, **kwargs)
