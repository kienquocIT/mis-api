from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.hrm.attendance.models import ShiftAssignment, ShiftInfo
from apps.shared import BaseMsg


class ShiftAssignmentListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()

    class Meta:
        model = ShiftAssignment
        fields = (
            'id',
            'employee',
            'shift',
            'date',
        )

    @classmethod
    def get_employee(cls, obj):
        return obj.employee.get_detail_minimal() if obj.employee else {}

    @classmethod
    def get_shift(cls, obj):
        return {
            'id': obj.shift_id,
            'title': obj.shift.title,
            'code': obj.shift.code,
        } if obj.shift else {}


class ShiftAssignmentCreateSerializer(serializers.ModelSerializer):
    employee_list = serializers.ListSerializer(child=serializers.UUIDField())
    shift = serializers.UUIDField()
    date_list = serializers.ListSerializer(child=serializers.DateField())

    class Meta:
        model = ShiftAssignment
        fields = (
            'employee_list',
            'shift',
            'date_list',
        )

    @classmethod
    def validate_employee_list(cls, value):
        if isinstance(value, list):
            if value:
                objs = Employee.objects.filter_on_company(id__in=value)
                if objs.count() == len(value):
                    return objs
                raise serializers.ValidationError({'employee': BaseMsg.NOT_EXIST})
            return value
        raise serializers.ValidationError({'employee': BaseMsg.MUST_BE_ARRAY})

    @classmethod
    def validate_shift(cls, value):
        try:
            return ShiftInfo.objects.get_on_company(id=value)
        except ShiftInfo.DoesNotExist:
            raise serializers.ValidationError({'shift': BaseMsg.NOT_EXIST})

    def create(self, validated_data):
        employee_list = validated_data.pop('employee_list')
        shift = validated_data.pop('shift')
        date_list = validated_data.pop('date_list')
        bulk_data = []
        for employee in employee_list:
            for date in date_list:
                bulk_data.append(ShiftAssignment(
                    employee=employee,
                    shift=shift,
                    date=date,
                    tenant_id=employee.tenant_id,
                    company_id=employee.company_id,
                ))
        results = ShiftAssignment.objects.bulk_create(bulk_data)
        return results[0]
