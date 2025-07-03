from rest_framework import serializers

from apps.hrm.attandance.models import ShiftInfo
from apps.shared import WORKING_DAYS
from apps.shared.translations.hrm import HRMMsg


class ShiftListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftInfo
        fields = (
            'id',
            'code',
            'title',
            'description'
        )


class ShiftCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    def validate(self, attrs):
        checkin_time = attrs.get('checkin_time')
        break_in_time = attrs.get('break_in_time')
        break_out_time = attrs.get('break_out_time')
        checkout_time = attrs.get('checkout_time')

        # validate break in must be later than check in time
        if checkin_time and break_in_time and checkin_time >= break_in_time:
            raise serializers.ValidationError({
                'break_in_time': HRMMsg.BREAK_IN_TIME_ERROR
            })

        # validate break out must be later than break in time
        if break_out_time and break_in_time and break_in_time >= break_out_time:
            raise serializers.ValidationError({
                'break_out_time': HRMMsg.BREAK_OUT_TIME_ERROR
            })

        # validate check out must be later than break out time
        if checkout_time and break_out_time and break_out_time >= checkout_time:
            raise serializers.ValidationError({
                'checkout_time': HRMMsg.CHECKOUT_TIME_ERROR
            })

    def create(self, validated_data):
        checkin_time_str = validated_data.get('checkin_time', '').strftime('%H:%M')
        checkout_time_str = validated_data.get('checkout_time', '').strftime('%H:%M')
        working_days = validated_data.get('working_day_list', [])
        if working_days and all(isinstance(i, bool) for i in working_days):
            active_days = [
                day_label for i, (idx, day_label) in enumerate(WORKING_DAYS)
                if i < len(working_days) and working_days[i]
            ]
        else:
            active_days = []
        description = f'{checkin_time_str} - {checkout_time_str} {", ".join(active_days)}'
        return ShiftInfo.objects.create(**validated_data, description=description)

    class Meta:
        model = ShiftInfo
        fields = (
            'title',
            'checkin_time',
            'checkin_gr_start',
            'checkin_gr_end',
            'checkin_threshold',
            'break_in_time',
            'break_in_gr_start',
            'break_in_gr_end',
            'break_in_threshold',
            'break_out_time',
            'break_out_gr_start',
            'break_out_gr_end',
            'break_out_threshold',
            'checkout_time',
            'checkout_gr_start',
            'checkout_gr_end',
            'checkout_threshold',
            'working_day_list',
        )
