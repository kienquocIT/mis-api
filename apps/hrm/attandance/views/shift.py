from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attandance.models import ShiftInfo
from apps.hrm.attandance.serializers import ShiftListSerializer, ShiftCreateSerializer, ShiftDetailSerializer, \
    ShiftUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin


class ShiftMasterDataList(BaseListMixin, BaseCreateMixin):
    queryset = ShiftInfo.objects
    serializer_list = ShiftListSerializer
    serializer_create = ShiftCreateSerializer
    serializer_detail = ShiftDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="Shift request list",
        operation_description="get shift request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create shift",
        operation_description="Create new shift"
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ShiftMasterDataDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ShiftInfo.objects
    serializer_detail = ShiftDetailSerializer
    serializer_update = ShiftUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Shift Detail')
    @mask_view(
        login_require=True,
        auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Update Shift')
    @mask_view(
        login_require=True,
        auth_require=False,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

