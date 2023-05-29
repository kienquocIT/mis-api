import time
from typing import Union
from uuid import UUID

from celery import uuid
from celery import shared_task
from django.db import models

from apps.shared import (
    FORMATTING, DisperseModel, MAP_FIELD_TITLE, call_task_background,
)
from ..models.config import (
    Workflow, Node, Association, CollaborationInForm, CollaborationOutForm, CollabInWorkflow,
    Zone,
)
from ..models.runtime import (
    Runtime, RuntimeStage, RuntimeAssignee, RuntimeLog,
)
from .docs import DocHandler

__all__ = [
    'call_new_runtime',
    'call_approval_task',
]


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
    def create_runtime_obj(cls, company_id, doc_id, app_code, task_bg_id) -> Runtime:
        """
        Call create runtime for Doc ID + App Code
        Args:
            task_bg_id:
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
                app_obj = application_model.objects.get(app_label=arr[0], code=arr[1])
                if Runtime.objects.filter(doc_id=doc_id, app=app_obj).exists():
                    raise ValueError('Runtime Obj is exist')
                doc_obj = DocHandler(doc_id, app_code).get_obj(default_filter={'company_id': company_id})
                print("doc_obj: ", doc_obj)
                if not doc_obj:
                    raise ValueError('Document Object does not exist')

                print('Doc Title: ', getattr(doc_obj, MAP_FIELD_TITLE[app_code], ''))
                return Runtime.objects.create(
                    doc_id=doc_id,
                    doc_title=getattr(doc_obj, MAP_FIELD_TITLE[app_code], ''),
                    app=app_obj,
                    doc_params={},
                    flow=None,  # default don't use WF then check apply WF
                    stage_currents=None,
                    task_bg_id=task_bg_id,
                    doc_employee_created=cls.employee_created_obj(doc_obj=doc_obj),
                )
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
    def call_new(cls, company_id, doc_id, app_code, task_bg_id) -> bool:
        """
        Call when new document create then apply/check apply workflow
        Args:
            task_bg_id:
            company_id:
            doc_id:
            app_code: "{app_label}.{model_name}"

        Returns:
            Boolean
        """
        # create runtime obj
        runtime_obj = cls.create_runtime_obj(company_id, doc_id, app_code, task_bg_id)
        time.sleep(10)
        return RuntimeStageHandler(
            runtime_obj=runtime_obj,
        ).apply(
            app_obj=cls._get_application_obj(app_code),

        )

    @classmethod
    def approval(cls, rt_assignee: RuntimeAssignee, employee_assignee_obj: models.Model) -> bool:
        if rt_assignee.is_done is False:
            runtime_obj = rt_assignee.stage.runtime

            # RuntimeStage logging
            # Update flag done
            RuntimeLogHandler(stage_obj=rt_assignee.stage, actor_obj=employee_assignee_obj).log_approval_doc()
            rt_assignee.is_done = True
            rt_assignee.action_perform.append(0)
            rt_assignee.action_perform = list(set(rt_assignee.action_perform))
            rt_assignee.save(update_fields=['is_done', 'action_perform'])

            # handle next stage
            if not RuntimeAssignee.objects.filter(stage=rt_assignee.stage, is_done=False).exists():
                task_bg_id = uuid()
                call_task_background(
                    call_next_stage,
                    *[
                        str(rt_assignee.stage.runtime_id),
                        str(rt_assignee.stage_id),
                    ],
                )
                runtime_obj.task_bg_id = task_bg_id
                runtime_obj.task_bg_state = 'PENDING'
                runtime_obj.save(update_fields=['task_bg_id', 'task_bg_state'])
                RuntimeStageHandler(
                    runtime_obj=runtime_obj,
                ).set_state_task_bg('SUCCESS')
            return True
        return False


class RuntimeStageHandler:
    def set_state_task_bg(self, state):
        """
        Args:
            state:

        Returns:

        """
        self.runtime_obj.task_bg_state = state
        self.runtime_obj.save(update_fields=['task_bg_state'])
        return True

    @classmethod
    def __get_zone_and_properties(cls, zone_objs: list[Zone]) -> list[dict]:
        return [{
            "id": str(obj.id),
            "title": obj.title,
            "remark": obj.remark,
            "properties": [str(x) for x in obj.properties.all().values_list('id', flat=True)]
        } for obj in zone_objs]

    @classmethod
    def __parse_collaboration(cls, node: Node, doc_params: dict = dict) -> dict:
        # OPTION_COLLABORATOR = (
        #     (0, WorkflowMsg.COLLABORATOR_IN),
        #     (1, WorkflowMsg.COLLABORATOR_OUT),
        #     (2, WorkflowMsg.COLLABORATOR_WF),
        # )
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

    def _create_assignee_and_zone(self, stage_obj: RuntimeStage) -> list[RuntimeAssignee]:
        if stage_obj.node:
            assignee_and_zone = self.__parse_collaboration(stage_obj.node, self.runtime_obj.doc_params)
            objs = []
            log_objs = []
            for emp_id, zone_and_properties in assignee_and_zone.items():
                objs.append(
                    RuntimeAssignee(
                        stage=stage_obj,
                        employee_id=emp_id,
                        zone_and_properties=zone_and_properties,
                    )
                )
                # create instance log
                log_obj_tmp = RuntimeLogHandler(stage_obj=stage_obj, actor_id=emp_id).log_new_assignee(
                    perform_created=False
                )
                # update some field need call save() (call bulk don't hit save())
                log_obj_tmp.before_force(force_insert=True)
                # add to list for call bulk create
                log_objs.append(log_obj_tmp)
            objs_created = RuntimeAssignee.objects.bulk_create(objs=objs)
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
            if is_next_stage:
                return self.run_next(workflow=workflow, stage_obj_currently=next_stage)
            self.set_state_task_bg('SUCCESS')
            print('Process next stopped: ', next_stage)
            return next_stage

        # call log and state errors
        if stage_obj_currently.code == 'completed':
            self.runtime_obj.status = 1
            self.runtime_obj.state = 2
            self.runtime_obj.save(update_fields=['status', 'state'])
        print('Association not pass: ', stage_obj_currently)
        return None

    def create_stage(self, node_passed: Node, **kwargs) -> (bool, RuntimeStage):
        """
        Create Runtime Stage
        Args:
            node_passed: Node was selected that passed compare params with condition
            **kwargs: field in RuntimeStage

        Returns:
            RuntimeStage Object
        """
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
            actions=node_passed.actions,
            exit_node_conditions=node_passed.condition,
            association_passed=kwargs.get('association_passed', None),
            from_stage=kwargs.get('from_stage', None)
        )
        match stage_obj.code:
            case 'initial':
                RuntimeLogHandler(stage_obj=stage_obj, actor_obj=self.runtime_obj.doc_employee_created).log_create_doc()
            case 'approved':
                RuntimeLogHandler(
                    stage_obj=stage_obj, actor_obj=self.runtime_obj.doc_employee_created
                ).log_approval_doc()
            case 'completed':
                RuntimeLogHandler(stage_obj=stage_obj, actor_obj=self.runtime_obj.doc_employee_created).log_finish_doc()
        # create assignee and zone (task)
        assignee_created = self._create_assignee_and_zone(stage_obj=stage_obj)
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
    def get_flow_applied(cls, app_obj: models.Model) -> (bool, Workflow):
        print(app_obj)
        return True, Workflow.objects.first()

    def apply(self, app_obj: models.Model) -> Union[bool, None]:
        self.set_state_task_bg('STARTED')
        state_global = None
        state_apply, flow_apply = self.get_flow_applied(app_obj)
        if state_apply:
            if not flow_apply or not isinstance(flow_apply, Workflow):
                raise ValueError('[RuntimeStageHandler][apply] Workflow must be required when config is apply flow.')
            self.runtime_obj.flow = flow_apply
            self.runtime_obj.state = 1  # in-progress
            self.runtime_obj.save(update_fields=['flow', 'state'])
            print('FLOW: ', flow_apply, self.runtime_obj.flow)
            wait_stage = self.run_stage(workflow=flow_apply)
            if wait_stage:
                state_global = True
        else:
            self.runtime_obj.state = 3  # finish with flow is non-apply.
        self.set_state_task_bg('SUCCESS')
        return state_global


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
    def __init__(
            self,
            stage_obj: RuntimeStage,
            actor_obj: DisperseModel(app_model='hr.employee').get_model() = None,
            actor_id: Union[UUID, str] = None,
    ):
        self.stage_obj = stage_obj
        if not actor_id and not actor_obj:
            raise AttributeError('Need actor for log')
        if actor_obj:
            self.actor_obj = actor_obj
        elif actor_id:
            self.actor_obj = DisperseModel(app_model='hr.employee').get_model().objects.get(pk=actor_id)

    @classmethod
    def perform_create(cls, objs: list[RuntimeLog]):
        return RuntimeLog.objects.bulk_create(objs)

    def log_create_doc(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Create document'
        )

    def log_new_assignee(self, perform_created: bool = True):
        data = {
            "actor": self.actor_obj,
            "runtime": self.stage_obj.runtime,
            "stage": self.stage_obj,
            "kind": 2,
            "action": 0,
            "msg": 'New task'
        }
        if perform_created is True:
            return RuntimeLog.objects.create(**data)
        return RuntimeLog(**data)

    def log_approval_doc(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Approved'
        )

    def log_finish_doc(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Finish flow'
        )

    def log_action_perform(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.stage_obj.runtime,
            stage=self.stage_obj,
            kind=2,
            action=0,
            msg='Perform a action'
        )


@shared_task
def call_new_runtime(
        company_id: Union[UUID, str], doc_id: Union[UUID, str], app_code: str, task_bg_id: Union[UUID, str]
):
    return RuntimeHandler().call_new(
        company_id=company_id,
        doc_id=doc_id,
        app_code=app_code,
        task_bg_id=task_bg_id,
    )


@shared_task
def call_next_stage(runtime_id: Union[UUID, str], stage_currently_id: Union[UUID, str]):
    # get objects from arguments
    runtime_obj = Runtime.objects.get(pk=runtime_id)
    stage_currently_obj = RuntimeStage.objects.get(pk=stage_currently_id)

    # new cls call run_next
    cls_handle = RuntimeStageHandler(
        runtime_obj=runtime_obj,
    )
    return cls_handle.run_next(
        workflow=runtime_obj.flow, stage_obj_currently=stage_currently_obj
    )


@shared_task
def call_approval_task(runtime_assignee_id: RuntimeAssignee, employee_id: models.Model):
    runtime_assignee_obj = RuntimeAssignee.objects.get(pk=runtime_assignee_id)
    employee_obj = DisperseModel(app_model='hr.employee').get_model().objects.get(pk=employee_id)
    return RuntimeHandler().approval(rt_assignee=runtime_assignee_obj, employee_assignee_obj=employee_obj)
