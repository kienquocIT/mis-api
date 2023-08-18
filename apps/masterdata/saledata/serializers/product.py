from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, Product
)
from apps.masterdata.saledata.models.price import Tax, Currency, Price
from apps.shared import ProductMsg
from .product_sub import CommonCreateUpdateProduct

PRODUCT_OPTION = [
    (0, _('Sale')),
    (1, _('Inventory')),
    (2, _('Purchase')),
]


class ProductListSerializer(serializers.ModelSerializer):
    general_product_type = serializers.SerializerMethodField()
    general_product_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_product_type',
            'general_product_category'
        )

    @classmethod
    def get_general_product_type(cls, obj):
        return {
           'id': str(obj.general_product_type.id),
           'title': obj.general_product_type.title,
           'code': obj.general_product_type.code
        }

    @classmethod
    def get_general_product_category(cls, obj):
        return {
            'id': str(obj.general_product_category.id),
            'title': obj.general_product_category.title,
            'code': obj.general_product_category.code
        }


def sub_validate_volume_obj(initial_data, validate_data):
    volume_obj = None
    if initial_data.get('volume_id', None):
        volume_obj = BaseItemUnit.objects.filter(id=initial_data['volume_id'])
    if volume_obj and validate_data.get('volume', None):
        volume_obj = volume_obj.first()
        return {
            'id': str(volume_obj.id),
            'title': volume_obj.title,
            'measure': volume_obj.measure,
            'value': validate_data['volume']
        }
    return {}


def sub_validate_weight_obj(initial_data, validate_data):
    weight_obj = None
    if initial_data.get('weight_id', None):
        weight_obj = BaseItemUnit.objects.filter(id=initial_data['weight_id'])
    if weight_obj and validate_data.get('weight', None):
        weight_obj = weight_obj.first()
        return {
            'id': str(weight_obj.id),
            'title': weight_obj.title,
            'measure': weight_obj.measure,
            'value': validate_data['weight']
        }
    return {}


def setup_price_list_data_in_sale(initial_data):
    sale_price_list = initial_data.get('sale_price_list', [])
    for item in sale_price_list:
        price_list_id = item.get('price_list_id', None)
        price_list_value = item.get('price_list_value', None)
        if not Price.objects.filter(id=price_list_id).exists() or not price_list_value:
            raise serializers.ValidationError({'sale_product_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
    return sale_price_list


class ProductCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
    )
    general_product_type = serializers.UUIDField()
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    sale_currency_using = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'title',
            'description',
            'product_choice',
            # General
            'general_product_type',
            'general_product_category',
            'general_uom_group',
            'width',
            'height',
            'length',
            'volume',
            'weight',
            # Sale
            'sale_default_uom',
            'sale_tax',
            'sale_currency_using',
            'sale_cost',
            # Inventory
            'inventory_uom',
            'inventory_level_min',
            'inventory_level_max',
            # Purchase
            'purchase_default_uom',
            'purchase_tax',
        )

    @classmethod
    def validate_general_product_type(cls, value):
        try:
            return ProductType.objects.get(id=value)
        except ProductType.DoesNotExist:
            raise serializers.ValidationError({'general_product_type': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_product_category(cls, value):
        try:
            return ProductCategory.objects.filter(id=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'general_product_category': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.filter(id=value)
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'general_product_uom_group': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_width(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'width': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_height(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'height': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_length(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'length': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_volume(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'volume': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_weight(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'weight': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_sale_default_uom(cls, value):
        if value:
            obj = UnitOfMeasure.objects.filter(id=value)
            if obj.count() == 1:
                return obj.first()
            raise serializers.ValidationError({'sale_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_tax(cls, value):
        if value:
            try:
                return Tax.objects.filter(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'sale_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_currency_using(cls, value):
        if value:
            try:
                return Currency.objects.filter(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'sale_currency_using': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_cost(cls, value):
        if value:
            if float(value) < 0:
                raise serializers.ValidationError({'sale_product_cost': ProductMsg.VALUE_INVALID})
            return value
        return None

    @classmethod
    def validate_inventory_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.filter(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'inventory_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_level_min(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_min': ProductMsg.NEGATIVE_VALUE})
            return value
        return None

    @classmethod
    def validate_inventory_level_max(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_max': ProductMsg.NEGATIVE_VALUE})
            return value
        return None

    @classmethod
    def validate_purchase_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.filter(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_purchase_tax(cls, value):
        if value:
            try:
                return Tax.objects.filter(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    def validate(self, validate_data):
        validate_data.update({'volume': sub_validate_volume_obj(self.initial_data, validate_data)})
        validate_data.update({'weight': sub_validate_weight_obj(self.initial_data, validate_data)})
        validate_data.update({'sale_product_price_list': setup_price_list_data_in_sale(self.initial_data)})
        return validate_data

    def create(self, validated_data):
        if Product.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'PRD.CODE.0001'
        else:
            latest_code = Product.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'PRD.CODE.000' + str(new_code)

        product = Product.objects.create(**validated_data, code=new_code)

        if 'volume' in validated_data and 'weight' in validated_data:
            measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
            if measure_data:
                CommonCreateUpdateProduct.create_measure(product, measure_data)
        if 0 in validated_data['product_choice']:
            CommonCreateUpdateProduct.create_price_list(
                product,
                self.initial_data.get('sale_price_list', []),
                validated_data
            )

        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()  # noqa
    sale_information = serializers.SerializerMethodField()
    inventory_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_information',
            'inventory_information',
            'sale_information',
            'purchase_information',
            'product_choice',
        )

    @classmethod
    def get_general_information(cls, obj):
        result = {
            'product_type': {
                'id': str(obj.general_product_type.id),
                'title': obj.general_product_type.title,
                'code': obj.general_product_type.code
            },
            'product_category': {
                'id': str(obj.general_product_category.id),
                'title': obj.general_product_category.title,
                'code': obj.general_product_category.code
            },
            'uom_group': {
                'id': str(obj.general_uom_group.id),
                'title': obj.general_uom_group.title,
                'code': obj.general_uom_group.code
            },
            'product_size': {
                "width": obj.width,
                "height": obj.height,
                "length": obj.length,
                "volume": {
                    "id": str(obj.volume['id']),
                    "title": obj.volume['title'],
                    "measure": obj.volume['measure'],
                    "value": obj.volume['value']
                } if obj.volume else {},
                "weight": {
                    "id": str(obj.weight['id']),
                    "title": obj.weight['title'],
                    "measure": obj.weight['measure'],
                    "value": obj.weight['value']
                } if obj.weight else {}
            }
        }
        return result

    @classmethod
    def get_sale_information(cls, obj):
        product_price_list = obj.product_price_product.all()
        sale_product_price_list = []
        for item in product_price_list:
            if item.uom_using_id == obj.sale_default_uom_id:
                sale_product_price_list.append(
                    {
                        'id': item.price_list_id,
                        'price': item.price,
                        'currency_using': item.currency_using.abbreviation,
                        'is_primary': item.currency_using.is_primary,
                        'title': item.price_list.title,
                        'is_auto_update': item.get_price_from_source
                    }
                )
        result = {
            'sale_product_cost': obj.sale_cost,
            'default_uom': {
                'id': str(obj.sale_default_uom.id),
                'title': obj.sale_default_uom.title,
                'code': obj.sale_default_uom.code
            } if obj.sale_default_uom else {},
            'tax': {
                'id': str(obj.sale_tax.id),
                'title': obj.sale_tax.title,
                'code': obj.sale_tax.code
            } if obj.sale_tax else {},
            'currency_using': {
                'id': str(obj.sale_currency_using.id),
                'title': obj.sale_currency_using.title,
                'code': obj.sale_currency_using.code,
                'abbreviation': obj.sale_currency_using.abbreviation
            } if obj.sale_currency_using else {},
            'sale_product_price_list': sale_product_price_list
        }
        return result

    @classmethod
    def get_inventory_information(cls, obj):
        result = {
            'uom': {
                'id': str(obj.inventory_uom.id),
                'title': obj.inventory_uom.title,
                'code': obj.inventory_uom.code
            } if obj.inventory_uom else {},
            'inventory_level_min': obj.inventory_level_min,
            'inventory_level_max': obj.inventory_level_max,
        }
        return result

    @classmethod
    def get_purchase_information(cls, obj):
        result = {
            'default_uom': {
                'id': str(obj.purchase_default_uom.id),
                'title': obj.purchase_default_uom.title,
                'code': obj.purchase_default_uom.code
            } if obj.purchase_default_uom else {},
            'tax': {
                'id': str(obj.purchase_tax.id),
                'title': obj.purchase_tax.title,
                'code': obj.purchase_tax.code
            } if obj.purchase_tax else {},
        }
        return result


class ProductUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
    )
    general_product_type = serializers.UUIDField()
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    sale_currency_using = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'title',
            'description',
            'product_choice',
            # General
            'general_product_type',
            'general_product_category',
            'general_uom_group',
            'width',
            'height',
            'length',
            'volume',
            'weight',
            # Sale
            'sale_default_uom',
            'sale_tax',
            'sale_currency_using',
            'sale_cost',
            # Inventory
            'inventory_uom',
            'inventory_level_min',
            'inventory_level_max',
            # Purchase
            'purchase_default_uom',
            'purchase_tax',
        )

    @classmethod
    def validate_general_product_type(cls, value):
        try:
            return ProductType.objects.get(id=value)
        except ProductType.DoesNotExist:
            raise serializers.ValidationError({'general_product_type': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_product_category(cls, value):
        try:
            return ProductCategory.objects.filter(id=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'general_product_category': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.filter(id=value)
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'general_product_uom_group': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_width(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'width': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_height(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'height': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_length(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'length': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_volume(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'volume': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_weight(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'weight': ProductMsg.PRODUCT_SIZE_IS_WRONG})
            return value
        return None

    @classmethod
    def validate_sale_default_uom(cls, value):
        if value:
            obj = UnitOfMeasure.objects.filter(id=value)
            if obj.count() == 1:
                return obj.first()
            raise serializers.ValidationError({'sale_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_tax(cls, value):
        if value:
            try:
                return Tax.objects.filter(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'sale_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_currency_using(cls, value):
        if value:
            try:
                return Currency.objects.filter(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'sale_currency_using': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_cost(cls, value):
        if value:
            if float(value) < 0:
                raise serializers.ValidationError({'sale_product_cost': ProductMsg.VALUE_INVALID})
            return value
        return None

    @classmethod
    def validate_inventory_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.filter(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'inventory_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_level_min(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_min': ProductMsg.NEGATIVE_VALUE})
            return value
        return None

    @classmethod
    def validate_inventory_level_max(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_max': ProductMsg.NEGATIVE_VALUE})
            return value
        return None

    @classmethod
    def validate_purchase_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.filter(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_purchase_tax(cls, value):
        if value:
            try:
                return Tax.objects.filter(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    def validate(self, validate_data):
        validate_data.update({'volume': sub_validate_volume_obj(self.initial_data, validate_data)})
        validate_data.update({'weight': sub_validate_weight_obj(self.initial_data, validate_data)})
        validate_data.update({'sale_product_price_list': setup_price_list_data_in_sale(self.initial_data)})
        return validate_data

    def update(self, instance, validated_data):
        instance.product_measure.all().delete()
        CommonCreateUpdateProduct.delete_price_list(
            instance,
            [i.get('id', None) for i in instance.sale_product_price_list]
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if 'volume' in validated_data and 'weight' in validated_data:
            measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
            if measure_data:
                CommonCreateUpdateProduct.create_measure(instance, measure_data)
        if 0 in validated_data['product_choice']:
            CommonCreateUpdateProduct.create_price_list(
                instance,
                self.initial_data.get('sale_price_list', []),
                validated_data
            )

        return instance


class ProductForSaleListSerializer(serializers.ModelSerializer):
    price_list = serializers.SerializerMethodField()
    product_choice = serializers.JSONField()
    sale_information = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'general_information',
            'sale_information',
            'price_list',
            'product_choice',
        )

    @classmethod
    def check_status_price(cls, valid_time_start, valid_time_end):
        current_time = timezone.now()
        if (not valid_time_start >= current_time) and (valid_time_end >= current_time):
            return 'Valid'
        if valid_time_end < current_time:
            return 'Expired'
        if valid_time_start >= current_time:
            return 'Invalid'
        return 'Undefined'

    @classmethod
    def get_price_list(cls, obj):
        return [
            {
                'id': price.price_list_id,
                'title': price.price_list.title,
                'value': price.price,
                'is_default': price.price_list.is_default,
                'price_status': cls.check_status_price(
                    price.price_list.valid_time_start,
                    price.price_list.valid_time_end
                ),
                'price_type': price.price_list.price_list_type,
            }
            for price in obj.product_price_product.all()
        ]

    @classmethod
    def get_sale_information(cls, obj):
        return {
            'default_uom': {
                'id': obj.default_uom_id,
                'title': obj.default_uom.title,
                'code': obj.default_uom.code
            } if obj.default_uom else {},
            'tax_code': {
                'id': obj.tax_code_id,
                'title': obj.tax_code.title,
                'code': obj.tax_code.code,
                'rate': obj.tax_code.rate
            } if obj.tax_code else {},
            'currency_using': {
                'id': obj.currency_using_id,
                'title': obj.currency_using.title,
                'code': obj.currency_using.code,
            } if obj.currency_using else {},
            'length': obj.length,
            'width': obj.width,
            'height': obj.height,
        }


class UnitOfMeasureOfGroupLaborListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = (
            'id',
            'title',
            'code',
            'group',
            'ratio',
        )

    @classmethod
    def get_group(cls, obj):
        return {
            'id': obj.group_id,
            'title': obj.group.title,
            'is_referenced_unit': obj.is_referenced_unit
        } if obj.group else {}
