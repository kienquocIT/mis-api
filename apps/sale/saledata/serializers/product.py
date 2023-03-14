from django.db.models import Q
from rest_framework import serializers
from apps.sale.saledata.models.product import (
    ProductType
)
from apps.shared import HRMsg
from apps.shared.translations.accounts import AccountsMsg


# Product Type
class ProductTypeListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'code', 'description')


class ProductTypeCreateSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('title', 'code', 'description')


class ProductTypeDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = ProductType
        fields = ('id', 'title', 'code', 'description')
