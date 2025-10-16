import uuid

from django.contrib.auth.models import AnonymousUser
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from apps.sales.serviceorder.models import ServiceOrderWorkOrderTask
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus, TaskAssigneeGroup, \
    OpportunityTaskConfig
from apps.sales.task.serializers import (
    OpportunityTaskListSerializer, OpportunityTaskCreateSerializer,
    OpportunityTaskDetailSerializer, OpportunityTaskUpdateSTTSerializer, OpportunityTaskLogWorkSerializer,
    OpportunityTaskStatusListSerializer, OpportunityTaskUpdateSerializer, OpportunityTaskEmployeeGroupSerializer,
    OpportunityTaskListHasGroupSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, \
    BaseDestroyMixin, HttpMsg

__all__ = [
    'OpportunityTaskList', 'OpportunityTaskDetail', 'OpportunityTaskSwitchSTT', 'OpportunityTaskLogWork',
    'OpportunityTaskStatusList', 'GroupAssigneeList', 'OpportunityTaskWithGroupList'
]

from apps.shared.extends.response import cus_response


class OpportunityTaskList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityTask.objects
    serializer_list = OpportunityTaskListSerializer
    serializer_create = OpportunityTaskCreateSerializer
    serializer_detail = OpportunityTaskDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_fields = {
        'parent_n': ['exact', 'isnull'],
        'opportunity': ['exact'],
        'employee_inherit': ['exact'],
        'task_status': ['exact'],
        'priority': ['exact'],
        'id': ['exact', 'in'],
        'end_date': ['exact', 'range']
        'task_status__is_finish': ['exact']
    }

    def get_queryset(self):
        return self.queryset.select_related(
            'parent_n', 'employee_inherit', 'opportunity', 'employee_created', 'task_status', 'project'
        ).prefetch_related(
            Prefetch(
                'service_order_work_order_task_task',
                queryset=ServiceOrderWorkOrderTask.objects.select_related(
                    'work_order__service_order',
                    'work_order__service_order__opportunity',
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Opportunity Task List",
        operation_description="List of opportunity task",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='task', model_code='opportunityTask', perm_code='view',
        opp_enabled=True, prj_enabled=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def manual_check_obj_create(self, body_data, **kwargs):
        # in this case, that create request without employee_inherit, and this employee has permission in settings task
        # created assignee group
        group_assignee = self.request.data.get('group_assignee')
        if group_assignee:
            uuid_obj = uuid.UUID(group_assignee, version=4)
            # Kiểm tra xem có phải version 4 không
            return str(uuid_obj) == group_assignee.lower()
        return super().manual_check_obj_create(body_data, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Task",
        operation_description="Lead create task for member of team via opportunity page or via Task page",
        request_body=OpportunityTaskCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='task', model_code='opportunityTask', perm_code='create',
        opp_enabled=True, prj_enabled=True
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.create(request, *args, **kwargs)


class OpportunityTaskWithGroupList(BaseListMixin):
    queryset = OpportunityTask.objects
    serializer_list = OpportunityTaskListHasGroupSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'parent_n': ['exact', 'isnull'],
        'opportunity': ['exact'],
        'employee_inherit': ['exact', 'isnull'],
        'task_status': ['exact'],
        'priority': ['exact'],
    }

    def get_queryset(self):
        if not isinstance(self.request.user, AnonymousUser) and getattr(self.request.user, 'employee_current', None):
            employee_current = self.request.user.employee_current.id
            return self.queryset.select_related(
                'parent_n', 'opportunity', 'employee_created', 'task_status', 'project', 'group_assignee'
            ).filter(
                group_assignee__employee_list_access__icontains=employee_current,
                employee_inherit__isnull=True
            )
        return OpportunityTask.objects.none()

    @swagger_auto_schema(
        operation_summary="Opportunity Task List has group assignee",
        operation_description="List of opportunity task has group assginee and employee inherit is null",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OpportunityTaskDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = OpportunityTask.objects
    serializer_detail = OpportunityTaskDetailSerializer
    serializer_update = OpportunityTaskUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return self.queryset.select_related(
            'parent_n', 'employee_inherit', 'employee_created', 'process', 'process_stage_app', 'task_status',
            'opportunity', 'project', 'group_assignee',
        ).prefetch_related(
            Prefetch(
                'service_order_work_order_task_task',
                queryset=ServiceOrderWorkOrderTask.objects.select_related(
                    'work_order__service_order',
                    'work_order__service_order__opportunity',
                ),
            ),
        )

    def manual_check_obj_retrieve(self, instance, **kwargs):
        # in this case, that get detail of request without employee_inherit, and this employee in group assignee
        # retrieve task detail
        employee_crt = self.request.user.employee_current_id
        group_assignee = instance.group_assignee
        if group_assignee and instance.employee_inherit is None:
            is_stage = False
            employee_list_access = group_assignee.employee_list_access
            for item in employee_list_access:
                if item == str(employee_crt):
                    is_stage = True
                    break
            return is_stage
        return super().manual_check_obj_retrieve(instance, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Task Detail",
        operation_description="Detail opportunity task",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='task', model_code='opportunityTask', perm_code='view',
        opp_enabled=True, prj_enabled=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # in this case, that get detail of request without employee_inherit, and this employee in group assignee
        # retrieve task detail
        employee_crt = self.request.user.employee_current_id
        group_assignee = instance.group_assignee
        if group_assignee and instance.employee_inherit is None:
            is_stage = False
            employee_list_access = group_assignee.employee_list_access
            for item in employee_list_access:
                if item == str(employee_crt):
                    is_stage = True
                    break
            return is_stage
        return super().manual_check_obj_retrieve(instance, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Task Update",
        operation_description="Opportunity task update",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='task', model_code='OpportunityTask', perm_code='edit',
        opp_enabled=True, prj_enabled=True,
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Task",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='task', model_code='OpportunityTask', perm_code='delete',
        opp_enabled=True, prj_enabled=False,
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, is_purge=True, **kwargs)


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
        if not isinstance(self.request.user, AnonymousUser) and getattr(self.request.user, 'company_current', None):
            company_current_obj = self.request.user.company_current
            if company_current_obj and hasattr(company_current_obj, 'opportunity_task_config_company'):
                task_config = company_current_obj.opportunity_task_config_company
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


class GroupAssigneeList(BaseListMixin, BaseCreateMixin):
    queryset = TaskAssigneeGroup.objects
    serializer_list = OpportunityTaskEmployeeGroupSerializer
    serializer_create = OpportunityTaskEmployeeGroupSerializer
    serializer_detail = OpportunityTaskEmployeeGroupSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_fields = {
        'id': ['exact', 'in'],
    }

    @classmethod
    def check_user_perm(cls, request):
        user_current = request.user
        config = OpportunityTaskConfig.objects.get(
            tenant=user_current.tenant_current, company=user_current.company_current
        )
        if config and str(user_current.employee_current.id) in config.user_allow_group_handle:
            return True
        return False

    @swagger_auto_schema(
        operation_summary="Task group assignee list",
        operation_description="List of group assignee in task",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Task group assignee create",
        operation_description="Lead create group assignee",
        request_body=OpportunityTaskEmployeeGroupSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def post(self, request, *args, **kwargs):
        has_perm = self.check_user_perm(request)
        if has_perm:
            return self.create(request, *args, **kwargs)
        return cus_response(
            {
                "status": status.HTTP_403_FORBIDDEN,
                "detail": HttpMsg.FORBIDDEN,
            }, status.HTTP_403_FORBIDDEN, is_errors=True
        )
