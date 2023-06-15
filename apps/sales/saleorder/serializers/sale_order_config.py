from rest_framework import serializers

from apps.sales.saleorder.models import SaleOrderAppConfig, ConfigOrderShortSale, ConfigOrderLongSale


class ShortConfigSerializer(serializers.ModelSerializer):
    is_choose_price_list = serializers.BooleanField(default=False)
    is_input_price = serializers.BooleanField(default=False)
    is_discount_on_product = serializers.BooleanField(default=False)
    is_discount_on_total = serializers.BooleanField(default=False)

    class Meta:
        model = ConfigOrderShortSale
        fields = (
            'is_choose_price_list',
            'is_input_price',
            'is_discount_on_product',
            'is_discount_on_total'
        )


class LongConfigSerializer(serializers.ModelSerializer):
    is_not_input_price = serializers.BooleanField(default=False)
    is_not_discount_on_product = serializers.BooleanField(default=False)
    is_not_discount_on_total = serializers.BooleanField(default=False)

    class Meta:
        model = ConfigOrderLongSale
        fields = (
            'is_not_input_price',
            'is_not_discount_on_product',
            'is_not_discount_on_total',
        )


class SaleOrderConfigUpdateSerializer(serializers.ModelSerializer):
    short_sale_config = ShortConfigSerializer()
    long_sale_config = LongConfigSerializer()

    class Meta:
        model = SaleOrderAppConfig
        fields = (
            'short_sale_config',
            'long_sale_config'
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # delete & create new short_sale_config
        instance.sale_order_config_short_sale.delete()
        ConfigOrderShortSale.objects.create(
            sale_order_config=instance,
            **validated_data['short_sale_config']
        )
        # delete & create new long_sale_config
        instance.sale_order_config_long_sale.delete()
        ConfigOrderLongSale.objects.create(
            sale_order_config=instance,
            **validated_data['long_sale_config']
        )
        return instance


class SaleOrderConfigDetailSerializer(serializers.ModelSerializer):
    short_sale_config = serializers.JSONField()
    long_sale_config = serializers.JSONField()

    class Meta:
        model = SaleOrderAppConfig
        fields = (
            'id',
            'short_sale_config',
            'long_sale_config'
        )
