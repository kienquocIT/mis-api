from django.http import HttpResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig, WorkingYearConfig, \
    WorkingHolidayConfig, LeaveAvailable
from apps.shared import LEAVE_YEARS_SENIORITY, LeaveMsg

__all__ = ['LeaveConfigDetailSerializer', 'LeaveTypeConfigCreateSerializer', 'LeaveTypeConfigDetailSerializer',
           'LeaveTypeConfigUpdateSerializer', 'LeaveTypeConfigDeleteSerializer', 'WorkingCalendarConfigListSerializer',
           'WorkingYearSerializer', 'WorkingHolidaySerializer', 'WorkingCalendarConfigUpdateSerializer'
           ]


class LeaveConfigDetailSerializer(serializers.ModelSerializer):
    leave_type = serializers.SerializerMethodField()
    year_senior = serializers.SerializerMethodField()

    def get_leave_type(self, obj):
        company_id = self.context.get('company_id', None)
        leave_type = [
            {
                'id': item[0],
                'title': item[1],
                'code': item[2],
                'paid_by': item[3],
                'remark': item[4],
                'balance_control': item[5],
                'is_lt_system': item[6],
                'is_lt_edit': item[7],
                'is_check_expiration': item[8],
                'no_of_paid': item[9],
                'prev_year': item[10],
            } for item in LeaveType.objects.filter(
                leave_config=obj,
                company_id=company_id
            ).order_by('-date_created').values_list(
                'id', 'title', 'code', 'paid_by', 'remark', 'balance_control', 'is_lt_system', 'is_lt_edit',
                'is_check_expiration', 'no_of_paid', 'prev_year'
            )
        ]
        return leave_type

    @classmethod
    def get_year_senior(cls, obj):  # noqa
        print(obj)
        return LEAVE_YEARS_SENIORITY

    class Meta:
        model = LeaveConfig
        fields = ('id', 'leave_type', 'year_senior')


class LeaveTypeConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ('id', 'title', 'code', 'paid_by', 'remark', 'balance_control', 'is_lt_system', 'is_lt_edit',
                  'is_check_expiration', 'no_of_paid', 'prev_year', 'leave_config')


class LeaveTypeConfigCreateSerializer(serializers.ModelSerializer):
    no_of_paid = serializers.IntegerField(required=False)

    class Meta:
        model = LeaveType
        fields = ('leave_config', 'paid_by', 'remark', 'balance_control', 'is_check_expiration', 'no_of_paid',
                  'title', 'code')

    @classmethod
    def validate_leave_config(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_ID_CONFIG})
        return value

    @classmethod
    def validate_code(cls, value):
        if value and LeaveType.objects.filter(code=value).exists():
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TYPE_CODE})
        return value

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TITLE})
        return value

    def leave_type_map_available_employee(self, l_type):
        for employee in Employee.objects.filter_current(fill__tenant=True, fill__company=True):
            LeaveAvailable.objects.create(
                leave_type=l_type,
                open_year=timezone.now().year,
                expiration_date=timezone.now().replace(month=12, day=31) if l_type.is_check_expiration else None,
                check_balance=True,
                employee_inherit=employee,
                company_id=self.context.get('company_id', None),
                tenant_id=self.context.get('tenant_id', None)
            )

    def create(self, validated_data):
        leave_type = LeaveType.objects.create(**validated_data)
        if leave_type.balance_control:
            # có quản lý số dư
            self.leave_type_map_available_employee(leave_type)
        return leave_type


class LeaveTypeConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ('leave_config', 'paid_by', 'remark', 'balance_control', 'is_check_expiration', 'no_of_paid',
                  'title', 'code', 'is_lt_system', 'is_lt_edit', 'no_of_paid', 'prev_year')

    def update_available_list(self, l_type):
        list_available = LeaveAvailable.objects.filter_current(fill__company=True, fill__tenant=True, leave_type=l_type)
        if list_available.exists():
            list_upd = []
            for available in list_available:
                available.check_balance = l_type.balance_control
                available.total = 0
                available.used = 0
                available.available = 0
                available.expiration_date = timezone.now().replace(
                    month=12, day=31
                ) if l_type.is_check_expiration else None
                list_upd.append(available)
            LeaveAvailable.objects.bulk_update(
                list_upd, fields=['check_balance', 'total', 'used', 'available', 'expiration_date']
            )
        else:
            # trường hợp else là case khi leave type đó từ ko check thành check quản lý số dư và leave available đó chưa
            # tạo record cho leave type này
            list_create = []
            for employee in Employee.objects.filter_current(fill__tenant=True, fill__company=True):
                list_create.append(
                    LeaveAvailable(
                        leave_type=l_type,
                        open_year=timezone.now().year,
                        expiration_date=timezone.now().replace(
                            month=12, day=31
                        ) if l_type.is_check_expiration else None,
                        check_balance=True,
                        employee_inherit=employee,
                        company_id=self.context.get('company_id', None),
                        tenant_id=self.context.get('tenant_id', None)
                    )
                )
            LeaveAvailable.objects.bulk_create(list_create)

    @classmethod
    def update_expiration_date(cls, l_type):
        list_available = LeaveAvailable.objects.filter_current(
            fill__company=True, fill__tenant=True, leave_type=l_type, leave_type__code='ANPY'
        )
        if list_available.exists():
            list_upd = []
            for available in list_available:
                date_current = timezone.now().replace(year=available.open_year, month=12, day=31)
                available.expiration_date = date_current + relativedelta(months=l_type.prev_year)
                list_upd.append(available)
            LeaveAvailable.objects.bulk_update(
                list_upd, fields=['expiration_date']
            )

    @classmethod
    def validate_leave_config(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_ID_CONFIG})
        return value

    def validate_code(self, value):
        if value and LeaveType.objects.exclude(id=str(self.instance.id)).filter_current(
                code=value, fill__company=True
        ).exists():
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TYPE_CODE})
        return value

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TITLE})
        return value

    def validate_no_of_paid(self, value):
        if self.instance.code == 'AN' and value < 12:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_NO_OF_PAID_ERROR})
        return value

    def validate(self, attrs):
        if not self.instance.is_lt_edit:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_UPDATE_LEAVE_TYPE})
        return attrs

    def update(self, instance, validated_data):
        change = False
        if 'balance_control' in validated_data and instance.balance_control != validated_data['balance_control']:
            change = True
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if instance.code == 'ANPY':
            self.update_expiration_date(instance)
        if change:
            self.update_available_list(instance)
        return instance


class LeaveTypeConfigDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ('id',)

    def delete(self, instance):  # noqa
        if instance.is_lt_edit and not instance.is_lt_system:
            instance.delete()
        else:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_DELETE_LEAVE_TYPE})
        #
        return '', HttpResponse(status=204)


class WorkingCalendarConfigListSerializer(serializers.ModelSerializer):
    years = serializers.SerializerMethodField()

    class Meta:
        model = WorkingCalendarConfig
        fields = ('id', 'working_days', 'years')

    @classmethod
    def get_years(cls, obj):
        filter_list = WorkingYearConfig.objects.filter(working_calendar=obj.id).order_by('config_year')
        if filter_list.exists():
            list_year = [
                {
                    'id': item[0],
                    'config_year': item[1],
                    'list_holiday': WorkingHolidaySerializer(
                        WorkingHolidayConfig.objects.filter(year_id=item[0]).order_by('holiday_date_to')
                        , many=True
                    ).data
                } for item in filter_list.values_list('id', 'config_year')
            ]
            return list_year
        return {}


class WorkingCalendarConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingCalendarConfig
        fields = ('id', 'working_days')


class WorkingYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingYearConfig
        fields = ('id', 'working_calendar', 'config_year')

    def validate_config_year(self, value):

        if value <= 0 or WorkingYearConfig.objects.filter(
                working_calendar_id=str(self.initial_data['working_calendar']),
                config_year=value
        ).exists():
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_DUPLICATE_YEAR})
        return value


class WorkingHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHolidayConfig
        fields = ('id', 'holiday_date_to', 'remark', 'year')

    def validate(self, validate_data):
        if WorkingHolidayConfig.objects.filter(
                year=validate_data['year'],
                holiday_date_to=validate_data['holiday_date_to']
        ).exists():
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_DUPLICATE_HOLIDAY})
        return validate_data
