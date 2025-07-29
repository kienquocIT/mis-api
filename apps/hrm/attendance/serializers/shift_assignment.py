from rest_framework import serializers

from apps.core.hr.models import Employee, Group
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
            'description': obj.shift.description,
            'checkin_time': obj.shift.checkin_time,
            'checkin_gr_start': obj.shift.checkin_gr_start,
            'checkin_gr_end': obj.shift.checkin_gr_end,
            'checkin_threshold': obj.shift.checkin_threshold,
            'break_in_time': obj.shift.break_in_time,
            'break_in_gr_start': obj.shift.break_in_gr_start,
            'break_in_gr_end': obj.shift.break_in_gr_end,
            'break_in_threshold': obj.shift.break_in_threshold,
            'break_out_time': obj.shift.break_out_time,
            'break_out_gr_start': obj.shift.break_out_gr_start,
            'break_out_gr_end': obj.shift.break_out_gr_end,
            'break_out_threshold': obj.shift.break_out_threshold,
            'checkout_time': obj.shift.checkout_time,
            'checkout_gr_start': obj.shift.checkout_gr_start,
            'checkout_gr_end': obj.shift.checkout_gr_end,
            'checkout_threshold': obj.shift.checkout_threshold,
            'working_day_list': obj.shift.working_day_list,
        } if obj.shift else {}


class ShiftAssignmentCreateSerializer(serializers.ModelSerializer):
    all_company = serializers.BooleanField(required=False)
    group_list = serializers.ListSerializer(child=serializers.UUIDField(required=False), required=False)
    group_employee_exclude_list = serializers.ListSerializer(
        child=serializers.UUIDField(required=False), required=False
    )
    employee_list = serializers.ListSerializer(child=serializers.UUIDField(required=False), required=False)
    shift = serializers.UUIDField(error_messages={
        'required': 'Must select shift to apply',
        'allow_null': 'Must select shift to apply',
    })
    date_list = serializers.ListSerializer(child=serializers.DateField(), error_messages={
        'required': 'Must select date to apply',
    })

    class Meta:
        model = ShiftAssignment
        fields = (
            'all_company',
            'group_list',
            'group_employee_exclude_list',
            'employee_list',
            'shift',
            'date_list',
        )

    @classmethod
    def validate_group_list(cls, value):
        if isinstance(value, list):
            if value:
                objs = Group.objects.filter_on_company(id__in=value)
                if objs.count() == len(value):
                    return objs
                raise serializers.ValidationError({'group': BaseMsg.NOT_EXIST})
            return value
        raise serializers.ValidationError({'group': BaseMsg.MUST_BE_ARRAY})

    @classmethod
    def validate_group_employee_exclude_list(cls, value):
        if isinstance(value, list):
            if value:
                objs = Employee.objects.filter_on_company(id__in=value)
                if objs.count() == len(value):
                    return objs
                raise serializers.ValidationError({'employee': BaseMsg.NOT_EXIST})
            return value
        raise serializers.ValidationError({'employee': BaseMsg.MUST_BE_ARRAY})

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

    def validate(self, validate_data):
        all_company = validate_data.get('all_company', False)
        group_list = validate_data.get('group_list', [])
        employee_list = validate_data.get('employee_list', [])
        if all_company is False and len(group_list) == 0 and len(employee_list) == 0:
            raise serializers.ValidationError({'detail': "Must select object to apply"})
        return validate_data

    def create(self, validated_data):
        all_company = validated_data.pop('all_company')
        group_list = validated_data.pop('group_list')
        group_employee_exclude_list = validated_data.pop('group_employee_exclude_list')
        employee_list = validated_data.pop('employee_list')
        shift = validated_data.pop('shift')
        date_list = validated_data.pop('date_list')
        bulk_data = []
        if all_company is True:
            employee_list = Employee.objects.filter_on_company()
        if all_company is False:
            group_list_employee = Employee.objects.filter_on_company(group_id__in=group_list).exclude(
                id__in=group_employee_exclude_list
            )
            if group_list_employee:
                if employee_list:
                    employee_list = employee_list | group_list_employee
                else:
                    employee_list = group_list_employee
        for employee in employee_list:
            # delete old
            olds = ShiftAssignment.objects.filter_on_company(employee=employee, date__in=date_list)
            if olds:
                olds.delete()
            # append bulk data
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
