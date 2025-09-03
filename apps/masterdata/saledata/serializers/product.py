from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.utils import AccountDeterminationForProductHandler
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models.product import ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, Product, \
    Manufacturer
from apps.masterdata.saledata.models.price import Tax, Currency, Price, ProductPriceList
from apps.sales.report.utils.inventory_log import ReportInvCommonFunc
from apps.shared import ProductMsg, PriceMsg, BaseMsg
from .product_sub import ProductCommonFunction
from ..models import ProductWareHouse

PRODUCT_OPTION = [(0, _('Sale')), (1, _('Inventory')), (2, _('Purchase'))]


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    if inventory_uom:
        return (log_quantity / inventory_uom.ratio) if inventory_uom.ratio else 0
    return 0


class ProductListSerializer(serializers.ModelSerializer):
    general_product_types_mapped = serializers.SerializerMethodField()
    general_product_category = serializers.SerializerMethodField()
    sale_tax = serializers.SerializerMethodField()
    sale_default_uom = serializers.SerializerMethodField()
    general_price = serializers.SerializerMethodField()
    general_uom_group = serializers.SerializerMethodField()
    inventory_uom = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'code', 'title', 'description',
            'product_choice',
            'general_product_types_mapped',
            'general_product_category',
            'general_traceability_method',
            'general_uom_group',
            'general_price',
            'sale_tax', 'sale_default_uom', 'is_public_website',
            'inventory_uom', 'valuation_method',
            'purchase_information',
            # Transaction information
            'stock_amount', 'wait_delivery_amount', 'wait_receipt_amount', 'available_amount', 'production_amount'
        )

    @classmethod
    def get_general_product_types_mapped(cls, obj):
        return [{
            'id': str(item.id), 'title': item.title, 'code': item.code,
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
            'id': obj.general_uom_group_id, 'title': obj.general_uom_group.title, 'code': obj.general_uom_group.code
        } if obj.general_uom_group else {}

    @classmethod
    def get_sale_tax(cls, obj):
        return {
            'id': obj.sale_tax_id, 'title': obj.sale_tax.title, 'code': obj.sale_tax.code, 'rate': obj.sale_tax.rate
        } if obj.sale_tax else {}

    @classmethod
    def get_sale_default_uom(cls, obj):
        return {
            'id': obj.sale_default_uom_id, 'title': obj.sale_default_uom.title, 'code': obj.sale_default_uom.code,
        } if obj.sale_default_uom else {}

    @classmethod
    def get_general_price(cls, obj):
        return obj.sale_price

    @classmethod
    def get_inventory_uom(cls, obj):
        return {
            "id": str(obj.inventory_uom.id), "title": obj.inventory_uom.title, 'ratio': obj.inventory_uom.ratio
        } if obj.inventory_uom else {}

    @classmethod
    def get_purchase_information(cls, obj):
        result = {
            'default_uom': {
                'id': obj.purchase_default_uom_id,
                'title': obj.purchase_default_uom.title,
                'code': obj.purchase_default_uom.code
            } if obj.purchase_default_uom else {},
            'tax': {
                'id': obj.purchase_tax_id,
                'title': obj.purchase_tax.title,
                'code': obj.purchase_tax.code,
                'rate': obj.purchase_tax.rate,
            } if obj.purchase_tax else {},
            'supplied_by': obj.supplied_by
        }
        return result


class ProductCreateSerializer(serializers.ModelSerializer):
    product_choice = serializers.ListField(child=serializers.ChoiceField(choices=PRODUCT_OPTION))
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    general_manufacturer = serializers.UUIDField(required=False, allow_null=True)
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    online_price_list = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    valuation_method = serializers.IntegerField(default=1, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    available_notify_quantity = serializers.FloatField(required=False, allow_null=True)
    duration_unit = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'code', 'title', 'description', 'product_choice', 'part_number',
            # General
            'general_product_category', 'general_uom_group', 'general_traceability_method', 'general_manufacturer',
            'standard_price', 'width', 'height', 'length', 'volume', 'weight',
            # Sale
            'sale_default_uom', 'sale_tax', 'online_price_list', 'available_notify', 'available_notify_quantity',
            # Inventory
            'inventory_uom', 'inventory_level_min', 'inventory_level_max', 'is_public_website',
            'valuation_method',
            # Purchase
            'purchase_default_uom', 'purchase_tax', 'supplied_by',
            # Accounting
            'account_deter_referenced_by',
            # Attribute
            'duration_unit'
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Product.objects.filter_on_company(code=value).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
            return value
        code_generated = CompanyFunctionNumber.auto_gen_code_based_on_config(app_code='product')
        if code_generated:
            return code_generated
        raise serializers.ValidationError({"code": f"{ProductMsg.CODE_NOT_NULL}. {BaseMsg.NO_CONFIG_AUTO_CODE}"})

    @classmethod
    def validate_product_choice(cls, value):
        value = list(map(int, value))
        for item in value:
            if item not in [0, 1, 2]:
                raise serializers.ValidationError({'product_choice': ProductMsg.INVALID_PRODUCT_CHOICE_VALUE})
        return value

    @classmethod
    def validate_general_product_category(cls, value):
        try:
            return ProductCategory.objects.get(id=value)
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'general_product_category': ProductMsg.PRODUCT_CATEGORY_NOT_EXIST})

    @classmethod
    def validate_general_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.get(id=value)
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'general_product_uom_group': ProductMsg.UOM_GROUP_NOT_EXIST})

    @classmethod
    def validate_general_manufacturer(cls, value):
        if value:
            try:
                return Manufacturer.objects.get(id=value)
            except Manufacturer.DoesNotExist:
                raise serializers.ValidationError({'general_manufacturer': ProductMsg.MANUFACTURER_DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_available_notify_quantity(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError(
                    {'available_notify_quantity': ProductMsg.NOTIFY_AVAILABLE_QUANTITY_VALUE_IS_WRONG}
                )
            return value
        return None

    @classmethod
    def validate_sale_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_sale_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'sale_tax': ProductMsg.TAX_NOT_EXIST})
        return None

    @classmethod
    def validate_online_price_list(cls, value):
        if value:
            try:
                price_list = Price.objects.get(id=value)
                if not Price.is_expired(price_list):
                    return price_list
                raise serializers.ValidationError(PriceMsg.PRICE_LIST_FOR_ONLINE_EXPIRED)
            except Price.DoesNotExist:
                raise serializers.ValidationError({'online_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'inventory_uom': ProductMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_inventory_level_min(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_min': ProductMsg.NEGATIVE_INVENTORY_VALUE})
            return value
        return None

    @classmethod
    def validate_inventory_level_max(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError({'inventory_level_max': ProductMsg.NEGATIVE_INVENTORY_VALUE})
            return value
        return None

    @classmethod
    def validate_valuation_method(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError({'valuation_method': ProductMsg.INVALID_VALUATION_METHOD})

    @classmethod
    def validate_purchase_default_uom(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.UOM_NOT_EXIST})
        return None

    @classmethod
    def validate_purchase_tax(cls, value):
        if value:
            try:
                return Tax.objects.get(id=value)
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.TAX_NOT_EXIST})
        return None

    @classmethod
    def validate_duration_unit(cls, value):
        if value:
            try:
                return UnitOfMeasure.objects.get(id=value)
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'duration_unit': ProductMsg.UOM_NOT_EXIST})
        return None

    def validate(self, validate_data):
        # validate dimension
        validate_data['width'] = ProductCommonFunction.validate_dimension(
            validate_data.get('width'), 'width', ProductMsg.W_IS_WRONG
        )
        validate_data['height'] = ProductCommonFunction.validate_dimension(
            validate_data.get('height'), 'height', ProductMsg.H_IS_WRONG
        )
        validate_data['length'] = ProductCommonFunction.validate_dimension(
            validate_data.get('length'), 'length', ProductMsg.L_IS_WRONG
        )
        validate_data['volume'] = ProductCommonFunction.validate_dimension(
            validate_data.get('volume'), 'volume', ProductMsg.VLM_IS_WRONG
        )
        validate_data['weight'] = ProductCommonFunction.validate_dimension(
            validate_data.get('weight'), 'weight', ProductMsg.WGT_IS_WRONG
        )
        # add sale_currency_using
        primary_crc = Currency.objects.filter_on_company(is_primary=True).first()
        if not primary_crc:
            raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_NOT_EXIST})
        validate_data['sale_currency_using'] = primary_crc

        if 1 in validate_data.get('product_choice', []):
            validate_data['duration_unit'] = None

        return validate_data

    def create(self, validated_data):
        validated_data.update(
            {'volume': ProductCommonFunction.sub_validate_volume_obj(self.initial_data, validated_data)}
        )
        validated_data.update(
            {'weight': ProductCommonFunction.sub_validate_weight_obj(self.initial_data, validated_data)}
        )
        validated_data.update(
            {'sale_product_price_list': ProductCommonFunction.setup_price_list_data_in_sale(self.initial_data)}
        )
        product_obj = Product.objects.create(**validated_data)
        ProductCommonFunction.create_product_types_mapped(
            product_obj, self.initial_data.get('product_types_mapped_list', [])
        )
        if 'volume' in validated_data and 'weight' in validated_data:
            measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
            if measure_data:
                ProductCommonFunction.create_measure(product_obj, measure_data)
        if 0 in validated_data.get('product_choice', []):
            ProductCommonFunction.create_price_list(
                product_obj,
                self.initial_data.get('sale_price_list', []),
                validated_data
            )

        ProductCommonFunction.create_component_mapped(
            product_obj, self.initial_data.get('component_list_data', [])
        )

        ProductCommonFunction.create_attribute_mapped(
            product_obj, self.initial_data.get('attribute_list_data', [])
        )

        ProductCommonFunction.create_product_variant_attribute(
            product_obj, self.initial_data.get('product_variant_attribute_list', [])
        )
        ProductCommonFunction.create_product_variant_item(
            product_obj, self.initial_data.get('product_variant_item_list', [])
        )
        AccountDeterminationForProductHandler.create_account_determination_for_product(product_obj, 0)
        AccountDeterminationForProductHandler.create_account_determination_for_product(product_obj, 1)
        AccountDeterminationForProductHandler.create_account_determination_for_product(product_obj, 2)
        AccountDeterminationForProductHandler.create_account_determination_for_product(product_obj, 3)
        CompanyFunctionNumber.auto_code_update_latest_number(app_code='product')
        return product_obj


class ProductQuickCreateSerializer(serializers.ModelSerializer):
    product_choice = serializers.ListField(child=serializers.ChoiceField(choices=PRODUCT_OPTION))
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    sale_default_uom = serializers.UUIDField(required=False)
    sale_tax = serializers.UUIDField(required=False)

    class Meta:
        model = Product
        fields = (
            'code', 'title', 'product_choice',
            'general_product_category', 'general_uom_group', 'general_traceability_method',
            'sale_default_uom', 'sale_tax',
        )

    @classmethod
    def validate_code(cls, value):
        return ProductCreateSerializer.validate_code(value)

    @classmethod
    def validate_general_product_category(cls, value):
        return ProductCreateSerializer.validate_general_product_category(value)

    @classmethod
    def validate_general_uom_group(cls, value):
        return ProductCreateSerializer.validate_general_uom_group(value)

    @classmethod
    def validate_sale_default_uom(cls, value):
        return ProductCreateSerializer.validate_sale_default_uom(value)

    @classmethod
    def validate_sale_tax(cls, value):
        return ProductCreateSerializer.validate_sale_tax(value)

    def validate(self, validate_data):
        if 0 not in validate_data.get('product_choice', []):
            raise serializers.ValidationError({'sale': 'Sale is required'})
        if 1 in validate_data.get('product_choice', []):
            validate_data['inventory_uom'] = validate_data.get('sale_default_uom')
        if 2 in validate_data.get('product_choice', []):
            validate_data['purchase_default_uom'] = validate_data.get('sale_default_uom')
            validate_data['purchase_tax'] = validate_data.get('sale_tax')

        default_pr = Price.objects.filter_on_company(is_default=True).first()
        if not default_pr:
            raise serializers.ValidationError({'default_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
        validate_data['default_price_list'] = default_pr

        primary_crc = Currency.objects.filter_on_company(is_primary=True).first()
        if not primary_crc:
            raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_NOT_EXIST})
        validate_data['sale_currency_using'] = primary_crc
        return validate_data

    def create(self, validated_data):
        default_pr = validated_data.pop('default_price_list')

        product = Product.objects.create(**validated_data)
        ProductCommonFunction.create_product_types_mapped(
            product, self.initial_data.get('product_types_mapped_list', [])
        )
        price_list_product_data = ProductCommonFunction.create_price_list_product(product, default_pr)
        product.sale_product_price_list = price_list_product_data
        product.save(update_fields=['sale_product_price_list'])
        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    general_information = serializers.SerializerMethodField()  # noqa
    sale_information = serializers.SerializerMethodField()
    inventory_information = serializers.SerializerMethodField()
    purchase_information = serializers.SerializerMethodField()
    product_warehouse_detail = serializers.SerializerMethodField()
    product_variant_attribute_list = serializers.SerializerMethodField()
    product_variant_item_list = serializers.SerializerMethodField()
    stock_amount = serializers.SerializerMethodField()
    wait_delivery_amount = serializers.SerializerMethodField()
    wait_receipt_amount = serializers.SerializerMethodField()
    available_amount = serializers.SerializerMethodField()
    component_list_data = serializers.SerializerMethodField()
    attribute_list_data = serializers.SerializerMethodField()
    duration_unit_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'code', 'title', 'description', 'part_number',
            'product_choice',
            'product_warehouse_detail',
            'general_information',
            'inventory_information',
            'sale_information',
            'purchase_information',
            'product_variant_attribute_list',
            'product_variant_item_list',
            'is_public_website',
            'account_deter_referenced_by',
            'attribute_list_data',
            # Transaction information
            'stock_amount', 'wait_delivery_amount', 'wait_receipt_amount', 'available_amount', 'production_amount',
            'component_list_data',
            'duration_unit_data'
        )

    @classmethod
    def get_general_information(cls, obj):
        result = {
            'general_product_types_mapped': [{
                'id': str(product_type.id),
                'title': product_type.title,
                'code': product_type.code,
                'is_service': product_type.is_service
            } if product_type else {} for product_type in obj.general_product_types_mapped.all()],
            'product_category': {
                'id': obj.general_product_category_id,
                'title': obj.general_product_category.title,
                'code': obj.general_product_category.code
            } if obj.general_product_category else {},
            'uom_group': {
                'id': obj.general_uom_group_id,
                'title': obj.general_uom_group.title,
                'code': obj.general_uom_group.code
            } if obj.general_uom_group else {},
            'general_manufacturer': {
                'id': obj.general_manufacturer_id,
                'title': obj.general_manufacturer.title,
                'code': obj.general_manufacturer.code
            } if obj.general_manufacturer else {},
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
            },
            'standard_price': obj.standard_price
        }
        return result

    @classmethod
    def get_sale_information(cls, obj):
        product_price_list = obj.product_price_product.all()
        sale_product_price_list = []
        for item in product_price_list:
            if item.uom_using_id == obj.sale_default_uom_id:
                sale_product_price_list.append({
                    'id': item.price_list_id,
                    'price': item.price,
                    'currency_using': item.currency_using.abbreviation,
                    'is_primary': item.currency_using.is_primary,
                    'title': item.price_list.title,
                    'is_auto_update': item.get_price_from_source
                })
        result = {
            'default_uom': {
                'id': obj.sale_default_uom_id, 'title': obj.sale_default_uom.title, 'code': obj.sale_default_uom.code
            } if obj.sale_default_uom else {},
            'tax': {
                'id': obj.sale_tax_id, 'title': obj.sale_tax.title, 'code': obj.sale_tax.code
            } if obj.sale_tax else {},
            'currency_using': {
                'id': obj.sale_currency_using_id,
                'title': obj.sale_currency_using.title,
                'code': obj.sale_currency_using.code,
                'abbreviation': obj.sale_currency_using.abbreviation
            } if obj.sale_currency_using else {},
            'sale_product_price_list': sale_product_price_list,
            'price_list_for_online_sale': {
                'id': obj.online_price_list_id, 'title': obj.online_price_list.title,
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
            'valuation_method': obj.valuation_method
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
            'supplied_by': obj.supplied_by
        }
        return result

    @classmethod
    def get_product_warehouse_detail(cls, obj):
        result = []
        product_warehouse = obj.product_warehouse_product.all().select_related(
            'warehouse', 'uom'
        ).order_by('warehouse__code')
        if obj.inventory_uom:
            for item in product_warehouse:
                if item.stock_amount > 0:
                    casted_stock_amount = cast_unit_to_inv_quantity(obj.inventory_uom, item.stock_amount)
                    cost_cfg = ReportInvCommonFunc.get_cost_config(obj.company)

                    result.append({
                        'id': item.id,
                        'warehouse': {
                            'id': item.warehouse_id, 'title': item.warehouse.title, 'code': item.warehouse.code,
                        } if item.warehouse else {},
                        'stock_amount': casted_stock_amount,
                        'cost': obj.get_cost_info_by_warehouse(
                            warehouse_id=item.warehouse_id, get_type=2
                        ) / casted_stock_amount if cost_cfg == [1] else None
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

    @classmethod
    def get_stock_amount(cls, obj):
        if obj.inventory_uom:
            stock = 0
            for product_wh in obj.product_warehouse_product.all():
                stock += product_wh.stock_amount
            return stock / obj.inventory_uom.ratio if obj.inventory_uom.ratio > 0 else 0
        return 0

    @classmethod
    def get_wait_delivery_amount(cls, obj):
        if obj.inventory_uom:
            casted_wd_amount = obj.wait_delivery_amount / obj.inventory_uom.ratio \
                if obj.inventory_uom.ratio != 0 else None
            return casted_wd_amount
        return None

    @classmethod
    def get_wait_receipt_amount(cls, obj):
        if obj.inventory_uom:
            casted_wr_amount = obj.wait_receipt_amount / obj.inventory_uom.ratio \
                if obj.inventory_uom.ratio != 0 else None
            return casted_wr_amount
        return None

    @classmethod
    def get_available_amount(cls, obj):
        if obj.inventory_uom:
            stock = 0
            for product_wh in obj.product_warehouse_product.all():
                stock += product_wh.stock_amount
            available = stock - obj.wait_delivery_amount + obj.wait_receipt_amount + obj.production_amount
            return available / obj.inventory_uom.ratio if obj.inventory_uom.ratio > 0 else 0
        return 0

    @classmethod
    def get_component_list_data(cls, obj):
        component_list_data = []
        for item in obj.product_components.all():
            component_list_data.append({
                'order': item.order,
                'component_name': item.component_name,
                'component_des': item.component_des,
                'component_quantity': item.component_quantity
            })
        return component_list_data

    @classmethod
    def get_attribute_list_data(cls, obj):
        return obj.product_attributes.all().values_list('attribute_id', flat=True)

    @classmethod
    def get_duration_unit_data(cls, obj):
        return {
            'id': obj.duration_unit_id,
            'title': obj.duration_unit.title,
            'code': obj.duration_unit.code,
            'group': {
                'id': obj.duration_unit.group_id,
                'title': obj.duration_unit.group.title,
                'code': obj.duration_unit.group.code
            } if obj.duration_unit.group else {},
        } if obj.duration_unit else {}


class ProductUpdateSerializer(serializers.ModelSerializer):
    product_choice = serializers.ListField(child=serializers.ChoiceField(choices=PRODUCT_OPTION))
    general_product_category = serializers.UUIDField()
    general_uom_group = serializers.UUIDField()
    general_manufacturer = serializers.UUIDField(required=False, allow_null=True)
    sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    sale_tax = serializers.UUIDField(required=False, allow_null=True)
    online_price_list = serializers.UUIDField(required=False, allow_null=True)
    inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    valuation_method = serializers.IntegerField(default=1, allow_null=True)
    purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    purchase_tax = serializers.UUIDField(required=False, allow_null=True)
    volume = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    available_notify_quantity = serializers.FloatField(required=False, allow_null=True)
    duration_unit = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'title',
            'description',
            'part_number',
            'product_choice',
            'general_product_category', 'general_uom_group', 'general_manufacturer', 'general_traceability_method',
            'standard_price',
            'width', 'height', 'length', 'volume', 'weight',
            'sale_default_uom', 'sale_tax', 'online_price_list', 'available_notify', 'available_notify_quantity',
            'inventory_uom', 'inventory_level_min', 'inventory_level_max',
            'valuation_method',
            'purchase_default_uom', 'purchase_tax', 'is_public_website', 'supplied_by', 'duration_unit'
        )

    @classmethod
    def validate_product_choice(cls, value):
        return ProductCreateSerializer.validate_product_choice(value)

    @classmethod
    def validate_general_product_category(cls, value):
        return ProductCreateSerializer.validate_general_product_category(value)

    @classmethod
    def validate_general_uom_group(cls, value):
        return ProductCreateSerializer.validate_general_uom_group(value)

    @classmethod
    def validate_general_manufacturer(cls, value):
        if value:
            try:
                return Manufacturer.objects.get(id=value)
            except Manufacturer.DoesNotExist:
                raise serializers.ValidationError({'general_manufacturer': ProductMsg.MANUFACTURER_DOES_NOT_EXIST})
        return None

    @classmethod
    def validate_available_notify_quantity(cls, value):
        return ProductCreateSerializer.validate_available_notify_quantity(value)

    @classmethod
    def validate_sale_default_uom(cls, value):
        return ProductCreateSerializer.validate_sale_default_uom(value)

    @classmethod
    def validate_online_price_list(cls, value):
        return ProductCreateSerializer.validate_online_price_list(value)

    @classmethod
    def validate_sale_tax(cls, value):
        return ProductCreateSerializer.validate_sale_tax(value)

    @classmethod
    def validate_inventory_uom(cls, value):
        return ProductCreateSerializer.validate_inventory_uom(value)

    @classmethod
    def validate_inventory_level_min(cls, value):
        return ProductCreateSerializer.validate_inventory_level_min(value)

    @classmethod
    def validate_inventory_level_max(cls, value):
        return ProductCreateSerializer.validate_inventory_level_max(value)

    @classmethod
    def validate_purchase_default_uom(cls, value):
        return ProductCreateSerializer.validate_purchase_default_uom(value)

    @classmethod
    def validate_purchase_tax(cls, value):
        return ProductCreateSerializer.validate_purchase_tax(value)

    @classmethod
    def validate_duration_unit(cls, value):
        print(value)
        return ProductCreateSerializer.validate_duration_unit(value)

    def validate(self, validate_data):
        # validate dimension
        validate_data['width'] = ProductCommonFunction.validate_dimension(
            validate_data.get('width'), 'width', ProductMsg.W_IS_WRONG
        )
        validate_data['height'] = ProductCommonFunction.validate_dimension(
            validate_data.get('height'), 'height', ProductMsg.H_IS_WRONG
        )
        validate_data['length'] = ProductCommonFunction.validate_dimension(
            validate_data.get('length'), 'length', ProductMsg.L_IS_WRONG
        )
        validate_data['volume'] = ProductCommonFunction.validate_dimension(
            validate_data.get('volume'), 'volume', ProductMsg.VLM_IS_WRONG
        )
        validate_data['weight'] = ProductCommonFunction.validate_dimension(
            validate_data.get('weight'), 'weight', ProductMsg.WGT_IS_WRONG
        )
        instance = self.instance
        being_used = instance.is_used_in_other_model()
        # kiểm tra trước khi cho phép thay đổi Product Type
        if sorted(self.initial_data.get('product_types_mapped_list', [])) != sorted(
                [str(prd_type_id) for prd_type_id in instance.product_product_types.values_list(
                    'product_type_id', flat=True
                )]) and being_used:
            raise serializers.ValidationError(
                {'product_types_mapped_list': _('This product is being used. Can not update product type.')}
            )
        # kiểm tra trước khi cho phép thay đổi UOM group
        if str(validate_data.get('general_uom_group').id) != str(instance.general_uom_group_id) and being_used:
            raise serializers.ValidationError(
                {'general_uom_group': _('This product is being used. Can not update general uom group.')}
            )
        # kiểm tra trước khi cho phép thay đổi PP truy xuất
        if validate_data.get('general_traceability_method') != instance.general_traceability_method and being_used:
            raise serializers.ValidationError(
                {'general_traceability_method': _('This product is being used. Can not update traceability method.')}
            )
        # kiểm tra trước khi cho phép thay đổi PP tính giá hàng tồn kho
        old_valuation_mtd = instance.valuation_method
        new_valuation_mtd = validate_data.get('valuation_method')
        if ProductWareHouse.objects.filter(product=instance).exists() and old_valuation_mtd != new_valuation_mtd:
            raise serializers.ValidationError(
                {'valuation_method': _("Cannot change the valuation method for products that have transactions.")}
            )

        if 1 in validate_data.get('product_choice', []):
            validate_data['duration_unit'] = None

        return validate_data

    def update(self, instance, validated_data):
        validated_data.update(
            {'volume': ProductCommonFunction.sub_validate_volume_obj(self.initial_data, validated_data)}
        )
        validated_data.update(
            {'weight': ProductCommonFunction.sub_validate_weight_obj(self.initial_data, validated_data)}
        )
        validated_data.update(
            {'sale_product_price_list': ProductCommonFunction.setup_price_list_data_in_sale(self.initial_data)}
        )
        instance.product_measure.all().delete()
        ProductPriceList.objects.filter(
            product=instance,
            uom_using_id=instance.sale_default_uom_id,
            currency_using_id=instance.sale_currency_using_id,
        ).delete()
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ProductCommonFunction.create_product_types_mapped(
            instance, self.initial_data.get('product_types_mapped_list', [])
        )
        if 'volume' in validated_data and 'weight' in validated_data:
            measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
            if measure_data:
                ProductCommonFunction.create_measure(instance, measure_data)
        if 0 in validated_data.get('product_choice', []):
            ProductCommonFunction.create_price_list(
                instance,
                self.initial_data.get('sale_price_list', []),
                validated_data
            )

        ProductCommonFunction.create_component_mapped(
            instance, self.initial_data.get('component_list_data', [])
        )

        ProductCommonFunction.create_attribute_mapped(
            instance, self.initial_data.get('attribute_list_data', [])
        )

        ProductCommonFunction.create_product_variant_attribute(
            instance, self.initial_data.get('product_variant_attribute_list', [])
        )
        ProductCommonFunction.update_product_variant_item(
            instance, self.initial_data.get('product_variant_item_list', [])
        )
        AccountDeterminationForProductHandler.create_account_determination_for_product(instance, 0)
        AccountDeterminationForProductHandler.create_account_determination_for_product(instance, 1)
        AccountDeterminationForProductHandler.create_account_determination_for_product(instance, 2)
        AccountDeterminationForProductHandler.create_account_determination_for_product(instance, 3)
        return instance


class UnitOfMeasureOfGroupLaborListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = UnitOfMeasure
        fields = ('id', 'title', 'code', 'group', 'ratio')

    @classmethod
    def get_group(cls, obj):
        return {
            'id': obj.group_id, 'title': obj.group.title, 'is_referenced_unit': obj.is_referenced_unit
        } if obj.group else {}
