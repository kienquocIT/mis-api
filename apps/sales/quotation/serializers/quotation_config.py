from rest_framework import serializers

from apps.sales.quotation.models import QuotationAppConfig, ConfigShortSale, ConfigLongSale


class ShortConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigShortSale
        fields = (
            'is_choose_price_list',
            'is_input_price',
            'is_discount_on_product',
            'is_discount_on_total'
        )


class LongConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigLongSale
        fields = (
            'is_not_input_price',
            'is_not_discount_on_product',
            'is_not_discount_on_total',
        )


class QuotationConfigUpdateSerializer(serializers.ModelSerializer):
    short_sale_config = ShortConfigSerializer()
    long_sale_config = LongConfigSerializer()

    class Meta:
        model = QuotationAppConfig
        fields = (
            'short_sale_config',
            'long_sale_config'
        )


class QuotationConfigDetailSerializer(serializers.ModelSerializer):
    short_sale_config = serializers.JSONField()
    long_sale_config = serializers.JSONField()

    class Meta:
        model = QuotationAppConfig
        fields = (
            'short_sale_config',
            'long_sale_config'
        )
