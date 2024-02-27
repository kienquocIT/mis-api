from datetime import datetime

from rest_framework import serializers
from apps.masterdata.saledata.models.periods import (
    Periods
)


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    software_start_using_time = serializers.SerializerMethodField()

    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date',
            'software_start_using_time'
        )

    @classmethod
    def get_software_start_using_time(cls, obj):
        software_start_using_time = obj.company.software_start_using_time
        if software_start_using_time.year == obj.fiscal_year:
            return f'{str(software_start_using_time.month).zfill(2)}/{str(software_start_using_time.year)}'
        return False


class PeriodsCreateSerializer(serializers.ModelSerializer):
    fiscal_year = serializers.IntegerField(allow_null=False)

    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date')

    @classmethod
    def validate_fiscal_year(cls, value):
        if value < datetime.now().year:
            raise serializers.ValidationError({"fiscal_year": 'Passed fiscal year'})
        if value < Periods.objects.filter_current(
                fill__tenant=True, fill__company=True, fiscal_year=value
        ).exists():
            raise serializers.ValidationError({"Period": 'This fiscal year has period already'})
        return value

    def validate(self, validate_data):
        validate_data['space_month'] = validate_data['start_date'].month - 1
        return validate_data

    def create(self, validated_data):
        period = Periods(**validated_data)
        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            period.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
            period.company.save(update_fields=['software_start_using_time'])
        return period


class PeriodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = (
            'id',
            'code',
            'title',
            'fiscal_year',
            'space_month',
            'start_date'
        )


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title')

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        software_start_using_time = self.initial_data.get('software_start_using_time')
        if software_start_using_time:
            instance.company.software_start_using_time = datetime.strptime(software_start_using_time, '%m/%Y')
            instance.company.save(update_fields=['software_start_using_time'])

        return instance
