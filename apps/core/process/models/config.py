from django.db import models

from apps.shared import MasterDataAbstractModel


class ProcessConfiguration(MasterDataAbstractModel):
    title = models.CharField(max_length=100)
    remark = models.TextField(blank=True, verbose_name='Remark of process')
    apply_start = models.DateTimeField(null=True)
    apply_finish = models.DateTimeField(null=True)
    stages = models.JSONField(default=dict, verbose_name='Stages configurate')
    global_app = models.JSONField(default=list, verbose_name='Cross-Stage Applications')
    for_opp = models.BooleanField(default=False, verbose_name='Process use for Opp')

    class Meta:
        verbose_name = 'Process'
        verbose_name_plural = 'Process'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProcessConfigurationMembers(MasterDataAbstractModel):
    process = models.ForeignKey('process.ProcessConfiguration', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Process Configuration Members'
        verbose_name_plural = 'Process Configuration Members'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
