import json

from django.db import models

from apps.shared import MasterDataAbstractModel, TASK_IN_OPTION, TASK_OUT_OPTION

__all__ = ['OpportunityTaskConfig']


class OpportunityTaskConfig(MasterDataAbstractModel):
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='opportunity_task_config_company',
    )
    list_status = models.JSONField(
        default=list,
        verbose_name='List of task status data backup',
        help_text=json.dumps(
            [
                {'name': 'To do', 'translate_name': 'Việc cần làm', 'id': 'id_str', 'order': 1},
                {'name': 'In Progress', 'translate_name': 'đang làm', 'id': 'id_str', 'order': 2},
                {'name': 'Completed', 'translate_name': 'đã hoàn thành', 'id': 'id_str', 'order': 3},
                {'name': 'Pending', 'translate_name': 'tạm ngưng', 'id': 'id_str', 'order': 4},
            ], ensure_ascii=False
        ).encode('utf8')
    )
    is_edit_date = models.BooleanField(
        default=False,
        verbose_name='Assignee can edit start/end date'
    )
    is_edit_est = models.BooleanField(
        default=False,
        verbose_name='Assignee can edit Estimate'
    )
    is_in_assign = models.BooleanField(
        default=True,
        verbose_name='Assigner can assign task to everyone'
    )
    in_assign_opt = models.IntegerField(
        default=0,
        verbose_name='option assign in opp/pro',
        choices=TASK_IN_OPTION
    )
    is_out_assign = models.BooleanField(
        default=True,
        verbose_name='Assigner can assign task to everyone'
    )
    out_assign_opt = models.IntegerField(
        default=0,
        verbose_name='option assign out opp/pro',
        choices=TASK_OUT_OPTION
    )

    class Meta:
        verbose_name = 'Opportunity task config'
        verbose_name_plural = 'Opportunity task config'
        default_permissions = ()
        permissions = ()
