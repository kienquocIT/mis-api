from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.eoffice.leave.models import LeaveRequest, LeaveRequestDateListRegister, LeaveAvailable, LeaveAvailableHistory
from apps.shared import LeaveMsg

__all__ = ['LeaveRequestListSerializer', 'LeaveRequestCreateSerializer', 'LeaveRequestDetailSerializer',
           'LeaveAvailableListSerializer', 'LeaveAvailableEditSerializer', 'LeaveAvailableHistoryListSerializer']


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
        company_id = self.context.get('company_id', None)
        tenant_id = self.context.get('tenant_id', None)
        try:
            with transaction.atomic():
                date_list = validated_data['detail_data']
                leave = LeaveRequest.objects.create(**validated_data)
                if leave:
                    list_date_res = []
                    for item in date_list:
                        list_date_res.append(
                            LeaveRequestDateListRegister(
                                company_id=company_id,
                                tenant_id=tenant_id,
                                order=item["order"],
                                leave_type_id=item["leave_type"]["id"],
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

    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total',
                  'system_status')

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
            fill__company=True, fill__tenant=True, leave_id=str(obj.id)
        )
        if date_list.exists():
            return [
                {
                    'id': item[0],
                    'order': item[1],
                    'leave_type': {
                        'id': item[2],
                        'title': item[3],
                        'code': item[4]
                    },
                    'date_from': item[5],
                    'morning_shift_f': item[6],
                    'date_to': item[7],
                    'morning_shift_t': item[8],
                    'subtotal': item[9],
                    'remark': item[10],
                } for item in date_list.values_list(
                    'id', 'order', 'leave_type', 'leave_type__title', 'leave_type__code', 'date_from',
                    'morning_shift_f', 'date_to', 'morning_shift_t', 'subtotal', 'remark'
                )
            ]
        return []


class LeaveAvailableListSerializer(serializers.ModelSerializer):
    leave_type = serializers.SerializerMethodField()

    @classmethod
    def get_leave_type(cls, obj):
        if obj.leave_type:
            return {
                'id': str(obj.leave_type_id),
                'title': obj.leave_type.title,
                'code': obj.leave_type.code
            }
        return {}

    class Meta:
        model = LeaveAvailable
        fields = ('id', 'leave_type', 'open_year', 'total', 'used', 'available', 'expiration_date')


class LeaveAvailableEditSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    adjusted_total = serializers.SerializerMethodField()
    remark = serializers.SerializerMethodField()

    class Meta:
        model = LeaveAvailable
        fields = ('employee_inherit', 'total', 'action', 'quantity', 'adjusted_total', 'remark')

    def create_history(self, instance, validated_data, init_data):
        employee_id = self.context.get('employee_id', None)
        history = LeaveAvailableHistory.objects.create(
            company_id=self.context.get('company_id', None),
            tenant_id=self.context.get('tenant_id', None),
            leave_available_id=str(instance.id),
            employee_inherit=validated_data['employee_inherit'],
            total=validated_data['total'],
            action=init_data['action'],
            quantity=init_data['quantity'],
            adjusted_total=init_data['adjusted_total'],
            remark=init_data['remark'],
            date_modified=timezone.now(),
            employee_modified_id=employee_id
        )
        if history:
            return True
        return False

    def update(self, instance, validated_data):
        try:
            initial_data = self.initial_data
            with transaction.atomic():
                update_total = 0
                if initial_data['action'] == '1':  # increase
                    update_total = instance.total + float(initial_data['quantity'])
                else:
                    update_total = instance.total - float(initial_data['quantity'])
                instance.total = update_total
                instance.available = instance.total - instance.used
                instance.save()
                if instance:
                    self.create_history(instance, validated_data, initial_data)
                return instance
        except Exception as create_error:
            print('error save leave available', create_error)
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_UPDATE_AVAILABLE_ERROR})


class LeaveAvailableHistoryListSerializer(serializers.ModelSerializer):
    open_year = serializers.SerializerMethodField()
    leave_available = serializers.SerializerMethodField()

    class Meta:
        model = LeaveAvailableHistory
        fields = ('id', 'leave_available', 'open_year', 'total', 'action', 'quantity', 'date_modified')

    @classmethod
    def get_open_year(cls, obj):
        open_year = '--'
        if obj.leave_available:
            open_year = obj.leave_available.open_year
        return open_year

    @classmethod
    def get_leave_available(cls, obj):
        return {
            "id": str(obj.leave_available_id),
            "title": obj.leave_available.leave_type.title,
        }
