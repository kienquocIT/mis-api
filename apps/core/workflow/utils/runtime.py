import logging
from datetime import timedelta
from typing import Union
from uuid import UUID

from django.db import models
from django.utils import timezone

from apps.core.log.tasks import (
    force_log_activity,
    force_new_notify_many,
)
from apps.shared import (
    FORMATTING, DisperseModel, MAP_FIELD_TITLE, call_task_background,
    WorkflowMsgNotify,
)
from apps.core.workflow.models import (
    WorkflowConfigOfApp,
    Workflow, Node, Association, CollaborationInForm, CollaborationOutForm, CollabInWorkflow,
    Zone,
    Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog,
)

logger = logging.getLogger(__name__)

__all__ = [
    'DocHandler',
    'RuntimeHandler',
    'RuntimeStageHandler',
    'RuntimeLogHandler',
]


class DocHandler:
    @property
    def model(self) -> models.Model:
        model_cls = DisperseModel(app_model=self.app_code).get_model()
        if model_cls and hasattr(model_cls, 'objects'):
            return model_cls
        raise ValueError('App code is incorrect. Value: ' + self.app_code)

    def __init__(self, doc_id, app_code):
        self.doc_id = doc_id
        self.app_code = app_code

    def get_obj(self, default_filter: dict) -> Union[models.Model, None]:
        try:
            return self.model.objects.get(pk=self.doc_id, **default_filter)
        except self.model.DoesNotExist:
            return None

    @classmethod
    def force_added(cls, obj):
        setattr(obj, 'system_status', 2)  # added
        obj.save(update_fields=['system_status'])
        return True

    @classmethod
    def force_added_with_runtime(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            setattr(obj, 'system_status', 2)  # added
            obj.save(update_fields=['system_status'])
            return True
        return False

    @classmethod
    def force_finish(cls, obj):
        setattr(obj, 'system_status', 3)  # finish
        obj.save(update_fields=['system_status'])
        return True

    @classmethod
    def force_finish_with_runtime(cls, runtime_obj, approved_or_rejected='approved'):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            match approved_or_rejected:
                case 'approved':
                    setattr(obj, 'system_status', 3)  # finish
                    obj.save(update_fields=['system_status'])
                case 'rejected':
                    setattr(obj, 'system_status', 4)  # cancel with reject
                    obj.save(update_fields=['system_status'])
            return True
        return False


class RuntimeHandler:
    @classmethod
    def employee_created_obj(cls, doc_obj) -> Union[None, models.Model]:
        if hasattr(doc_obj, 'employee_created'):
            return doc_obj.employee_created
        return None

    @classmethod
    def _get_application_model(cls) -> models.Model:
        """
        Get Model class Application
        Returns:

        """
        return DisperseModel(app_model='base.application').get_model()

    @classmethod
    def _get_application_obj(cls, app_code) -> Union[models.Model, None]:
        """
        Get Application Obj by App_Model
        Args:
            app_code: "app.model"

        Returns:
            Application Object
        """
        application_model = cls._get_application_model()
        try:
            arr = app_code.split(".")
            if len(arr) == 2:
                return application_model.objects.get(app_label=arr[0], code=arr[1])
        except application_model.DoesNotExist:
            pass
        return None

    @classmethod
    def get_document_obj(cls, doc_id: Union[UUID, str], app_code: str) -> Union[models.Model, None]:
        """
        Get Doc Obj by Doc ID and App_code (checked=_get_application_obj)
        Args:
            doc_id: UUID4
            app_code: "app.model"

        Returns:
            Document Object
        """
        if cls._get_application_obj(app_code):
            doc_models = DisperseModel(app_model=app_code).get_model()
            if doc_models:
                try:
                    return doc_models.objects.get(pk=doc_id)
                except doc_models.DoesNotExist:
                    pass
        return None

    @classmethod
    def create_runtime_obj(cls, tenant_id, company_id, doc_id, app_code, employee_created, employee_inherit) -> Runtime:
        """
        Call create runtime for Doc ID + App Code
        Args:
            employee_inherit:
            employee_created:
            tenant_id:
            company_id:
            doc_id:
            app_code:

        Returns:
            Runtime Object
        """
        application_model = cls._get_application_model()
        try:
            arr = app_code.split(".")
            if len(arr) == 2:
                # check runtime exist
                app_obj = application_model.objects.get(app_label=arr[0], code=arr[1])
                if Runtime.objects.filter(
                        tenant_id=tenant_id, company_id=company_id,
                        doc_id=doc_id, app=app_obj,
                ).exists():
                    raise ValueError('Runtime Obj is exist')

                # check doc exist
                doc_obj = DocHandler(doc_id, app_code).get_obj(
                    default_filter={'tenant_id': tenant_id, 'company_id': company_id}
                )
                if not doc_obj:
                    raise ValueError('Document Object does not exist')

                runtime_obj = Runtime.objects.create(
                    tenant_id=tenant_id,
                    company_id=company_id,
                    doc_id=doc_id,
                    doc_title=getattr(doc_obj, MAP_FIELD_TITLE[app_code], ''),
                    app=app_obj,
                    doc_params={},
                    flow=None,  # default don't use WF then check apply WF
                    stage_currents=None,
                    doc_employee_created=employee_created,
                    doc_employee_inherit=employee_inherit,
                )
                # update runtime to doc
                doc_obj.workflow_runtime = runtime_obj
                doc_obj.save(update_fields=['workflow_runtime'])
                return runtime_obj
        except application_model.DoesNotExist:
            raise AttributeError('App code runtime is incorrect')
        except ValueError as err:
            print('err: ', err)
            raise err
        raise AttributeError('App code should be {app_label}.{model_name}')

    @classmethod
    def get_runtime_obj(cls, doc_id, app_code):
        """
        Get Runtime Object by Doc ID + App Code
        Args:
            doc_id:
            app_code:

        Returns:
            Runtime Object
        """
        application_model = cls._get_application_model()
        try:
            app_obj = application_model.objects.get(app_model=app_code)
            return Runtime.objects.get(doc_id=doc_id, app=app_obj)
        except application_model.DoesNotExist:
            pass
        except Runtime.DoesNotExist:
            pass
        return None

    @classmethod
    def action_perform(
            cls,
            rt_assignee: RuntimeAssignee,
            employee_assignee_obj: models.Model,
            action_code: int,
    ) -> bool:
        if rt_assignee.is_done is False:
            runtime_obj = rt_assignee.stage.runtime

            # WORKFLOW_ACTION = {
            #     0: WorkflowMsg.ACTION_CREATE,
            #     1: WorkflowMsg.ACTION_APPROVED,
            #     2: WorkflowMsg.ACTION_REJECT,
            #     3: WorkflowMsg.ACTION_RETURN,
            #     4: WorkflowMsg.ACTION_RECEIVE,
            #     5: WorkflowMsg.ACTION_TODO,
            # }
            match action_code:
                case 0:
                    ...
                case 1:  # approved
                    # RuntimeStage logging
                    # Update flag done
                    RuntimeLogHandler(
                        stage_obj=rt_assignee.stage,
                        actor_obj=employee_assignee_obj,
                        is_system=False,
                    ).log_approval_task(action_number=1)
                    rt_assignee.is_done = True
                    rt_assignee.action_perform.append(action_code)
                    rt_assignee.action_perform = list(set(rt_assignee.action_perform))
                    rt_assignee.save(update_fields=['is_done', 'action_perform'])

                    # handle next stage
                    if not RuntimeAssignee.objects.filter(stage=rt_assignee.stage, is_done=False).exists():
                        # new cls call run_next
                        RuntimeStageHandler(
                            runtime_obj=runtime_obj,
                        ).run_next(
                            workflow=runtime_obj.flow, stage_obj_currently=rt_assignee.stage
                        )
                        # update runtime object
                        RuntimeStageHandler(
                            runtime_obj=runtime_obj,
                        ).set_state_task_bg('SUCCESS')
                case 2:  # reject
                    # RuntimeStage logging
                    # Update flag done
                    RuntimeLogHandler(
                        stage_obj=rt_assignee.stage,
                        actor_obj=employee_assignee_obj,
                        is_system=False,
                    ).log_approval_task(action_number=2)
                    rt_assignee.is_done = True
                    rt_assignee.action_perform.append(action_code)
                    rt_assignee.action_perform = list(set(rt_assignee.action_perform))
                    rt_assignee.save(update_fields=['is_done', 'action_perform'])

                    # update doc to reject
                    DocHandler.force_finish_with_runtime(runtime_obj, approved_or_rejected='rejected')

                    # handle next stage
                    # close all assignee waiting
                    # update runtime + doc with reject
                    RuntimeStageHandler(runtime_obj=runtime_obj).reject_runtime_by_assignee(
                        stage_runtime_currently=rt_assignee.stage,
                    )
                case 3:  # return
                    RuntimeStageHandler(runtime_obj=runtime_obj).return_begin_runtime_by_assignee(
                        stage_runtime_currently=rt_assignee.stage,
                    )
                case 4:  # receive
                    cls.action_perform(
                        rt_assignee=rt_assignee,
                        employee_assignee_obj=employee_assignee_obj,
                        action_code=1,
                    )
                case 5:  # To do
                    ...
            return True
        return False


class RuntimeStageHandler:
    def reject_runtime_by_assignee(self, stage_runtime_currently: RuntimeStage):
        self.runtime_obj.state = 2  # finish
        self.runtime_obj.status = 2
        self.runtime_obj.save(update_fields=['state', 'status'])
        RuntimeLogHandler(
            stage_obj=stage_runtime_currently,
            actor_obj=self.runtime_obj.doc_employee_created,
            is_system=True,
        ).log_finish_station_doc(final_state_num=2, msg_log='Document was rejected')  # reject
        return True

    def return_begin_runtime_by_assignee(
            self,
            stage_runtime_currently: RuntimeStage,
    ):
        RuntimeLogHandler(
            stage_obj=stage_runtime_currently,
            actor_obj=self.runtime_obj.doc_employee_created,
            is_system=False,
        ).log_return_task()  # return

        config_cls = WFConfigSupport(workflow=self.runtime_obj.flow)
        initial_node = config_cls.get_initial_node()
        if initial_node:
            _is_next_stage, next_stage = self.create_stage(
                node_passed=initial_node,
                from_stage=stage_runtime_currently,
                **{'is_return': True},
            )
            if next_stage:
                self.runtime_obj.stage_currents = next_stage
                self.runtime_obj.save()
                stage_runtime_currently.to_stage = next_stage
                stage_runtime_currently.save()
            self.set_state_task_bg('SUCCESS')
            return True
        return False

    def set_state_task_bg(self, state, field_saved=None):
        """
        Args:
            state:
            field_saved:

        Returns:

        """
        field_saved = field_saved if isinstance(field_saved, list) else []
        self.runtime_obj.task_bg_state = state
        self.runtime_obj.save(update_fields=['task_bg_state'] + field_saved)
        return True

    @classmethod
    def __get_zone_and_properties(cls, zone_objs: list[Zone]) -> list[dict]:
        result = []
        for obj in zone_objs:
            properties = []
            properties_detail = []
            for detail in obj.properties.all():
                properties.append(str(detail.id))
                properties_detail.append(
                    {
                        'id': str(detail.id),
                        'code': str(detail.code),
                        'type': str(detail.type),
                        'content_type': str(detail.content_type),
                        'properties': str(detail.properties),
                        'compare_operator': str(detail.compare_operator),
                        'remark': str(detail.remark),
                    }
                )
            result.append(
                {
                    "id": str(obj.id),
                    "title": obj.title,
                    "remark": obj.remark,
                    "properties": properties,
                    "properties_detail": properties_detail,
                }
            )
        return result

    @classmethod
    def __parse_collaboration(
            cls, node: Node, doc_params: dict = dict, employee_creator_id: Union[UUID, str, any] = None
    ) -> dict:
        # OPTION_COLLABORATOR = (
        #     (0, WorkflowMsg.COLLABORATOR_IN),
        #     (1, WorkflowMsg.COLLABORATOR_OUT),
        #     (2, WorkflowMsg.COLLABORATOR_WF),
        # )
        state_system, code_system = WFConfigSupport.check_stage_is_system(node)
        if state_system and code_system == WFConfigSupport.code_node_initial and employee_creator_id:
            return {
                str(employee_creator_id): cls.__get_zone_and_properties(node.zones_initial_node.all())
            }
        try:
            collab_opt = node.option_collaborator
            match collab_opt:
                case 0:
                    in_form_obj = CollaborationInForm.objects.get(node=node)
                    app_properties = in_form_obj.app_property
                    if not app_properties:
                        raise ValueError('Application Properties must be required with collab in form')
                    employee_id = doc_params.get(app_properties.code, None)
                    if not employee_id:
                        raise ValueError('Get employee from IN FORM return None')
                    return {
                        str(employee_id): cls.__get_zone_and_properties(in_form_obj.zone.all())
                    }
                case 1:
                    out_form_obj = CollaborationOutForm.objects.get(node=node)
                    zones = cls.__get_zone_and_properties(out_form_obj.zone.all())
                    return {
                        str(_id): zones for _id in out_form_obj.employees.all().values_list('id', flat=True)
                    }
                case 2:
                    return {
                        str(collab.employee_id): cls.__get_zone_and_properties(collab.zone.all())
                        for collab in CollabInWorkflow.objects.filter(node=node)
                    }
        except CollaborationInForm.DoesNotExist:
            pass
        except CollaborationOutForm.DoesNotExist:
            pass
        return {}

    def _create_assignee_and_zone(self, stage_obj: RuntimeStage, is_return: bool) -> list[RuntimeAssignee]:
        if stage_obj.node:
            # get assignee and zone
            assignee_and_zone = self.__parse_collaboration(
                node=stage_obj.node,
                doc_params=self.runtime_obj.doc_params,
                employee_creator_id=self.runtime_obj.doc_employee_created_id if is_return else None,
            )

            # convert assignee and zone to simple data
            employee_ids_zones = {}
            objs = []
            log_objs = []
            for emp_id, zone_and_properties in assignee_and_zone.items():
                obj_assignee = RuntimeAssignee(
                    stage=stage_obj,
                    employee_id=emp_id,
                    zone_and_properties=zone_and_properties,
                )
                obj_assignee.before_save(force_insert=True)
                objs.append(obj_assignee)

                # create instance log
                log_obj_tmp = RuntimeLogHandler(
                    stage_obj=stage_obj,
                    actor_id=emp_id,
                    is_system=True,
                ).log_new_assignee(
                    perform_created=False,
                    is_return=is_return,
                )
                # update some field need call save() (call bulk don't hit save())
                log_obj_tmp.before_save(force_insert=True)
                # add to list for call bulk create
                log_objs.append(log_obj_tmp)
                # push employee to stages.assignees
                employee_ids_zones.update({emp_id: zone_and_properties})

            # create runtime assignee
            objs_created = RuntimeAssignee.objects.bulk_create(objs=objs)

            # active hook push notify
            HookEventHandler(runtime_obj=self.runtime_obj, is_return=is_return).push_base_notify(
                runtime_assignee_obj=objs_created,
            )

            # update assignee and zone to Stage
            stage_obj.assignee_and_zone_data = employee_ids_zones
            stage_obj.save(update_fields=['assignee_and_zone_data'])

            # create log
            RuntimeLogHandler.perform_create(log_objs)
            return objs_created
        return []

    def run_next(self, workflow: Workflow, stage_obj_currently: RuntimeStage) -> Union[RuntimeStage, None]:
        config_cls = WFConfigSupport(workflow=workflow)
        association_passed = config_cls.get_next(stage_obj_currently.node, self.runtime_obj.doc_params)
        if association_passed and isinstance(association_passed, Association):
            is_next_stage, next_stage = self.create_stage(
                node_passed=association_passed.node_out,
                association_passed=association_passed,
                from_stage=stage_obj_currently,
            )
            if next_stage:
                self.runtime_obj.stage_currents = next_stage
                self.runtime_obj.save()
                stage_obj_currently.to_stage = next_stage
                stage_obj_currently.save()

                # check if stage is approved then auto added
                if next_stage.code == 'approved':
                    # call added doc obj
                    DocHandler.force_added_with_runtime(self.runtime_obj)
            if is_next_stage:
                return self.run_next(workflow=workflow, stage_obj_currently=next_stage)
            self.set_state_task_bg('SUCCESS')
            return next_stage

        # update some field when go to completed
        if stage_obj_currently.code == 'completed':
            self.runtime_obj.status = 1
            self.runtime_obj.state = 2
            self.runtime_obj.save(update_fields=['status', 'state'])
            DocHandler.force_finish_with_runtime(self.runtime_obj)
        elif stage_obj_currently.code == 'approved':
            # call added doc obj
            DocHandler.force_added_with_runtime(self.runtime_obj)
        return None

    @classmethod
    def replace_actions(cls, actions: list[any], is_return: bool):
        if is_return is True:
            actions = [x for x in actions if x not in (0, '0')]
            actions.append(4)
            actions = list(set(actions))
        return actions

    def create_stage(self, node_passed: Node, **kwargs) -> (bool, RuntimeStage):
        """
        Create Runtime Stage
        Args:
            node_passed: Node was selected that passed compare params with condition
            **kwargs: field in RuntimeStage

        Returns:
            RuntimeStage Object
        """
        is_return = kwargs.pop('is_return', False)
        actions = self.replace_actions(node_passed.actions, is_return=is_return)
        stage_obj = RuntimeStage.objects.create(
            runtime=self.runtime_obj,
            node=node_passed,
            title=node_passed.title,
            code=node_passed.code_node_system,
            node_data={
                "id": str(node_passed.id),
                "title": node_passed.title,
                "code": node_passed.code,
                "date_created": FORMATTING.parse_datetime(node_passed.date_created)
            },
            actions=actions,
            exit_node_conditions=node_passed.condition,
            association_passed=kwargs.get('association_passed', None),
            from_stage=kwargs.get('from_stage', None)
        )
        match stage_obj.code:
            case 'initial':
                RuntimeLogHandler(
                    stage_obj=stage_obj,
                    actor_obj=self.runtime_obj.doc_employee_created,
                    is_system=True,
                ).log_create_doc(is_return=is_return)
            case 'approved':
                RuntimeLogHandler(
                    stage_obj=stage_obj,
                    actor_obj=self.runtime_obj.doc_employee_created,
                    is_system=True,
                ).log_approval_station()
            case 'completed':
                RuntimeLogHandler(
                    stage_obj=stage_obj,
                    actor_obj=self.runtime_obj.doc_employee_created,
                    is_system=True,
                ).log_finish_station_doc(final_state_num=1, msg_log='Final complete station')
        # create assignee and zone (task)
        assignee_created = self._create_assignee_and_zone(stage_obj=stage_obj, is_return=is_return)
        if len(assignee_created) == 0:
            return True, stage_obj
        return False, stage_obj

    def run_stage(self, workflow: Workflow) -> Union[RuntimeStage, None]:
        config_cls = WFConfigSupport(workflow=workflow)
        initial_node = config_cls.get_initial_node()
        if initial_node:
            _is_next_init, init_stage = self.create_stage(initial_node)
            self.runtime_obj.stage_currents = init_stage
            self.runtime_obj.save()
            if _is_next_init:
                return self.run_next(workflow=workflow, stage_obj_currently=init_stage)
            return init_stage
        return None

    def __init__(self, runtime_obj: Runtime):
        if not isinstance(runtime_obj, Runtime):
            raise AttributeError('[RuntimeStageHandler] runtime_obj must be required.')
        self.runtime_obj = runtime_obj

    @classmethod
    def get_flow_applied(cls, runtime_obj: Runtime, app_obj: models.Model) -> (bool, int, Workflow):
        app_wf_config = WorkflowConfigOfApp.objects.filter(
            tenant=runtime_obj.tenant,
            company=runtime_obj.company,
            application=app_obj,
        ).first()
        if app_wf_config:
            return True, app_wf_config.mode, app_wf_config.workflow_currently
        return False, None, None

    def apply(self, app_obj: models.Model) -> Union[bool, None]:
        self.set_state_task_bg('STARTED')
        field_saved = ['state', 'start_mode']
        have_config, mode_wf, flow_apply = self.get_flow_applied(self.runtime_obj, app_obj)
        if have_config is True:
            self.runtime_obj.start_mode = mode_wf
            if mode_wf == 0:  # un-apply
                self.runtime_obj.state = 3  # finish with flow is non-apply.
                self.runtime_obj.status = 1  # finish with flow is non-apply.
                field_saved += ['status']
                state_task = 'SUCCESS'
                DocHandler.force_finish_with_runtime(self.runtime_obj)
            elif mode_wf == 1:  # apply
                if not flow_apply or not isinstance(flow_apply, Workflow):
                    raise ValueError('[RuntimeStageHandler][apply] Workflow must be required with apply flow.')
                self.runtime_obj.flow = flow_apply
                self.runtime_obj.state = 1  # in-progress
                self.runtime_obj.save(update_fields=['flow', 'state'])
                self.run_stage(workflow=flow_apply)
                state_task = 'SUCCESS'
            elif mode_wf == 2:  # pending
                self.runtime_obj.state = 0  # created
                state_task = 'PENDING'
            else:  # not support
                raise ValueError(
                    '[RuntimeStageHandler][apply] Mode app workflow must be choice in '
                    '[0: un-apply, 1: apply, 2: pending].'
                )
        else:
            state_task = 'SUCCESS'
            self.runtime_obj.start_mode = None
            self.runtime_obj.state = 3  # finish with flow is non-apply.
            self.runtime_obj.satus = 1  # finish with flow is non-apply.
            field_saved += ['status']
            DocHandler.force_finish_with_runtime(self.runtime_obj)
        self.set_state_task_bg(state_task, field_saved=field_saved)
        return True


class WFConfigSupport:
    code_node_initial = 'initial'
    code_node_approval = 'approved'
    code_node_complete = 'completed'

    @classmethod
    def compare_condition(cls, condition: list, params: dict) -> bool:
        print('cond: ', condition)
        print('params: ', params)
        return True

    def __init__(self, workflow: Workflow):
        if not isinstance(workflow, Workflow):
            raise AttributeError('[WFConfigSupport] Workflow must be required')
        self.flow = workflow

    @classmethod
    def check_stage_is_system(cls, node_obj: Node):
        if node_obj:
            if node_obj.code_node_system == cls.code_node_initial:
                return True, cls.code_node_initial
            if node_obj.code_node_system == cls.code_node_approval:
                return True, cls.code_node_approval
            if node_obj.code_node_system == cls.code_node_complete:
                return True, cls.code_node_complete
        return False, None

    def get_initial_node(self) -> Union[Node, None]:
        try:
            return Node.objects.get(workflow=self.flow, is_system=True, code_node_system=self.code_node_initial)
        except Node.DoesNotExist:
            pass
        return None

    def get_approved_node(self) -> Union[Node, None]:
        try:
            return Node.objects.get(workflow=self.flow, is_system=True, code_node_system=self.code_node_approval)
        except Node.DoesNotExist:
            pass
        return None

    def get_completed_node(self) -> Union[Node, None]:
        try:
            return Node.objects.get(workflow=self.flow, is_system=True, code_node_system=self.code_node_complete)
        except Node.DoesNotExist:
            pass
        return None

    def get_next(self, node_input: Node, params: dict) -> Union[Association, None]:
        association_passed = [
            obj for obj in Association.objects.filter(workflow_id=self.flow, node_in=node_input) if
            self.compare_condition(obj.condition, params) is True
        ]
        match len(association_passed):
            case 0:
                return None
            case 1:
                return association_passed[0]
            case _x if _x > 1:
                raise ValueError('Association passed large more than 1.')
        return None


class RuntimeLogHandler:
    @staticmethod
    def get_correct_date_log(runtime_obj: Runtime, seconds_compare_and_add: int):
        delta_time = timezone.now() - runtime_obj.date_created
        if delta_time.seconds > seconds_compare_and_add:
            return timezone.now()
        return timezone.now() + timedelta(seconds=seconds_compare_and_add)

    def __init__(
            self,
            stage_obj: RuntimeStage,
            actor_obj: DisperseModel(app_model='hr.employee').get_model() = None,
            actor_id: Union[UUID, str] = None,
            is_system: bool = False,
    ):
        self.is_system = is_system
        self.stage_obj = stage_obj
        if not actor_id and not actor_obj:
            self.actor_obj = None
        elif actor_obj:
            self.actor_obj = actor_obj
        elif actor_id:
            self.actor_obj = DisperseModel(app_model='hr.employee').get_model().objects.get(pk=actor_id)
        else:
            self.actor_obj = None

    @classmethod
    def perform_create(cls, objs: list[RuntimeLog]):
        return RuntimeLog.objects.bulk_create(objs)

    def log_create_doc(self, is_return=False):
        runtime_obj = self.stage_obj.runtime
        if runtime_obj:
            # force log run WF
            call_task_background(
                force_log_activity,
                **{
                    'tenant_id': runtime_obj.tenant_id,
                    'company_id': runtime_obj.company_id,
                    'request_method': '',
                    'date_created': RuntimeLogHandler.get_correct_date_log(runtime_obj, 3),
                    # + 10s for this crated after doc log created
                    'doc_id': runtime_obj.doc_id,
                    'doc_app': runtime_obj.app_code,
                    'automated_logging': True,
                    'user_id': None,
                    'employee_id': None,
                    'msg': 'Re-run begin station' if is_return else 'Runtime Workflow is successfully',
                    'data_change': {},
                    'change_partial': False,
                },
            )
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Re-run begin station' if is_return else 'Create document',
            is_system=self.is_system,
        )

    def log_new_assignee(self, perform_created: bool = True, is_return: bool = False):
        data = {
            "actor": self.actor_obj,
            "runtime": self.stage_obj.runtime,
            "stage": self.stage_obj,
            "kind": 2,
            "action": 0,
            "msg": WorkflowMsgNotify.was_return_begin if is_return else WorkflowMsgNotify.new_task,
            "is_system": self.is_system,
        }
        if perform_created is True:
            return RuntimeLog.objects.create(**data)
        return RuntimeLog(**data)

    def log_approval_station(self):
        runtime_obj = self.stage_obj.runtime
        if runtime_obj:
            call_task_background(
                force_log_activity,
                **{
                    'tenant_id': runtime_obj.tenant_id,
                    'company_id': runtime_obj.company_id,
                    'date_created': RuntimeLogHandler.get_correct_date_log(runtime_obj, 6),
                    'doc_id': runtime_obj.doc_id,
                    'doc_app': runtime_obj.app_code,
                    'automated_logging': True,
                    'msg': 'Final approval station',
                },
            )
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Approved',
            is_system=self.is_system,
        )

    def log_approval_task(self, action_number):
        action_choices = {
            1: 'Approved',
            2: 'Rejected',
        }
        # msg choice in: ['Approved']
        call_task_background(
            force_log_activity,
            **{
                'tenant_id': self.stage_obj.runtime.tenant_id,
                'company_id': self.stage_obj.runtime.company_id,
                'date_created': timezone.now(),
                'doc_id': self.stage_obj.runtime.doc_id,
                'doc_app': self.stage_obj.runtime.app_code,
                'automated_logging': False,
                'user_id': None,
                'employee_id': self.actor_obj.id,
                'msg': action_choices[action_number],
                'task_workflow_id': None,
            },
        )
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg=action_choices[action_number],
            is_system=self.is_system,
        )

    def log_return_task(self):
        call_task_background(
            force_log_activity,
            **{
                'tenant_id': self.stage_obj.runtime.tenant_id,
                'company_id': self.stage_obj.runtime.company_id,
                'date_created': timezone.now(),
                'doc_id': self.stage_obj.runtime.doc_id,
                'doc_app': self.stage_obj.runtime.app_code,
                'automated_logging': False,
                'user_id': None,
                'employee_id': self.actor_obj.id,
                'msg': 'Return to begin station',
                'task_workflow_id': None,
            },
        )
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Return to begin station',
            is_system=self.is_system,
        )

    def log_finish_station_doc(self, final_state_num=1, msg_log=''):
        final_state_choices = {
            1: 'Approved',
            2: 'Reject',
        }
        runtime_obj = self.stage_obj.runtime
        if runtime_obj:
            call_task_background(
                force_log_activity,
                **{
                    'tenant_id': runtime_obj.tenant_id,
                    'company_id': runtime_obj.company_id,
                    'date_created': RuntimeLogHandler.get_correct_date_log(runtime_obj, 9),
                    'doc_id': runtime_obj.doc_id,
                    'doc_app': runtime_obj.app_code,
                    'automated_logging': True,
                    'msg': msg_log,
                },
            )
        return RuntimeLog.objects.create(
            # actor=self.actor_obj,
            actor=None,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Finish flow' + f' with {final_state_choices[final_state_num]}',
            is_system=self.is_system,
        )

    def log_action_perform(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Perform a action',
            is_system=self.is_system,
        )

    def log_update_at_zone(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=1,  # in doc
            action=0,
            msg='Update data at zone',
            is_system=self.is_system,
        )


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
