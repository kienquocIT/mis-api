from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView

from apps.sales.task.models.config import TaskConfig
from apps.sales.task.serializers.config import TaskConfigDetailSerializer, TaskConfigUpdateSerializer
from apps.shared import (
    BaseRetrieveMixin, BaseUpdateMixin,
    mask_view, DisperseModel, ResponseController, TypeCheck,
    call_task_background,
)
from apps.sales.delivery.models import (
    DeliveryConfig,
)
from apps.sales.delivery.serializers import (
    DeliveryConfigDetailSerializer, DeliveryConfigUpdateSerializer,
)
from apps.sales.delivery.tasks import (
    task_active_delivery_from_sale_order,
)

__all__ = [
    'TaskConfigDetail',
]


class TaskConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = TaskConfig.objects
    serializer_detail = TaskConfigDetailSerializer
    serializer_update = TaskConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Task Config Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Task Config Update",
        request_body=TaskConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)
