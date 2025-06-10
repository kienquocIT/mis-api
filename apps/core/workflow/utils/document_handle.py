import logging
from typing import Union

from django.db import models, transaction
from django.utils import timezone

from apps.core.mailer.tasks import send_mail_workflow
from apps.core.process.utils import ProcessRuntimeControl
from apps.core.workflow.utils.runtime_sub import HookEventHandler
from apps.shared import (DisperseModel, call_task_background, )

logger = logging.getLogger(__name__)


class DocHandler:
    @staticmethod
    def get_app_id(obj):
        if hasattr(obj, '__class__'):
            try:
                return obj.__class__.get_app_id()
            except Exception as err:
                logger.error(
                    'Get app_id of object is error: %s - %s, %s',
                    str(getattr(obj, 'id', None)),
                    str(obj.__class__),
                    str(err)
                )
        return None

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

    def filter_first_obj(self, default_filter: dict) -> Union[models.Model, None]:
        first_obj = self.model.objects.filter(**default_filter).first()
        return first_obj if first_obj else None

    @classmethod
    def force_in_progress_with_runtime(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            system_status = 1  # created
            ProcessRuntimeControl.update_status_of_doc(
                app_id=cls.get_app_id(obj),
                doc_id=obj.id,
                date_now=timezone.now(),
                status=system_status,
            )
            return True
        return False

    @classmethod
    def force_pending_with_runtime(cls, runtime_obj):
        return cls.force_in_progress_with_runtime(runtime_obj=runtime_obj)

    @classmethod
    def force_added(cls, obj):
        system_status = 2
        setattr(obj, 'system_status', system_status)  # added
        obj.save(update_fields=['system_status'])
        ProcessRuntimeControl.update_status_of_doc(
            app_id=cls.get_app_id(obj),
            doc_id=obj.id,
            date_now=timezone.now(),
            status=system_status,
        )
        return True

    @classmethod
    def force_added_with_runtime(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            return cls.force_added(obj)
        return False

    @classmethod
    def force_finish(cls, obj):
        system_status = 3
        setattr(obj, 'system_status', system_status)  # finish
        setattr(obj, 'date_approved', timezone.now())  # date finish (approved)
        update_fields = ['system_status', 'date_approved']
        if hasattr(obj, 'is_change'):
            if obj.is_change is False:
                setattr(obj, 'document_root_id', obj.id)  # store obj.id to document_root_id for change
                setattr(obj, 'document_change_order', 1)  # set document_change_order = 1 (document root)
                update_fields.append('document_root_id')
                update_fields.append('document_change_order')
        try:
            with transaction.atomic():
                # cancel document root or previous document before finish new document
                DocHandler.force_cancel_doc_previous(document_change=obj)
                # save finish
                obj.save(update_fields=update_fields)
        except Exception as err:
            print(err)
            return False
        ProcessRuntimeControl.update_status_of_doc(
            app_id=cls.get_app_id(obj),
            doc_id=obj.id,
            date_now=timezone.now(),
            status=system_status,
        )
        return True

    @classmethod
    def force_return_owner(cls, runtime_obj, remark):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            HookEventHandler(runtime_obj=runtime_obj).push_notify_return_owner(doc_obj=obj, remark=remark)
            # send mail
            if hasattr(obj, 'employee_inherit_id'):
                DocHandler.send_mail(emp_id=obj.employee_inherit_id, runtime_obj=runtime_obj, workflow_type=1)
            return True
        return False

    @classmethod
    def force_finish_with_runtime(cls, runtime_obj, approved_or_rejected='approved'):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            match approved_or_rejected:
                case 'approved':
                    DocHandler.force_finish(obj=obj)
                case 'rejected':
                    system_status = 4
                    setattr(obj, 'system_status', system_status)  # cancel with reject
                    obj.save(update_fields=['system_status'])
                    ProcessRuntimeControl.update_status_of_doc(
                        app_id=cls.get_app_id(obj),
                        doc_id=obj.id,
                        date_now=timezone.now(),
                        status=system_status,
                    )
            HookEventHandler(runtime_obj=runtime_obj).push_notify_end_workflow(
                doc_obj=obj, end_type=0 if approved_or_rejected == 'approved' else 1
            )
            # send mail
            if hasattr(obj, 'employee_inherit_id'):
                workflow_type = 2 if approved_or_rejected == 'approved' else 3
                DocHandler.send_mail(
                    emp_id=obj.employee_inherit_id, runtime_obj=runtime_obj, workflow_type=workflow_type
                )
            return True
        return False

    @classmethod
    def force_update_current_stage(cls, runtime_obj, stage_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            setattr(obj, 'current_stage', stage_obj)
            setattr(obj, 'current_stage_title', stage_obj.title)
            obj.save(update_fields=['current_stage', 'current_stage_title'])
            return True
        return False

    @classmethod
    def force_update_next_node_collab(cls, runtime_obj, next_association_id, next_node_collab_id):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            setattr(obj, 'next_association_id', next_association_id)
            setattr(obj, 'next_node_collab_id', next_node_collab_id)
            obj.save(update_fields=['next_association_id', 'next_node_collab_id'])
            return True
        return False

    @classmethod
    def get_next_association(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            if hasattr(obj, 'next_association'):
                return obj.next_association
        return None

    @classmethod
    def get_next_node_collab_id(cls, runtime_obj):
        obj = DocHandler(runtime_obj.doc_id, runtime_obj.app_code).get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if obj:
            if hasattr(obj, 'next_node_collab_id'):
                return obj.next_node_collab_id
        return None

    @classmethod
    def force_cancel_doc_previous(cls, document_change):
        doc_previous = DocHandler.get_doc_previous(document_change=document_change)
        if doc_previous:
            system_status = 4
            setattr(doc_previous, 'system_status', system_status)
            setattr(doc_previous, 'is_change', True)
            doc_previous.save(update_fields=['system_status', 'is_change'])
            ProcessRuntimeControl.update_status_of_doc(
                app_id=cls.get_app_id(doc_previous),
                doc_id=doc_previous.id,
                date_now=timezone.now(),
                status=system_status,
            )
        return True

    @classmethod
    def get_doc_previous(cls, document_change):
        document_target = None
        if all(hasattr(document_change, attr) for attr in ('document_change_order', 'document_root_id')):
            if document_change.document_change_order and document_change.document_root_id:
                if document_change.document_change_order == 1:
                    document_target = DocHandler(
                        document_change.document_root_id, document_change._meta.label_lower
                    ).get_obj(
                        default_filter={
                            'tenant_id': document_change.tenant_id,
                            'company_id': document_change.company_id
                        }
                    )
                if document_change.document_change_order > 1:
                    document_target = DocHandler(None, document_change._meta.label_lower).filter_first_obj(
                        default_filter={
                            'tenant_id': document_change.tenant_id, 'company_id': document_change.company_id,
                            'document_change_order': document_change.document_change_order - 1,
                            'document_root_id': document_change.document_root_id,
                        }
                    )
        return document_target

    @classmethod
    def send_mail(cls, emp_id, runtime_obj, workflow_type):
        emp_obj = DocHandler(emp_id, 'hr.Employee').get_obj(
            default_filter={'tenant_id': runtime_obj.tenant_id, 'company_id': runtime_obj.company_id}
        )
        if emp_obj:
            if hasattr(emp_obj, 'user_id'):
                mail_config_cls = DisperseModel(app_model='mailer.MailConfig').get_model()
                if mail_config_cls and hasattr(mail_config_cls, 'get_config'):
                    config_obj = mail_config_cls.get_config(
                        tenant_id=runtime_obj.tenant_id, company_id=runtime_obj.company_id
                    )
                    if config_obj and config_obj.is_active:
                        call_task_background(
                            my_task=send_mail_workflow,
                            **{
                                'tenant_id': str(runtime_obj.tenant_id),
                                'company_id': str(runtime_obj.company_id),
                                'user_id': str(emp_obj.user_id) if emp_obj.user_id else None,
                                'employee_id': str(emp_id),
                                'runtime_id': str(runtime_obj.id),
                                'workflow_type': workflow_type,
                            }
                        )
        return True
