from drf_yasg.utils import swagger_auto_schema
from apps.core.company.models import Company
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin
from apps.core.tenant.serializers import (TenantDetailSerializer,)


class TenantDetail(BaseListMixin, BaseCreateMixin):
    queryset = Company.object_normal.all()
    serializer_list = TenantDetailSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Detail",
        operation_description="Tenant Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
