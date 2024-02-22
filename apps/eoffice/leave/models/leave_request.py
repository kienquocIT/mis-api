import json

from django.db import models
from django.utils import timezone

from apps.shared import DataAbstractModel, TYPE_LIST, LeaveMsg

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
        if not self.code:
            task = LeaveRequest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_delete=False,
                system_status__gte=2
            ).count()
            char = "L"
            num_quotient, num_remainder = divmod(task, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def minus_available(self):
        # trừ leave available và ghi history
        type_list = self.detail_data
        for item in type_list:
            leave_available = LeaveAvailable.objects.filter(id=item['leave_available']['id'])
            # nếu ko có quản lý số dư thì ko trừ available
            if leave_available.exists():
                available = leave_available.first()
                if available.check_balance:
                    # các leave có quản lý số dư dc phép trừ stock
                    # nếu số dư ko đủ raise lỗi
                    if item['subtotal'] > available.available:
                        raise ValueError(LeaveMsg.EMPTY_AVAILABLE_NUMBER)
                    if available.check_balance:
                        crt_time = timezone.now().date()
                        leave_exp = available.expiration_date
                        if crt_time > leave_exp:
                            raise ValueError(LeaveMsg.EMPTY_DATE_EXPIRED)
                    available.used += item['subtotal']
                    available.available = available.total - available.used
                    available.save(update_fields=['used', 'available'])

                    LeaveAvailableHistory.objects.create(
                        employee_inherit=available.employee_inherit,
                        tenant=available.tenant,
                        company=available.company,
                        leave_available=available,
                        open_year=available.open_year,
                        total=available.total - item['subtotal'],
                        action=2,
                        quantity=item['subtotal'],
                        adjusted_total=item['subtotal'],
                        remark=str(TYPE_LIST[2][1]),
                        type_arises=3
                    )

    def before_save(self):
        self.minus_available()
        self.create_code()

    def save(self, *args, **kwargs):
        if self.system_status == 3:
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
    open_year = models.IntegerField(
        verbose_name='Opening year',
        null=True,
        default=0,
        help_text='year of annual created'
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
