import json

from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, MasterDataAbstractModel
OVERTIME_TYPE = (
    (0, 'post_shift'),
    (1, 'weekend'),
    (2, 'holiday'),
    (3, 'other'),
)


class OvertimeRequest(DataAbstractModel):
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
        default=dict,
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
    reason = models.CharField(
        max_length=250,
        verbose_name="remarks",
        null=True,
        blank=True
    )
    date_list = models.JSONField(
        verbose_name="date list of employee selected for OT",
        default=list,
        help_text=json.dumps(
            [
                {"date": "2025-12-22", "type": "0", "shift": {}, },
                {"date": "2025-12-18", "type": "1", "shift": {}, },
                {"date": "2025-12-16", "type": "1", "shift": {}, },
            ]
        )
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
                        CompanyFunctionNumber.auto_gen_code_based_on_config(
                            app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                        )
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Overtime request'
        verbose_name_plural = 'Overtime request'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OTMapWithEmployeeShift(MasterDataAbstractModel):
    overtime_request = models.ForeignKey(
        OvertimeRequest,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="ot_map_with_employee_shift"
    )
    shift = models.ForeignKey(
        'attendance.ShiftInfo',
        on_delete=models.CASCADE,
        verbose_name="shift",
        related_name="ot_map_with_shift_info",
        null=True
    )
    date = models.DateField(
        help_text='Date ot selected',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employee_map_with_otmap"
    )
    type = models.IntegerField(
        default=0,
        choices=OVERTIME_TYPE,
        verbose_name="type of overtime",
    )

    class Meta:
        verbose_name = 'Overtime request map with employee'
        verbose_name_plural = 'Overtime request map with employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
