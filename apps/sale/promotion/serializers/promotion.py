from rest_framework import serializers

from apps.sale.promotion.models import Promotion, CustomerByList, CustomerByCondition, DiscountMethod, GiftMethod

__all__ = ['PromotionListSerializer', 'PromotionCreateSerializer']

from apps.shared import PromoMsg


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
            'discount_method'
        )


class PromotionCreateSerializer(serializers.ModelSerializer):
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

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": PromoMsg.PROMO_REQ_TITLE})

    @classmethod
    def validate_valid_date_start(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"valid_date_start": PromoMsg.PROMO_REQ_VALID_DATE})

    @classmethod
    def validate_valid_date_end(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"valid_date_end": PromoMsg.PROMO_REQ_VALID_DATE})\

    @classmethod
    def validate_customer_type(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"customer_type": PromoMsg.PROMO_REQ_VALID_DATE})

    def create(self, validated_data):
        # valid customer by list
        if 'customer_by_list' in validated_data:
            customer_list = validated_data['customer_by_list']
            if validated_data['customer_type'] == 1 and not customer_list:
                raise serializers.ValidationError({"customer": PromoMsg.PROMO_REQ_VALID_CUSTOMER_LIST})
        # valid customer by condition
        if 'customer_by_condition' in validated_data:
            customer_cond = validated_data['customer_by_condition']
            if validated_data['customer_type'] == 1 and not customer_cond:
                raise serializers.ValidationError({"customer": PromoMsg.PROMO_REQ_VALID_CUSTOMER_COND})

        # promotion = Promotion.objects.create(**validated_data)
        # list_term = validated_data['term']
        # if list_term:
        #     create_term(list_term, pm_term)
        return validated_data
