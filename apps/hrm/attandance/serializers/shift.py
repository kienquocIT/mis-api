from datetime import datetime, time

from rest_framework import serializers

from apps.hrm.attandance.models.shift import ShiftInfo
from apps.shared.translations.hrm import HRMMsg


class CommonFunction:
    @staticmethod
    def validate_time_fields(validate_data):
        def is_valid_time(val):
            if isinstance(val, time):
                return True
            if isinstance(value, str):
                try:
                    datetime.strptime(val, "%H:%M")
                    return True
                except ValueError:
                    return False
            return False

        time_fields = {
            'checkin_time': HRMMsg.VALIDATE_TIME_FORMAT_ERROR,
            'break_in_time': HRMMsg.VALIDATE_TIME_FORMAT_ERROR,
            'break_out_time': HRMMsg.VALIDATE_TIME_FORMAT_ERROR,
            'checkout_time': HRMMsg.VALIDATE_TIME_FORMAT_ERROR,
        }

        for field, error_msg in time_fields.items():
            value = validate_data.get(field)
            if value and not is_valid_time(value):
                raise serializers.ValidationError({field: error_msg})

        return validate_data

    @staticmethod
    def validate_shift_time_order(validate_data):
        checkin_time = validate_data.get('checkin_time', '')
        break_in_time = validate_data.get('break_in_time', '')
        break_out_time = validate_data.get('break_out_time', '')
        checkout_time = validate_data.get('checkout_time', '')

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
        return validate_data


class ShiftListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftInfo
        fields = (
            'id',
            'code',
            'title',
            'description',
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


class ShiftCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    working_day_list = serializers.JSONField()

    def validate(self, validate_data):
        CommonFunction.validate_time_fields(validate_data)
        CommonFunction.validate_shift_time_order(validate_data)
        return validate_data

    def create(self, validated_data):
        checkin_time_str = validated_data.get('checkin_time', '').strftime('%H:%M')
        checkout_time_str = validated_data.get('checkout_time', '').strftime('%H:%M')
        working_days = validated_data.get('working_day_list', [])
        active_days = [key for key, val in working_days.items() if val] if working_days else []
        description = f'{checkin_time_str} - {checkout_time_str} {", ".join(active_days)}'
        create_data = ShiftInfo.objects.create(**validated_data, description=description)
        return create_data

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


class ShiftDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftInfo
        fields = (
            'id',
            'code',
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


class ShiftUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    working_day_list = serializers.JSONField()

    def validate(self, validate_data):
        return ShiftCreateSerializer().validate(validate_data)

    def update(self, instance, validated_data):
        checkin_time_str = validated_data.get('checkin_time', '').strftime('%H:%M')
        checkout_time_str = validated_data.get('checkout_time', '').strftime('%H:%M')
        working_days = validated_data.get('working_day_list', [])
        active_days = [key for key, val in working_days.items() if val] if working_days else []
        description = f'{checkin_time_str} - {checkout_time_str} {", ".join(active_days)}'

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.description = description
        instance.save()
        return instance

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
