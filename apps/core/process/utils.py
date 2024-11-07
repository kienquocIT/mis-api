__all__ = [
    'ProcessRuntimeControl',
]

from datetime import datetime
from uuid import UUID

from django.utils import timezone
from rest_framework import serializers

from apps.core.process.models import Process, ProcessStageApplication, ProcessDoc, ProcessStage
from apps.core.process.msg import ProcessMsg
from apps.shared import TypeCheck


class ProcessRuntimeControl:
    @classmethod
    def check_application_state_done(cls, stage_app_obj: ProcessStageApplication) -> bool or None:
        if stage_app_obj.max == "n":
            return stage_app_obj.was_done
        try:
            max_num = int(stage_app_obj.max)
        except ValueError:
            return None
        return stage_app_obj.amount >= max_num

    @classmethod
    def check_application_state_add_new(cls, stage_app_obj: ProcessStageApplication) -> bool or None:
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

    def __init__(self, process_obj: Process, key_raise_error: str = 'process'):
        self.key_raise_error: str = key_raise_error
        self.process_obj: Process = process_obj

    def get_application(self, app_id: UUID or str):
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

    def check_opp(self, opp_id) -> True or serializers.ValidationError:
        if opp_id != self.process_obj.opp_id:
            raise serializers.ValidationError({self.key_raise_error: ProcessMsg.OPP_NOT_MATCH})
        return True

    def validate_process(self, app_id: UUID or str, opp_id: UUID or str = None) -> bool or serializers.ValidationError:
        self.check_opp(opp_id=opp_id)
        app_obj = self.get_application(app_id=app_id)
        if app_obj and isinstance(app_obj, ProcessStageApplication):
            if self.check_application_state_add_new(stage_app_obj=app_obj):
                return True
            raise serializers.ValidationError({self.key_raise_error: ProcessMsg.DOCUMENT_QUALITY_IS_FULL})
        raise serializers.ValidationError({self.key_raise_error: ProcessMsg.APPLICATION_NOT_SUPPORT})

    def play_process(self) -> Process:
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
            for app_config in stage_config.get('application', []):
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
                )
            if idx == 0:  # loop play with zero, 1 is first user stages
                self.process_obj.stage_current = stage_obj
        self.process_obj.save(update_fields=['stage_current'])
        self.check_stages_current()
        return self.process_obj

    def register_doc(
            self,
            app_id: UUID or str,
            doc_id: UUID or str,
            doc_title: str,
            employee_created_id: UUID or str,
            date_created: datetime,
    ):
        stage_app_obj = self.get_application(app_id=app_id)
        if stage_app_obj and self.check_application_state_add_new(stage_app_obj):
            ProcessDoc.objects.create(
                tenant=self.process_obj.tenant,
                company=self.process_obj.company,
                process=self.process_obj,
                stage_app=stage_app_obj,
                doc_id=doc_id,
                title=doc_title,
                employee_created_id=employee_created_id,
                date_created=date_created,
            )
            stage_app_obj.amount_count(commit=True)
            self.check_stages_current(from_stages_app=stage_app_obj)
            return stage_app_obj
        return None

    def finish_process(self):
        self.process_obj.stage_current.was_done = True
        self.process_obj.stage_current.date_done = timezone.now()
        self.process_obj.stage_current.save(update_fields=['was_done', 'date_done'])

        self.process_obj.was_done = True
        self.process_obj.date_done = timezone.now()
        self.process_obj.stage_current = None
        self.process_obj.save(update_fields=['was_done', 'date_done', 'stage_current'])
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
        return self.check_stages_current()

    def check_stages_current(self, from_stages_app: ProcessStageApplication = None):
        if self.process_obj:
            if self.process_obj.stage_current:
                stage_current = self.process_obj.stage_current

                # update app
                if isinstance(from_stages_app, ProcessStageApplication):
                    self.update_stages_app(stage_app_obj=from_stages_app)

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
                # call next when the stages is not system
                return self.next_stage_current()
        return False

    def update_stages_app(self, stage_app_obj: ProcessStageApplication):
        if stage_app_obj.was_done is False:
            if self.check_application_state_done(stage_app_obj):
                stage_app_obj.was_done = True
                stage_app_obj.date_done = timezone.now()
                stage_app_obj.save(update_fields=['was_done', 'date_done'])
        return stage_app_obj.was_done
