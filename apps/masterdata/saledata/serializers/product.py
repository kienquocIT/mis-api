from datetime import datetime
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.product import (
    ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, Product, ProductProductType,
    ProductVariantAttribute, ProductVariant
)
from apps.masterdata.saledata.models.price import Tax, Currency, Price
from apps.shared import ProductMsg, PriceMsg
from .product_sub import CommonCreateUpdateProduct

PRODUCT_OPTION = [
    (0, _('Sale')),
    (1, _('Inventory')),
    (2, _('Purchase')),
]


class ProductListSerializer(serializers.ModelSerializer):
    general_product_types_mapped = serializers.SerializerMethodField()
    general_product_category = serializers.SerializerMethodField()
    sale_tax = serializers.SerializerMethodField()
    sale_default_uom = serializers.SerializerMethodField()
    general_price = serializers.SerializerMethodField()
    general_uom_group = serializers.SerializerMethodField()
    inventory_uom = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_product_types_mapped',
            'general_product_category',
            'general_traceability_method',
            'general_uom_group',
            'sale_tax',
            'sale_default_uom',
            'product_choice',
            'general_price',
            'inventory_uom',
            # Transaction information
            'stock_amount',
            'wait_delivery_amount',
            'wait_receipt_amount',
            'available_amount',
            'is_public_website'
        )

    @classmethod
    def get_general_product_types_mapped(cls, obj):
        return [{
            'id': str(item.id),
            'title': item.title,
            'code': item.code,
            'cost_list': obj.get_unit_cost_list_of_all_warehouse()
        } for item in obj.general_product_types_mapped.all()]

    @classmethod
    def get_general_product_category(cls, obj):
        return {
            'id': obj.general_product_category_id,
            'title': obj.general_product_category.title,
            'code': obj.general_product_category.code
        } if obj.general_product_category else {}

    @classmethod
    def get_general_uom_group(cls, obj):
        return {
            'id': obj.general_uom_group_id,
            'title': obj.general_uom_group.title,
            'code': obj.general_uom_group.code
        } if obj.general_uom_group else {}

    @classmethod
    def get_sale_tax(cls, obj):
        return {
            'id': obj.sale_tax_id,
            'title': obj.sale_tax.title,
            'code': obj.sale_tax.code,
            'rate': obj.sale_tax.rate
        } if obj.sale_tax else {}

    @classmethod
    def get_sale_default_uom(cls, obj):
        return {
            'id': obj.sale_default_uom_id,
            'title': obj.sale_default_uom.title,
            'code': obj.sale_default_uom.code,
        } if obj.sale_default_uom else {}

    @classmethod
    def get_general_price(cls, obj):
        return obj.sale_price

    @classmethod
    def get_inventory_uom(cls, obj):
        return {
            "id": str(obj.inventory_uom.id),
            "title": obj.inventory_uom.title
        } if obj.inventory_uom else {}


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


def create_product_types_mapped(product_obj, product_types_mapped_list):
    bulk_info = []
    for item in product_types_mapped_list:
        bulk_info.append(ProductProductType(product=product_obj, product_type_id=item))
    ProductProductType.objects.filter(product=product_obj).delete()
    ProductProductType.objects.bulk_create(bulk_info)
    return True


def check_expired_price_list(price_list):
    if not price_list.valid_time_end.date() < datetime.now().date():
        return True
    return False


def create_product_variant_attribute(product_obj, product_variant_attribute_list):
    bulk_info = []
    for item in product_variant_attribute_list:
        bulk_info.append(ProductVariantAttribute(product=product_obj, **item))
    ProductVariantAttribute.objects.filter(product=product_obj).delete()
    ProductVariantAttribute.objects.bulk_create(bulk_info)
    return True


def create_product_variant_item(product_obj, product_variant_item_list):
    bulk_info = []
    for item in product_variant_item_list:
        bulk_info.append(ProductVariant(product=product_obj, **item))
    ProductVariant.objects.bulk_create(bulk_info)
    return True


def update_product_variant_item(product_obj, product_variant_item_update_list):
    bulk_info = []
    for item in product_variant_item_update_list:
        if item.get('variant_value_id', None):
            variant_value_id = item.pop('variant_value_id')
            ProductVariant.objects.filter(id=variant_value_id).update(**item)
        else:
            bulk_info.append(ProductVariant(product=product_obj, **item))
    ProductVariant.objects.bulk_create(bulk_info)
    return True


class ProductCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
    )
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    sale_currency_using = serializers.UUIDField(required=False, allow_null=True)
    online_price_list = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    available_notify_quantity = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'description',
            'product_choice',
            # General
            'general_product_category',
            'general_uom_group',
            'general_traceability_method',
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
            'online_price_list',
            'available_notify',
            'available_notify_quantity',
            # Inventory
            'inventory_uom',
            'inventory_level_min',
            'inventory_level_max',
            # Purchase
            'purchase_default_uom',
            'purchase_tax',
            'is_public_website'
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Product.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})

    @classmethod
    def validate_general_product_category(cls, value):
        try:
            return ProductCategory.objects.get(id=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'general_product_category': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.get(id=value)
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
    def validate_available_notify_quantity(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'available_notify_quantity': ProductMsg.VALUE_INVALID})
            return value
        return None

    @classmethod
    def validate_sale_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'sale_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_currency_using(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
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
    def validate_online_price_list(cls, value):
        if value:
            try:
                price_list = Price.objects.get(id=value)
                if check_expired_price_list(price_list):
                    return price_list
                raise serializers.ValidationError(PriceMsg.PRICE_LIST_FOR_ONLINE_EXPIRED)
            except Price.DoesNotExist:
                raise serializers.ValidationError({'online_price_list': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
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
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_purchase_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    def create(self, validated_data):
        validated_data.update({'volume': sub_validate_volume_obj(self.initial_data, validated_data)})
        validated_data.update({'weight': sub_validate_weight_obj(self.initial_data, validated_data)})
        validated_data.update({'sale_product_price_list': setup_price_list_data_in_sale(self.initial_data)})
        product = Product.objects.create(**validated_data)
        create_product_types_mapped(product, self.initial_data.get('product_types_mapped_list', []))
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
        create_product_variant_attribute(product, self.initial_data.get('product_variant_attribute_list', []))
        create_product_variant_item(product, self.initial_data.get('product_variant_item_list', []))
        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()  # noqa
    sale_information = serializers.SerializerMethodField()
    inventory_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()
    product_warehouse_detail = serializers.SerializerMethodField()
    product_variant_attribute_list = serializers.SerializerMethodField()
    product_variant_item_list = serializers.SerializerMethodField()

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
            'product_warehouse_detail',
            # Transaction information
            'stock_amount',
            'wait_delivery_amount',
            'wait_receipt_amount',
            'available_amount',
            'is_public_website',
            'product_variant_attribute_list',
            'product_variant_item_list'
        )

    @classmethod
    def get_general_information(cls, obj):
        result = {
            'general_product_types_mapped': [{
                'id': str(product_type.id), 'title': product_type.title, 'code': product_type.code
            } for product_type in obj.general_product_types_mapped.all()],
            'product_category': {
                'id': obj.general_product_category_id,
                'title': obj.general_product_category.title,
                'code': obj.general_product_category.code
            },
            'uom_group': {
                'id': obj.general_uom_group_id,
                'title': obj.general_uom_group.title,
                'code': obj.general_uom_group.code
            },
            'traceability_method': obj.general_traceability_method,
            'product_size': {
                "width": obj.width, "height": obj.height, "length": obj.length,
                "volume": {
                    "id": str(obj.volume['id']),
                    "title": obj.volume['title'],
                    "measure": obj.volume['measure'],
                    "value": obj.volume['value']
                } if 'id' in obj.volume else {},
                "weight": {
                    "id": str(obj.weight['id']),
                    "title": obj.weight['title'],
                    "measure": obj.weight['measure'],
                    "value": obj.weight['value']
                } if 'id' in obj.weight else {}
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
                'id': obj.sale_default_uom_id,
                'title': obj.sale_default_uom.title,
                'code': obj.sale_default_uom.code
            } if obj.sale_default_uom else {},
            'tax': {
                'id': obj.sale_tax_id,
                'title': obj.sale_tax.title,
                'code': obj.sale_tax.code
            } if obj.sale_tax else {},
            'currency_using': {
                'id': obj.sale_currency_using_id,
                'title': obj.sale_currency_using.title,
                'code': obj.sale_currency_using.code,
                'abbreviation': obj.sale_currency_using.abbreviation
            } if obj.sale_currency_using else {},
            'sale_product_price_list': sale_product_price_list,
            'price_list_for_online_sale': {
                'id': obj.online_price_list_id,
                'title': obj.online_price_list.title,
            } if obj.online_price_list else {},
            'available_notify': obj.available_notify,
            'available_notify_quantity': obj.available_notify_quantity
        }
        return result

    @classmethod
    def get_inventory_information(cls, obj):
        result = {
            'uom': {
                'id': obj.inventory_uom_id, 'title': obj.inventory_uom.title, 'code': obj.inventory_uom.code
            } if obj.inventory_uom else {},
            'inventory_level_min': obj.inventory_level_min,
            'inventory_level_max': obj.inventory_level_max,
        }
        return result

    @classmethod
    def get_purchase_information(cls, obj):
        result = {
            'default_uom': {
                'id': obj.purchase_default_uom_id,
                'title': obj.purchase_default_uom.title,
                'code': obj.purchase_default_uom.code
            } if obj.purchase_default_uom else {},
            'tax': {
                'id': obj.purchase_tax_id, 'title': obj.purchase_tax.title, 'code': obj.purchase_tax.code
            } if obj.purchase_tax else {},
        }
        return result

    @classmethod
    def get_product_warehouse_detail(cls, obj):
        result = []
        product_warehouse = obj.product_warehouse_product.all().select_related(
            'warehouse', 'uom'
        ).order_by('warehouse__code')
        for item in product_warehouse:
            uom_ratio_src = obj.inventory_uom.ratio if obj.inventory_uom else 0
            uom_ratio_des = item.uom.ratio if item.uom else 0
            if uom_ratio_src and uom_ratio_des:
                ratio_convert = float(uom_ratio_src / uom_ratio_des)
                result.append({
                    'id': item.id,
                    'warehouse': {
                        'id': item.warehouse_id, 'title': item.warehouse.title, 'code': item.warehouse.code,
                    } if item.warehouse else {},
                    'stock_amount': ratio_convert * item.stock_amount,
                    'cost': obj.get_unit_cost_by_warehouse(item.warehouse_id)
                })
        return result

    @classmethod
    def get_product_variant_attribute_list(cls, obj):
        return [{
            'id': item.id,
            'attribute_title': item.attribute_title,
            'attribute_value_list': item.attribute_value_list,
            'attribute_config': item.attribute_config
        } for item in obj.product_variant_attributes.all()]

    @classmethod
    def get_product_variant_item_list(cls, obj):
        return [{
            'id': item.id,
            'variant_value_list': item.variant_value_list,
            'variant_name': item.variant_name,
            'variant_des': item.variant_des,
            'variant_SKU': item.variant_SKU,
            'variant_extra_price': item.variant_extra_price,
            'is_active': item.is_active,
        } for item in obj.product_variants.all()]


class ProductUpdateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    product_choice = serializers.ListField(
        child=serializers.ChoiceField(choices=PRODUCT_OPTION),
    )
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    sale_currency_using = serializers.UUIDField(required=False, allow_null=True)
    online_price_list = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    available_notify_quantity = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'code',
            'title',
            'description',
            'product_choice',
            # General
            'general_product_category',
            'general_uom_group',
            'general_traceability_method',
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
            'online_price_list',
            'available_notify',
            'available_notify_quantity',
            # Inventory
            'inventory_uom',
            'inventory_level_min',
            'inventory_level_max',
            # Purchase
            'purchase_default_uom',
            'purchase_tax',
            'is_public_website'
        )

    def validate_code(self, value):
        if value:
            if Product.objects.filter_current(
                    fill__tenant=True, fill__company=True, code=value
            ).exclude(code=self.instance.code).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})

    @classmethod
    def validate_general_product_category(cls, value):
        try:
            return ProductCategory.objects.get(id=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'general_product_category': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_general_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.get(id=value)
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
    def validate_available_notify_quantity(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'available_notify_quantity': ProductMsg.VALUE_INVALID})
            return value
        return None

    @classmethod
    def validate_sale_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_online_price_list(cls, value):
        if value:
            try:
                price_list = Price.objects.get(id=value)
                if check_expired_price_list(price_list):
                    return price_list
                raise serializers.ValidationError(PriceMsg.PRICE_LIST_FOR_ONLINE_EXPIRED)
            except Price.DoesNotExist:
                raise serializers.ValidationError({'online_price_list': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_currency_using(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
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
    def validate_sale_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'sale_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
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
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_purchase_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.DOES_NOT_EXIST})
        return None

    def update(self, instance, validated_data):
        validated_data.update({'volume': sub_validate_volume_obj(self.initial_data, validated_data)})
        validated_data.update({'weight': sub_validate_weight_obj(self.initial_data, validated_data)})
        validated_data.update({'sale_product_price_list': setup_price_list_data_in_sale(self.initial_data)})
        instance.product_measure.all().delete()
        CommonCreateUpdateProduct.delete_price_list(
            instance,
            [i.get('price_list_id', None) for i in instance.sale_product_price_list]
        )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_product_types_mapped(instance, self.initial_data.get('product_types_mapped_list', []))
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
        create_product_variant_attribute(instance, self.initial_data.get('product_variant_attribute_list', []))
        update_product_variant_item(instance, self.initial_data.get('product_variant_item_list', []))
        return instance


class ProductForSaleListSerializer(serializers.ModelSerializer):
    price_list = serializers.SerializerMethodField()
    product_choice = serializers.JSONField()
    general_information = serializers.SerializerMethodField()
    sale_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()
    cost_list = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_information',
            'description',
            'purchase_information',
            'sale_information',
            'purchase_information',
            'price_list',
            'product_choice',
            'sale_cost',
            'cost_list',
        )

    @classmethod
    def check_status_price(cls, valid_time_start, valid_time_end):
        current_time = datetime.now().date()
        if (not valid_time_start.date() >= current_time) and (valid_time_end.date() >= current_time):
            return 'Valid'
        if valid_time_end.date() < current_time:
            return 'Expired'
        if valid_time_start.date() >= current_time:
            return 'Invalid'
        return 'Undefined'

    @classmethod
    def get_price_list(cls, obj):
        return [
            {
                'id': str(price.price_list_id), 'title': price.price_list.title,
                'value': price.price, 'is_default': price.price_list.is_default,
                'price_status': cls.check_status_price(
                    price.price_list.valid_time_start,
                    price.price_list.valid_time_end
                ), 'price_type': price.price_list.price_list_type,
            }
            for price in obj.product_price_product.all()
        ]

    @classmethod
    def get_general_information(cls, obj):
        return {
            'product_type': [{
                'id': str(product_type.id), 'title': product_type.title,
                'code': product_type.code
            } for product_type in obj.general_product_types_mapped.all()],
            'product_category': {
                'id': str(obj.general_product_category_id), 'title': obj.general_product_category.title,
                'code': obj.general_product_category.code
            } if obj.general_product_category else {},
            'uom_group': {
                'id': str(obj.general_uom_group_id), 'title': obj.general_uom_group.title,
                'code': obj.general_uom_group.code
            } if obj.general_uom_group else {},
        }

    @classmethod
    def get_sale_information(cls, obj):
        return {
            'default_uom': {
                'id': str(obj.sale_default_uom_id), 'title': obj.sale_default_uom.title,
                'code': obj.sale_default_uom.code, 'ratio': obj.sale_default_uom.ratio,
                'rounding': obj.sale_default_uom.rounding,
                'is_referenced_unit': obj.sale_default_uom.is_referenced_unit,
            } if obj.sale_default_uom else {},
            'tax_code': {
                'id': str(obj.sale_tax_id), 'title': obj.sale_tax.title,
                'code': obj.sale_tax.code, 'rate': obj.sale_tax.rate
            } if obj.sale_tax else {},
            'currency_using': {
                'id': str(obj.sale_currency_using_id), 'title': obj.sale_currency_using.title,
                'code': obj.sale_currency_using.code,
            } if obj.sale_currency_using else {},
            'length': obj.length,
            'width': obj.width,
            'height': obj.height,
        }

    @classmethod
    def get_purchase_information(cls, obj):
        return {
            'uom': {
                'id': str(obj.purchase_default_uom_id), 'title': obj.purchase_default_uom.title,
                'code': obj.purchase_default_uom.code, 'ratio': obj.purchase_default_uom.ratio,
                'rounding': obj.purchase_default_uom.rounding,
                'is_referenced_unit': obj.purchase_default_uom.is_referenced_unit,
            } if obj.purchase_default_uom else {},
            'tax': {
                'id': str(obj.purchase_tax_id), 'title': obj.purchase_tax.title,
                'code': obj.purchase_tax.code, 'rate': obj.purchase_tax.rate,
            } if obj.purchase_tax else {},
        }

    @classmethod
    def get_cost_list(cls, obj):
        wh_dict = {}
        for product_inventory in obj.report_inventory_by_month_product.all():
            if str(product_inventory.warehouse_id) not in wh_dict:
                wh_dict.update({
                    str(product_inventory.warehouse_id): {
                        'warehouse': {
                            'id': str(product_inventory.warehouse_id),
                            'title': product_inventory.warehouse.title,
                            'code': product_inventory.warehouse.code
                        } if product_inventory.warehouse else {},
                        'cost': product_inventory.current_cost
                    }
                })
        return [value for key, value in wh_dict.items()]


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
