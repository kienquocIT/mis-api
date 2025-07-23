from django.db import models

from apps.shared import MasterDataAbstractModel


class ShiftAssignment(MasterDataAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="employee",
        related_name="shift_assignment_employee",
    )
    shift = models.ForeignKey(
        'attendance.ShiftInfo',
        on_delete=models.CASCADE,
        verbose_name="shift",
        related_name="shift_assignment_shift",
    )
    date = models.DateField()

    class Meta:
        verbose_name = 'Shift Assignment'
        verbose_name_plural = 'Shift Assignments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
