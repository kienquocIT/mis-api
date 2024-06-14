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
                        so_item=so_item,
                        registered_quantity=0,
                        registered_data={}
                    )
                )
        GoodsRegistrationLineDetail.objects.bulk_create(bulk_info)
        return goods_registration

    @classmethod
    def update_registered_quantity_when_receipt(cls, sale_order, product_data):
        gre = sale_order.goods_registration_so.first()
        if gre:
            so_items = sale_order.sale_order_product_sale_order.filter(product__isnull=False).select_related('product')
            gre_line_detail = GoodsRegistrationLineDetail.objects.filter(
                goods_registration=gre,
                so_item=so_items.filter(product_id=product_data['product_id']).first(),
            ).first()
            if gre_line_detail:
                gre_line_detail.registered_quantity += product_data['registered_quantity']
                gre_line_detail.available_quantity += product_data['registered_quantity']
                gre_line_detail.registered_data += product_data['registered_data']
                gre_line_detail.save(update_fields=['registered_quantity', 'available_quantity', 'registered_data'])
                if len(product_data['registered_data'][0]['lot_data']) > 0:
                    GoodsRegistrationLot.objects.create(
                        goods_registration_item=gre_line_detail,
                        lot_registered=product_data['registered_data'][0]['lot_data']['lot_id'],
                        lot_registered_quantity=product_data['registered_data'][0]['lot_data']['lot_quantity']
                    )
        else:
            raise ValueError('Not Exist: Sale Order does not have Goods Registration')


class GoodsRegistrationLineDetail(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='goods_registration_line_detail'
    )
    so_item = models.ForeignKey(
        'saleorder.SaleOrderProduct', on_delete=models.CASCADE, related_name='goods_registration_line_detail_so_item'
    )
    registered_quantity = models.FloatField(default=0)
    others_quantity = models.FloatField(default=0)
    available_quantity = models.FloatField(default=0)
    registered_data = models.JSONField(default=list)
    # registered_data_format = [{
    #     'product_id': ...,
    #     'registered_quantity': ...,
    #     'registered_data': [{
    #         'goods_receipt_id': ...,
    #         'warehouse_id': ...,
    #         'lot_data': {
    #             'lot_id': ..., 'lot_number': ..., 'lot_quantity': ...
    #         }
    #     }]
    # }]

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
