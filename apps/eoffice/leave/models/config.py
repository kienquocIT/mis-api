import json

from django.db import models

from apps.shared import SimpleAbstractModel, MasterDataAbstractModel

__all__ = ['LeaveConfig', 'LeaveType', 'WorkingCalendarConfig', 'WorkingYearConfig', 'WorkingHolidayConfig']

PAID_BY = (
    (1, 'Company salary'),
    (2, 'Social insurance'),
    (3, 'Unpaid'),
)


class LeaveConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='company_leave_config',
    )

    class Meta:
        verbose_name = 'Leave Config of Company'
        verbose_name_plural = 'Leave Config of Company'
        default_permissions = ()
        permissions = ()


class LeaveType(MasterDataAbstractModel):
    leave_config = models.ForeignKey(
        LeaveConfig,
        on_delete=models.CASCADE,
        related_name="leave_type_config",
        null=False
    )
    paid_by = models.IntegerField(
        verbose_name="paid by",
        help_text="Choose paid of leave type",
        choices=PAID_BY,
        default=3
    )
    remark = models.CharField(
        verbose_name="remark",
        help_text="description of leave type",
        null=True,
        blank=True,
        max_length=255,
    )
    balance_control = models.BooleanField(
        verbose_name="Balance management",
        help_text="If value is True this leave type can control surplus",
        default=False
    )
    is_lt_system = models.BooleanField(
        verbose_name="is system",
        help_text="default type system",
        default=False
    )
    is_lt_edit = models.BooleanField(
        verbose_name="is edit",
        help_text="this type can edit",
        default=True
    )
    is_check_expiration = models.BooleanField(
        verbose_name="is check expired",
        help_text="allow check expiration",
        default=False
    )
    data_expired = models.DateTimeField(
        null=True,
        verbose_name='Date expired'
    )
    no_of_paid = models.IntegerField(
        verbose_name="number of type",
        help_text="number of leave type",
        default=0,
        null=True
    )
    prev_year = models.IntegerField(
        verbose_name="Previous year",
        help_text="number of previous year",
        default=0
    )

    class Meta:
        verbose_name = 'Leave Config of Company'
        verbose_name_plural = 'Leave Config of Company'
        default_permissions = ()
        permissions = ()


class WorkingCalendarConfig(MasterDataAbstractModel):
    working_days = models.JSONField(
        default=dict,
        verbose_name='json working days',
        help_text=json.dumps(
            {

                0: {
                    'work': False,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                1: {
                    'work': True,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                2: {
                    'work': True,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                3: {
                    'work': True,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                4: {
                    'work': True,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                5: {
                    'work': True,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
                6: {
                    'work': False,
                    'mor': {'from': '08:00 AM', 'to': '12:00 AM'},
                    'aft': {'from': '13:30 PM', 'to': '17:30 PM'}
                },
            }
        )
    )

    class Meta:
        verbose_name = 'Leave Holiday of Company'
        verbose_name_plural = 'Leave Holiday of Company'
        default_permissions = ()
        permissions = ()


class WorkingYearConfig(SimpleAbstractModel):
    working_calendar = models.ForeignKey(
        'leave.WorkingCalendarConfig',
        on_delete=models.CASCADE,
        verbose_name="working calendar config",
        related_name="working_year_working_calendar",
        null=True
    )
    config_year = models.IntegerField(
        default=1995,
        verbose_name='number year holiday',
    )


class WorkingHolidayConfig(SimpleAbstractModel):
    holiday_date_from = models.DateField(verbose_name='holiday from', null=True)
    holiday_date_to = models.DateField(verbose_name='holiday to', null=True)
    year = models.ForeignKey(
        'leave.WorkingYearConfig',
        on_delete=models.CASCADE,
        verbose_name="working calendar config",
        related_name="working_year_working_calendar",
        null=True
    )
    remark = models.CharField(
        max_length=500, null=False, verbose_name='description'
    )
