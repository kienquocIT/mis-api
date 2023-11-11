import json
from copy import deepcopy

from django.db import models

from apps.shared import DataAbstractModel, TYPE_LIST

__all__ = ['LeaveRequestDateListRegister', 'LeaveRequest', 'LeaveAvailable', 'LeaveAvailableHistory']


class LeaveRequestDateListRegister(DataAbstractModel):
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

    def minus_available(self):
        # trừ leave available và ghi history
        type_list = self.detail_data
        for item in type_list:
            leave_type = item['leave_type']
            if leave_type['leave_type']['code'] == 'ANPY':
                get_leave = LeaveAvailable.objects.filter(
                    employee_inherit_id=self.employee_inherit_id, leave_type_id=leave_type['leave_type']['id'],
                    check_balance=True
                ).order_by('open_year')
            else:
                get_leave = LeaveAvailable.objects.get(
                    employee_inherit_id=self.employee_inherit_id, leave_type_id=leave_type['leave_type']['id'],
                    check_balance=True
                )
            if not get_leave.exists():
                continue
            leave_result = get_leave.first()
            # nếu ko phải là phép dư năm trước
            if not leave_type['leave_type']['code'] == 'ANPY':
                if item['subtotal'] > leave_result.available:
                    raise ValueError("Day off large than leave available")
                leave_result.used += item['subtotal']
                leave_result.available = leave_result.total - leave_result.used
            else:  # pylint: disable=R1724
                # lỗi ko xài else sau continue này đang logic đúng.
                if item['subtotal'] > leave_result.available:
                    odd = item['subtotal'] - deepcopy(leave_result.available)
                    leave_result.used += leave_result.available
                    leave_result.available = 0
                    leave_result.save(update_fields=['used', 'total', 'available'])

                    # create history log
                    LeaveAvailableHistory.objects.create(
                        employee_inherit=leave_result.employee_inherit,
                        tenant=leave_result.tenant,
                        company=leave_result.company,
                        leave_available=leave_result,
                        total=0,
                        action=2,
                        quantity=item['subtotal'] - odd,
                        adjusted_total=item['subtotal'] - odd,
                        remark=str(TYPE_LIST[2][1]),
                        type_arises=3
                    )
                    leave_second = get_leave[1]
                    if odd > leave_second.available:
                        raise ValueError("Day off large than leave available")
                    leave_second.used += odd
                    leave_second.available = leave_second.total - leave_second.used
                    leave_second.save(update_fields=['used', 'total', 'available'])
                    LeaveAvailableHistory.objects.create(
                        employee_inherit=leave_second.employee_inherit,
                        tenant=leave_second.tenant,
                        company=leave_second.company,
                        leave_available=leave_second,
                        total=leave_second.total - odd,
                        action=2,
                        quantity=odd,
                        adjusted_total=odd,
                        remark=str(TYPE_LIST[2][1]),
                        type_arises=3
                    )
                    continue
                else:
                    leave_result.used += item['subtotal']
                    leave_result.available = leave_result.total - leave_result.used
            leave_result.save(update_fields=['used', 'total', 'available'])
            LeaveAvailableHistory.objects.create(
                employee_inherit=leave_result.employee_inherit,
                tenant=leave_result.tenant,
                company=leave_result.company,
                leave_available=leave_result,
                total=leave_result.total - item['subtotal'],
                action=2,
                quantity=item['subtotal'],
                adjusted_total=item['subtotal'],
                remark=str(TYPE_LIST[2][1]),
                type_arises=3
            )
        return True

    def before_save(self):
        self.minus_available()
        self.create_code()

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            self.before_save()
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Leave request'
        verbose_name_plural = 'Leave request'
        ordering = ('-start_day',)
        default_permissions = ()
        permissions = ()


class LeaveAvailable(DataAbstractModel):
    leave_type = models.ForeignKey(
        'leave.LeaveType',
        on_delete=models.CASCADE,
        related_name="leave_annual_available_map_leave_type",
        help_text='foreign key to leave type model'
    )
    open_year = models.IntegerField(
        verbose_name='Opening year',
        null=True,
        help_text='year of annual created'
    )
    total = models.FloatField(
        verbose_name='Total annual can user in this year',
        null=True,
        default=0,
    )
    used = models.FloatField(
        verbose_name='employee used',
        null=True,
        default=0
    )
    available = models.FloatField(
        verbose_name='number of day can use',
        null=True,
        default=0
    )
    expiration_date = models.DateField(
        verbose_name='date expiration',
        null=True,
    )
    check_balance = models.BooleanField(
        verbose_name="balance control of type related leave type",
        default=False
    )

    class Meta:
        verbose_name = 'Leave annual available each employee'
        verbose_name_plural = 'Leave annual available each employee'
        ordering = ('-open_year',)
        default_permissions = ()
        permissions = ()


class LeaveAvailableHistory(DataAbstractModel):
    leave_available = models.ForeignKey(
        'leave.LeaveAvailable',
        on_delete=models.CASCADE,
        related_name="leave_available_map_history",
        help_text='foreign key to leave history'
    )
    total = models.FloatField(
        verbose_name='Total annual can user in this year',
        null=True,
        default=0,
    )
    action = models.CharField(
        choices=[('1', 'Increase'), ('2', 'Decrease')], default='1', max_length=10
    )
    quantity = models.FloatField(
        verbose_name='number of day change',
        null=True,
        default=0
    )
    adjusted_total = models.FloatField(
        verbose_name='number after change',
        null=True, default=0
    )
    remark = models.CharField(
        verbose_name='Descriptions',
        max_length=500,
        null=True,
    )
    type_arises = models.IntegerField(
        verbose_name="paid by",
        help_text="Choose paid of leave type",
        choices=TYPE_LIST,
    )

    class Meta:
        verbose_name = 'Leave annual available history each employee'
        verbose_name_plural = 'Leave annual available history each employee'
        ordering = ('-date_modified',)
        default_permissions = ()
        permissions = ()
