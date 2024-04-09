import logging
from datetime import timedelta
from typing import Union
from uuid import UUID

from django.db import models
from django.utils import timezone
from rest_framework import serializers

from apps.core.log.tasks import (force_log_activity,)
from apps.core.workflow.utils.runtime_sub import WFValidateHandler
from apps.shared import (DisperseModel, MAP_FIELD_TITLE, call_task_background,)
from apps.core.workflow.models import (Runtime, RuntimeLog,)

logger = logging.getLogger(__name__)

__all__ = [
    'DocHandler',
    'RuntimeAfterFinishHandler',
    'RuntimeAFLogHandler',
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
        setattr(obj, 'date_approved', timezone.now())  # date finish (approved)
        obj.save(update_fields=['system_status', 'date_approved'])
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
                    setattr(obj, 'date_approved', timezone.now())  # date finish (approved)
                    obj.save(update_fields=['system_status', 'date_approved'])
                case 'rejected':
                    setattr(obj, 'system_status', 4)  # cancel with reject
                    obj.save(update_fields=['system_status'])
            return True
        return False

    @classmethod
    def force_open_change_request(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            # check referenced
            check = WFValidateHandler.is_object_referenced(obj=obj)
            if check is False:
                return True
            raise serializers.ValidationError({'detail': "This document is referenced by another document"})
        return False

    @classmethod
    def force_reject(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            # check referenced
            check = WFValidateHandler.is_object_referenced(obj=obj)
            if check is False:
                setattr(obj, 'system_status', 4)  # cancel with reject
                obj.save(update_fields=['system_status'])
            else:
                raise serializers.ValidationError({'detail': "This document is referenced by another document"})
            return True
        return False

    @classmethod
    def force_update_current_stage(cls, runtime_obj, stage_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            setattr(obj, 'current_stage', stage_obj)
            setattr(obj, 'current_stage_title', stage_obj.title)
            obj.save(update_fields=['current_stage', 'current_stage_title'])
            return True
        return False

    @classmethod
    def force_update_next_node_collab(cls, runtime_obj, next_node_collab_id):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            setattr(obj, 'next_node_collab_id', next_node_collab_id)
            obj.save(update_fields=['next_node_collab_id'])
            return True
        return False

    @classmethod
    def get_next_node_collab_id(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={
                'tenant_id': runtime_obj.tenant_id,
                'company_id': runtime_obj.company_id,
            }
        )
        if obj:
            if hasattr(obj, 'next_node_collab_id'):
                return obj.next_node_collab_id
        return None


class RuntimeAfterFinishHandler:
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
    def action_perform_after_finish(
            cls,
            runtime_obj: Runtime,
            action_code: int,
            # data_cr: dict,
    ) -> bool:
        if runtime_obj:
            # WORKFLOW_ACTION = {
            #     0: WorkflowMsg.ACTION_CREATE,
            #     1: WorkflowMsg.ACTION_APPROVED,
            #     2: WorkflowMsg.ACTION_REJECT,
            #     3: WorkflowMsg.ACTION_RETURN,
            #     4: WorkflowMsg.ACTION_RECEIVE,
            #     5: WorkflowMsg.ACTION_TODO,
            # }
            match action_code:
                case 1:  # open cr
                    DocHandler.force_open_change_request(runtime_obj=runtime_obj)
                case 2:  # reject
                    DocHandler.force_reject(runtime_obj=runtime_obj)
                case 3:  # save cr
                    ...
            return True
        return False


class RuntimeAFLogHandler:
    @staticmethod
    def get_correct_date_log(runtime_obj: Runtime, seconds_compare_and_add: int):
        delta_time = timezone.now() - runtime_obj.date_created
        if delta_time.seconds > seconds_compare_and_add:
            return timezone.now()
        return timezone.now() + timedelta(seconds=seconds_compare_and_add)

    def __init__(
            self,
            runtime_obj: Runtime,
            actor_obj: DisperseModel(app_model='hr.employee').get_model() = None,
            actor_id: Union[UUID, str] = None,
            is_system: bool = False,
            remark: str = '',
    ):
        self.is_system = is_system
        self.runtime_obj = runtime_obj
        if not actor_id and not actor_obj:
            self.actor_obj = None
        elif actor_obj:
            self.actor_obj = actor_obj
        elif actor_id:
            self.actor_obj = DisperseModel(app_model='hr.employee').get_model().objects.get(pk=actor_id)
        else:
            self.actor_obj = None
        self.remark = remark

    @classmethod
    def perform_create(cls, objs: list[RuntimeLog]):
        return RuntimeLog.objects.bulk_create(objs)

    def log_reject_task(self):
        call_task_background(
            force_log_activity,
            **{
                'tenant_id': self.runtime_obj.tenant_id,
                'company_id': self.runtime_obj.company_id,
                'date_created': timezone.now(),
                'doc_id': self.runtime_obj.doc_id,
                'doc_app': self.runtime_obj.app_code,
                'automated_logging': False,
                'user_id': None,
                'employee_id': self.actor_obj.id,
                'msg': "Rejected by owner",
                'task_workflow_id': None,
            },
        )
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.runtime_obj,
            kind=2,
            action=0,
            msg="Rejected by owner",
            is_system=self.is_system,
        )

    def log_finish_station_doc(self, final_state_num=1, msg_log=''):
        final_state_choices = {
            1: 'Approved',
            2: 'Reject',
        }
        runtime_obj = self.runtime_obj
        if runtime_obj:
            call_task_background(
                force_log_activity,
                **{
                    'tenant_id': runtime_obj.tenant_id,
                    'company_id': runtime_obj.company_id,
                    'date_created': RuntimeAFLogHandler.get_correct_date_log(runtime_obj, 9),
                    'doc_id': runtime_obj.doc_id,
                    'doc_app': runtime_obj.app_code,
                    'automated_logging': True,
                    'msg': msg_log,
                },
            )
        return RuntimeLog.objects.create(
            # actor=self.actor_obj,
            actor=None,
            runtime=self.runtime_obj,
            kind=2,
            action=0,
            msg='Finish flow' + f' with {final_state_choices[final_state_num]}',
            is_system=self.is_system,
        )

    def log_action_perform(self):
        return RuntimeLog.objects.create(
            actor=self.actor_obj,
            runtime=self.runtime_obj,
            kind=2,
            action=0,
            msg='Perform a action',
            is_system=self.is_system,
        )
