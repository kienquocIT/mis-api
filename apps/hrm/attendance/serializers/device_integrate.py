from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.hrm.attendance.models import DeviceIntegrateEmployee, AttendanceDevice
from apps.shared import BaseMsg


class AttendanceDeviceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceDevice
        fields = (
            'id',
            'title',
            'device_ip',
            'username',
            'password',
            'minor_codes',
            'is_using',
        )


class AttendanceDeviceCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    device_ip = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

    class Meta:
        model = AttendanceDevice
        fields = (
            'title',
            'device_ip',
            'username',
            'password',
            'minor_codes',
            'is_using',
        )

    def create(self, validated_data):
        device = AttendanceDevice.objects.create(**validated_data)
        return device


class AttendanceDeviceUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceDevice
        fields = (
            'title',
            'device_ip',
            'username',
            'password',
            'minor_codes',
            'is_using',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class DeviceIntegrateEmployeeListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = DeviceIntegrateEmployee
        fields = (
            'id',
            'employee',
            'device_employee_id',
            'device_employee_name',
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}


class DeviceIntegrateEmployeeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceIntegrateEmployee
        fields = ()

    def create(self, validated_data):
        results = DeviceIntegrateEmployee.call_integrate(
            tenant_id=validated_data.get('tenant_id', None),
            company_id=validated_data.get('company_id', None),
        )
        return results[0]


class DeviceIntegrateEmployeeUpdateSerializer(serializers.ModelSerializer):
    employee = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DeviceIntegrateEmployee
        fields = (
            'employee',
        )

    @classmethod
    def validate_employee(cls, value):
        try:
            return Employee.objects.get_on_company(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': BaseMsg.NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
