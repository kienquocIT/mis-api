import json

from django.db import models

from apps.shared import MasterDataAbstractModel

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
    user_allow_group_handle = models.JSONField(
        default=dict,
        verbose_name='List of employee data backup',
        help_text=json.dumps(
            {
                'uuid': {
                    'id': 'uuid4', 'full_name': 'Nguyen van A',
                    'group': {'id': 'uuid4', 'title': 'group received task group'}
                },
                'uuid2': {
                    'id': 'uuid4', 'full_name': 'Nguyen van B',
                    'group': {'id': 'uuid4', 'title': 'group received task group'}
                },
            }, ensure_ascii=False
        ).encode('utf8')
    )

    class Meta:
        verbose_name = 'Opportunity task config'
        verbose_name_plural = 'Opportunity task config'
        default_permissions = ()
        permissions = ()
