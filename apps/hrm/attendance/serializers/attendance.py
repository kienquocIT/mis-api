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


class AttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = (
            'date',
        )

    def validate(self, validate_data):
        date = validate_data.pop('date')
        objs_created = Attendance.push_attendance_data(date=date)
        if not objs_created:
            raise serializers.ValidationError({'detail': "Get attendance data fail"})
        validate_data.update({'instance': objs_created[0]})
        return validate_data

    def create(self, validated_data):
        result = validated_data.pop('instance')
        return result
