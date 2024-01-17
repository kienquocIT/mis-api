from datetime import datetime

from rest_framework import serializers
from apps.masterdata.saledata.models.periods import (
    Periods
)


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'start_date')


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


class PeriodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'start_date')


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title')
