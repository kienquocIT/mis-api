from django.utils import timezone
from apps.core.log.tasks import (
    force_log_activity,
    force_new_notify_many
)
from apps.shared import (
    call_task_background,
    WorkflowMsgNotify
)
from apps.core.workflow.models import RuntimeLog, Runtime, RuntimeAssignee


class HookEventHandler:
    def __init__(self, runtime_obj: Runtime, is_return: bool = False):
        self.runtime_obj = runtime_obj
        self.is_return = is_return

    def push_base_notify(self, runtime_assignee_obj: list[RuntimeAssignee]):
        try:
            args_arr = []
            for obj in runtime_assignee_obj:
                if obj.is_done is False:
                    args_arr.append(
                        {
                            'tenant_id': self.runtime_obj.tenant_id,
                            'company_id': self.runtime_obj.company_id,
                            'title': self.runtime_obj.doc_title,
                            'msg': WorkflowMsgNotify.was_return_begin if self.is_return else WorkflowMsgNotify.new_task,
                            'date_created': timezone.now(),
                            'doc_id': self.runtime_obj.doc_id,
                            'doc_app': self.runtime_obj.app_code,
                            'user_id': None,
                            'employee_id': obj.employee_id,
                            'employee_sender_id': None,
                        }
                    )
            if len(args_arr) > 0:
                call_task_background(
                    force_new_notify_many,
                    *[args_arr],
                )
            return True
        except Exception as err:
            print('push_base_notify: ', str(err))
        return False


class WFSupportFunctionsHandler:

    @classmethod
    def get_assignee_node_in_wf(cls, collab, doc_employee_inherit):
        if collab.in_wf_option == 1 and doc_employee_inherit:  # BY POSITION
            if not doc_employee_inherit.group:
                raise ValueError('Employee inherit does not have group')
            if collab.position_choice == 1:  # 1st manager
                if not doc_employee_inherit.group.first_manager_id:
                    raise ValueError('1st manager is not defined')
                if doc_employee_inherit.group.first_manager_id == doc_employee_inherit.id:
                    return cls.get_manager_upper_group(doc_employee_inherit.group)
                return doc_employee_inherit.group.first_manager_id
            if collab.position_choice == 2:  # 2nd manager
                if not doc_employee_inherit.group.second_manager_id:
                    raise ValueError('2nd manager is not defined')
                return doc_employee_inherit.group.second_manager_id
            if collab.position_choice == 3:  # Beneficiary (Document inherit)
                return doc_employee_inherit.id
        if collab.in_wf_option == 2:  # BY EMPLOYEE
            return collab.employee_id
        raise ValueError('Can not find assignee for this node')

    @classmethod
    def get_manager_upper_group(cls, group):
        if group.parent_n:
            if group.parent_n.first_manager_id:
                return group.parent_n.first_manager_id
        raise ValueError('1st manager is not defined')

    @classmethod
    def update_runtime_when_error(cls, stage_obj, value_error):
        stage_obj.runtime.state = 4  # fail
        stage_obj.runtime.status = 2  # fail
        stage_obj.runtime.save(update_fields=['state', 'status'])
        # log error
        msg = 'Workflow error: ' + str(value_error)
        cls.log_runtime_error(stage_obj=stage_obj, msg=msg)
        raise value_error

    @classmethod
    def log_runtime_error(cls, stage_obj, msg):
        call_task_background(
            force_log_activity,
            **{
                'tenant_id': stage_obj.runtime.tenant_id,
                'company_id': stage_obj.runtime.company_id,
                'date_created': timezone.now(),
                'doc_id': stage_obj.runtime.doc_id,
                'doc_app': stage_obj.runtime.app_code,
                'automated_logging': False,
                'user_id': None,
                'employee_id': None,
                'msg': msg,
                'task_workflow_id': None,
            },
        )
        return RuntimeLog.objects.create(
            actor=None,
            runtime=stage_obj.runtime,
            stage=stage_obj,
            kind=2,
            action=0,
            msg=msg,
            is_system=True,
        )
