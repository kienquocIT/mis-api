from copy import deepcopy

from rest_framework import serializers

from apps.masterdata.promotion.models import Promotion, CustomerByList, CustomerByCondition, DiscountMethod, GiftMethod

__all__ = ['PromotionListSerializer', 'PromotionCreateSerializer', 'PromotionDetailSerializer',
           'PromotionUpdateSerializer']

from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.product import Product

from apps.shared import PromoMsg


def check_customer_list():
    # customer = Account.objects.filter(id__in=data, is_active=True).exists()
    # if not customer:
    #     raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})
    return True
def check_customer_cond(data):
    result_list = []
    for val in data:
        result_list.append(val.result)
    customer = Account.objects.filter(id__in=result_list, is_active=True)
    if len(customer) != len(result_list):
        raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})
    return True


def check_discount_method(discount):
    if discount['percent_fix_amount']:
        if 'percent_value' not in discount or discount['percent_value'] == float(0):
            raise serializers.ValidationError({"percent_value": PromoMsg.ERROR_PERCENT_VALUE})
    else:
        if 'fix_value' not in discount or discount['fix_value'] == float(0):
            raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
    if 'is_on_order' in discount and discount['is_on_order']:
        if discount['is_minimum'] and discount['minimum_value'] == float(0):
            raise serializers.ValidationError({"minimum_value": PromoMsg.ERROR_MINIMUM_PURCHASE})
    if 'is_on_product' in discount and discount['is_on_product']:
        if not discount['product_selected']:
            raise serializers.ValidationError({"product_selected": PromoMsg.ERROR_PRO_SELECTED})
        if discount['is_min_quantity'] and discount['num_minimum'] == int(0):
            raise serializers.ValidationError({"num_minimum": PromoMsg.ERROR_MINIMUM_QUANTITY})
    if 'free_shipping' in discount \
            and discount['free_shipping'] \
            and ('fix_value' not in discount or discount['fix_value'] == float(0)):
        raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
    return True

def check_gift_method(gift):
    if gift['is_free_product']:
        product = Product.objects.filter(id=gift['product_received']).first()
        if not gift['num_product_received'] or product:
            raise serializers.ValidationError({"free_product": PromoMsg.ERROR_FREE_PRODUCT})
    if gift['is_min_purchase'] and gift['min_purchase_cost'] == 0:
        raise serializers.ValidationError({"min_purchase_cost": PromoMsg.ERROR_MIN_PURCHASE_TOTAL})
    if gift['is_purchase']:
        product = Product.objects.filter(id=gift['purchase_product']).first()
        if gift['purchase_num'] == 0 or not product:
            raise serializers.ValidationError({"purchase_product": PromoMsg.ERROR_PRODUCT_PURCHASE})
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
            'percent_value',
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
            'id',
            'title',
            'valid_date_end',
        )


class PromotionCreateSerializer(serializers.ModelSerializer):
    discount_method = DiscountMethodSerializer(required=False)
    gift_method = GiftMethodSerializer(required=False)
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
        raise serializers.ValidationError({"valid_date_end": PromoMsg.ERROR_VALID_DATE})

    @classmethod
    def validate_customer_type(cls, value):
        if isinstance(value, int):
            return value
        raise serializers.ValidationError({"customer_type": PromoMsg.ERROR_VALID_DATE})

    def create(self, validated_data):
        discount = deepcopy(validated_data.get('discount_method', {}))
        gift = deepcopy(validated_data.get('gift_method', {}))
        # valid customer by list
        if validated_data['customer_type'] == 1:
            # customer_list = validated_data.get('customer_by_list', [])
            # check customer is available
            check_customer_list()

        # valid customer by condition
        if validated_data['customer_type'] == 2:
            customer_cond = validated_data.get('customer_by_condition')
            check_customer_cond(customer_cond)

        if validated_data.get('is_discount'):
            if not discount:
                raise serializers.ValidationError({"discount_method": PromoMsg.ERROR_DISCOUNT_METHOD})
            # check valid data when user select discount method
            check_discount_method(discount)
            validated_data['discount_method']['product_selected'] = {
                'id': str(discount.get('product_selected').id),
                'title': str(discount.get('product_selected').title),
                'code': str(discount.get('product_selected').code)
            }
        elif validated_data.get('is_gift'):
            if not gift:
                raise serializers.ValidationError({"gift_method": PromoMsg.ERROR_GIFT})
            check_gift_method(gift)
            validated_data['gift_method']['product_received'] = {
                'id': str(gift.get('product_received').id),
                'title': str(gift.get('product_received').title),
                'code': str(gift.get('product_received').code)
            }
            if gift.get('purchase_product'):
                validated_data['gift_method']['purchase_product'] = {
                    'id': str(gift.get('purchase_product').id),
                    'title': str(gift.get('purchase_product').title),
                    'code': str(gift.get('purchase_product').code)
                }
        else:
            raise serializers.ValidationError({"method": PromoMsg.ERROR_MISSING_METHOD})
        instance = Promotion.objects.create(**validated_data)
        if instance:
            if validated_data.get('is_discount', False) and discount:
                DiscountMethod.objects.create(**discount, promotion=instance)
            if validated_data.get('is_gift', False) and gift:
                GiftMethod.objects.create(**gift, promotion=instance)
        return instance


class PromotionDetailSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    customer_by_list = serializers.SerializerMethodField()
    customer_by_condition = serializers.SerializerMethodField()
    discount_method = serializers.JSONField()
    gift_method = serializers.JSONField()
    class Meta:
        model = Promotion
        fields = (
            'id',
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
            'is_gift',
            'discount_method',
            'gift_method'
        )

    @classmethod
    def get_currency(cls, obj):
        currency = obj.currency
        return {
            'id': currency.id,
            'title': currency.title,
            'code': currency.code,
        }

    @classmethod
    def get_customer_by_list(cls, obj):
        return [
            {'id': item[0], 'name': item[1], 'code': item[2]}
            for item in CustomerByList.objects.filter(promotion=obj).values_list(
                'customer_id',
                'customer__name',
                'customer__code'
            )
        ]

    @classmethod
    def get_customer_by_condition(cls, obj):
        return [
            {'id': item[0], 'property': item[1], 'operator': item[2], 'result': item[3],
             'property_type': item[4], 'logic': item[5], 'order': item[6]}
            for item in CustomerByCondition.objects.filter(promotion=obj).values_list(
                'id',
                'property',
                'operator',
                'result',
                'property_type',
                'logic',
                'order'
            )
        ]


class PromotionUpdateSerializer(serializers.ModelSerializer):
    discount_method = DiscountMethodSerializer(required=False)
    gift_method = GiftMethodSerializer(required=False)
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
        raise serializers.ValidationError({"valid_date_end": PromoMsg.ERROR_VALID_DATE})

    @classmethod
    def validate_customer_type(cls, value):
        if isinstance(value, int):
            return value
        raise serializers.ValidationError({"customer_type": PromoMsg.ERROR_VALID_DATE})

    def update(self, instance, validated_data):
        # update
        for key, value in validated_data.items():
            setattr(instance, key, value)
        new_discount = deepcopy(validated_data.get('discount_method', {}))
        new_gift = deepcopy(validated_data.get('gift_method'), {})
        if new_discount:
            check_discount_method(new_discount)
            if new_discount.get('product_selected'):
                instance.discount_method['product_selected'] = {
                    'id': str(new_discount.get('product_selected').id),
                    'title': str(new_discount.get('product_selected').title),
                    'code': str(new_discount.get('product_selected').code)
                }
        if new_gift:
            check_gift_method(new_gift)
            if new_gift.get('product_received', None):
                instance.gift_method['product_received'] = {
                    'id': str(new_gift.get('product_received').id),
                    'title': str(new_gift.get('product_received').title),
                    'code': str(new_gift.get('product_received').code)
                }
            if new_gift.get('purchase_product', None):
                instance.gift_method['purchase_product'] = {
                    'id': str(new_gift.get('purchase_product').id),
                    'title': str(new_gift.get('purchase_product').title),
                    'code': str(new_gift.get('purchase_product').code)
                }
        instance.save()

        # delete old discount and gift
        if instance:
            discount = DiscountMethod.objects.filter(promotion=instance)
            if discount:
                discount.delete()
                if new_discount:
                    DiscountMethod.objects.create(**new_discount, promotion=instance)
            gift = GiftMethod.objects.filter(promotion=instance)
            if gift:
                gift.delete()
                if new_gift:
                    GiftMethod.objects.create(**new_gift, promotion=instance)
        return instance
