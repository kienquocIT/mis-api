import json

from rest_framework import serializers

from apps.masterdata.saledata.models import (
    UnitOfMeasureGroup, ProductType, ProductCategory,
    Product, ProductProductType, ProductMeasurements,
)
from apps.masterdata.saledata.serializers import (
    PRODUCT_OPTION,
)
from apps.shared import ProductMsg, BaseMsg

from apps.core.base.models import Currency as BaseCurrency, BaseItemUnit
from apps.core.hr.models import Employee


class ProductImportSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    general_product_category = serializers.CharField()
    general_product_types_mapped = serializers.CharField()
    general_uom_group = serializers.CharField()
    length = serializers.CharField(required=False, allow_null=True)
    height = serializers.CharField(required=False, allow_null=True)
    width = serializers.CharField(required=False, allow_null=True)
    volume = serializers.CharField(required=False, allow_null=True)
    weight = serializers.CharField(required=False, allow_null=True)
    # sale_default_uom = serializers.UUIDField(required=False, allow_null=True)
    # sale_tax = serializers.UUIDField(required=False, allow_null=True)
    # sale_currency_using = serializers.UUIDField(required=False, allow_null=True)
    # online_price_list = serializers.UUIDField(required=False, allow_null=True)
    # inventory_uom = serializers.UUIDField(required=False, allow_null=True)
    # purchase_default_uom = serializers.UUIDField(required=False, allow_null=True)
    # purchase_tax = serializers.UUIDField(required=False, allow_null=True)

    # available_notify_quantity = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'code', 'title', 'description', 'product_choice', 'part_number',
            # General
            'general_product_category',
            'general_product_types_mapped'
            'general_uom_group',
            'general_traceability_method',
            'width', 'height', 'length', 'volume', 'weight',
            # Sale
            # 'sale_default_uom', 'sale_tax', 'sale_currency_using', 'online_price_list',
            # 'available_notify', 'available_notify_quantity',
            # # Inventory
            # 'inventory_uom', 'inventory_level_min', 'inventory_level_max', 'is_public_website',
            # # Purchase
            # 'purchase_default_uom', 'purchase_tax', 'supplied_by', 'standard_price'
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Product.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})

    @classmethod
    def validate_general_product_types_mapped(cls, value):
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(",")]))
            objs = ProductType.objects.filter_current(fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return [item for item in objs]
            raise serializers.ValidationError({'general_product_types_mapped': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'general_product_types_mapped': ProductMsg.NOT_NULL})

    @classmethod
    def validate_general_product_category(cls, value):
        if value:
            try:
                return ProductCategory.objects.get_current(fill__company=True, code=value)
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError({'general_product_category': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'general_product_category': ProductMsg.NOT_NULL})

    @classmethod
    def validate_general_uom_group(cls, value):
        if value:
            try:
                return UnitOfMeasureGroup.objects.get_current(fill__company=True, code=value)
            except UnitOfMeasureGroup.DoesNotExist:
                raise serializers.ValidationError(ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_EXIST)
        raise serializers.ValidationError({'general_uom_group': ProductMsg.NOT_NULL})

    @classmethod
    def validate_width(cls, value):
        if value:
            if float(value) <= 0:
                raise serializers.ValidationError(ProductMsg.PRODUCT_SIZE_IS_WRONG)
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

    # @classmethod
    # def validate_available_notify_quantity(cls, value):
    #     if value:
    #         if float(value) <= 0:
    #             raise serializers.ValidationError({'available_notify_quantity': ProductMsg.VALUE_INVALID})
    #         return value
    #     return None
    #
    # @classmethod
    # def validate_sale_default_uom(cls, value):
    #     if 0 in cls.product_choice:
    #         if value:
    #             try:
    #                 return UnitOfMeasure.objects.get_current(fill__company=True, code=value)
    #             except UnitOfMeasure.DoesNotExist:
    #                 raise serializers.ValidationError({'sale_default_uom': ProductMsg.DOES_NOT_EXIST})
    #         raise serializers.ValidationError({'sale_default_uom': ProductMsg.NOT_NULL})
    #
    # @classmethod
    # def validate_sale_tax(cls, value):
    #     if 0 in cls.product_choice:
    #         if value:
    #             try:
    #                 return Tax.objects.get_current(fill__company=True, code=value)
    #             except Tax.DoesNotExist:
    #                 raise serializers.ValidationError({'sale_tax': ProductMsg.DOES_NOT_EXIST})
    #         raise serializers.ValidationError({'sale_tax': ProductMsg.NOT_NULL})
    #
    # @classmethod
    # def validate_sale_product_price_list(cls, value):
    #     pass

    def create(self, validated_data):
        #create volume object
        volume_obj = BaseItemUnit.objects.filter(title='volume')
        if volume_obj:
            volume_obj = volume_obj.first()
            validated_data.update({
               'volume': {
                   'id': str(volume_obj.id),
                    'title': volume_obj.title,
                    'measure': volume_obj.measure,
                    'value': validated_data['volume']
               }
            })

        #create weight object:
        weight_obj = BaseItemUnit.objects.filter(title='weight')
        if weight_obj:
            weight_obj = weight_obj.first()
            validated_data.update({
                'weight': {
                    'id': str(weight_obj.id),
                    'title': weight_obj.title,
                    'measure': weight_obj.measure,
                    'value': validated_data['weight']
                }
            })
        general_product_types_mapped_list = validated_data.pop('general_product_types_mapped',[])
        product = Product.objects.create(**validated_data)

        #create product_measurements
        if 'volume' in validated_data and 'weight' in validated_data:
            measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
            if measure_data:
                if 'id' in measure_data['volume']:
                    volume_id = validated_data['volume']['id']
                    ProductMeasurements.objects.create(
                        product=product,
                        measure_id=volume_id,
                        value=measure_data['volume']['value']
                    )
                if 'id' in measure_data['weight']:
                    weight_id = validated_data['weight']['id']
                    ProductMeasurements.objects.create(
                        product=product,
                        measure_id=weight_id,
                        value=measure_data['weight']['value']
                    )

        #add data to table ProductProductType
        bulk_info = []
        for item in general_product_types_mapped_list:
            bulk_info.append(ProductProductType(product=product, product_type_id=item.id))
        ProductProductType.objects.filter(product=product).delete()
        ProductProductType.objects.bulk_create(bulk_info)

        return product


class ProductImportReturnSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = (
            'code', 'title', 'description', 'product_choice', 'part_number',
            # General
            'general_product_category',
            'general_uom_group',
            'general_traceability_method',
            'width', 'height', 'length', 'volume', 'weight',
            # Sale
            # 'sale_default_uom', 'sale_tax', 'sale_currency_using', 'online_price_list',
            # 'available_notify', 'available_notify_quantity',
            # # Inventory
            # 'inventory_uom', 'inventory_level_min', 'inventory_level_max', 'is_public_website',
            # # Purchase
            # 'purchase_default_uom', 'purchase_tax', 'supplied_by', 'standard_price'
        )
