from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseListMixin, mask_view

from apps.core.log.models import ActivityLog
from apps.core.log.serializers import ActivityListSerializer


class ActivityLogList(BaseListMixin):
    queryset = ActivityLog.objects
    list_hidden_field = ['tenant_id', 'company_id']
    serializer_list = ActivityListSerializer
    filterset_fields = {
        'doc_id': ['exact'],
        'doc_app': ['exact'],
        'user_id': ['exact'],
        'employee_id': ['exact'],
    }

    @swagger_auto_schema(operation_summary='Activity Log')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
