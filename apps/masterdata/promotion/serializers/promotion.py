from rest_framework import serializers

from apps.masterdata.promotion.models import Promotion, CustomerByList, CustomerByCondition, DiscountMethod, GiftMethod

__all__ = ['PromotionListSerializer', 'PromotionCreateSerializer']

from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.product import Product

from apps.shared import PromoMsg


def check_customer_list(data):
    # for item in data:
    # customer = Account.objects.filter(id__in=data, title="Customner", is_active=True).exists()
    # if not customer:
    #     raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})
    return True


def check_discount_method(discount):
    if discount['percent_fix_amount']:
        if 'percent_value' not in discount and discount['percent_value'] == '':
            raise serializers.ValidationError({"percent_value": PromoMsg.ERROR_PERCENT_VALUE})
    else:
        if 'fix_value' not in discount and discount['fix_value'] == '':
            raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
    if discount['is_on_order']:
        if not discount['is_minimum'] and discount['minimum_value'] == 0:
            raise serializers.ValidationError({"minimum_value": PromoMsg.ERROR_MINIMUM_PURCHASE})
    if discount['is_on_product']:
        if not discount['product_selected']:
            raise serializers.ValidationError({"product_selected": PromoMsg.ERROR_PRO_SELECTED})
        product = Product.objects.filter(id=discount['product_selected']).exists()
        if not product:
            raise serializers.ValidationError({"product_selected": PromoMsg.ERROR_PRO_SELECTED})
        if discount['is_min_quantity'] and discount['num_minimum'] == 0:
            raise serializers.ValidationError({"product_selected": PromoMsg.ERROR_MINIMUM_QUANTITY})
    if discount['free_shipping'] and discount['fix_value'] == 0:
        raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
    return True

def check_gift_method(gift):

    return True

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
        raise serializers.ValidationError({"title": PromoMsg.ERROR_NAME})

    @classmethod
    def validate_valid_date_start(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"valid_date_start": PromoMsg.ERROR_VALID_DATE})

    @classmethod
    def validate_valid_date_end(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"valid_date_end": PromoMsg.ERROR_VALID_DATE})\

    @classmethod
    def validate_customer_type(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"customer_type": PromoMsg.ERROR_VALID_DATE})

    def create(self, validated_data):
        # valid customer by list
        if 'customer_by_list' in validated_data:
            customer_list = validated_data['customer_by_list']
            # check customer is available
            check_customer_list(customer_list)
            if validated_data['customer_type'] == 1 and not customer_list:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})
        # valid customer by condition
        if 'customer_by_condition' in validated_data:
            customer_cond = validated_data['customer_by_condition']
            if validated_data['customer_type'] == 1 and not customer_cond:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_COND})
        if 'is_discount' in validated_data and validated_data['is_discount']:
            discount = validated_data['discount_method']
            if not discount:
                raise serializers.ValidationError({"discount_method": PromoMsg.ERROR_DISCOUNT_METHOD})
            # check valid data when user select discount method
            check_discount_method(discount)
        if 'is_gift' in validated_data and validated_data['is_gift']:
            gift = validated_data['gift_method']
            if not gift:
                raise serializers.ValidationError({"gift_method": PromoMsg.ERROR_GIFT})

        # promotion = Promotion.objects.create(**validated_data)
        # list_term = validated_data['term']
        # if list_term:
        #     create_term(list_term, pm_term)
        return validated_data
