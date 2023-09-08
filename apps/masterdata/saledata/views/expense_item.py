from drf_yasg.utils import swagger_auto_schema  # noqa

from apps.masterdata.saledata.models import ExpenseItem
from apps.masterdata.saledata.serializers import ExpenseItemListSerializer, ExpenseItemCreateSerializer, \
    ExpenseItemUpdateSerializer
from apps.masterdata.saledata.serializers.expense_item import ExpenseItemDetailSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = ['ExpenseItemList', 'ExpenseItemDetail']


class ExpenseItemList(BaseListMixin, BaseCreateMixin):
    queryset = ExpenseItem.objects
    serializer_list = ExpenseItemListSerializer
    serializer_create = ExpenseItemCreateSerializer
    serializer_detail = ExpenseItemListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'expense_parent',
        )

    @swagger_auto_schema(
        operation_summary="Expense Item list",
        operation_description="Expense Item list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Expense Item",
        operation_description="Create new Expense Item",
        request_body=ExpenseItemCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExpenseItemDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ExpenseItem.objects
    serializer_detail = ExpenseItemDetailSerializer
    serializer_update = ExpenseItemUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'expense_parent'
        )

    @swagger_auto_schema(
        operation_summary="Expense item detail",
        operation_description="Get Expense item detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Expense Item",
        operation_description="Update Expense item by ID",
        request_body=ExpenseItemUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
