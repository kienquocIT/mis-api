from rest_framework import serializers

from apps.sale.promotion.models import Promotion, CustomerByList, CustomerByCondition, DiscountMethod, GiftMethod

__all__ = ['PromotionListSerializer', 'PromotionCreateSerializer']


class CustomerByListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerByList
        fields = (
            'id',
            'customer',
        )


class CustomerByConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerByCondition
        fields = (
            'property',
            'operator',
            'result',
            'property_type',
            'logic',
            'order'
        )


class DiscountMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscountMethod
        fields = (
            'id',
            'promotion',
            'before_after_tax',
            'percent_fix_amount',
            'fix_value',
            'use_count',
            'times_condition',
            'max_usages',
            'is_on_order',
            'is_minimum',
            'minimum_value',
            'is_on_product',
            'product_selected',
            'is_min_quantity',
            'num_minimum',
            'free_shipping',
        )


class GiftMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftMethod
        fields = (
            'id',
            'promotion',
            'use_count',
            'times_condition',
            'max_usages',
            'is_free_product',
            'num_product_received',
            'product_received',
            'is_min_purchase',
            'before_after_tax',
            'min_purchase_cost',
            'is_purchase',
            'purchase_num',
            'purchase_product',
        )


class PromotionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = (
            'title',
            'valid_date_end',
        )


class PromotionCreateSerializer(serializers.ModelSerializer):
    customer_by_list = CustomerByListSerializer(many=True)
    customer_by_condition = CustomerByConditionSerializer(many=True)
    discount_method = DiscountMethodSerializer()
    gift_method = GiftMethodSerializer()

    class Meta:
        model = Promotion
        fields = (
            'title',
            'valid_date_start',
            'valid_date_end',
            'remark',
            'currency',
            'customer_type',
            'customer_by_list',
            'customer_by_condition',
            'customer_remark',
            'is_discount',
            'is_coupons',
            'is_gift',
            'discount_method',
            'gift_method'
        )

    # @classmethod
    # def validate_title(cls, value):
    #     if value:
    #         return value
    #     raise serializers.ValidationError({"title": "Title is required"})
    #
    # @classmethod
    # def validate_term(cls, value):
    #     if isinstance(value, list) and value:
    #         return value
    #     raise serializers.ValidationError({"term": "Term must be at least one rows"})

    def create(self, validated_data):
        promotion = Promotion.objects.create(**validated_data)
        # list_term = validated_data['term']
        # if list_term:
        #     create_term(list_term, pm_term)
        return promotion
