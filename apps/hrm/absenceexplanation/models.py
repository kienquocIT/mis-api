from django.db import models

from apps.shared import DataAbstractModel, ABSENCE_TYPE


class AbsenceExplanation(DataAbstractModel):
    description = models.TextField()
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='employee',
        related_name='absent_employee'
    )
    date = models.DateField(help_text="Absence explanation for")
    type = models.SmallIntegerField(
        default=0,
        choices=ABSENCE_TYPE
    )
    reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Absence Explanation of HRM'
        verbose_name_plural = 'Absence Explanations of HRM'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
