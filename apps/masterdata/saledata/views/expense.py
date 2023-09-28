from drf_yasg.utils import swagger_auto_schema # noqa

from apps.masterdata.saledata.models.product import Expense
from apps.masterdata.saledata.serializers.expense import (
    ExpenseListSerializer, ExpenseCreateSerializer,
    ExpenseDetailSerializer, ExpenseUpdateSerializer, ExpenseForSaleListSerializer,
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ExpenseList(BaseListMixin, BaseCreateMixin):
    queryset = Expense.objects
    search_fields = ['title']
    serializer_list = ExpenseListSerializer
    serializer_create = ExpenseCreateSerializer
    serializer_detail = ExpenseDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'uom_group',
            'uom',
        )

    @swagger_auto_schema(
        operation_summary="Expense list",
        operation_description="Expense list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Expense",
        operation_description="Create new Expense",
        request_body=ExpenseCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExpenseDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Expense.objects
    serializer_detail = ExpenseDetailSerializer
    serializer_update = ExpenseUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'uom', 'uom_group'
        )

    @swagger_auto_schema(
        operation_summary="Expense detail",
        operation_description="Get Expense detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Expense",
        operation_description="Update Expense by ID",
        request_body=ExpenseUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Expenses use for sale applications
class ExpenseForSaleList(BaseListMixin):
    queryset = Expense.objects
    search_fields = ['title']
    serializer_list = ExpenseForSaleListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "uom",
            "uom_group"
        )

    @swagger_auto_schema(
        operation_summary="Expense for sale list",
        operation_description="Expense for sale list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
