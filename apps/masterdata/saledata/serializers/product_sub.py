from rest_framework import serializers
from apps.masterdata.saledata.models import ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, \
    ProductMeasurements
from apps.masterdata.saledata.models.price import ProductPriceList, Tax, Currency
from apps.shared import ProductMsg


class CommonCreateUpdateProduct:
    @classmethod
    def validate_product_type(cls, value):
        try:
            return ProductType.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except ProductType.DoesNotExist:
            raise serializers.ValidationError({'product_type': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_product_category(cls, value):
        try:
            return ProductCategory.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except ProductCategory.DoesNotExist:
            raise serializers.ValidationError({'product_category': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_uom_group(cls, value):
        try:
            return UnitOfMeasureGroup.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except UnitOfMeasureGroup.DoesNotExist:
            raise serializers.ValidationError({'uom_group': ProductMsg.DOES_NOT_EXIST})

    # For Sale
    @classmethod
    def validate_default_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'default_uom': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_tax_code(cls, value):
        try:
            return Tax.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax_code': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_currency_using(cls, value):
        try:
            return Currency.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except Currency.DoesNotExist:
            raise serializers.ValidationError({'currency': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_length(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'length': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None

    @classmethod
    def validate_width(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'width': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None

    @classmethod
    def validate_height(cls, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError({'height': ProductMsg.VALUE_GREATER_THAN_ZERO})
            return value
        return None

    # For inventory
    @classmethod
    def validate_inventory_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get_current(
                fill__company=True,
                fill__tenant=True,
                id=value
            )
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'inventory_uom': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_inventory_level_min(cls, value):
        if value:
            if value <= 0:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
            return value
        return None

    @classmethod
    def validate_inventory_level_max(cls, value):
        if value:
            if value <= 0:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)
            return value
        return None

    @classmethod
    def validate_general_information(cls, validated_data):
        product_type = validated_data.get('product_type', None)
        product_category = validated_data.get('product_category', None)
        uom_group = validated_data.get('uom_group', None)
        return {
            'product_type': {
                'id': str(product_type.id),
                'title': product_type.title,
                'code': product_type.code
            },
            'product_category': {
                'id': str(product_category.id),
                'title': product_category.title,
                'code': product_category.code
            },
            'uom_group': {
                'id': str(uom_group.id),
                'title': uom_group.title,
                'code': uom_group.code
            }
        }

    @classmethod
    def validate_sale_information(cls, validated_data):
        default_uom = validated_data.get('default_uom', None)
        tax_code = validated_data.get('tax_code', None)
        currency_using = validated_data.get('currency_using', None)
        length = validated_data.get('length', None)
        width = validated_data.get('width', None)
        height = validated_data.get('height', None)
        measure = validated_data.get('measure', None)
        return {
            'default_uom': {
                'id': str(default_uom.id),
                'title': default_uom.title,
                'code': default_uom.code
            } if default_uom else None,
            'tax_code': {
                'id': str(tax_code.id),
                'title': tax_code.title,
                'code': tax_code.code
            } if tax_code else None,
            'currency_using': {
                'id': str(currency_using.id),
                'title': currency_using.title,
                'code': currency_using.code,
                'abbreviation': currency_using.abbreviation
            } if currency_using else None,
            'measure': measure if measure else [],
            'length': length,
            'width': width,
            'height': height
        }

    @classmethod
    def validate_inventory_information(cls, validated_data):
        inventory_uom = validated_data.get('inventory_uom', None)
        inventory_level_min = validated_data.get('inventory_level_min', None)
        inventory_level_max = validated_data.get('inventory_level_max', None)
        return {
            'uom': {
                'id': str(inventory_uom.id),
                'title': inventory_uom.title,
                'code': inventory_uom.code
            } if inventory_uom else None,
            'inventory_level_min': inventory_level_min if inventory_level_min else None,
            'inventory_level_max': inventory_level_max if inventory_level_max else None,
        }

    @classmethod
    def create_price_list(cls, product, data_price, validated_data):
        if data_price:
            objs = []
            for item in data_price:
                get_price_from_source = False
                if item.get('is_auto_update', None) == '1':
                    get_price_from_source = True
                objs.append(
                    ProductPriceList(
                        price_list_id=item.get('price_list_id', None),
                        product=product,
                        price=float(item.get('price_value', None)),
                        currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
                        uom_using_id=validated_data['sale_information'].get('default_uom', {}).get('id', None),
                        uom_group_using_id=validated_data['general_information'].get('uom_group', {}).get('id', None),
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)

    @classmethod
    def create_measure(cls, product, data):
        data_bulk = [ProductMeasurements(
            product=product,
            measure_id=item['unit']['id'],
            value=item['value']
        ) for item in data]

        ProductMeasurements.objects.bulk_create(data_bulk)

    @classmethod
    def update_price_list(cls, product, data_price_list, validated_data):
        if data_price_list:
            objs = []
            for item in data_price_list:
                get_price_from_source = False
                if item.get('is_auto_update', None) == '1':
                    get_price_from_source = True

                currency_using_id = validated_data['sale_information'].get('currency_using', {}).get('id', None)
                default_uom_id = validated_data['sale_information'].get('default_uom', {}).get('id', None)
                uom_group_id = validated_data['general_information'].get('uom_group', {}).get('id', None)
                objs.append(
                    ProductPriceList(
                        price_list_id=item.get('price_list_id', None),
                        product=product,
                        price=float(item.get('price_value', None)),
                        currency_using_id=currency_using_id,
                        uom_using_id=default_uom_id,
                        uom_group_using_id=uom_group_id,
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)

    @classmethod
    def delete_price_list(cls, product):
        product_price_list_item = ProductPriceList.objects.filter(
            product=product,
            currency_using=product.currency_using,
            uom_using=product.default_uom
        )
        if product_price_list_item:
            product_price_list_item.delete()
