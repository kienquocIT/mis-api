from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.task.models.config import OpportunityTaskConfig
from apps.sales.task.serializers.config import TaskConfigDetailSerializer, TaskConfigUpdateSerializer
from apps.shared import (
    BaseRetrieveMixin, BaseUpdateMixin,
    mask_view
)

__all__ = [
    'TaskConfigDetail',
]


class TaskConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityTaskConfig.objects
    serializer_detail = TaskConfigDetailSerializer
    serializer_update = TaskConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Task Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Task Config Update",
        request_body=TaskConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
