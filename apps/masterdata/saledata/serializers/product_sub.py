from apps.masterdata.saledata.models import ProductMeasurements
from apps.masterdata.saledata.models.price import ProductPriceList


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

    @classmethod
    def delete_price_list(cls, product, price_list_id):
        product_price_list_item = ProductPriceList.objects.filter(
            product=product,
            uom_using_id=product.sale_default_uom_id,
            currency_using_id=product.sale_currency_using_id,
            price_list_id__in=price_list_id,
        )
        if product_price_list_item:
            product_price_list_item.delete()
