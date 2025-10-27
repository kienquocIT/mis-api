from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.masterdata.saledata.models.price import Price, Currency
from apps.masterdata.saledata.models.product import (
    UnitOfMeasure, ProductSpecificIdentificationSerialNumber, Product
)
from apps.masterdata.saledata.serializers.product_common import ProductCommonFunction
from apps.masterdata.saledata.serializers.product import ProductCreateSerializer
from apps.shared import ProductMsg


PRODUCT_OPTION = [(0, _('Sale')), (1, _('Inventory')), (2, _('Purchase'))]


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
            'sale_default_uom', 'sale_tax', 'description',
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


class ProductSpecificIdentificationSerialNumberListSerializer(serializers.ModelSerializer):
    new_description = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecificIdentificationSerialNumber
        fields = (
            'id',
            'product_id',
            'product_warehouse_serial_id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
            # trường này lưu giá trị thực tế đích danh (PP này chỉ apply cho SP serial)
            'specific_value',
            'serial_status',
            'new_description',
        )

    @classmethod
    def get_new_description(cls, obj):
        if obj.product_warehouse_serial:
            for pw_modified in obj.product_warehouse_serial.pw_modified_pw_serial.all():
                return pw_modified.new_description
        return ''
