from django.db import models

from apps.shared import MasterDataAbstractModel


class ShiftInfo(MasterDataAbstractModel):
    checkin_time = models.TimeField(default=None, verbose_name='The start time')
    checkin_gr_start = models.TimeField(default=None)
    checkin_gr_end = models.TimeField(default=None)
    checkin_threshold = models.PositiveSmallIntegerField()

    break_in_time = models.TimeField(default=None, verbose_name='The break start time')
    break_in_gr_start = models.TimeField(default=None)
    break_in_gr_end = models.TimeField(default=None)
    break_in_threshold = models.PositiveSmallIntegerField()

    break_out_time = models.TimeField(default=None, verbose_name='The break end time')
    break_out_gr_start = models.TimeField(default=None)
    break_out_gr_end = models.TimeField(default=None)
    break_out_threshold = models.PositiveSmallIntegerField()

    checkout_time = models.TimeField(default=None, verbose_name='The end time')
    checkout_gr_start = models.TimeField(default=None)
    checkout_gr_end = models.TimeField(default=None)
    checkout_threshold = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Shift information'
        verbose_name_plural = 'List shift information'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
