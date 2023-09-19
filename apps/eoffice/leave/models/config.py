from django.db import models

from apps.shared import SimpleAbstractModel, MasterDataAbstractModel
from apps.shared.translations import LeaveMsg

PAID_BY = (
    (1, str(LeaveMsg.PAID_BY_ONE)),
    (2, str(LeaveMsg.PAID_BY_TWO)),
    (3, str(LeaveMsg.PAID_BY_THREE)),
)

__all__ = ['LeaveConfig', 'LeaveType']


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
        default=0
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
