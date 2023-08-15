from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, ProductMeasurements
)
from apps.masterdata.saledata.models.price import ProductPriceList, Tax, Currency, Price
from apps.core.base.models import BaseItemUnit
from apps.shared import ProductMsg


class CommonCreateUpdateProduct:
    @classmethod
    def validate_general_data(cls, value):
        general_product_type = ProductType.objects.filter(id=value.get('general_product_type', None))
        general_product_category = ProductCategory.objects.filter(id=value.get('general_product_category', None))
        general_uom_group = UnitOfMeasureGroup.objects.filter(id=value.get('general_product_uom_group', None))

        if general_product_type.count() != 1:
            raise serializers.ValidationError({'general_product_type': ProductMsg.DOES_NOT_EXIST})
        if general_product_category.count() != 1:
            raise serializers.ValidationError({'general_product_category': ProductMsg.DOES_NOT_EXIST})
        if general_uom_group.count() != 1:
            raise serializers.ValidationError({'general_product_uom_group': ProductMsg.DOES_NOT_EXIST})

        general_product_size_dict = value.get('general_product_size', {})
        volume_obj = None
        weight_obj = None
        if len(general_product_size_dict) > 0:
            volume_obj = BaseItemUnit.objects.filter(id=general_product_size_dict['volume_id'])
            weight_obj = BaseItemUnit.objects.filter(id=general_product_size_dict['weight_id'])
            for key, val in general_product_size_dict.items():
                if key not in ['volume_id', 'weight_id']:
                    if not val.isnumeric() and float(val) <= 0:
                        raise serializers.ValidationError({'general_product_size': ProductMsg.PRODUCT_SIZE_IS_WRONG})

        return {
            'product_type': {
                'id': str(general_product_type[0].id),
                'title': general_product_type[0].title,
                'code': general_product_type[0].code
            },
            'product_category': {
                'id': str(general_product_category[0].id),
                'title': general_product_category[0].title,
                'code': general_product_category[0].code
            },
            'uom_group': {
                'id': str(general_uom_group[0].id),
                'title': general_uom_group[0].title,
                'code': general_uom_group[0].code
            },
            'product_size': {
                "width": general_product_size_dict['width'],
                "height": general_product_size_dict['height'],
                "length": general_product_size_dict['length'],
                "volume": {
                    "id": str(volume_obj[0].id),
                    "title": str(volume_obj[0].title),
                    "measure": str(volume_obj[0].measure),
                    "value": general_product_size_dict['volume']
                } if volume_obj[0] else {},
                "weight": {
                    "id": str(weight_obj[0].id),
                    "title": str(weight_obj[0].title),
                    "measure": str(weight_obj[0].measure),
                    "value": general_product_size_dict['weight']
                } if weight_obj[0] else {}
            } if len(general_product_size_dict) > 0 else {}
        }

    @classmethod
    def validate_sale_data(cls, value):
        sale_product_cost = value.get('sale_product_cost', None)
        sale_currency_using = Currency.objects.filter(id=value.get('currency_using', None))
        sale_default_uom = UnitOfMeasure.objects.filter(id=value.get('sale_product_default_uom', None))
        sale_tax = Tax.objects.filter(id=value.get('sale_product_tax', None))

        if sale_product_cost:
            if float(sale_product_cost) < 0:
                raise serializers.ValidationError({'sale_product_cost': ProductMsg.VALUE_INVALID})
        if sale_currency_using.count() != 1:
            raise serializers.ValidationError({'sale_currency_using': ProductMsg.CURRENCY_DOES_NOT_EXIST})
        if sale_default_uom.count() != 1:
            raise serializers.ValidationError({'sale_product_default_uom': ProductMsg.DOES_NOT_EXIST})
        if sale_tax.count() != 1:
            raise serializers.ValidationError({'sale_product_tax': ProductMsg.DOES_NOT_EXIST})

        sale_product_price_list = value.get('sale_product_price_list', [])
        if len(sale_product_price_list) > 0:
            for item in sale_product_price_list:
                price_list_id = item.get('price_list_id', None)
                price_list_value = item.get('price_list_value', None)
                if not Price.objects.filter(id=price_list_id).exists() or not price_list_value:
                    raise serializers.ValidationError({'sale_product_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})

        return {
            'sale_product_cost': sale_product_cost,
            'default_uom': {
                'id': str(sale_default_uom[0].id),
                'title': sale_default_uom[0].title,
                'code': sale_default_uom[0].code
            },
            'tax': {
                'id': str(sale_tax[0].id),
                'title': sale_tax[0].title,
                'code': sale_tax[0].code
            },
            'currency_using': {
                'id': str(sale_currency_using[0].id),
                'title': sale_currency_using[0].title,
                'code': sale_currency_using[0].code,
                'abbreviation': sale_currency_using[0].abbreviation
            },
            'sale_product_price_list': sale_product_price_list
        }

    @classmethod
    def validate_inventory_data(cls, value):
        inventory_uom = UnitOfMeasure.objects.filter(id=value.get('inventory_product_uom', None))
        min_value = 0
        max_value = 0
        inventory_level_min = value.get('inventory_level_min', None)
        inventory_level_max = value.get('inventory_level_max', None)

        if inventory_uom.count() != 1:
            raise serializers.ValidationError({'inventory_product_uom': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
        if inventory_level_min:
            if float(inventory_level_min) < 0:
                raise serializers.ValidationError({'inventory_level_min': ProductMsg.VALUE_INVALID})
            min_value = float(inventory_level_min)
        if inventory_level_max:
            if float(inventory_level_max) < 0:
                raise serializers.ValidationError({'inventory_level_max': ProductMsg.VALUE_INVALID})
            max_value = float(inventory_level_max)
        if inventory_level_min and inventory_level_max:
            if min_value > max_value:
                raise serializers.ValidationError(ProductMsg.WRONG_COMPARE)

        return {
            'uom': {
                'id': str(inventory_uom[0].id),
                'title': inventory_uom[0].title,
                'code': inventory_uom[0].code
            },
            'inventory_level_min': inventory_level_min if inventory_level_min else None,
            'inventory_level_max': inventory_level_max if inventory_level_max else None,
        }

    @classmethod
    def validate_purchase_data(cls, value):
        purchase_default_uom = UnitOfMeasure.objects.filter(id=value.get('purchase_product_default_uom', None))
        purchase_product_tax = Tax.objects.filter(id=value.get('purchase_product_tax', None))

        if purchase_default_uom.count() != 1:
            raise serializers.ValidationError({'purchase_default_uom': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})
        if purchase_product_tax.count() != 1:
            raise serializers.ValidationError({'purchase_product_tax': ProductMsg.TAX_DOES_NOT_EXIST})

        return {
            'default_uom': {
                'id': str(purchase_default_uom[0].id),
                'title': purchase_default_uom[0].title,
                'code': purchase_default_uom[0].code
            },
            'tax': {
                'id': str(purchase_product_tax[0].id),
                'title': purchase_product_tax[0].title,
                'code': purchase_product_tax[0].code
            },
        }

    @classmethod
    def validate_information(cls, general_infor, sale_infor, inventory_infor, purchase_infor, validated_data):
        if 1 in validated_data['product_choice']:
            if len(general_infor.get('general_product_size', {})) <= 0:
                raise serializers.ValidationError({'general_product_size': ProductMsg.PRODUCT_SIZE_NOT_NULL})

        validated_data['general_information'] = CommonCreateUpdateProduct.validate_general_data(general_infor)

        validated_data['sale_information'] = CommonCreateUpdateProduct.validate_sale_data(
            sale_infor
        ) if 0 in validated_data['product_choice'] else {}

        validated_data['inventory_information'] = CommonCreateUpdateProduct.validate_inventory_data(
            inventory_infor
        ) if 1 in validated_data['product_choice'] else {}

        validated_data['purchase_information'] = CommonCreateUpdateProduct.validate_purchase_data(
            purchase_infor
        ) if 2 in validated_data['product_choice'] else {}

        general_infor = validated_data['general_information']
        sale_infor = validated_data['sale_information']
        inventory_infor = validated_data['inventory_information']
        purchase_infor = validated_data['purchase_information']
        # General
        validated_data['general_product_type_id'] = general_infor.get('product_type', None).get('id', None)
        validated_data['general_product_category_id'] = general_infor.get('product_category', None).get('id', None)
        validated_data['general_uom_group_id'] = general_infor.get('uom_group', None).get('id', None)
        validated_data['general_product_size'] = general_infor.get('product_size', [])
        # Sale
        if sale_infor:
            validated_data['sale_default_uom_id'] = sale_infor.get('default_uom', None).get('id', None)
            validated_data['sale_tax_id'] = sale_infor.get('tax', None).get('id', None)
            validated_data['sale_currency_using_id'] = sale_infor.get('currency_using', None).get('id', None)
            validated_data['sale_cost'] = sale_infor.get('sale_product_cost', None)
            validated_data['sale_product_price_list'] = sale_infor.get('sale_product_price_list', [])
        # Inventory
        if inventory_infor:
            validated_data['inventory_uom_id'] = inventory_infor.get('uom', None).get('id', None)
            validated_data['inventory_level_min'] = inventory_infor.get('inventory_level_min', None)
            validated_data['inventory_level_max'] = inventory_infor.get('inventory_level_max', None)
        # Purchase
        if purchase_infor:
            validated_data['purchase_tax_id'] = purchase_infor.get('tax', None).get('id', None)
            validated_data['purchase_default_uom_id'] = purchase_infor.get('default_uom', None).get('id', None)

        return validated_data

    @classmethod
    def create_price_list(cls, product, data_price, validated_data):
        if data_price:
            objs = []
            for item in data_price:
                get_price_from_source = False
                if item.get('is_auto_update', None) == 'true':
                    get_price_from_source = True
                objs.append(
                    ProductPriceList(
                        price_list_id=item.get('price_list_id', None),
                        price=float(item.get('price_list_value', None)),
                        product=product,
                        currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
                        uom_using_id=validated_data['sale_information'].get('default_uom', {}).get('id', None),
                        uom_group_using_id=validated_data['general_information'].get('uom_group', {}).get('id', None),
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)

    @classmethod
    def create_measure(cls, product, data_measure):
        volume_id = None
        weight_id = None
        if len(data_measure['volume']) > 0:
            volume_id = data_measure['volume']['id']
        if len(data_measure['weight']) > 0:
            weight_id = data_measure['weight']['id']
        data_bulk = [
            ProductMeasurements(product=product, measure_id=volume_id, value=data_measure['volume']['value']),
            ProductMeasurements(product=product, measure_id=weight_id, value=data_measure['weight']['value'])
        ]
        ProductMeasurements.objects.bulk_create(data_bulk)

    @classmethod
    def update_price_list(cls, product, data_price, validated_data):
        if data_price:
            objs = []
            for item in data_price:
                get_price_from_source = False
                if item.get('is_auto_update', None) == 'true':
                    get_price_from_source = True
                objs.append(
                    ProductPriceList(
                        price_list_id=item.get('price_list_id', None),
                        price=float(item.get('price_list_value', None)),
                        product=product,
                        currency_using_id=validated_data['sale_information'].get('currency_using', {}).get('id', None),
                        uom_using_id=validated_data['sale_information'].get('default_uom', {}).get('id', None),
                        uom_group_using_id=validated_data['general_information'].get('uom_group', {}).get('id', None),
                        get_price_from_source=get_price_from_source
                    )
                )
            if len(objs) > 0:
                ProductPriceList.objects.bulk_create(objs)

    @classmethod
    def delete_price_list(cls, product, price_list_id):
        product_price_list_item = ProductPriceList.objects.filter(
            product=product,
            price_list_id__in=price_list_id,
        )
        if product_price_list_item:
            product_price_list_item.delete()
