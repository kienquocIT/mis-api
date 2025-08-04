from django.db import models

from apps.hrm.attendance.utils.logical_attendance import DeviceIntegrate
from apps.shared import MasterDataAbstractModel


class AttendanceDevice(MasterDataAbstractModel):
    device_ip = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    minor_codes = models.JSONField(default=list)

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
    def call_integrate(cls, device_ip, username, password, tenant_id, company_id):
        result_list = []
        for data_integrate in DeviceIntegrate.get_user(
                device_ip=device_ip,
                username=username,
                password=password,
        ):
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
