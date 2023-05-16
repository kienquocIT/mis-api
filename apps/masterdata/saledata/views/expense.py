from drf_yasg.utils import swagger_auto_schema # noqa
from rest_framework.permissions import IsAuthenticated

from apps.masterdata.saledata.models.product import Expense
from apps.masterdata.saledata.serializers.expense import ExpenseListSerializer, ExpenseCreateSerializer, \
    ExpenseDetailSerializer, ExpenseUpdateSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ExpenseList(BaseListMixin, BaseCreateMixin):
    queryset = Expense.objects
    serializer_list = ExpenseListSerializer
    serializer_create = ExpenseCreateSerializer
    serializer_detail = ExpenseDetailSerializer
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
        request_body=ExpenseCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExpenseDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects
    serializer_detail = ExpenseDetailSerializer
    serializer_update = ExpenseUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Expense detail",
        operation_description="Get Expense detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Expense",
        operation_description="Update Expense by ID",
        request_body=ExpenseUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
