import calendar
from datetime import date

from rest_framework import serializers
from apps.hrm.attendance.models.attendance import Attendance


class AttendanceListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            'id',
            'code',
            'title',
            'employee',
            'shift',
            'checkin_time',
            'checkout_time',
            'date',
            'attendance_status',
            'is_late',
            'is_early_leave'
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


class AttendanceDetailSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            'id',
            'code',
            'title',
            'employee',
            'shift',
            'checkin_time',
            'checkout_time',
            'date',
            'attendance_status',
            'is_late',
            'is_early_leave'
        )


def get_all_days_in_month(year, month):
    today = date.today()
    num_days = calendar.monthrange(year, month)[1]

    return [
        date(year, month, day).strftime("%Y-%m-%d")
        for day in range(1, num_days + 1)
        if date(year, month, day) <= today
    ]


class AttendanceCreateSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()

    class Meta:
        model = Attendance
        fields = (
            'month',
            'year',
        )

    def validate(self, validate_data):
        month = validate_data.pop('month')
        year = validate_data.pop('year')
        dates = get_all_days_in_month(year=year, month=month)
        objs_created = []
        for date_check in dates:
            objs_create = Attendance.push_attendance_data(date=date_check)
            if not objs_created:
                objs_created = objs_create
        if not objs_created:
            raise serializers.ValidationError({'detail': "Get attendance data fail"})
        validate_data.update({'instance': objs_created[0]})
        return validate_data

    def create(self, validated_data):
        result = validated_data.pop('instance')
        return result
