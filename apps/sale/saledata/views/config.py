from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sale.saledata.models.config import PaymentTerm
from apps.sale.saledata.serializers.config import PaymentTermCreateSerializer, PaymentTermListSerializer, \
    PaymentTermDetailSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseDestroyMixin, BaseUpdateMixin


class ConfigPaymentTermList(BaseListMixin, BaseCreateMixin):
    queryset = PaymentTerm.objects.all()
    serializer_list = PaymentTermListSerializer
    serializer_create = PaymentTermCreateSerializer
    serializer_detail = PaymentTermDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Payment terms list",
        operation_description="Payment terms list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment terms",
        operation_description="Create new Payment terms",
        request_body=PaymentTermCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ConfigPaymentTermDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    permission_classes = [IsAuthenticated]
    queryset = PaymentTerm.objects
    serializer_detail = PaymentTermDetailSerializer
    serializer_update = PaymentTermDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Payment terms detail",
        operation_description="Get config payment terms detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.serializer_class = PaymentTermDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = PaymentTermDetailSerializer
        return self.update(request, *args, **kwargs)

    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
