__all__ = ['ProjectConfigDetail']

from drf_yasg.utils import swagger_auto_schema

from apps.sales.project.models import ProjectConfig
from apps.sales.project.serializers import ProjectConfigDetailSerializer, ProjectConfigUpdateSerializer
from apps.shared import BaseRetrieveMixin, BaseUpdateMixin, mask_view


class ProjectConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProjectConfig.objects
    serializer_detail = ProjectConfigDetailSerializer
    serializer_update = ProjectConfigUpdateSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Project Config Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Project Config Update",
        request_body=ProjectConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
