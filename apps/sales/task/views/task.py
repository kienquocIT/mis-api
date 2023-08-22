from drf_yasg.utils import swagger_auto_schema

from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus
from apps.sales.task.serializers import (
    OpportunityTaskListSerializer, OpportunityTaskCreateSerializer,
    OpportunityTaskDetailSerializer, OpportunityTaskUpdateSTTSerializer, OpportunityTaskLogWorkSerializer,
    OpportunityTaskStatusListSerializer, OpportunityTaskUpdateSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = [
    'OpportunityTaskList', 'OpportunityTaskDetail', 'OpportunityTaskSwitchSTT', 'OpportunityTaskLogWork',
    'OpportunityTaskStatusList'
]


class OpportunityTaskList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityTask.objects
    serializer_list = OpportunityTaskListSerializer
    serializer_create = OpportunityTaskCreateSerializer
    serializer_detail = OpportunityTaskDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_fields = {
        'parent_n': ['exact'],
    }

    def get_queryset(self):
        return self.queryset.select_related('parent_n', 'assign_to', 'opportunity')

    @swagger_auto_schema(
        operation_summary="Opportunity Task List",
        operation_description="List of opportunity task",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='task', model_code='opportunitytask', perm_code='view', )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Task",
        operation_description="Lead create task for member of team via opportunity page or via Task page",
        request_body=OpportunityTaskCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='task', model_code='opportunitytask', perm_code='create', )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.create(request, *args, **kwargs)


class OpportunityTaskDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = OpportunityTask.objects
    serializer_detail = OpportunityTaskDetailSerializer
    serializer_update = OpportunityTaskUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return self.queryset.select_related('parent_n', 'assign_to', 'employee_created')

    @swagger_auto_schema(
        operation_summary="Opportunity Task Detail",
        operation_description="Detail opportunity task",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Task Update",
        operation_description="Opportunity task update",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='task', model_code='opportunitytask', perm_code='edit', )
    def put(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Task",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='task', model_code='opportunitytask', perm_code='delete', )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OpportunityTaskSwitchSTT(BaseUpdateMixin):
    queryset = OpportunityTask.objects
    serializer_detail = OpportunityTaskUpdateSTTSerializer
    serializer_update = OpportunityTaskUpdateSTTSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Opportunity Task Update status",
        operation_description="Opportunity task update status",
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class OpportunityTaskLogWork(BaseCreateMixin):
    queryset = OpportunityLogWork.objects
    serializer_create = OpportunityTaskLogWorkSerializer
    serializer_detail = OpportunityTaskLogWorkSerializer
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Opportunity Task Log Work",
        operation_description="Opportunity task Log Work",
        request_body=OpportunityTaskLogWorkSerializer,
    )
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'employee': request.user.employee_current
        }
        return self.create(request, *args, **kwargs)


class OpportunityTaskStatusList(BaseListMixin):
    queryset = OpportunityTaskStatus.objects
    serializer_list = OpportunityTaskStatusListSerializer
    filterset_fields = {
        'task_config': ['exact'],
    }
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        task_config = self.request.user.company_current.opportunity_task_config_company
        if task_config:
            return super().get_queryset().filter(task_config_id=task_config.id)
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Opportunity Task Status List",
        operation_description="List of opportunity task status",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
