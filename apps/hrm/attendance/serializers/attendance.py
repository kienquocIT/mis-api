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
