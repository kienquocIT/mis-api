from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attandance.models import ShiftInfo
from apps.hrm.attandance.serializers import ShiftListSerializer, ShiftCreateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


class ShiftMasterDataList(BaseListMixin, BaseCreateMixin):
    queryset = ShiftInfo.objects
    serializer_list = ShiftListSerializer
    serializer_create = ShiftCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Shift request list",
        operation_description="get shift request list"
    )
    @mask_view(
        login_require=True, auth_require=True,
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
    def get(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
