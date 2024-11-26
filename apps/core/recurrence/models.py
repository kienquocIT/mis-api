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

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("R")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(codes=existing_codes)
        if num_max is None:
            code = 'R0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'R{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code(company_id=self.company_id)
        # hit DB
        super().save(*args, **kwargs)


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
