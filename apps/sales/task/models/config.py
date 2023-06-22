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
        verbose_name='Delivery Config',
        help_text=json.dumps(
            [
                {'name': 'Todo', 'translate_name': 'Việc cần làm'},
                {'name': 'In Progress', 'translate_name': 'đang làm'},
                {'name': 'Completed', 'translate_name': 'đã hoàn thành'},
                {'name': 'Pending', 'translate_name': 'tạm ngưng'},
            ], ensure_ascii=False
        ).encode('utf8')
    )

    class Meta:
        verbose_name = 'Task Config of Company'
        verbose_name_plural = 'Task Config of Company'
        default_permissions = ()
        permissions = ()
