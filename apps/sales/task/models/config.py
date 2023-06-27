import json

from django.db import models

from apps.shared import SimpleAbstractModel

__all__ = ['OpportunityTaskConfig']


class OpportunityTaskConfig(SimpleAbstractModel):
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

    class Meta:
        verbose_name = 'Opportunity task config'
        verbose_name_plural = 'Opportunity task config'
        default_permissions = ()
        permissions = ()
