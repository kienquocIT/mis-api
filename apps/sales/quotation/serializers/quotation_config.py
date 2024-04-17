from rest_framework import serializers

from apps.sales.quotation.models import QuotationAppConfig, ConfigShortSale, ConfigLongSale


class ShortConfigSerializer(serializers.ModelSerializer):
    is_choose_price_list = serializers.BooleanField(default=False)
    is_input_price = serializers.BooleanField(default=False)
    is_discount_on_product = serializers.BooleanField(default=False)
    is_discount_on_total = serializers.BooleanField(default=False)

    class Meta:
        model = ConfigShortSale
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
            'long_sale_config',
            'is_require_payment',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # delete & create new short_sale_config
        instance.quotation_config_short_sale.delete()
        ConfigShortSale.objects.create(
            quotation_config=instance,
            **validated_data['short_sale_config']
        )
        # delete & create new long_sale_config
        instance.quotation_config_long_sale.delete()
        ConfigLongSale.objects.create(
            quotation_config=instance,
            **validated_data['long_sale_config']
        )
        return instance


class QuotationConfigDetailSerializer(serializers.ModelSerializer):
    short_sale_config = serializers.JSONField()
    long_sale_config = serializers.JSONField()

    class Meta:
        model = QuotationAppConfig
        fields = (
            'id',
            'short_sale_config',
            'long_sale_config',
            'is_require_payment',
        )
