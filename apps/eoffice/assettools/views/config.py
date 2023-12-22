__all__ = ['AssetToolConfigDetail']

from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseUpdateMixin, BaseRetrieveMixin, mask_view
from ..models import AssetToolsConfig
from ..serializers import AssetToolsConfigDetailSerializers, AssetToolsConfigDetailUpdateSerializers


class AssetToolConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AssetToolsConfig.objects
    serializer_detail = AssetToolsConfigDetailSerializers
    serializer_update = AssetToolsConfigDetailUpdateSerializers
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('product_type').prefetch_related(
            'employee_tools_list_access', 'warehouse'
        )

    @swagger_auto_schema(
        operation_summary="Asset tools config",
        operation_description="Detail of asset tools config",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Asset tools config update",
        request_body=AssetToolsConfigDetailUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
