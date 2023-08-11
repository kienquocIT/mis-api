from django.utils import timezone
from django.db import models
from apps.shared import SimpleAbstractModel, MasterDataAbstractModel


class Process(MasterDataAbstractModel):
    process_step_datas = models.JSONField(
        default=list,
        help_text='Step in process'
    )
    date_modified = models.DateTimeField(
        default=timezone.now,
        # auto_now_add=True,
        help_text='Date modified this record in last',
    )

    class Meta:
        default_permissions = ()
        permissions = ()


class SaleFunction(MasterDataAbstractModel):
    function = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='function_application'
    )

    is_free = models.BooleanField(
        default=False
    )
    is_in_process = models.BooleanField(
        default=False
    )

    is_default = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = 'Function Process'
        verbose_name_plural = 'Functions Process'
        ordering = ('function',)
        default_permissions = ()
        permissions = ()


class SaleProcessStep(SimpleAbstractModel):
    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name='process',
    )
    function = models.ForeignKey(
        SaleFunction,
        on_delete=models.CASCADE,
        related_name='function_process_step',
    )
    function_title = models.CharField(
        max_length=500
    )
    subject = models.TextField(
        help_text='subject of function',
    )
    order = models.PositiveIntegerField(
        default=0,
    )
    is_current = models.BooleanField(
        help_text='step current',
        default=False,
    )
    is_completed = models.BooleanField(
        help_text='step completed',
        default=False,
    )

    def skip_step(self):
        self.is_completed = True
        self.save()
        steps = SaleProcessStep.objects.filter(
            order__in=[
                self.order,
                self.order + 1
            ]
        )

        step_current = steps.filter(
            order=self.order
        )
        if all(step.is_completed for step in step_current):
            next_step = steps.filter(
                order=self.order + 1
            )
            if len(next_step) > 0:
                step_current.update(
                    is_current=False
                )
                next_step.update(
                    is_current=True
                )

    def set_current(self):
        pre_step = SaleProcessStep.objects.filter(
            order__lt=self.order
        )
        pre_step.update(
            is_completed=True,
            is_current=False
        )
        self.is_current = True
        self.save()

    class Meta:
        verbose_name = 'Process Step'
        verbose_name_plural = 'Process Steps'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
