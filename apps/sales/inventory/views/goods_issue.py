from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsIssue
from apps.sales.inventory.serializers import GoodsIssueListSerializer, GoodsIssueCreateSerializer, \
    GoodsIssueDetailSerializer
from apps.sales.inventory.serializers.goods_issue import GoodsIssueUpdateSerializer

from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsIssueList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsIssue.objects
    search_fields = ['title']
    serializer_list = GoodsIssueListSerializer
    serializer_create = GoodsIssueCreateSerializer
    serializer_detail = GoodsIssueDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Goods issue List",
        operation_description="Get Goods issue List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods issue",
        operation_description="Create new Goods issue",
        request_body=GoodsIssueCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsIssueDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = GoodsIssue.objects
    serializer_detail = GoodsIssueDetailSerializer
    serializer_update = GoodsIssueUpdateSerializer
    detail_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "inventory_adjustment",
        )

    @swagger_auto_schema(
        operation_summary="Goods issue detail",
        operation_description="Get Goods issue detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods issue",
        operation_description="Update Goods issue by ID",
        request_body=GoodsIssueUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
