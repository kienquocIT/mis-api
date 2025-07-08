from django.db import models

from apps.shared import MasterDataAbstractModel


class ShiftInfo(MasterDataAbstractModel):
    checkin_time = models.TimeField(verbose_name='The start time')
    checkin_gr_start = models.TimeField()
    checkin_gr_end = models.TimeField()
    checkin_threshold = models.FloatField()

    break_in_time = models.TimeField(verbose_name='The break start time')
    break_in_gr_start = models.TimeField()
    break_in_gr_end = models.TimeField()
    break_in_threshold = models.FloatField()

    break_out_time = models.TimeField(verbose_name='The break end time')
    break_out_gr_start = models.TimeField()
    break_out_gr_end = models.TimeField()
    break_out_threshold = models.FloatField()

    checkout_time = models.TimeField(verbose_name='The end time')
    checkout_gr_start = models.TimeField()
    checkout_gr_end = models.TimeField()
    checkout_threshold = models.FloatField()

    working_day_list = models.JSONField(default=dict)
    # working_day_list = {
    #   'Mon': True,
    #   'Tue': False,
    #   ...
    # }
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Shift information'
        verbose_name_plural = 'Shift information'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if not self.code:
            count = ShiftInfo.objects.filter_on_company().count() + 1
            self.code = f'SH00{count}'
        super().save(*args, **kwargs)
