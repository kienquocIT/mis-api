from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.serializers.config import PaymentTermCreateSerializer, PaymentTermListSerializer, \
    PaymentTermDetailSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseDestroyMixin, BaseUpdateMixin


class ConfigPaymentTermList(BaseListMixin, BaseCreateMixin):
    queryset = PaymentTerm.objects
    serializer_list = PaymentTermListSerializer
    serializer_create = PaymentTermCreateSerializer
    serializer_detail = PaymentTermDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Payment terms list",
        operation_description="Payment terms list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment terms",
        operation_description="Create new Payment terms",
        request_body=PaymentTermCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ConfigPaymentTermDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = PaymentTerm.objects
    serializer_detail = PaymentTermDetailSerializer
    serializer_update = PaymentTermDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Payment terms detail",
        operation_description="Get config payment terms detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
