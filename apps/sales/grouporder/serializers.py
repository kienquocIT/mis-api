from django.utils import timezone
from rest_framework import serializers

from apps.masterdata.saledata.models import ProductPriceList
from apps.masterdata.saledata.models.product import Product

class GroupOrderProductListSerializer(serializers.ModelSerializer):
    bom_product = serializers.SerializerMethodField()
    general_price = serializers.SerializerMethodField()
    product_price_list_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'standard_price',
            'bom_product',
            'general_price',
            'product_price_list_data'
        )

    @classmethod
    def get_bom_product(cls, obj):
        bom_obj = obj.bom_product.first()
        return {
            'id': bom_obj.id,
            'title': bom_obj.title,
            'sum_price': bom_obj.sum_price,
        } if bom_obj else {}

    @classmethod
    def get_general_price(cls, obj):
        general_product_price_obj = obj.product_price_product.filter(price_list__is_default=True).first()
        return {
            'id': general_product_price_obj.id,
            'price': general_product_price_obj.price,
        } if general_product_price_obj else {}

    @classmethod
    def get_product_price_list_data(cls, obj):
        product_price_list = obj.product_price_product.all()
        sale_product_price_list = []
        for item in product_price_list:
            if item.uom_using_id == obj.sale_default_uom_id and item.price_list.valid_time_end > timezone.now():
                sale_product_price_list.append({
                    'id': item.id,
                    'price': item.price,
                    'title': item.price_list.title,
                    'is_default': item.price_list.is_default,
                })
        return sale_product_price_list

class GroupOrderProductPriceListListSerializer(serializers.ModelSerializer):
    price_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductPriceList
        fields = (
            'id',
            'price',
            'price_data'
        )

    @classmethod
    def get_price_data(cls, obj):
        return {
            'id': obj.price_list.id,
            'title': obj.price_list.title
        } if obj.price_list else {}
