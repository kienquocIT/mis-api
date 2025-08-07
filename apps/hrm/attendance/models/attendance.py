from django.db import models

from apps.hrm.attendance.utils.logical_attendance import AttendanceHandler
from apps.shared import MasterDataAbstractModel, ATTENDANCE_STATUS, DisperseModel


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
        related_name='attendance_shift',
        null=True,
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
    def push_attendance_data(cls, date):
        m_log = DisperseModel(app_model='attendance.AccessLog').get_model()
        m_employee = DisperseModel(app_model='hr.Employee').get_model()
        if m_employee and m_log and hasattr(m_employee, 'objects') and hasattr(m_log, 'push_access_log'):
            m_log.push_access_log(date=date)
            for employee_id in m_employee.objects.filter_on_company().values_list('id', flat=True):
                data_parse = AttendanceHandler.check_attendance(
                    employee_id=employee_id,
                    date=date,
                )

                # delete old records for them same employee and date
                cls.objects.filter(employee_id=employee_id, date=date).delete()

                # create new records
                cls.objects.bulk_create([cls(**data) for data in data_parse])
        print('push_attendance_data done.')
        return True

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ('-date',)
        default_permissions = ()
        permissions = ()
