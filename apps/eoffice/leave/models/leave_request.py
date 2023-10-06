import json
from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = ['LeaveRequestDateListRegister', 'LeaveRequest']


class LeaveRequestDateListRegister(SimpleAbstractModel):
    order = models.IntegerField(
        null=True,
        verbose_name='index row in date list',
        help_text='index row in date list'
    )
    leave_type = models.ForeignKey(
        'leave.LeaveType',
        on_delete=models.CASCADE,
        related_name="leave_request_date_list_frk_leave_type",
        null=True,
        help_text='foreign key to leave type model'
    )
    date_from = models.DateField(
        null=True,
        verbose_name='Date from leave',
        help_text='date register from'
    )
    morning_shift_f = models.BooleanField(
        verbose_name='morning or afternoon shift of date from',
        help_text='morning or afternoon shift of date from'
    )
    date_to = models.DateField(
        null=True,
        verbose_name='Date to leave',
        help_text='date to register to'
    )
    morning_shift_t = models.BooleanField(
        verbose_name='morning or afternoon shift of date to',
        help_text='morning or afternoon shift of date to'
    )
    subtotal = models.FloatField(
        verbose_name='total day per line detail',
        help_text='total day of record',
        null=True,
    )
    remark = models.CharField(
        verbose_name='descriptions',
        max_length=500,
        null=True,
    )
    leave = models.ForeignKey(
        'leave.LeaveRequest',
        on_delete=models.CASCADE,
        related_name="leave_request_date_leave",
        null=False,
        help_text='Leave request ID'
    )

    class Meta:
        verbose_name = 'Leave Config of Company'
        verbose_name_plural = 'Leave Config of Company'
        ordering = ('-order',)
        default_permissions = ()
        permissions = ()


class LeaveRequest(DataAbstractModel):
    request_date = models.DateField(
        null=True,
        verbose_name='request date'
    )
    detail_data = models.JSONField(
        default=list,
        null=True,
        help_text=json.dumps(
            [
                {
                    'order': 0,
                    'leave_type': 'bce75617-b78e4-1258-689d-caf5ebaa7c6',
                    'date_from': '2023-08-12',
                    'morning_shift_f': True,
                    'date_to': '2023-08-12',
                    'morning_shift_t': False,
                    'subtotal': 1,
                    'remark': 'lorem ipsum'
                },
            ]
        )
    )
    start_day = models.DateField(
        null=True,
        verbose_name='Date start of list request'
    )
    total = models.FloatField(
        verbose_name='total',
        help_text='total day of request',
        null=True
    )

    def create_code(self):
        # auto create code (temporary)
        task = LeaveRequest.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        if not self.code:
            char = "L"
            temper = task + 1
            code = f"{char}{temper:03d}"
            self.code = code

    def before_save(self):
        self.create_code()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Leave request'
        verbose_name_plural = 'Leave request'
        ordering = ('-start_day',)
        default_permissions = ()
        permissions = ()
