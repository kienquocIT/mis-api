from django.db import models

from apps.shared import SimpleAbstractModel


class EmployeeHRNotMapEmployeeHRM(SimpleAbstractModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        related_name='employee_hr',
        null=True
    )
    is_mapped = models.BooleanField(verbose_name='company employee mapped to employee HRM', default=False)

    class Meta:
        verbose_name = 'Employee HR Map Employee HRM'
        verbose_name_plural = 'Employee HR Map Employee HRM'
        unique_together = ('company', 'employee')
        ordering = ('is_mapped',)
        default_permissions = ()
        permissions = ()
