from datetime import datetime

from rest_framework import serializers
from apps.masterdata.saledata.models.periods import (
    Periods
)


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'space_month', 'start_date')


class PeriodsCreateSerializer(serializers.ModelSerializer):
    fiscal_year = serializers.IntegerField(allow_null=False)

    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date')

    @classmethod
    def validate_fiscal_year(cls, value):
        if value < datetime.now().year:
            raise serializers.ValidationError({"fiscal_year": 'Passed fiscal year'})
        return value

    def validate(self, validate_data):
        validate_data['space_month'] = validate_data['start_date'].month - 1
        return validate_data


class PeriodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'space_month', 'start_date')


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title')
