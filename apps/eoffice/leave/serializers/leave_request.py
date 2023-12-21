from collections import Counter

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.leave.models import LeaveRequest, LeaveRequestDateListRegister, LeaveAvailable, LeaveAvailableHistory
from apps.shared import LeaveMsg, AbstractDetailSerializerModel, SYSTEM_STATUS, TYPE_LIST, TypeCheck

__all__ = ['LeaveRequestListSerializer', 'LeaveRequestCreateSerializer', 'LeaveRequestDetailSerializer',
           'LeaveAvailableListSerializer', 'LeaveAvailableEditSerializer', 'LeaveAvailableHistoryListSerializer',
           'LeaveRequestDateListRegisterSerializer', 'LeaveRequestUpdateSerializer'
           ]


class LeaveRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = (
            'id',
            'title',
            'code',
            'start_day',
            'total',
            'system_status'
        )


class LeaveRequestDateListRegisterSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_title(cls, obj):
        if obj.leave:
            return obj.leave.title
        return ''

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.leave:
            leave = obj.leave
            return {
                'id': leave.employee_inherit_id,
                'full_name': leave.employee_inherit.get_full_name()
            }
        return {}

    class Meta:
        model = LeaveRequestDateListRegister
        fields = (
            'date_from',
            'date_to',
            'morning_shift_f',
            'morning_shift_t',
            'remark',
            'employee_inherit',
            'title'
        )


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    detail_data = serializers.JSONField(allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ('title', 'employee_inherit_id', 'request_date', 'detail_data', 'start_day', 'total', 'system_status')

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TITLE})
        return value

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_REQUEST})
        return value

    @classmethod
    def validate_detail_data(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_DAYOFF})
        return value

    @decorator_run_workflow
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
                        leave_available = item["leave_available"]
                        if isinstance(leave_available['leave_type'], dict):
                            leave_type_id = leave_available["leave_type"]['id']
                        list_date_res.append(
                            LeaveRequestDateListRegister(
                                company_id=company_id,
                                tenant_id=tenant_id,
                                employee_inherit=leave.employee_inherit,
                                order=item["order"],
                                leave_type_id=leave_type_id,
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


class LeaveRequestDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    detail_data = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'code', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total',
                  'system_status')

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}',
                "group": {
                    "id": str(obj.employee_inherit.group_id),
                    "title": obj.employee_inherit.group.title,
                    "code": obj.employee_inherit.group.code
                } if obj.employee_inherit.group_id else {}
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None

    @classmethod
    def get_detail_data(cls, obj):
        if obj.detail_data:
            available_list = LeaveAvailable.objects.filter_current(
                fill__company=True, employee_inherit_id=obj.employee_inherit_id
            )
            # return for item in
            data_list = LeaveRequestDateListRegister.objects.filter_current(
                fill__company=True, fill__tenant=True, leave_id=str(obj.id)
            ).order_by('order')
            if data_list.exists() and available_list.exists():
                get_detail_data = []
                for item in data_list:
                    available = available_list.get(leave_type_id=item.leave_type_id)
                    # if (value.morning_shift_f) value.date_from += ' 00:00:00'
                    # else value.date_from += ' 12:00:00'
                    # if (value.morning_shift_t) value.date_to += ' 12:00:00'
                    # else value.date_to += ' 23:59:59'
                    get_detail_data.append(
                        {
                            'id': item.id,
                            'order': item.order,
                            'remark': item.remark,
                            'date_from': f'{str(item.date_from)} {"00:00:00" if item.morning_shift_f else "12:00:00"}',
                            'date_to': f'{item.date_to} {"12:00:00" if item.morning_shift_t else "23:59:59"}',
                            'subtotal': item.subtotal,
                            'leave_available': {
                                'id': str(available.id),
                                'used': available.used,
                                'total': available.total,
                                'available': available.available,
                                'open_year': available.open_year,
                                'leave_type': {
                                    'id': str(item.leave_type.id),
                                    'title': item.leave_type.title,
                                    'code': item.leave_type.code
                                },
                                'check_balance': available.check_balance,
                                'expiration_date': available.expiration_date,
                            },
                            'morning_shift_f': item.morning_shift_f,
                            'morning_shift_t': item.morning_shift_t,
                        }
                    )
                return get_detail_data
        return []


class LeaveRequestUpdateSerializer(AbstractDetailSerializerModel):
    detail_data = serializers.JSONField(allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'code', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total',
                  'system_status')

    def update_detail_data(self, instance, detail_list):
        company_id = str(self.context.get('company_id', ''))
        tenant_id = str(self.context.get('tenant_id', ''))
        current_list = [str(item.id) for item in LeaveRequestDateListRegister.objects.filter(leave=instance)]
        try:
            with transaction.atomic():
                list_data_current = []
                data_delete = []
                data_create = []
                for item in detail_list:
                    leave_type_id = item['leave_available']['leave_type']['id']
                    if 'id' not in item or item['id'] == '':
                        # create new
                        data_create.append(
                            LeaveRequestDateListRegister(
                                company_id=company_id,
                                tenant_id=tenant_id,
                                order=item["order"],
                                leave_type_id=leave_type_id,
                                date_from=item["date_from"],
                                morning_shift_f=item["morning_shift_f"],
                                date_to=item["date_to"],
                                morning_shift_t=item["morning_shift_t"],
                                subtotal=float(item["subtotal"]),
                                remark=item["remark"],
                                leave=instance
                            )
                        )
                    elif 'id' in item and TypeCheck.check_uuid(item['id']) and item['id'] in current_list:
                        list_data_current.append(
                            LeaveRequestDateListRegister(
                                id=item['id'],
                                company_id=company_id,
                                tenant_id=tenant_id,
                                order=item["order"],
                                leave_type_id=leave_type_id,
                                date_from=item["date_from"],
                                morning_shift_f=item["morning_shift_f"],
                                date_to=item["date_to"],
                                morning_shift_t=item["morning_shift_t"],
                                subtotal=float(item["subtotal"]),
                                remark=item["remark"],
                                leave=instance
                            )
                        )
                        data_delete.append(item['id'])
                data_delete = Counter(current_list) - Counter(data_delete)
                data_delete = [element for element, count in data_delete.most_common()]
                if len(data_delete) > 0:
                    LeaveRequestDateListRegister.objects.filter(id__in=data_delete).delete()
                if len(data_create) > 0:
                    LeaveRequestDateListRegister.objects.bulk_create(data_create)
                if len(list_data_current) > 0:
                    LeaveRequestDateListRegister.objects.bulk_update(
                        list_data_current, fields=['order', 'leave_type_id', 'date_from', 'morning_shift_f', 'date_to',
                                                   'morning_shift_t', 'subtotal', 'remark']
                    )
        except Exception as create_error:
            print('error save leave request', create_error)
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_EMP_DAYOFF})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        self.update_detail_data(instance, validated_data['detail_data'])
        return instance


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
        fields = ('id', 'leave_type', 'open_year', 'total', 'used', 'available', 'expiration_date', 'check_balance')


class LeaveAvailableEditSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    adjusted_total = serializers.SerializerMethodField()
    remark = serializers.SerializerMethodField()

    class Meta:
        model = LeaveAvailable
        fields = ('employee_inherit', 'total', 'action', 'quantity', 'adjusted_total', 'remark', 'expiration_date')

    def create_history(self, instance, validated_data):
        employee_id = self.context.get('employee_id', None)
        init_data = self.initial_data
        history = LeaveAvailableHistory.objects.create(
            company_id=self.context.get('company_id', None),
            tenant_id=self.context.get('tenant_id', None),
            leave_available_id=str(instance.id),
            employee_inherit=validated_data['employee_inherit'],
            total=validated_data['total'],
            action=init_data['action'],
            quantity=init_data['quantity'],
            adjusted_total=init_data.get('adjusted_total', 0),
            remark=init_data.get('remark', ''),
            date_modified=timezone.now(),
            employee_modified_id=employee_id,
            type_arises=init_data.get('type_arises', 1)
        )
        if history:
            return True
        return False

    def validate(self, validate_date):
        initial_data = self.initial_data
        if 'quantity' in initial_data and float(initial_data.get('quantity')) <= 0:
            raise serializers.ValidationError({"Detail": LeaveMsg.ERROR_QUANTITY})
        return validate_date

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
                    self.create_history(instance, validated_data)
                return instance
        except Exception as create_error:
            print('error save leave available', create_error)
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_UPDATE_AVAILABLE_ERROR})


class LeaveAvailableHistoryListSerializer(serializers.ModelSerializer):
    open_year = serializers.SerializerMethodField()
    leave_available = serializers.SerializerMethodField()
    type_arises = serializers.SerializerMethodField()

    class Meta:
        model = LeaveAvailableHistory
        fields = ('id', 'leave_available', 'open_year', 'total', 'action', 'quantity', 'date_modified', 'type_arises')

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

    @classmethod
    def get_type_arises(cls, obj):
        num = obj.type_arises - 1
        return TYPE_LIST[num][1]
