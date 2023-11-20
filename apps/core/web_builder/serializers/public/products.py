from rest_framework import serializers

from apps.masterdata.saledata.models import Product


class PublicProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'code', 'available_amount', 'avatar', 'description', 'sale_price')
