from datetime import datetime

from django.db import models

from apps.hrm.attendance.utils.logical_attendance import DeviceIntegrate
from apps.shared import MasterDataAbstractModel


class AttendanceDevice(MasterDataAbstractModel):
    device_ip = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    minor_codes = models.JSONField(default=list)
    is_using = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Attendance Device'
        verbose_name_plural = 'Attendance Devices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DeviceIntegrateEmployee(MasterDataAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="employee",
        related_name="device_integrate_employee",
        null=True,
    )
    device_employee_id = models.CharField(max_length=50, blank=True)
    device_employee_name = models.CharField(max_length=100, blank=True)

    @classmethod
    def call_integrate(cls, tenant_id, company_id):
        result_list = []
        for data_integrate in DeviceIntegrate.get_user():
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id,
                device_employee_id=data_integrate.get('employeeNo', ''),
                defaults={
                    'device_employee_name': data_integrate.get('name', ''),
                }
            )
            result_list.append(obj)
        return result_list

    class Meta:
        verbose_name = 'Device Integrate Employee'
        verbose_name_plural = 'Device Integrate Employees'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


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
    device_employee_id = models.CharField(max_length=50, blank=True)
    device_employee_name = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(null=True, help_text='date time of logging')
    minor = models.CharField(max_length=100, blank=True)
    recognition_type = models.CharField(max_length=50, blank=True, help_text='type of logging')

    # example: Card, Face, Fingertip

    @classmethod
    def push_access_log(cls, date):
        # cls.objects.filter_on_company(timestamp__date=date).delete()
        bulk_data = []
        device_config = DeviceIntegrate.get_device_config()
        if device_config:
            logs = DeviceIntegrate.get_attendance_log(date=date)
            employee_integrate = DeviceIntegrateEmployee.objects.filter_on_company(
                device_employee_id__in=[data.get('employeeNoString', '') for data in logs],
                employee__isnull=False,
            )
            if employee_integrate:
                for log in logs:
                    for employee_int in employee_integrate:
                        if employee_int.device_employee_id == log.get('employeeNoString', ''):
                            dt_obj = datetime.fromisoformat(log.get('time', None))
                            dt_naive = dt_obj.replace(tzinfo=None)
                            bulk_data.append(cls(
                                device_id=device_config.id,
                                employee_id=employee_int.employee_id,
                                device_employee_id=employee_int.device_employee_id,
                                device_employee_name=employee_int.device_employee_name,
                                timestamp=dt_naive,
                                minor=log.get('minor', ''),
                                tenant_id=employee_int.tenant_id,
                                company_id=employee_int.company_id,
                            ))
                            break
                cls.objects.bulk_create(bulk_data)
        print('push_access_log done.')
        return True

    class Meta:
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'
        ordering = ('-timestamp',)
        default_permissions = ()
        permissions = ()
