from datetime import datetime
from copy import deepcopy

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.leave.models import LeaveRequest, LeaveRequestDateListRegister, LeaveAvailable, LeaveAvailableHistory
from apps.shared import LeaveMsg, AbstractDetailSerializerModel, SYSTEM_STATUS, TYPE_LIST

__all__ = ['LeaveRequestListSerializer', 'LeaveRequestCreateSerializer', 'LeaveRequestDetailSerializer',
           'LeaveAvailableListSerializer', 'LeaveAvailableEditSerializer', 'LeaveAvailableHistoryListSerializer',
           'LeaveRequestDateListRegisterSerializer', 'LeaveRequestUpdateSerializer'
           ]


class LeaveRequestListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": obj.employee_inherit.get_full_name()
            }
        return {}

    class Meta:
        model = LeaveRequest
        fields = (
            'id',
            'title',
            'employee_inherit',
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
            'id',
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
        special_stock = {'FF': 0, 'MY': 0, 'MC': 0}
        for item in value:
            available = item["leave_available"]
            if item["subtotal"] > available["total"] and available["check_balance"]:
                raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_AVAILABLE_NUMBER})

            if available["leave_type"]["code"] in special_stock:
                special_stock[available["leave_type"]["code"]] += item['subtotal']
                if special_stock[available["leave_type"]["code"]] > available["total"]:
                    raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_AVAILABLE_NUMBER})
            d_from = datetime.strptime(item["date_from"], "%Y-%m-%d")
            d_to = datetime.strptime(item["date_to"], "%Y-%m-%d")
            if d_from > d_to:
                raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_DATE_ERROR})
            if d_from == d_to and (not item['morning_shift_f'] and item['morning_shift_t']):
                raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_DATE_ERROR})
            if available["check_balance"]:
                crt_time = timezone.now().date()
                leave_exp = datetime.strptime(available['expiration_date'], '%Y-%m-%d').date()
                if crt_time > leave_exp:
                    raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_DATE_EXPIRED})
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
            # code new
            for item in obj.detail_data:
                try:
                    available = LeaveAvailable.objects.select_related('leave_type').get_current(
                        employee_inherit_id=obj.employee_inherit_id, company=obj.company,
                        id=item["leave_available"]["id"]
                    )
                    if available:
                        item["leave_available"] = {
                            "id": item["leave_available"]["id"],
                            "check_balance": available.check_balance,
                            "expiration_date": available.expiration_date,
                            "open_year": available.open_year,
                            "total": available.total,
                            "used": available.used,
                            "available": max(available.total - available.used, 0),
                        }
                        l_type = available.leave_type
                        item["leave_available"]["leave_type"] = {
                            "id": l_type.id,
                            "title": l_type.title,
                            "code": l_type.code
                        }
                except LeaveAvailable.DoesNotExist:
                    return []
            return obj.detail_data
        return []


class LeaveRequestUpdateSerializer(AbstractDetailSerializerModel):
    detail_data = serializers.JSONField(allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ('id', 'title', 'code', 'employee_inherit', 'request_date', 'detail_data', 'start_day', 'total',
                  'system_status')

    @classmethod
    def validate_detail_data(cls, value):
        special_stock = {'FF': 0, 'MY': 0, 'MC': 0}
        for item in value:
            available = item["leave_available"]
            if available["check_balance"]:
                crt_time = timezone.now().date()
                leave_exp = datetime.strptime(available['expiration_date'], '%Y-%m-%d').date()
                if crt_time > leave_exp:
                    raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_DATE_EXPIRED})
            if item["subtotal"] > available["total"] and available["check_balance"]:
                raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_AVAILABLE_NUMBER})

            if available["leave_type"]["code"] in special_stock:
                special_stock[available["leave_type"]["code"]] += item['subtotal']
                if special_stock[available["leave_type"]["code"]] > available["total"]:
                    raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_AVAILABLE_NUMBER})
            d_from = datetime.strptime(item["date_from"], "%Y-%m-%d")
            d_to = datetime.strptime(item["date_to"], "%Y-%m-%d")
            if d_from > d_to:
                raise serializers.ValidationError({'detail': LeaveMsg.EMPTY_DATE_ERROR})
        return value

    def update_detail_data(self, instance, detail_list):
        company_id = str(self.context.get('company_id', ''))
        tenant_id = str(self.context.get('tenant_id', ''))
        LeaveRequestDateListRegister.objects.filter(leave=instance).delete()
        data_create = []
        for item in detail_list:
            data_create.append(
                LeaveRequestDateListRegister(
                    company_id=company_id,
                    tenant_id=tenant_id,
                    order=item["order"],
                    leave_type_id=item['leave_available']['leave_type']['id'],
                    date_from=item["date_from"],
                    morning_shift_f=item["morning_shift_f"],
                    date_to=item["date_to"],
                    morning_shift_t=item["morning_shift_t"],
                    subtotal=float(item["subtotal"]),
                    remark=item["remark"],
                    leave=instance
                )
            )
        LeaveRequestDateListRegister.objects.bulk_create(data_create)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if 'detail_data' in validated_data and validated_data['detail_data']:
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

    def create_history(self, instance, validated_data, bf_total):
        employee_id = self.context.get('employee_id', None)
        init_data = self.initial_data
        history = LeaveAvailableHistory.objects.create(
            company_id=self.context.get('company_id', None),
            tenant_id=self.context.get('tenant_id', None),
            leave_available_id=str(instance.id),
            open_year=instance.open_year,
            employee_inherit=validated_data['employee_inherit'],
            total=bf_total,
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
                before_total = deepcopy(instance.available)
                if initial_data['action'] == '1':  # increase
                    update_total = instance.total + float(initial_data['quantity'])
                else:
                    update_total = instance.total - float(initial_data['quantity'])
                instance.total = update_total
                instance.available = instance.total - instance.used
                instance.save()
                if instance:
                    self.create_history(instance, validated_data, before_total)
                return instance
        except Exception as create_error:
            print('error save leave available', create_error)
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_UPDATE_AVAILABLE_ERROR})


class LeaveAvailableHistoryListSerializer(serializers.ModelSerializer):
    leave_available = serializers.SerializerMethodField()
    type_arises = serializers.SerializerMethodField()

    class Meta:
        model = LeaveAvailableHistory
        fields = ('id', 'leave_available', 'open_year', 'total', 'action', 'quantity', 'date_modified', 'type_arises')

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
