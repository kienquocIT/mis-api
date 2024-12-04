from django.db import models
from apps.shared import MasterDataAbstractModel, SYSTEM_STATUS


class Process(MasterDataAbstractModel):
    title = models.CharField(max_length=100)
    remark = models.TextField(blank=True, verbose_name='Remark of process')
    config = models.ForeignKey('process.ProcessConfiguration', null=True, on_delete=models.SET_NULL)
    stages = models.JSONField(default=dict, verbose_name='Stages configurate')
    global_app = models.JSONField(default=list, verbose_name='Cross-Stage Applications')
    opp = models.ForeignKey(
        'opportunity.Opportunity', null=True, on_delete=models.SET_NULL, related_name='process_of_opp',
    )
    is_ready = models.BooleanField(default=True, verbose_name='State ready of process')
    stage_current = models.ForeignKey(
        'process.ProcessStage', null=True, on_delete=models.SET_NULL,
        related_name='stage_current_of_process',
    )

    was_done = models.BooleanField(default=False)
    date_done = models.DateTimeField(null=True)

    members = models.JSONField(default=list, help_text='Employee ID List for lookup')

    def __str__(self):
        return f'{self.title} - {self.is_ready}'

    class Meta:
        verbose_name = 'Process'
        verbose_name_plural = 'Process'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProcessMembers(MasterDataAbstractModel):
    process = models.ForeignKey('process.Process', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Process Members'
        verbose_name_plural = 'Process Members'
        default_permissions = ()
        permissions = ()
        ordering = ['date_created']


class ProcessStage(MasterDataAbstractModel):
    process = models.ForeignKey('process.Process', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    remark = models.TextField(blank=True, verbose_name='Remark of process')
    system_code = models.CharField(max_length=10, null=True)
    is_system = models.BooleanField(default=False)
    order_number = models.SmallIntegerField(default=1)

    was_done = models.BooleanField(default=False)
    date_done = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.title} - {self.is_system} - {self.system_code}'

    class Meta:
        verbose_name = 'Process Stage'
        verbose_name_plural = 'Process Stage'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProcessStageApplication(MasterDataAbstractModel):
    process = models.ForeignKey('process.Process', on_delete=models.CASCADE)
    stage = models.ForeignKey('process.ProcessStage', on_delete=models.CASCADE, null=True)
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    remark = models.TextField(blank=True, verbose_name='Remark of process')
    amount = models.SmallIntegerField(default=0)
    amount_approved = models.SmallIntegerField(default=0)
    min = models.CharField(default="0", max_length=2)
    max = models.CharField(default="0", max_length=2)
    was_done = models.BooleanField(default=False)
    date_done = models.DateTimeField(null=True, default=None)
    order_number = models.SmallIntegerField(default=1)
    created_full = models.BooleanField(
        default=False, help_text='Status: Maximum number of creations allowed has been reached'
    )

    def __str__(self):
        return f'{self.title}'

    def amount_count(self, commit=True):
        update_fields = ['amount']
        self.amount = ProcessDoc.objects.filter(stage_app=self).count()
        if self.max != 'n':
            try:
                max_num = int(self.max)
            except ValueError:
                pass
            else:
                if max_num >= self.amount:
                    self.created_full = True
                    update_fields.append('created_full')
        if commit is True:
            self.save(update_fields=update_fields)
        return self

    def amount_approved_count(self, commit=True):
        self.amount_approved = ProcessDoc.objects.filter(
            stage_app=self, system_status__in=ProcessDoc.APPROVED_STATUS
        ).count()
        if commit is True:
            self.save(update_fields=['amount_approved'])
        return self

    class Meta:
        verbose_name = 'Process Stage Application'
        verbose_name_plural = 'Process Stage Application'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProcessDoc(MasterDataAbstractModel):
    process = models.ForeignKey('process.Process', on_delete=models.CASCADE)
    stage_app = models.ForeignKey('process.ProcessStageApplication', on_delete=models.CASCADE)
    doc_id = models.UUIDField()
    system_status = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(SYSTEM_STATUS),
    )
    date_status = models.JSONField(default=list, help_text='[{"status": 0, "datetime": ""},]')

    APPROVED_STATUS = [2, 3]

    def __str__(self):
        return f'{self.title} - {self.doc_id}'

    class Meta:
        verbose_name = 'Process Document'
        verbose_name_plural = 'Process Document'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProcessActivity(MasterDataAbstractModel):
    process = models.ForeignKey('process.Process', on_delete=models.CASCADE)
    stage = models.ForeignKey('process.ProcessStage', null=True, on_delete=models.SET_NULL)
    app = models.ForeignKey('process.ProcessStageApplication', null=True, on_delete=models.SET_NULL)
    doc = models.ForeignKey('process.ProcessDoc', null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Process Activity'
        verbose_name_plural = 'Process Activity'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
