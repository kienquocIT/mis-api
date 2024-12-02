__all__ = [
    'ProcessRuntimeControl',
]

import logging
from datetime import datetime
from uuid import UUID

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, exceptions

from apps.core.process.models import (
    Process, ProcessStageApplication, ProcessDoc, ProcessStage, ProcessConfiguration,
    ProcessMembers, ProcessActivity,
)
from apps.core.process.msg import ProcessMsg
from apps.shared import TypeCheck, DisperseModel

logger = logging.getLogger(__name__)


class ProcessRuntimeControl:  # pylint: disable=R0904
    @classmethod
    def approved_amount(cls, stage_app_obj: ProcessStageApplication):
        return ProcessDoc.objects.filter(
            stage_app=stage_app_obj,
            system_status__in=ProcessDoc.APPROVED_STATUS,
        ).count()

    @classmethod
    def check_application_auto_state_done(cls, stage_app_obj: ProcessStageApplication) -> bool or None:
        # approved >= max : auto done
        # min < approved < max : allow call done
        approved_amount = cls.approved_amount(stage_app_obj=stage_app_obj)
        if stage_app_obj.max == "n":
            return stage_app_obj.was_done
        try:
            max_num = int(stage_app_obj.max)
        except ValueError:
            return None
        return approved_amount >= max_num

    @classmethod
    def check_application_can_state_done(cls, stage_app_obj: ProcessStageApplication) -> bool or None:
        # approved >= max : auto done
        # min < approved < max : allow call done
        approved_amount = cls.approved_amount(stage_app_obj=stage_app_obj)
        if stage_app_obj.was_done:
            return False
        try:
            min_num = int(stage_app_obj.min)
        except ValueError:
            return None
        return approved_amount >= min_num

    @classmethod
    def check_application_state_add_new(cls, stage_app_obj: ProcessStageApplication) -> bool or None:
        if not stage_app_obj.stage:
            # stage app global
            pass
        elif stage_app_obj.stage.order_number > stage_app_obj.process.stage_current.order_number:
            # deny create for stages is coming!
            return False

        if stage_app_obj.max == "n":
            return True
        try:
            max_num = int(stage_app_obj.max)
        except ValueError:
            return None
        return stage_app_obj.amount < max_num

    @classmethod
    def get_process_obj(cls, process_id: UUID or str, key_raise_error: str = 'process'):
        if process_id and TypeCheck.check_uuid(process_id):
            try:
                process_obj = Process.objects.get_current(fill__tenant=True, fill__company=True, pk=process_id)
            except Process.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        key_raise_error: ProcessMsg.PROCESS_NOT_FOUND
                    }
                )
            return process_obj
        raise serializers.ValidationError(
            {
                key_raise_error: ProcessMsg.PROCESS_NOT_FOUND
            }
        )

    @classmethod
    def get_process_stage_app(
            cls, stage_app_id: UUID or str, app_id: UUID or str, key_raise_error: str = 'process_stage_app'
    ):
        if stage_app_id and TypeCheck.check_uuid(stage_app_id):
            try:
                return ProcessStageApplication.objects.get_current(
                    fill__tenant=True, fill__company=True,
                    pk=stage_app_id, application_id=app_id,
                )
            except ProcessStageApplication.DoesNotExist:
                pass
        raise serializers.ValidationError(
            {
                key_raise_error: ProcessMsg.PROCESS_STAGE_APP_NOT_FOUND
            }
        )

    @classmethod
    def create_process_from_config(cls, title: str, remark: str, config: ProcessConfiguration, **kwargs) -> Process:
        return Process.objects.create(
            title=title, remark=remark, config=config, stages=config.stages, global_app=config.global_app,
            **kwargs,
            tenant=config.tenant, company=config.company,
        )

    @classmethod
    def get_process_config(cls, process_config_id: UUID or str, for_opp: bool, key_raise_error: str = 'process_config'):
        if process_config_id and TypeCheck.check_uuid(process_config_id):
            try:
                process_config_obj = ProcessConfiguration.objects.get_current(
                    fill__tenant=True,
                    fill__company=True,
                    pk=process_config_id
                )
            except ProcessConfiguration.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        key_raise_error: ProcessMsg.PROCESS_CONFIG_NOT_FOUND
                    }
                )
            if process_config_obj.for_opp is True:
                if for_opp is False:
                    raise serializers.ValidationError(
                        {
                            key_raise_error: ProcessMsg.PROCESS_ONLY_OPP
                        }
                    )
            else:
                if for_opp is True:
                    raise serializers.ValidationError(
                        {
                            key_raise_error: ProcessMsg.PROCESS_NOT_SUPPORT_OPP
                        }
                    )
            if process_config_obj.is_active is False:
                raise serializers.ValidationError(
                    {
                        key_raise_error: ProcessMsg.PROCESS_DEACTIVATE
                    }
                )

            date_now = timezone.now()
            if process_config_obj.apply_start and process_config_obj.apply_start > date_now:
                start_str = process_config_obj.apply_start.strftime("%m/%d/%Y, %H:%M:%S")
                raise serializers.ValidationError(
                    {
                        key_raise_error: ProcessMsg.PROCESS_NOT_START.format(start_date=start_str)
                    }
                )
            if process_config_obj.apply_finish and process_config_obj.apply_finish < date_now:
                end_str = process_config_obj.apply_finish.strftime("%m/%d/%Y, %H:%M:%S")
                raise serializers.ValidationError(
                    {
                        key_raise_error: ProcessMsg.PROCESS_FINISHED.format(end_date=end_str)
                    }
                )
            return process_config_obj
        raise serializers.ValidationError(
            {
                key_raise_error: ProcessMsg.PROCESS_NOT_FOUND
            }
        )

    @classmethod
    def check_permit_process(
            cls, process_obj: Process, employee_id: UUID or str
    ) -> True or exceptions.PermissionDenied:
        if process_obj and employee_id:
            if ProcessMembers.objects.filter(process=process_obj, employee_id=employee_id).exists():
                return True
        raise exceptions.PermissionDenied

    @classmethod
    def check_permit_process_app(
            cls, stage_app: ProcessStageApplication, employee_id: UUID or str
    ) -> True or exceptions.PermissionDenied:
        if stage_app and isinstance(stage_app, ProcessStageApplication) and employee_id:
            if ProcessMembers.objects.filter(process=stage_app.process, employee_id=employee_id).exists():
                return True
        raise exceptions.PermissionDenied

    def __init__(self, process_obj: Process, key_raise_error: str = 'process'):
        self.key_raise_error: str = key_raise_error
        self.process_obj: Process = process_obj

    def get_application(self, app_id: UUID or str) -> ProcessStageApplication:
        try:
            app_obj = ProcessStageApplication.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                process=self.process_obj,
                stage=self.process_obj.stage_current,
                application_id=app_id,
            )
        except ProcessStageApplication.DoesNotExist:
            raise serializers.ValidationError(
                {
                    self.key_raise_error: ProcessMsg.APPLICATION_NOT_SUPPORT
                }
            )
        return app_obj

    def validate_process(
            self,
            process_stage_app_obj: ProcessStageApplication,
            employee_id: UUID or str = None,
            opp_id: UUID or str = None,
    ) -> bool or serializers.ValidationError:
        # permit for employee in process if fill value into employee_created_id
        if employee_id:
            self.check_permit_process_app(stage_app=process_stage_app_obj, employee_id=employee_id)

        # for add new
        if process_stage_app_obj and isinstance(process_stage_app_obj, ProcessStageApplication):
            # check stage app match with process
            if process_stage_app_obj.process != self.process_obj:
                raise serializers.ValidationError({self.key_raise_error: ProcessMsg.APPLICATION_NOT_SUPPORT})

            # check opp match with process
            if str(opp_id) != str(self.process_obj.opp_id):
                raise serializers.ValidationError({self.key_raise_error: ProcessMsg.OPP_NOT_MATCH})

            if self.check_application_state_add_new(stage_app_obj=process_stage_app_obj):
                return True
            raise serializers.ValidationError({self.key_raise_error: ProcessMsg.DOCUMENT_QUALITY_IS_FULL})
        raise serializers.ValidationError({self.key_raise_error: ProcessMsg.APPLICATION_NOT_SUPPORT})

    def add_members(self, employee_created_id: UUID = None):
        if self.process_obj.employee_created_id:
            ProcessMembers.objects.create(
                tenant=self.process_obj.tenant,
                company=self.process_obj.company,
                process=self.process_obj,
                employee=self.process_obj.employee_created,
                employee_created_id=employee_created_id,
            )
        return True

    def play_process(self) -> Process:
        self.add_members()

        for idx, stage_config in enumerate(self.process_obj.stages):
            is_system = stage_config.get('is_system', False)
            system_code = stage_config.get('system_code', None)
            stage_obj = ProcessStage.objects.create(
                tenant=self.process_obj.tenant,
                company=self.process_obj.company,
                process=self.process_obj,
                title=stage_config['title'],
                remark=stage_config.get('remark', ''),
                is_system=is_system,
                system_code=system_code,
                order_number=idx + 1,
            )
            for index, app_config in enumerate(stage_config.get('application', [])):
                ProcessStageApplication.objects.create(
                    tenant=self.process_obj.tenant,
                    company=self.process_obj.company,
                    process=self.process_obj,
                    stage=stage_obj,
                    application_id=app_config['application'],
                    title=app_config['title'],
                    remark=app_config.get('remark', ''),
                    amount=0,
                    min=app_config.get('min', '0'),
                    max=app_config.get('max', '0'),
                    order_number=index + 1,
                )
            if idx == 0:  # loop play with zero, 1 is first user stages
                self.process_obj.stage_current = stage_obj
        for index, app_config in enumerate(self.process_obj.global_app):
            ProcessStageApplication.objects.create(
                tenant=self.process_obj.tenant,
                company=self.process_obj.company,
                process=self.process_obj,
                stage=None,
                application_id=app_config['application'],
                title=app_config['title'],
                remark=app_config.get('remark', ''),
                amount=0,
                min=app_config.get('min', '0'),
                max=app_config.get('max', '0'),
                order_number=index + 1,
            )
        self.process_obj.save(update_fields=['stage_current'])
        self.log(
            title='Init process',
            code='INIT_PROCESS',
            employee_created_id=self.process_obj.employee_created_id,
        )
        self.check_stages_current()
        return self.process_obj

    def register_doc(
            self,
            process_stage_app_obj: ProcessStageApplication,
            app_id: UUID or str,
            doc_id: UUID or str,
            doc_title: str,
            employee_created_id: UUID or str,
            date_created: datetime,
    ):
        if process_stage_app_obj and isinstance(process_stage_app_obj, ProcessStageApplication):
            try:
                self.check_permit_process_app(stage_app=process_stage_app_obj, employee_id=employee_created_id)
            except exceptions.PermissionDenied:
                return False
            if str(process_stage_app_obj.application_id) == str(app_id):
                if process_stage_app_obj and self.check_application_state_add_new(process_stage_app_obj):
                    process_doc_obj = ProcessDoc.objects.create(
                        tenant=self.process_obj.tenant,
                        company=self.process_obj.company,
                        process=self.process_obj,
                        stage_app=process_stage_app_obj,
                        doc_id=doc_id,
                        title=doc_title,
                        employee_created_id=employee_created_id,
                        date_created=date_created,
                    )
                    process_stage_app_obj.amount_count(commit=True)
                    self.log(
                        title='Register documents',
                        code='REGISTER_DOCUMENT',
                        stage=process_stage_app_obj.stage,
                        doc=process_doc_obj,
                        employee_created_id=employee_created_id,
                    )
                    if process_stage_app_obj.application.is_workflow is False:
                        # auto finish when not apply workflow
                        self.update_status_of_doc(
                            app_id=process_stage_app_obj.application_id,
                            doc_id=doc_id,
                            date_now=timezone.now(),
                            status=3
                        )
                        self.log(
                            title='Auto approved',
                            code='AUTO_APPROVED',
                            stage=process_stage_app_obj.stage,
                            doc=process_doc_obj,
                            employee_created_id=employee_created_id,
                        )
                    self.check_stages_current(from_stages_app=process_stage_app_obj)
                    return process_stage_app_obj
        return None

    def finish_process(self):
        self.process_obj.stage_current.was_done = True
        self.process_obj.stage_current.date_done = timezone.now()
        self.process_obj.stage_current.save(update_fields=['was_done', 'date_done'])

        self.process_obj.was_done = True
        self.process_obj.date_done = timezone.now()
        self.process_obj.stage_current = None
        self.process_obj.save(update_fields=['was_done', 'date_done', 'stage_current'])

        self.log(
            title='Finish process',
            code='FINISH_STAGES',
            employee_created_id=self.process_obj.employee_created_id,
        )

        return True

    def next_stage_current(self):
        try:
            next_stages = ProcessStage.objects.get(
                process=self.process_obj, order_number=self.process_obj.stage_current.order_number + 1
            )
        except ProcessStage.DoesNotExist:
            return None
        self.process_obj.stage_current = next_stages
        self.process_obj.save(update_fields=['stage_current'])
        self.log(
            title='Entering new stages',
            code='NEXT_STAGES',
            stage=next_stages,
            employee_created_id=self.process_obj.employee_created_id,
        )
        return self.check_stages_current()

    def check_stages_current(self, from_stages_app: ProcessStageApplication = None):
        if self.process_obj:
            if self.process_obj.stage_current:
                # update stage app was registered doc in app
                if isinstance(from_stages_app, ProcessStageApplication):
                    self.update_stages_app(stage_app_obj=from_stages_app)

                # check current stage
                stage_current = self.process_obj.stage_current

                # counter app not done
                amount_not_done = ProcessStageApplication.objects.filter(
                    process=self.process_obj,
                    stage=stage_current,
                    was_done=False
                ).count()
                if amount_not_done != 0:
                    # keep current by have app is not done
                    return False
                # update flag done and date done of stages
                stage_current.was_done = True
                stage_current.date_done = timezone.now()

                # stages is system
                if stage_current.is_system is True:
                    if stage_current.system_code == 'start':
                        return self.next_stage_current()
                    if stage_current.system_code == 'end':
                        return self.finish_process()
                    print(f'Stages current: System code "{stage_current.system_code}" not support')
                    return False
                # call next when the stages are not system
                return self.next_stage_current()
        return False

    def update_stages_app(self, stage_app_obj: ProcessStageApplication):
        if stage_app_obj.was_done is False:
            if self.check_application_auto_state_done(stage_app_obj):
                stage_app_obj.was_done = True
                stage_app_obj.date_done = timezone.now()
                stage_app_obj.save(update_fields=['was_done', 'date_done'])
        return stage_app_obj.was_done

    @classmethod
    def get_doc_obj(cls, app_id, doc_id):
        app_cls = DisperseModel(app_model='base.application').get_model()
        try:
            app_obj = app_cls.objects.get(pk=app_id)
        except app_cls.DoesNotExist:
            logger.error('[ProcessRuntimeControl][get_doc_obj] Base App not found: app=%s', app_id)
            raise ValueError('Base App not found: ' + app_id)
        model_cls = DisperseModel(app_model=f'{app_obj.app_label}.{app_obj.model_code}').get_model()
        if model_cls and hasattr(model_cls, 'objects'):
            try:
                return model_cls.objects.get(pk=doc_id)
            except model_cls.DoesNotExist:
                logger.error(
                    f'[ProcessRuntimeControl][get_doc_obj] '  # pylint: disable=W1309
                    f'Document Object is not found doc=%s', doc_id
                )
                raise ValueError('Document Object is not found ' + doc_id)
        logger.error(
            f'[ProcessRuntimeControl][get_doc_obj] '  # pylint: disable=W1309
            f'Model Doc not found: doc=%s - app=%s', doc_id, app_id
        )
        raise ValueError('Model Doc not found: ' + doc_id + ' - ' + app_id)

    @classmethod
    def update_status_of_doc(cls, app_id, doc_id, date_now: datetime, status: int = None, skip_check_state=False):
        """
        Sync system_status of doc to ProcessDoc
        Args:
            skip_check_state:
            date_now:
            app_id:
            doc_id:
            status: This value is not provide, query get object doc then get system_status

        Returns:

        """
        if not status:
            doc_obj = cls.get_doc_obj(app_id=app_id, doc_id=doc_id)
            if doc_obj:
                status = getattr(doc_obj, 'system_status', 0)
        if isinstance(status, int):
            try:
                process_doc = ProcessDoc.objects.get(doc_id=doc_id, stage_app__application_id=app_id)
            except ProcessDoc.DoesNotExist:
                logger.error(
                    f'[ProcessRuntimeControl][update_status_of_doc] '  # pylint: disable=W1309
                    f'ProcessDoc get does not exist: app=%s - doc=%s', app_id, doc_id
                )
                return False

            # update doc
            process_doc.system_status = status
            process_doc.date_status.append(
                {
                    "status": status,
                    "datetime": date_now.strftime(
                        settings.REST_FRAMEWORK['DATETIME_FORMAT']
                    )
                }
            )
            process_doc.save(update_fields=['system_status', 'date_status'])
            # update approved amount of Stages APp
            process_doc.stage_app.amount_approved_count(commit=True)
            # check current stages status
            if not skip_check_state:
                ProcessRuntimeControl(process_obj=process_doc.process).check_stages_current(
                    from_stages_app=process_doc.stage_app
                )
            return True
        return False

    def log(self, title, code=None,employee_created_id=None, **kwargs):
        if isinstance(self.process_obj, Process):
            return ProcessActivity.objects.create(
                tenant=self.process_obj.tenant,
                company=self.process_obj.company,
                process=self.process_obj,
                title=title,
                code=code,
                employee_created_id=employee_created_id,
                **kwargs
            )
        return None
