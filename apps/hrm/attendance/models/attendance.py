from django.db import models

from apps.hrm.attendance.utils.logical_attendance import AttendanceHandler
from apps.shared import MasterDataAbstractModel, ATTENDANCE_STATUS


class AccessLog(MasterDataAbstractModel):
    device = models.ForeignKey(
        'attendance.AttendanceDevice',
        on_delete=models.CASCADE,
        verbose_name='attendance device',
        related_name='access_log_device',
        null=True,
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='employee',
        related_name='access_log_employee'
    )
    timestamp = models.DateTimeField(null=True, help_text='date time of logging')
    recognition_type = models.CharField(max_length=50, blank=True, help_text='type of logging')

    # example: Card, Face, Fingertip

    class Meta:
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'
        ordering = ('-timestamp',)
        default_permissions = ()
        permissions = ()


class Attendance(MasterDataAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='employee',
        related_name='attendance_employee'
    )
    shift = models.ForeignKey(
        'attendance.ShiftInfo',
        on_delete=models.CASCADE,
        verbose_name='shift',
        related_name='attendance_shift'
    )
    checkin_time = models.TimeField(null=True)
    checkout_time = models.TimeField(null=True)
    date = models.DateField(null=True, help_text='date log attendance')
    attendance_status = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(ATTENDANCE_STATUS),
    )
    leave = models.ForeignKey(
        'leave.LeaveRequest',
        on_delete=models.CASCADE,
        verbose_name='leave',
        related_name='attendance_leave',
        null=True,
    )
    leave_data = models.JSONField(
        default=dict,
        help_text="read data leave, back-up for getting list or detail"
    )
    business_trip = models.ForeignKey(
        'businesstrip.BusinessRequest',
        on_delete=models.CASCADE,
        verbose_name='business trip',
        related_name='attendance_business_trip',
        null=True,
    )
    business_trip_data = models.JSONField(
        default=dict,
        help_text="read data business trip, backup for getting list or detail"
    )
    is_late = models.BooleanField(
        default=False,
        help_text="check if the attendance is marked as late after checking logic"
    )
    is_early_leave = models.BooleanField(
        default=False,
        help_text="check if the attendance is marked as early leave after checking logic"
    )

    @classmethod
    def push_attendance_data(cls, employee_id, date):
        data_parse = AttendanceHandler.check_attendance(
            employee_id=employee_id,
            date=date,
        )

        # delete old records for them same employee and date
        cls.objects.filter(employee_id=employee_id, date=date).delete()

        # create new records
        cls.objects.bulk_create([cls(**data) for data in data_parse])
        return True

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ('-date',)
        default_permissions = ()
        permissions = ()
