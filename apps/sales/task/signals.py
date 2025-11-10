from uuid import UUID
import datetime

from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from apps.core.mailer.tasks import prepare_send_mail_new_task
from apps.sales.project.tasks import create_project_news
from apps.sales.task.tasks import opp_task_summary
from apps.sales.task.models import OpportunityTask, OpportunityTaskSummaryDaily
from apps.sales.task.tasks import log_task_status
from apps.shared import call_task_background, Caching
from apps.shared.translations.sales import SaleTask


class OppTaskSummaryHandler:
    @property
    def key_cache(self):
        return f'opp_task_daily_{str(self.employee_id)}_{timezone.now().strftime("%Y_%m_%d")}'

    @classmethod
    def report_set_cache(cls, cls_cache: Caching, key, value):
        date_now = timezone.now()
        # timeout is next day with time 00:00:01.0000
        timeout = (
                datetime.datetime.combine(
                    date_now.date() + datetime.timedelta(days=1),
                    datetime.time(second=1)
                ) - date_now
        ).seconds
        return cls_cache.set(key=key, value=value, timeout=timeout)

    def __init__(self, employee_id):
        self.employee_id = employee_id

    def get_obj(self):
        cls_cache = Caching()
        key_cache = self.key_cache
        value_cache = cls_cache.get(key=key_cache)
        if isinstance(value_cache, self.__class__):
            if getattr(value_cache, 'state', 0) == 1:
                return value_cache
            return None
        else:
            try:
                obj = OpportunityTaskSummaryDaily.objects.get(employee_id=self.employee_id)
            except OpportunityTaskSummaryDaily.DoesNotExist:
                OpportunityTaskSummaryDaily.objects.create(
                    employee_id=self.employee_id,
                    state=0,
                    updated_at=timezone.now(),
                )
                call_task_background(
                    my_task=opp_task_summary,
                    **{
                        'employee_id': self.employee_id,
                    }
                )
            else:
                if obj.updated_at.date() == timezone.now().date():
                    if obj.state == 1:
                        self.report_set_cache(cls_cache=cls_cache, key=key_cache, value=obj)
                        return obj
                    return None
                else:
                    obj.state = 0
                    obj.updated_at = timezone.now()
                    obj.save(update_fields=['state', 'updated_at'])
                    call_task_background(
                        my_task=opp_task_summary,
                        **{
                            'employee_id': self.employee_id,
                        }
                    )
        return None

    @classmethod
    def summary_report(cls, obj: OpportunityTaskSummaryDaily):
        return obj.get_detail()


@receiver(pre_save, sender=OpportunityTask)
def track_employee_before_save(sender, instance, **kwargs):
    """Track old employee_inherit_id trước khi save"""
    try:
        old_values = instance.get_old_value(['employee_inherit_id'])
        instance._old_employee_inherit_id = old_values.get('employee_inherit_id')
    except Exception as e:
        print('error get old value', e)
        instance._old_employee_inherit_id = None


@receiver(post_save, sender=OpportunityTask)
def opp_task_changes(sender, instance, created, **kwargs):
    if instance.employee_inherit_id and instance.task_status:
        # Detect assignee change
        old_employee_id = getattr(instance, '_old_employee_inherit_id', None)
        is_assignee_changed = (
                not created and
                old_employee_id is not None and
                old_employee_id != instance.employee_inherit_id
        )
        # Determine status
        if created:
            status = 'ASSIGN_TASK'
        elif is_assignee_changed:
            status = 'ASSIGN_TASK'  # ✅ Detect assignee change
        elif instance.percent_completed in ['100', 100]:
            status = "FINISH_TASK"
        else:
            status = instance.task_status.title
        call_task_background(
            my_task=log_task_status,
            **{
                'task_id': str(instance.id),
                'tenant_id': str(instance.tenant_id),
                'company_id': str(instance.company_id),
                'employee_inherit_id': str(instance.employee_inherit_id),
                'status': status,
                'status_translate': instance.task_status.translate_name,
                'date_changes': instance.date_modified,
                'task_color': instance.task_status.task_color,
            }
        )

        call_task_background(
            my_task=opp_task_summary,
            **{
                'employee_id': instance.employee_inherit_id,
            }
        )
        # ✅ KHÁC: Update old assignee nếu có change
        if is_assignee_changed and old_employee_id:
            call_task_background(
                my_task=opp_task_summary,
                **{'employee_id': old_employee_id}
            )

    if created:
        # resolve task data
        if instance.task_status.task_kind in [0, 1] \
                and instance.employee_created and instance.employee_inherit \
                and instance.employee_inherit.email \
                and instance.employee_created.email != instance.employee_inherit.email:
            # check nếu người tạo và người nhận có email và 2 user này ko cùng 1 người
            task_kwargs = {
                'tenant_id': str(instance.tenant_id),
                'company_id': str(instance.company_id),
                'doc_id': str(instance.id),
                'doc_app': 'task.opportunitytask',
                'employee_inherit_full_name': instance.employee_inherit.get_full_name(),
                'employee_inherit_email': instance.employee_inherit.email,
                'employee_created': instance.employee_created.get_full_name(),
            }
            if len(task_kwargs) > 0:
                call_task_background(
                    my_task=prepare_send_mail_new_task,
                    **{
                        'data_list': task_kwargs
                    }
                )
            print('finish run send mail new task')


@receiver(post_save, sender=OpportunityTaskSummaryDaily)
def post_save_opp_task_summary(sender, instance, created, **kwargs):
    summary_obj = OppTaskSummaryHandler(employee_id=instance.employee_id)
    summary_obj.report_set_cache(
        cls_cache=Caching(),
        key=summary_obj.key_cache,
        value=instance,
    )


@receiver(post_delete, sender=OpportunityTask)
def post_delete_opp_task(sender, instance, **kwargs):
    # create news feed
    if instance.project:
        call_task_background(
            my_task=create_project_news,
            **{
                'project_id': str(instance.project.id),
                'employee_inherit_id': str(instance.employee_inherit.id),
                'employee_created_id': str(instance.employee_created.id),
                'application_id': str('e66cfb5a-b3ce-4694-a4da-47618f53de4c'),
                'document_id': str(instance.id),
                'document_title': str(instance.title),
                'title': SaleTask.DELETED_A,
                'msg': '',
            }
        )
    if instance.parent_n:
        task_parent = instance.parent_n
        if task_parent.child_task_count > 0:
            task_parent.child_task_count -= 1
            task_parent.save(update_fields=['child_task_count'])
