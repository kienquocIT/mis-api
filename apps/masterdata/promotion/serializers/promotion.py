from rest_framework import serializers

from apps.masterdata.promotion.models import Promotion, CustomerByList, CustomerByCondition, DiscountMethod, GiftMethod

__all__ = ['PromotionListSerializer', 'PromotionCreateSerializer', 'PromotionDetailSerializer',
           'PromotionUpdateSerializer']

from apps.masterdata.saledata.models import AccountAccountTypes, Product, AccountGroup, Industry

from apps.shared import PromoMsg, ACCOUNT_COMPANY_SIZE, ACCOUNT_REVENUE


def check_customer_list(data):
    customer = AccountAccountTypes.objects.filter(account__id__in=data, account_type__account_type_order=0)
    if len(data) != customer.count():
        return False
    return True


def check_customer_cond(data):
    for val in data:
        if 'property' in val:
            if int(val['property']) == 0 and not AccountGroup.objects.filter(id=val['result']).exists():
                raise serializers.ValidationError({"property_group": PromoMsg.ERROR_PROPERTY_GROUP})
            if int(val['property']) == 1 and not Industry.objects.filter(id=val['result']).exists():
                raise serializers.ValidationError({"property_industry": PromoMsg.ERROR_PROPERTY_INDUSTRY})
            if int(val['property']) == 2:
                is_check = any(item[0] == int(val['result']) for item in ACCOUNT_COMPANY_SIZE)
                if not is_check:
                    raise serializers.ValidationError({"property_industry": PromoMsg.ERROR_PROPERTY_COMPANY_SIZE})
            if int(val['property']) == 3:
                is_check2 = any(item[0] == int(val['result']) for item in ACCOUNT_REVENUE)
                if not is_check2:
                    raise serializers.ValidationError({"property_industry": PromoMsg.ERROR_PROPERTY_REVENUE})
    return True


def create_discount_method(validated_data, instance):
    discount_method = validated_data.get('discount_method', {})
    if discount_method:
        product_selected = discount_method.get('product_selected', {})
        del discount_method['product_selected']
        DiscountMethod.objects.create(
            **discount_method,
            promotion=instance,
            product_selected_id=product_selected.get('id', None)
        )


def create_gift_method(validated_data, instance):
    gift_method = validated_data.get('gift_method', {})
    if gift_method:
        product_received = gift_method.get('product_received', '')
        purchase_product = gift_method.get('purchase_product', '')
        del gift_method['purchase_product']
        del gift_method['product_received']
        if product_received:
            GiftMethod.objects.create(
                **gift_method,
                promotion=instance,
                product_received_id=product_received.get('id', None)
            )
        if purchase_product:
            GiftMethod.objects.create(
                **gift_method,
                promotion=instance,
                purchase_product_id=purchase_product.get('id', None)
            )


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
    product_selected = serializers.UUIDField()

    class Meta:
        model = DiscountMethod
        fields = (
            'before_after_tax',
            'percent_fix_amount',
            'percent_value',
            'max_percent_value',
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

    @classmethod
    def validate_product_selected(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(product.id),
                'title': str(product.title),
                'code': str(product.code),
            }
        except Product.DoesNotExist:
            return serializers.ValidationError({"product_selected": PromoMsg.ERROR_PRO_SELECTED})

    @classmethod
    def validate(cls, validate_data):  # pylint: disable=W0221
        if 'before_after_tax' not in validate_data:
            raise serializers.ValidationError({"before_after_tax": PromoMsg.ERROR_IS_BE_AF})
        if 'percent_fix_amount' not in validate_data:
            raise serializers.ValidationError({"percent_fix_amount": PromoMsg.ERROR_IS_PER_FIX})
        if bool(validate_data['percent_fix_amount']) and validate_data['percent_value'] == float(0):
            raise serializers.ValidationError({"percent_value": PromoMsg.ERROR_PERCENT_VALUE})
        if not bool(validate_data['percent_fix_amount']) and validate_data['fix_value'] == float(0):
            raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
        if 'use_count' not in validate_data:
            raise serializers.ValidationError({"use_count": PromoMsg.ERROR_USER_COUNT})
        if 'times_condition' not in validate_data:
            raise serializers.ValidationError({"times_condition": PromoMsg.ERROR_TIME_COND})
        if 'is_minimum' in validate_data and validate_data['minimum_value'] == float(0):
            raise serializers.ValidationError({"minimum_value": PromoMsg.ERROR_MINIMUM_PURCHASE})
        if 'is_on_product' in validate_data and 'product_selected' not in validate_data:
            raise serializers.ValidationError({"product_selected": PromoMsg.ERROR_PRO_SELECTED})
        if 'is_min_quantity' in validate_data and validate_data['num_minimum'] == int(0):
            raise serializers.ValidationError({"num_minimum": PromoMsg.ERROR_MINIMUM_QUANTITY})
        if 'free_shipping' in validate_data \
                and bool(validate_data['free_shipping']) \
                and ('fix_value' not in validate_data or validate_data['fix_value'] == float(0)):
            raise serializers.ValidationError({"fix_value": PromoMsg.ERROR_FIXED_AMOUNT})
        return validate_data


class GiftMethodSerializer(serializers.ModelSerializer):
    product_received = serializers.UUIDField()
    purchase_product = serializers.UUIDField()

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

    @classmethod
    def validate_product_received(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(product.id),
                'title': str(product.title),
                'code': str(product.code),
            }
        except Product.DoesNotExist:
            return serializers.ValidationError({"product_received": PromoMsg.ERROR_FREE_PRODUCT})

    @classmethod
    def validate_purchase_product(cls, value):
        try:
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(product.id),
                'title': str(product.title),
                'code': str(product.code),
            }
        except Product.DoesNotExist:
            return serializers.ValidationError({"purchase_product": PromoMsg.ERROR_PRODUCT_PURCHASE})

    @classmethod
    def validate(cls, validate_data):  # pylint: disable=W0221
        if bool(validate_data['is_free_product']):
            if validate_data['num_product_received'] == 0:
                raise serializers.ValidationError({"free_product": PromoMsg.ERROR_FREE_PRODUCT})
        if 'is_min_purchase' in validate_data and validate_data['is_min_purchase'] and \
                validate_data['min_purchase_cost'] == float(0):
            raise serializers.ValidationError({"min_purchase_cost": PromoMsg.ERROR_MIN_PURCHASE_TOTAL})
        if 'is_purchase' in validate_data and validate_data['is_purchase']:
            if validate_data['purchase_num'] == 0:
                raise serializers.ValidationError({"purchase_product": PromoMsg.ERROR_PRODUCT_PURCHASE})
        return validate_data


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

    @classmethod
    def validate(cls, validate_data):  # pylint: disable=W0221
        discount = validate_data.get('discount_method', {})
        gift = validate_data.get('gift_method', {})

        # valid customer by list
        if validate_data['customer_type'] == 1:
            customer_list = validate_data.get('customer_by_list', [])
            # check customer is available
            is_checked = check_customer_list(customer_list)
            if not is_checked:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})

        # valid customer by condition
        if validate_data['customer_type'] == 2:
            customer_cond = validate_data.get('customer_by_condition', [])
            is_checked = check_customer_cond(customer_cond)
            if not is_checked:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_COND})

        # valid discount method
        if validate_data.get('is_discount', False):
            if not discount:
                raise serializers.ValidationError({"discount_method": PromoMsg.ERROR_DISCOUNT_METHOD})

        if validate_data.get('is_gift', False):
            if not gift:
                raise serializers.ValidationError({"gift_method": PromoMsg.ERROR_GIFT})
        return validate_data

    def create(self, validated_data):
        instance = Promotion.objects.create(**validated_data)
        if instance:
            # create discount method
            create_discount_method(validated_data, instance)

            # create gift method
            create_gift_method(validated_data, instance)
        return instance


class PromotionDetailSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    get_customer_by_list = serializers.SerializerMethodField()
    get_customer_by_condition = serializers.SerializerMethodField()

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
        if obj.currency:
            return {
                'id': obj.currency_id,
                'title': obj.currency.title,
                'abbreviation': obj.currency.abbreviation,
            }
        return {}

    @classmethod
    def get_customer_by_list(cls, obj):  # pylint: disable=E0102
        return [
            {'id': item[0], 'name': item[1], 'code': item[2]}
            for item in CustomerByList.objects.filter(promotion=obj).values_list(
                'customer_id',
                'customer__name',
                'customer__code'
            )
        ]

    @classmethod
    def get_customer_by_condition(cls, obj):  # pylint: disable=E0102
        return [
            {
                'id': item[0], 'property': item[1], 'operator': item[2], 'result': item[3],
                'property_type': item[4], 'logic': item[5], 'order': item[6]
            }
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

    @classmethod
    def validate(cls, validate_data):  # pylint: disable=W0221
        discount = validate_data.get('discount_method', {})
        gift = validate_data.get('gift_method', {})

        # valid customer by list
        if validate_data['customer_type'] == 1:
            customer_list = validate_data.get('customer_by_list', [])
            # check customer is available
            is_checked = check_customer_list(customer_list)
            if not is_checked:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_LIST})

        # valid customer by condition
        if validate_data['customer_type'] == 2:
            customer_cond = validate_data.get('customer_by_condition', [])
            is_checked = check_customer_cond(customer_cond)
            if not is_checked:
                raise serializers.ValidationError({"customer": PromoMsg.ERROR_CUSTOMER_COND})

        # valid discount method
        if validate_data.get('is_discount', False):
            if not discount:
                raise serializers.ValidationError({"discount_method": PromoMsg.ERROR_DISCOUNT_METHOD})

        if validate_data.get('is_gift', False):
            if not gift:
                raise serializers.ValidationError({"gift_method": PromoMsg.ERROR_GIFT})
        return validate_data

    def update(self, instance, validated_data):
        # update
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # delete old discount and gift method and update if had new product
        if instance:
            discount = DiscountMethod.objects.filter(promotion=instance)
            if discount:
                discount.delete()
                create_discount_method(validated_data, instance)
            gift = GiftMethod.objects.filter(promotion=instance)
            if gift:
                gift.delete()
                create_gift_method(validated_data, instance)
        return instance
