from datetime import datetime

from rest_framework import serializers

from apps.hrm.attendance.models.shift import ShiftInfo
from apps.shared.translations.hrm import HRMMsg


class CommonFunction:
    @staticmethod
    def is_valid_time(value):
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%H:%M")
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def _validate_time_threshold(field_prefix: str, data: dict, errors: dict):
        time_val = data.get(f'{field_prefix}_time', '')
        gr_end_val = data.get(f'{field_prefix}_gr_end', '')
        threshold_val = data.get(f'{field_prefix}_threshold', 0)

        fmt = "%H:%M"

        if time_val and gr_end_val:
            try:
                gr_end_time = datetime.strptime(gr_end_val, fmt)
                standard_time = datetime.strptime(time_val, fmt)
            except ValueError:
                errors[f'{field_prefix}_time'] = "Time must be in HH:MM format."
                errors[f'{field_prefix}_gr_end'] = "Time must be in HH:MM format."
                return

            diff_minutes = (gr_end_time - standard_time).total_seconds() / 60
            try:
                threshold_val = float(threshold_val)
            except ValueError:
                errors[f'{field_prefix}_threshold'] = "Threshold must be a number."
                return

            if threshold_val > diff_minutes:
                errors[f'{field_prefix}_threshold'] = (
                    f"{field_prefix.replace('_', ' ').capitalize()} threshold must be between "
                    f"{field_prefix.replace('_', ' ')} time and grace end."
                )

    @staticmethod
    def validate_time_fields(validate_data):
        time_data = validate_data.pop('time_data')
        time_fields = {
            'checkin_time': f"Check in time {HRMMsg.FORMAT_ERROR}",
            'checkin_gr_start': f"Check in grace start time {HRMMsg.FORMAT_ERROR}",
            'checkin_gr_end': f"Check in grace end time {HRMMsg.FORMAT_ERROR}",

            'break_in_time': f"Break in time {HRMMsg.FORMAT_ERROR}",
            'break_in_gr_start': f"Break in grace start time {HRMMsg.FORMAT_ERROR}",
            'break_in_gr_end': f"Break in grace end time {HRMMsg.FORMAT_ERROR}",

            'break_out_time': f"Break out time {HRMMsg.FORMAT_ERROR}",
            'break_out_gr_start': f"Break out grace start time {HRMMsg.FORMAT_ERROR}",
            'break_out_gr_end': f"Break out grace end time {HRMMsg.FORMAT_ERROR}",

            'checkout_time': f"Check out time {HRMMsg.FORMAT_ERROR}",
            'checkout_gr_start': f"Check out grace start time {HRMMsg.FORMAT_ERROR}",
            'checkout_gr_end': f"Check out grace end time {HRMMsg.FORMAT_ERROR}",
        }

        for field, error_msg in time_fields.items():
            value = time_data.get(field)
            if value and not CommonFunction.is_valid_time(value):
                raise serializers.ValidationError({field: error_msg})
            validate_data[field] = value
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

    @staticmethod
    def validate_threshold_minutes(validate_data):
        """
        Validate ngưỡng phải nằm trong khoảng Time và Grace End
        Ví dụ:
            Time = "7:30"
            Grace End = "8:30"
        Lúc này Threshold không được quá 60p.
        """
        errors = {}

        for prefix in ['checkin', 'break_in', 'break_out', 'checkout']:
            CommonFunction._validate_time_threshold(prefix, validate_data, errors)

        if errors:
            raise serializers.ValidationError(errors)

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
    time_data = serializers.JSONField(default=dict)

    def validate(self, validate_data):
        CommonFunction.validate_time_fields(validate_data)
        CommonFunction.validate_shift_time_order(validate_data)
        CommonFunction.validate_threshold_minutes(validate_data)

        checkin_time_str = validate_data.get('checkin_time', '')
        checkout_time_str = validate_data.get('checkout_time', '')
        working_days = validate_data.get('working_day_list', [])
        active_days = [key for key, val in working_days.items() if val] if working_days else []
        validate_data['description'] = f'{checkin_time_str} - {checkout_time_str} {", ".join(active_days)}'

        return validate_data

    def create(self, validated_data):
        shift_obj = ShiftInfo.objects.create(**validated_data)
        return shift_obj

    class Meta:
        model = ShiftInfo
        fields = (
            'title',
            'time_data',
            'checkin_threshold',
            'break_in_threshold',
            'break_out_threshold',
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
    time_data = serializers.JSONField(default=dict)

    def validate(self, validate_data):
        return ShiftCreateSerializer().validate(validate_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = ShiftInfo
        fields = (
            'title',
            'time_data',
            'checkin_threshold',
            'break_in_threshold',
            'break_out_threshold',
            'checkout_threshold',
            'working_day_list',
        )


class ShiftImportCreateSerializer(serializers.ModelSerializer):

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

    def create(self, validated_data):
        checkin_time_str = validated_data.get('checkin_time', '')
        checkout_time_str = validated_data.get('checkout_time', '')
        working_days = validated_data.get('working_day_list', [])
        active_days = [key for key, val in working_days.items() if val] if working_days else []
        validated_data['description'] = f'{checkin_time_str} - {checkout_time_str} {", ".join(active_days)}'
        return ShiftInfo.objects.create(**validated_data)
