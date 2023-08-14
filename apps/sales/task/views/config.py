from drf_yasg.utils import swagger_auto_schema

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
    queryset = OpportunityTaskConfig.objects
    serializer_detail = TaskConfigDetailSerializer
    serializer_update = TaskConfigUpdateSerializer
    list_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Task Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Task Config Update",
        request_body=TaskConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
