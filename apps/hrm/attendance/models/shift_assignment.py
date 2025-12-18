from django.db import models

from apps.shared import MasterDataAbstractModel


# CONFIG
class ShiftAssignmentAppConfig(MasterDataAbstractModel):
    employees_config = models.JSONField(
        default=list,
        help_text="Employee list that allowed to use shift assignment"
    )

    class Meta:
        verbose_name = 'Shift Assignment Config'
        verbose_name_plural = 'Shift Assignment Configs'
        default_permissions = ()
        permissions = ()


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
        null=True,
    )
    date = models.DateField()

    class Meta:
        verbose_name = 'Shift Assignment'
        verbose_name_plural = 'Shift Assignments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
