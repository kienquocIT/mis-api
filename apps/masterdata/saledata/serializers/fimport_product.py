import logging
from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    UnitOfMeasureGroup, ProductType, ProductCategory,
    Product, ProductProductType, ProductMeasurements, UnitOfMeasure, Currency, Price, ProductPriceList
)
from apps.masterdata.saledata.serializers import (
    CommonCreateUpdateProduct, ProductCreateSerializer
)
from apps.shared import ProductMsg
from apps.core.base.models import BaseItemUnit


logger = logging.getLogger(__name__)

class ProductImportListSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Product
        fields = (
            'code', 'title', 'description', 'product_choice', 'part_number',
            # General
            'general_product_category',
            'general_product_types_mapped',
            'general_uom_group',
            'general_traceability_method',
            'width', 'height', 'length', 'volume', 'weight',
            # Sale
            'sale_default_uom', 'sale_tax', 'sale_general_price',
            # Inventory
            'inventory_uom', 'valuation_method', 'standard_price',
            # Purchase
            'purchase_default_uom', 'purchase_tax', 'supplied_by',
        )

    @classmethod
    def validate_code(cls, value):
        ProductCreateSerializer.validate_code(value)

    @classmethod
    def validate_product_choice(cls, value):
        ProductCreateSerializer.validate_product_choice(value)

    @classmethod
    def validate_general_product_types_mapped(cls, value):
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(",")]))
            objs = ProductType.objects.filter_current(fill__tenant=True, fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return list(objs)
            raise serializers.ValidationError({'general_product_types_mapped': ProductMsg.PRODUCT_TYPE_NOT_EXIST})
        raise serializers.ValidationError({'general_product_types_mapped': ProductMsg.PRODUCT_TYPE_NOT_NULL})

    @classmethod
    def validate_general_product_category(cls, value):
        if value:
            try:
                return ProductCategory.objects.get_current(fill__tenant=True, fill__company=True, code=value)
            except ProductCategory.DoesNotExist:
                raise serializers.ValidationError({'general_product_category': ProductMsg.PRODUCT_CATEGORY_NOT_EXIST})
        raise serializers.ValidationError({'general_product_category': ProductMsg.PRODUCT_CATEGORY_NOT_NULL})

    @classmethod
    def validate_general_uom_group(cls, value):
        if value:
            try:
                return UnitOfMeasureGroup.objects.get_current(fill__tenant=True, fill__company=True, code=value)
            except UnitOfMeasureGroup.DoesNotExist:
                raise serializers.ValidationError({'general_uom_group': ProductMsg.UOM_GROUP_NOT_EXIST})
        raise serializers.ValidationError({'general_uom_group': ProductMsg.UOM_GROUP_NOT_NULL})

    @classmethod
    def validate_width(cls, value):
        return ProductCreateSerializer.validate_width(value)

    @classmethod
    def validate_height(cls, value):
        return ProductCreateSerializer.validate_height(value)

    @classmethod
    def validate_length(cls, value):
        return ProductCreateSerializer.validate_length(value)

    @classmethod
    def validate_volume(cls, value):
        return ProductCreateSerializer.validate_volume(value)

    @classmethod
    def validate_weight(cls, value):
        return ProductCreateSerializer.validate_weight(value)

    def validate(self, validate_data):
        product_choice = validate_data.get('product_choice', [])
        if 0 in product_choice:
            # valid sale_default_uom
            if not validate_data.get('sale_default_uom'):
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.UOM_NOT_NULL})
            sale_default_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True, fill__company=True, code=validate_data.get('sale_default_uom')
            ).first()
            if not sale_default_uom:
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.UOM_NOT_EXIST})
            validate_data['sale_default_uom'] = sale_default_uom
            # valid sale_tax
            if not validate_data.get('sale_tax'):
                raise serializers.ValidationError({'sale_tax': ProductMsg.TAX_NOT_NULL})
            sale_tax = UnitOfMeasure.objects.filter_current(
                fill__tenant=True, fill__company=True, code=validate_data.get('sale_tax')
            ).first()
            if not sale_tax:
                raise serializers.ValidationError({'sale_tax': ProductMsg.TAX_NOT_EXIST})
            validate_data['sale_tax'] = sale_tax
            # valid sale_general_price
            try:
                sale_general_price = float(validate_data.get('sale_general_price', 0))
                if sale_general_price < 0:
                    raise serializers.ValidationError({'sale_general_price': ProductMsg.INVALID_SALE_GENERAL_PRICE})
            except Exception as error:
                raise serializers.ValidationError({'sale_general_price_error': error})
            # find sale_currency_using
            sale_currency_using = Currency.objects.filter_current(
                fill__tenant=True, fill__company=True, is_primary=True
            ).first()
            if sale_currency_using:
                validate_data['sale_currency_using'] = sale_currency_using
            else:
                raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_NOT_EXIST})

            if str(sale_default_uom.group_id) != str(validate_data.get('general_uom_group').id):
                raise serializers.ValidationError({'sale_default_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
        else:
            validate_data['sale_default_uom'] = None
            validate_data['sale_tax'] = None
            validate_data['sale_general_price'] = 0

        if 1 in product_choice:
            # valid inventory_uom
            if not validate_data.get('inventory_uom'):
                raise serializers.ValidationError({'inventory_uom': ProductMsg.UOM_NOT_NULL})
            inventory_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True, fill__company=True, code=validate_data.get('inventory_uom')
            ).first()
            if not inventory_uom:
                raise serializers.ValidationError({'inventory_uom': ProductMsg.UOM_NOT_EXIST})
            validate_data['inventory_uom'] = inventory_uom
            if str(inventory_uom.group_id) != str(validate_data.get('general_uom_group').id):
                raise serializers.ValidationError({'inventory_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
            # valid valuation_method
            try:
                valuation_method = int(validate_data.get('valuation_method', 1))
                if valuation_method not in [0, 1, 2]:
                    raise serializers.ValidationError({'valuation_method': ProductMsg.INVALID_PRODUCT_CHOICE_VALUE})
            except Exception as error:
                raise serializers.ValidationError({'valuation_method_error': error})
            # valid standard_price
            try:
                standard_price = float(validate_data.get('standard_price', 0))
                if standard_price < 0:
                    raise serializers.ValidationError({'standard_price': ProductMsg.INVALID_STANDARD_PRICE})
            except Exception as error:
                raise serializers.ValidationError({'standard_price_error': error})
        else:
            validate_data['inventory_uom'] = None
            validate_data['valuation_method'] = 1
            validate_data['standard_price'] = 0

        if 2 in product_choice:
            # valid purchase_default_uom
            if not validate_data.get('purchase_default_uom'):
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.UOM_NOT_NULL})
            purchase_default_uom = UnitOfMeasure.objects.filter_current(
                fill__tenant=True, fill__company=True, code=validate_data.get('purchase_default_uom')
            ).first()
            if not purchase_default_uom:
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.UOM_NOT_EXIST})
            validate_data['purchase_default_uom'] = purchase_default_uom
            if str(purchase_default_uom.group_id) != str(validate_data.get('general_uom_group').id):
                raise serializers.ValidationError({'purchase_default_uom': ProductMsg.UNIT_OF_MEASURE_GROUP_NOT_MATCH})
            # valid purchase_tax
            if not validate_data.get('purchase_tax'):
                raise serializers.ValidationError({'purchase_tax': ProductMsg.TAX_NOT_NULL})
            purchase_tax = UnitOfMeasure.objects.filter_current(
                fill__tenant=True, fill__company=True, code=validate_data.get('purchase_tax')
            ).first()
            if not purchase_tax:
                raise serializers.ValidationError({'purchase_tax': ProductMsg.TAX_NOT_EXIST})
            validate_data['purchase_tax'] = purchase_tax
            # valid supplied_by
            try:
                supplied_by = int(validate_data.get('supplied_by', 0))
                if supplied_by not in [0, 1]:
                    raise serializers.ValidationError({'supplied_by': ProductMsg.INVALID_SUPPLY_BY})
            except Exception as error:
                raise serializers.ValidationError({'supplied_by_error': error})
        else:
            validate_data['purchase_default_uom'] = None
            validate_data['purchase_tax'] = None
            validate_data['supplied_by'] = 0

        return validate_data

    def create(self, validated_data): # pylint: disable=R0914
        try:
            with transaction.atomic():
                # create volume object
                volume_obj = BaseItemUnit.objects.filter(title='volume')
                if volume_obj and validated_data.get('volume'):
                    volume_obj = volume_obj.first()
                    validated_data['volume'] = {
                        'id': str(volume_obj.id),
                        'title': volume_obj.title,
                        'measure': volume_obj.measure,
                        'value': validated_data.get('volume')
                    }
                # create weight object
                weight_obj = BaseItemUnit.objects.filter(title='weight')
                if weight_obj and validated_data.get('weight'):
                    weight_obj = weight_obj.first()
                    validated_data['weight'] = {
                        'id': str(weight_obj.id),
                        'title': weight_obj.title,
                        'measure': weight_obj.measure,
                        'value': validated_data.get('weight')
                    }
                # get all price list by company that are auto updated
                sale_general_price = validated_data.pop('sale_general_price', 0)
                general_product_types_mapped_list = validated_data.pop('general_product_types_mapped', [])
                # create
                product = Product.objects.create(**validated_data)
                # create product_measurements
                if 'volume' in validated_data and 'weight' in validated_data:
                    measure_data = {
                        'weight': validated_data.get('weight', {}),
                        'volume': validated_data.get('volume', {})
                    }
                    if all([
                        'id' in measure_data.get('volume', {}),
                        measure_data.get('volume', {}).get('value') is not None
                    ]):
                        ProductMeasurements.objects.create(
                            product=product,
                            measure_id=measure_data.get('volume', {}).get('id'),
                            value=measure_data.get('volume', {}).get('value')
                        )
                    if all([
                        'id' in measure_data.get('weight', {}),
                        measure_data.get('weight', {}).get('value') is not None
                    ]):
                        ProductMeasurements.objects.create(
                            product=product,
                            measure_id=measure_data.get('weight', {}).get('id'),
                            value=measure_data.get('weight', {}).get('value')
                        )
                # add data to table ProductProductType
                bulk_info = []
                for item in general_product_types_mapped_list:
                    bulk_info.append(ProductProductType(product=product, product_type=item))
                ProductProductType.objects.filter(product=product).delete()
                ProductProductType.objects.bulk_create(bulk_info)
                # create price list
                if 0 in validated_data.get('product_choice', []):
                    prod_price_bulk_info = []
                    default_pr = Price.objects.filter_current(
                        fill__tenant=True, fill__company=True, is_default=True
                    ).first()
                    if default_pr:
                        prod_price_bulk_info.append(ProductPriceList(
                            product=product,
                            price_list_id=default_pr.id,
                            price=sale_general_price,
                            currency_using=validated_data.get('sale_currency_using'),
                            uom_using=validated_data.get('sale_default_uom'),
                            uom_group_using=validated_data.get('general_uom_group'),
                            get_price_from_source=False
                        ))
                        sale_product_price_list = Price.objects.filter_current(
                            fill__tenant=True, fill__company=True, auto_update=True
                        )
                        for price_list in sale_product_price_list:
                            cumulative_factor = CommonCreateUpdateProduct.get_cumulative_factor(price_list)
                            price = sale_general_price * cumulative_factor
                            prod_price_bulk_info.append(ProductPriceList(
                                product=product,
                                price_list=price_list,
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
            raise serializers.ValidationError({'import_product_error': err})
        return product


class ProductImportDetailSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = ('id',)
