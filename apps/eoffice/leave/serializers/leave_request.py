from django.db import transaction
from rest_framework import serializers

from apps.eoffice.leave.models import LeaveRequest, LeaveRequestDateListRegister
from apps.shared import LeaveMsg

__all__ = ['LeaveRequestListSerializer', 'LeaveRequestCreateSerializer', 'LeaveRequestDetailSerializer']


class LeaveRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'code', 'start_day', 'total', 'system_status')


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    detail_data = serializers.JSONField(allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ('title', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total')

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TITLE})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_REQUEST})
        return value

    @classmethod
    def validate_detail_data(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_DAYOFF})
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                date_list = validated_data['detail_data']
                leave = LeaveRequest.objects.create(**validated_data)
                if leave:
                    list_date_res = []
                    for item in date_list:
                        list_date_res.append(
                            LeaveRequestDateListRegister(
                                order=item["order"],
                                leave_type_id=item["leave_type"],
                                date_from=item["date_from"],
                                morning_shift_f=item["morning_shift_f"],
                                date_to=item["date_to"],
                                morning_shift_t=item["morning_shift_t"],
                                subtotal=float(item["subtotal"]),
                                remark=item["remark"],
                                leave_id=str(leave.id)
                            )
                        )
                    LeaveRequestDateListRegister.objects.bulk_create(list_date_res)
                    return leave
        except Exception as create_error:
            print('error save leave request', create_error)
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_DAYOFF})
        return False


class LeaveRequestDetailSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    detail_data = serializers.JSONField(allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total')

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    @classmethod
    def get_detail_data(cls, obj):
        date_list = LeaveRequestDateListRegister.objects.filter_current(
            fill__company=True, fill__tenant=True, leave=obj.id
        )
        if date_list.exists():
            return [
                {
                    'id': item[0],
                    'order': item[1],
                    'leave_type': item[2],
                    'date_from': item[3],
                    'morning_shift_f': item[4],
                    'date_to': item[5],
                    'morning_shift_t': item[6],
                    'subtotal': item[7],
                    'remark': item[8],
                } for item in date_list.values_list(
                    'id', 'order', 'leave_type', 'date_from', 'morning_shift_f',
                    'date_to', 'morning_shift_t', 'subtotal', 'remark'
                )
            ]
        return []
