from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.periods import (
    Periods
)
from apps.shared import ProductMsg


# Product Type
class PeriodsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'start_date')


class PeriodsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date')


class PeriodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('id', 'code', 'title', 'fiscal_year', 'start_date')


class PeriodsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periods
        fields = ('code', 'title', 'fiscal_year', 'start_date')
