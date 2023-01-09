from drf_yasg.utils import swagger_auto_schema
from apps.core.company.models import Company
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin
from apps.core.tenant.serializers import (TenantInformationSerializer,)


class TenantInformation(BaseListMixin, BaseCreateMixin):
    queryset = Company.object_normal.all()
    serializer_list = TenantInformationSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Information",
        operation_description="Tenant Information",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
