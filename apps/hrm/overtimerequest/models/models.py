import json

from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel

OVERTIME_TYPE = (
    (0, 'post_shift'),
    (1, 'weekend'),
    (2, 'holiday'),
    (3, 'other'),
)


class OvertimeRequest(DataAbstractModel):
    shift = models.ForeignKey(
        'attendance.ShiftInfo',
        on_delete=models.SET_NULL,
        verbose_name="Shift",
        null=True,
        blank=True,
        related_name='overtime_request_shift'
    )
    employee_list = models.JSONField(
        verbose_name="employee list",
        default=list,
        help_text='[uuid, uuid]'
    )
    employee_list_data = models.JSONField(
        verbose_name="employee list data",
        default=list,
        help_text=json.dumps(
            [
                {
                    'full_name': 'Nguyen Van A',
                    'group': {'id': 'uuid', 'title': 'group aaa'}
                },
                {
                    'full_name': 'Nguyen Thi B',
                    'group': {'id': 'uuid', 'title': 'group bbb'}
                }
            ]
        )
    )
    employee_created_data = models.JSONField(
        verbose_name="employee created data",
        default=list,
        help_text=json.dumps(
            {
                'id': 'uuid',
                'full_name': 'Nguyen Van A',
                'group': {'id': 'uuid', 'title': 'group aaa'}
            }
        )
    )
    employee_inherit_data = models.JSONField(
        verbose_name="employee inherit data",
        default=list,
        help_text=json.dumps(
            {
                'id': 'uuid',
                'full_name': 'Nguyen Van A',
                'group': {'id': 'uuid', 'title': 'group aaa'}
            }
        )
    )
    start_time = models.TimeField(
        verbose_name="time start OT",
    )
    end_time = models.TimeField(
        verbose_name="end time OT",
    )
    start_date = models.DateField(
        verbose_name="start date OT",
    )
    end_date = models.DateField(
        verbose_name="end date OT",
    )
    ot_type = models.IntegerField(
        verbose_name="Overtime type",
        choices=OVERTIME_TYPE,
        null=True,
        blank=True
    )
    reason = models.CharField(
        max_length=250,
        verbose_name="remarks",
        null=True,
        blank=True
    )

    def before_save(self):
        if self.employee_created and self.system_status == 1:
            self.employee_created_data = {
                'id': str(self.employee_created_id),
                'full_name': self.employee_created.get_full_name(),
                'code': self.employee_created.code,
                'group': {
                    'id': str(self.employee_created.group.id),
                    'title': self.employee_created.group.title
                } if self.employee_created.group else {}
            }
        if self.employee_inherit and self.system_status == 1:
            self.employee_inherit_data = {
                'id': str(self.employee_inherit_id),
                'full_name': self.employee_inherit.get_full_name(),
                'code': self.employee_inherit.code,
                'group': {
                    'id': str(self.employee_inherit.group.id),
                    'title': self.employee_inherit.group.title
                } if self.employee_inherit.group else {}
            }

    def save(self, *args, **kwargs):
        self.before_save()
        if self.system_status == 3:
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
                    if 'date_approved' in kwargs['update_fields']:
                        CompanyFunctionNumber.auto_gen_code_based_on_config('overtimerequest', True, self, kwargs)
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Overtime request'
        verbose_name_plural = 'Overtime request'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
