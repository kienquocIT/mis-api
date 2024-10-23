from datetime import datetime
from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models import (
    ProductMeasurements, ProductProductType, ProductVariantAttribute, ProductVariant
)
from apps.masterdata.saledata.models.price import ProductPriceList, Price
from apps.shared import ProductMsg


class CommonCreateUpdateProduct:
    @classmethod
    def create_price_list_product(cls, product, price_list, bulk_info):
        for item in price_list.price_parent.all():
            bulk_info.append(ProductPriceList(
                product=product, price_list=item, price=0,
                currency_using=product.sale_currency_using,
                uom_using=product.sale_default_uom,
                uom_group_using=product.general_uom_group,
                get_price_from_source=True
            ))
            cls.create_price_list_product(product, item, bulk_info)  # đệ quy tìm bảng giá con
        return bulk_info

    @classmethod
    def create_price_list(cls, product, data_price, validated_data):
        default_pr = Price.objects.filter_current(fill__tenant=True, fill__company=True, is_default=True).first()
        if default_pr:
            if len(data_price) == 0:
                ProductPriceList.objects.create(
                    product=product,
                    price_list=default_pr,
                    price=0,
                    currency_using=product.sale_currency_using,
                    uom_using=product.sale_default_uom,
                    uom_group_using=product.general_uom_group
                )
                bulk_info = cls.create_price_list_product(product, default_pr, [])
                ProductPriceList.objects.bulk_create(bulk_info)
            else:
                objs = []
                for item in data_price:
                    objs.append(ProductPriceList(
                        product=product,
                        price_list_id=item.get('price_list_id', None),
                        price=float(item.get('price_list_value', 0)),
                        currency_using=validated_data.get('sale_currency_using'),
                        uom_using=validated_data.get('sale_default_uom'),
                        uom_group_using=validated_data.get('general_uom_group'),
                        get_price_from_source=item.get('is_auto_update', None) == 'true'
                    ))
                    if str(default_pr.id) == item.get('price_list_id', None):
                        product.sale_price = float(item.get('price_list_value', 0))
                        product.save()
                ProductPriceList.objects.bulk_create(objs)
            return True
        return False

    @classmethod
    def create_measure(cls, product, data_measure):
        volume_id = data_measure['volume']['id'] if len(data_measure['volume']) > 0 else None
        weight_id = data_measure['weight']['id'] if len(data_measure['weight']) > 0 else None
        if volume_id and 'value' in data_measure['volume']:
            ProductMeasurements.objects.create(
                product=product,
                measure_id=volume_id,
                value=data_measure['volume']['value']
            )
        if weight_id and 'value' in data_measure['weight']:
            ProductMeasurements.objects.create(
                product=product,
                measure_id=weight_id,
                value=data_measure['weight']['value']
            )
        return True

    @classmethod
    def sub_validate_volume_obj(cls, initial_data, validate_data):
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

    @classmethod
    def sub_validate_weight_obj(cls, initial_data, validate_data):
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

    @classmethod
    def setup_price_list_data_in_sale(cls, initial_data):
        sale_price_list = initial_data.get('sale_price_list', [])
        for item in sale_price_list:
            price_list_id = item.get('price_list_id', None)
            price_list_value = float(item.get('price_list_value', 0))
            if not Price.objects.filter(id=price_list_id).exists() or price_list_value < 0:
                raise serializers.ValidationError({'sale_product_price_list': ProductMsg.PRICE_LIST_NOT_EXIST})
        return sale_price_list

    @classmethod
    def create_product_types_mapped(cls, product_obj, product_types_mapped_list):
        bulk_info = []
        for item in product_types_mapped_list:
            bulk_info.append(ProductProductType(product=product_obj, product_type_id=item))
        ProductProductType.objects.filter(product=product_obj).delete()
        ProductProductType.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_product_variant_attribute(cls, product_obj, product_variant_attribute_list):
        bulk_info = []
        for item in product_variant_attribute_list:
            bulk_info.append(ProductVariantAttribute(product=product_obj, **item))
        ProductVariantAttribute.objects.filter(product=product_obj).delete()
        ProductVariantAttribute.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_product_variant_item(cls, product_obj, product_variant_item_list):
        bulk_info = []
        for item in product_variant_item_list:
            bulk_info.append(ProductVariant(product=product_obj, **item))
        ProductVariant.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def update_product_variant_item(cls, product_obj, product_variant_item_update_list):
        bulk_info = []
        for item in product_variant_item_update_list:
            if item.get('variant_value_id', None):
                variant_value_id = item.pop('variant_value_id')
                ProductVariant.objects.filter(id=variant_value_id).update(**item)
            else:
                bulk_info.append(ProductVariant(product=product_obj, **item))
        ProductVariant.objects.bulk_create(bulk_info)
        return True
    