import logging
from django.db import transaction
from rest_framework import serializers

from apps.masterdata.saledata.models import (
    UnitOfMeasureGroup, ProductType, ProductCategory,
    Product, ProductProductType, ProductMeasurements, UnitOfMeasure, Tax, Currency, Price, ProductPriceList
)
from apps.masterdata.saledata.serializers import (
     CommonCreateUpdateProduct,
)
from apps.shared import ProductMsg, BaseMsg

from apps.core.base.models import BaseItemUnit


logger = logging.getLogger(__name__)

class ProductImportSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=150)
    title = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    part_number = serializers.CharField(max_length=150, allow_null=True, allow_blank=True)
    # general
    general_product_category = serializers.CharField()
    general_product_types_mapped = serializers.CharField()
    general_uom_group = serializers.CharField()
    length = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    height = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    width = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    volume = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    weight = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    product_choice = serializers.JSONField(default=list)
    # sale
    sale_default_uom = serializers.CharField(required=False, allow_null=True)
    sale_tax = serializers.CharField(required=False, allow_null=True)
    sale_general_price = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    inventory_uom = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    valuation_method = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    standard_price = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    purchase_default_uom = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    purchase_tax = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    supplied_by = serializers.CharField(required=False,allow_null=True, default=0)
    # available_notify = serializers.BooleanField()
    # available_notify_quantity = serializers.CharField(required=False, allow_null=True)

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
            'sale_default_uom', 'sale_tax', 'sale_general_price'
            # Inventory
            'inventory_uom', 'valuation_method', 'standard_price',
            # Purchase
            'purchase_default_uom', 'purchase_tax', 'supplied_by',
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Product.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": ProductMsg.CODE_NOT_NULL})

    @classmethod
    def validate_product_choice(cls, value):
        for item in value:
            if int(item) not in [0,1,2]:
                raise serializers.ValidationError({'product_choice': ProductMsg.VALUE_INVALID})
        return value

    @classmethod
    def validate_general_product_types_mapped(cls, value):
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(",")]))
            objs = ProductType.objects.filter_current(fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return list(objs)
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

    def validate_sale_default_uom(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        general_uom_group_code = self.initial_data.get('general_uom_group')
        general_uom_group = UnitOfMeasureGroup.objects.filter_current(fill__company=True,
                                                                      code=general_uom_group_code).first()
        if 0 in product_choice:
            if value:
                try:
                    uom_obj = UnitOfMeasure.objects.get_current(fill__company=True, code=value)
                    if uom_obj.group_id != general_uom_group.id:
                        raise serializers.ValidationError(
                            {'sale_default_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
                    return uom_obj
                except UnitOfMeasure.DoesNotExist:
                    raise serializers.ValidationError({'sale_default_uom': BaseMsg.NOT_EXIST})
            raise serializers.ValidationError({'sale_default_uom': ProductMsg.NOT_NULL})
        return None

    def validate_sale_tax(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        if 0 in product_choice:
            if value:
                try:
                    return Tax.objects.get_current(fill__company=True, code=value)
                except Tax.DoesNotExist:
                    raise serializers.ValidationError({'sale_tax': BaseMsg.NOT_EXIST})
            raise serializers.ValidationError({'sale_tax': ProductMsg.NOT_NULL})
        return None

    def validate_sale_general_price(self,value):
        product_choice = self.initial_data.get('product_choice', [])
        if 0 in product_choice:
            if isinstance(float(value), (int,float)) and float(value) > 0:
                return float(value)
            raise serializers.ValidationError({'sale_general_price': ProductMsg.VALUE_INVALID})
        return None

    def validate_inventory_uom(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        general_uom_group_code = self.initial_data.get('general_uom_group')
        general_uom_group = UnitOfMeasureGroup.objects.filter_current(fill__company=True,
                                                                      code=general_uom_group_code).first()
        if 1 in product_choice:
            if value:
                try:
                    uom_obj =  UnitOfMeasure.objects.get_current(fill__company=True, code=value)
                    if uom_obj.group_id != general_uom_group.id:
                        raise serializers.ValidationError({'inventory_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
                    return uom_obj
                except UnitOfMeasure.DoesNotExist:
                    raise serializers.ValidationError({'inventory_uom': BaseMsg.NOT_EXIST})
            raise serializers.ValidationError({'inventory_uom': ProductMsg.NOT_NULL})
        return None

    def validate_valuation_method(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        if 1 in product_choice:
            if int(value) not in [0, 1, 2]:
                raise serializers.ValidationError({'valuation_method': ProductMsg.VALUE_INVALID})
            return value
        return None

    def validate_standard_price(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        if 1 in product_choice:
            if isinstance(float(value), (int,float)) and float(value) > 0:
                return float(value)
            raise serializers.ValidationError({'standard_price': ProductMsg.VALUE_INVALID})
        return None

    def validate_purchase_default_uom(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        general_uom_group_code = self.initial_data.get('general_uom_group')
        general_uom_group = UnitOfMeasureGroup.objects.filter_current(fill__company=True,
                                                                      code=general_uom_group_code).first()
        if 2 in product_choice:
            if value:
                try:
                    uom_obj = UnitOfMeasure.objects.get_current(fill__company=True, code=value)
                    if uom_obj.group_id != general_uom_group.id:
                        raise serializers.ValidationError(
                            {'purchase_default_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
                    return uom_obj
                except UnitOfMeasure.DoesNotExist:
                    raise serializers.ValidationError({'purchase_default_uom':  BaseMsg.NOT_EXIST})
            raise serializers.ValidationError({'purchase_default_uom': ProductMsg.NOT_NULL})
        return None

    def validate_purchase_tax(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        if 2 in product_choice:
            if value:
                try:
                    return Tax.objects.get_current(fill__company=True, code=value)
                except Tax.DoesNotExist:
                    raise serializers.ValidationError({'purchase_tax': BaseMsg.NOT_EXIST})
            raise serializers.ValidationError({'purchase_default_uom': ProductMsg.NOT_NULL})
        return None

    def validate_supplied_by(self, value):
        product_choice = self.initial_data.get('product_choice', [])
        if 2 in product_choice:
            if value is not None:
                if int(value) not in [0,1]:
                    raise serializers.ValidationError({'supplied_by': ProductMsg.VALUE_INVALID})
                return value
            raise serializers.ValidationError({'supplied_by': ProductMsg.NOT_NULL})
        return 0

    def create(self, validated_data): # pylint: disable=R0914
        try:
            with transaction.atomic():
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

                sale_currency_using = Currency.objects.filter_current(fill__company=True, is_primary=True).first()
                validated_data.update({
                    'sale_currency_using': sale_currency_using,
                })

                # get all price list by company that are auto updated
                sale_general_price = validated_data.pop('sale_general_price',[])

                general_product_types_mapped_list = validated_data.pop('general_product_types_mapped',[])
                product = Product.objects.create(**validated_data)

                #create product_measurements
                if 'volume' in validated_data and 'weight' in validated_data:
                    measure_data = {'weight': validated_data['weight'], 'volume': validated_data['volume']}
                    if measure_data:
                        if 'id' in measure_data['volume'] and measure_data['volume']['value'] is not None:
                            volume_id = validated_data['volume']['id']
                            ProductMeasurements.objects.create(
                                product=product,
                                measure_id=volume_id,
                                value=measure_data['volume']['value']
                            )
                        if 'id' in measure_data['weight'] and measure_data['weight']['value'] is not None:
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

                if 0 in validated_data['product_choice']:
                    prod_price_bulk_info = []
                    # create price list
                    default_pr = Price.objects.filter_current(fill__tenant=True, fill__company=True,
                                                              is_default=True).first()
                    if default_pr:
                        # general price list
                        prod_price_bulk_info.append(ProductPriceList(
                            product=product,
                            price_list_id=default_pr.id,
                            price=sale_general_price,
                            currency_using=validated_data.get('sale_currency_using'),
                            uom_using=validated_data.get('sale_default_uom'),
                            uom_group_using=validated_data.get('general_uom_group'),
                            get_price_from_source=False
                        ))
                        sale_product_price_list = Price.objects.filter_current(fill__company=True, auto_update=True)
                        for price_list in sale_product_price_list:
                            cumulative_factor = CommonCreateUpdateProduct.get_cumulative_factor(price_list)
                            price = sale_general_price * cumulative_factor
                            prod_price_bulk_info.append(ProductPriceList(
                                product=product,
                                price_list_id=price_list.id,
                                price=float(price),
                                currency_using=validated_data.get('sale_currency_using'),
                                uom_using=validated_data.get('sale_default_uom'),
                                uom_group_using=validated_data.get('general_uom_group'),
                                get_price_from_source=True
                            ))
                        product.sale_price = sale_general_price
                        product.save()
                        ProductPriceList.objects.bulk_create(prod_price_bulk_info)
        except Exception as err:
            logger.error(msg=f'Import product errors: {str(err)}')
            raise serializers.ValidationError({'product': 'Error'})
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
            # 'sale_default_uom', 'sale_tax',
            # Inventory
            'inventory_uom',
            # # Purchase
            'purchase_default_uom', 'purchase_tax', 'supplied_by',
        )
