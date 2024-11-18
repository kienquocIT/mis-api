from django.db import models

from apps.shared import MasterDataAbstractModel, RECURRENCE_PERIOD, RECURRENCE_STATUS, RECURRENCE_ACTION


class Recurrence(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)
    application_data = models.JSONField(default=dict, help_text="data json of application")
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}'
    )
    doc_template_id = models.UUIDField(verbose_name='Main document show diagram')
    doc_template_data = models.JSONField(default=dict)
    period = models.SmallIntegerField(choices=RECURRENCE_PERIOD, default=1)
    repeat = models.IntegerField(default=1, help_text="number of recurrences")

    # use if period is daily
    date_daily = models.DateField(null=True)
    # use if period is weekly
    weekday = models.IntegerField(default=0, help_text="(0 = Sunday, 1 = Monday, ...)")
    # use if period is monthly
    monthday = models.IntegerField(default=1, help_text="1, 2, 3,...31")
    # use if period yearly
    date_yearly = models.DateField(null=True)

    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    date_next = models.DateField(null=True)

    next_recurrences = models.JSONField(default=list, help_text="list date (YYYY-MM-DD) of next recurrences")

    recurrence_status = models.SmallIntegerField(choices=RECURRENCE_STATUS, default=0)

    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='recurrence_employee_inherit',
    )

    class Meta:
        verbose_name = 'Recurrence'
        verbose_name_plural = 'Recurrences'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecurrenceTask(MasterDataAbstractModel):
    recurrence = models.ForeignKey(
        Recurrence,
        on_delete=models.CASCADE,
        verbose_name="Recurrence",
        related_name="recurrence_next_recurrence",
    )
    date_next = models.DateField(null=True, help_text="next recurrence date")
    recurrence_action = models.SmallIntegerField(choices=RECURRENCE_ACTION, default=0)

    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='recurrence_task_employee_inherit',
    )

    class Meta:
        verbose_name = 'Recurrence Task'
        verbose_name_plural = 'Recurrences Tasks'
        ordering = ('-date_next',)
        default_permissions = ()
        permissions = ()
