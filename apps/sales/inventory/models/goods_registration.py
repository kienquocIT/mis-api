from django.db import models
from apps.shared import DataAbstractModel, SimpleAbstractModel


class GoodsRegistration(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder', on_delete=models.CASCADE, related_name='goods_registration_so'
    )

    class Meta:
        verbose_name = 'Goods Registration'
        verbose_name_plural = 'Goods Registrations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create_goods_registration_when_sale_order_approved(cls, sale_order):
        if sale_order.company.company_config.cost_per_project:  # Case 5
            goods_registration = GoodsRegistration.objects.create(
                code=f'GRe-{sale_order.code}',
                title=f'{sale_order.code}-GoodsRegistration',
                sale_order=sale_order,
                employee_inherit_id=sale_order.employee_inherit_id,
                employee_created_id=sale_order.employee_created_id,
                company_id=sale_order.company_id,
                tenant_id=sale_order.tenant_id,
                system_status=1
            )
            bulk_info = []
            for so_item in sale_order.sale_order_product_sale_order.filter(product__isnull=False):
                if 1 in so_item.product.product_choice:
                    bulk_info.append(
                        GoodsRegistrationLineDetail(
                            goods_registration=goods_registration,
                            so_item=so_item
                        )
                    )
            GoodsRegistrationLineDetail.objects.bulk_create(bulk_info)
            return goods_registration
        return None

    @classmethod
    def update_registered_quantity_when_receipt(cls, sale_order, stock_info):
        if sale_order.opportunity:
            gre = sale_order.goods_registration_so.first()
            so_item = sale_order.sale_order_product_sale_order.filter(product=stock_info['product']).first()
            if gre and so_item:
                gre_item = GoodsRegistrationLineDetail.objects.filter(goods_registration=gre, so_item=so_item).first()
                if gre_item:
                    gre_item.this_registered += stock_info['quantity']
                    gre_item.this_registered_value += stock_info['value']
                    gre_item.this_available = gre_item.this_registered - gre_item.this_others
                    gre_item.this_available_value = gre_item.this_registered_value - gre_item.this_others_value
                    gre_item.registered_data += [{
                        'product_id': str(stock_info['product'].id),
                        'product_code': stock_info['product'].code,
                        'warehouse_id': str(stock_info['warehouse'].id),
                        'warehouse_code': stock_info['warehouse'].code,
                        'system_date': str(stock_info['system_date']),
                        'posting_date': str(stock_info['posting_date']),
                        'document_date': str(stock_info['document_date']),
                        'stock_type': stock_info['stock_type'],
                        'trans_id': stock_info['trans_id'],
                        'trans_code': stock_info['trans_code'],
                        'trans_title': stock_info['trans_title'],
                        'quantity': stock_info['quantity'],
                        'cost': stock_info['cost'],
                        'value': stock_info['value'],
                        'lot_data': stock_info['lot_data']
                    }]
                    gre_item.save(update_fields=[
                        'this_registered', 'this_registered_value',
                        'this_available', 'this_available_value',
                        'registered_data'
                    ])
                    if len(stock_info['lot_data']) > 0:
                        GoodsRegistrationLot.objects.create(
                            goods_registration_item=gre_item,
                            lot_registered_id=stock_info['lot_data']['lot_id'],
                            lot_registered_quantity=stock_info['lot_data']['lot_quantity']
                        )
        return True


class GoodsRegistrationLineDetail(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='goods_registration_line_detail'
    )
    so_item = models.ForeignKey(
        'saleorder.SaleOrderProduct', on_delete=models.CASCADE, related_name='goods_registration_line_detail_so_item'
    )

    this_registered = models.FloatField(default=0)
    this_registered_value = models.FloatField(default=0)

    this_others = models.FloatField(default=0)
    this_others_value = models.FloatField(default=0)

    this_available = models.FloatField(default=0)
    this_available_value = models.FloatField(default=0)

    registered_data = models.JSONField(default=list)

    out_registered = models.FloatField(default=0)
    out_registered_value = models.FloatField(default=0)

    out_delivered = models.FloatField(default=0)
    out_delivered_value = models.FloatField(default=0)

    out_remain = models.FloatField(default=0)
    out_remain_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Registration Line Detail'
        verbose_name_plural = 'Goods Registration Lines Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationLot(SimpleAbstractModel):
    goods_registration_item = models.ForeignKey(
        GoodsRegistrationLineDetail, on_delete=models.CASCADE, related_name='goods_registration_item_lot'
    )
    lot_registered = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, related_name='goods_registration_lot_registered'
    )
    lot_registered_quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Registration Lot'
        verbose_name_plural = 'Goods Registration Lots'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationSerial(SimpleAbstractModel):
    goods_registration_item = models.ForeignKey(
        GoodsRegistrationLineDetail, on_delete=models.CASCADE, related_name='goods_registration_item_serial'
    )
    sn_registered = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, related_name='goods_registration_sn_registered'
    )

    class Meta:
        verbose_name = 'Goods Registration Serial'
        verbose_name_plural = 'Goods Registration Serials'
        ordering = ()
        default_permissions = ()
        permissions = ()
