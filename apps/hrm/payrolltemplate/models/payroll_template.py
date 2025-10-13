import json

from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel

from .payroll_attribute import DATA_TYPE, DATA_SOURCE


class PayrollTemplate(DataAbstractModel):
    department_applied = models.ManyToManyField(
        'hr.Group',
        through='SalaryTemplateEmployeeGroup',
        symmetrical=False,
        related_name='group_payrolltemplate_department_applied'
    )
    department_applied_data = models.JSONField(
        default=list,
        null=True,
        verbose_name='Save department data',
        help_text=json.dumps([
            {'id': 'uuid', 'title': 'name', 'code': 'COD'},
            {'id': 'uuid', 'title': 'name', 'code': 'COD'},
        ])
    )
    remarks = models.TextField(blank=True)
    attribute_list = models.JSONField(
        default=list,
        null=True,
        verbose_name='Save department data',
        help_text=json.dumps([
            {
                'name': 'attr name', 'code': 'attr_code', 'type': DATA_TYPE, 'source': DATA_SOURCE, 'formula': 'str',
                'mandatory': True, 'order': 0
            },
            {
                'name': 'attr name', 'code': 'attr_code', 'type': DATA_TYPE, 'source': DATA_SOURCE, 'formula': 'str',
                'mandatory': True, 'order': 1
            },
        ])
    )

    def save(self, *args, **kwargs):
        if self.system_status == 3:
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
                    if 'date_approved' in kwargs['update_fields']:
                        CompanyFunctionNumber.auto_gen_code_based_on_config('payrolltemplate', True, self, kwargs)
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Payroll template'
        verbose_name_plural = 'Payroll template'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class SalaryTemplateEmployeeGroup(SimpleAbstractModel):
    salary_template = models.ForeignKey(
        PayrollTemplate, on_delete=models.CASCADE,
        related_name='salarytemplate_map_employee_group'
    )
    department_applied = models.ForeignKey(
        'hr.Group', on_delete=models.CASCADE, related_name='group_map_salarytemplate'
    )

    class Meta:
        verbose_name = 'Salary template map group'
        verbose_name_plural = 'Salary template map with employee group'
        ordering = ()
        default_permissions = ()
        permissions = ()
