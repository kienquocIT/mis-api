from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, ProductMeasurements
)
from apps.masterdata.saledata.models.price import ProductPriceList, Tax, Currency, Price
from apps.core.base.models import BaseItemUnit
from apps.shared import ProductMsg


class CommonCreateUpdateProduct:
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
                        currency_using_id=validated_data.get('sale_currency_using', {}).id,
                        uom_using_id=validated_data.get('sale_default_uom', {}).id,
                        uom_group_using_id=validated_data.get('general_uom_group', {}).id,
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
