from drf_yasg.utils import swagger_auto_schema # noqa
from rest_framework.permissions import IsAuthenticated
from apps.masterdata.saledata.models.shipping import Shipping
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ShippingList(BaseListMixin, BaseCreateMixin):
    queryset = Shipping.objects.select_related()
    # serializer_list = ExpenseListSerializer
    # serializer_create = ExpenseCreateSerializer
    # serializer_detail = ExpenseDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Expense list",
        operation_description="Expense list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Expense",
        operation_description="Create new Expense",
        # request_body=ExpenseCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ShippingDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated] # noqa
    queryset = Shipping.objects
    # serializer_detail = ExpenseDetailSerializer
    # serializer_update = ExpenseCreateSerializer

    @swagger_auto_schema(
        operation_summary="Expense detail",
        operation_description="Get Expense detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        # self.serializer_class = ExpenseDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Expense",
        operation_description="Update Expense by ID",
        # request_body=ExpenseUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        # self.serializer_class = ExpenseUpdateSerializer
        return self.update(request, *args, **kwargs)
