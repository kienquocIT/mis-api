import json

from django.db import models

from apps.shared import MasterDataAbstractModel


class ContractTemplate(MasterDataAbstractModel):
    template = models.TextField(blank=True)
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='contract_template_map_app'
    )
    members = models.JSONField(
        default=list,
        help_text='["employee_01_id", "employee_01_id"]',
        verbose_name='members assignee',
    )
    signatures = models.JSONField(
        default=dict,
        verbose_name='signatures parameter of contract',
        help_text=json.dumps(
            {
                'sign_01': ['emp_01_id', 'emp_02_id'],
                'sign_02': ['emp_01_id', 'emp_02_id'],
            }
        )
    )

    class Meta:
        verbose_name = 'Contract template list'
        verbose_name_plural = 'get contract template list'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
