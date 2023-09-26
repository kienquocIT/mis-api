from django.http import HttpResponse

from rest_framework import serializers

from apps.eoffice.leave.models import LeaveConfig, LeaveType, WorkingCalendarConfig, WorkingYearConfig, \
    WorkingHolidayConfig
from apps.shared import LEAVE_YEARS_SENIORITY, LeaveMsg

__all__ = ['LeaveConfigDetailSerializer', 'LeaveTypeConfigCreateSerializer', 'LeaveTypeConfigDetailSerializer',
           'LeaveTypeConfigUpdateSerializer', 'LeaveTypeConfigDeleteSerializer', 'WorkingCalendarConfigListSerializer',
           'WorkingYearSerializer', 'WorkingHolidaySerializer'
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


class LeaveTypeConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ('leave_config', 'paid_by', 'remark', 'balance_control', 'is_check_expiration', 'no_of_paid',
                  'title', 'code', 'is_lt_system', 'is_lt_edit', 'no_of_paid', 'prev_year')

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

    def validate_title(self, value):
        if not value and self.instance.code != 'AN' or self.instance.code != 'ANPY':
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_LEAVE_TITLE})
        return value

    def update(self, instance, validated_data):
        if not instance.is_lt_edit:
            raise serializers.ValidationError({'detail': LeaveMsg.ERROR_UPDATE_LEAVE_TYPE})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
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
                        WorkingHolidayConfig.objects.filter(year_id=item[0])
                        , many=True).data
                } for item in filter_list.values_list('id', 'config_year')
            ]
            return list_year
        return {}


class WorkingYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingYearConfig
        fields = ('id', 'working_calendar', 'config_year')


class WorkingHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHolidayConfig
        fields = ('id', 'holiday_date_to', 'remark', 'year')
