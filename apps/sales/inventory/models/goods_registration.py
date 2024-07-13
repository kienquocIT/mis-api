from django.db import models
from apps.masterdata.saledata.models import ProductWareHouseSerial
from apps.shared import DataAbstractModel, SimpleAbstractModel


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    return (log_quantity / inventory_uom.ratio) if inventory_uom.ratio else 0


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
    def check_and_create_goods_registration(cls, sale_order):
        if sale_order.company.company_config.cost_per_project:  # Project
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
            sale_order.has_regis = True
            sale_order.save(update_fields=['has_regis'])
            bulk_info = []
            for so_item in sale_order.sale_order_product_sale_order.filter(product__isnull=False):
                if 1 in so_item.product.product_choice:  # inventory
                    bulk_info.append(
                        GoodsRegistrationItem(
                            goods_registration=goods_registration,
                            so_item=so_item,
                            product=so_item.product
                        )
                    )
            GoodsRegistrationItem.objects.bulk_create(bulk_info)
            return goods_registration
        return None

    @classmethod
    def update_gre_general(cls, gre_item, stock_info):
        casted_quantity_to_inv = cast_unit_to_inv_quantity(stock_info['product'].inventory_uom, stock_info['quantity'])
        gre_item.this_registered += casted_quantity_to_inv * stock_info['stock_type']
        gre_item.this_registered_value += stock_info['value'] * stock_info['stock_type']
        gre_item.this_available = gre_item.this_registered
        gre_item.this_available_value = gre_item.this_registered_value

        # create sub, save by inventory uom
        GoodsRegistrationItemSub.objects.create(
            goods_registration=gre_item.goods_registration,
            gre_item=gre_item,
            warehouse=stock_info['warehouse'],
            quantity=casted_quantity_to_inv,
            cost=stock_info['value'] / casted_quantity_to_inv,
            value=stock_info['value'],
            stock_type=stock_info['stock_type'],
            uom=stock_info['product'].inventory_uom,
            trans_id=stock_info['trans_id'],
            trans_code=stock_info['trans_code'],
            trans_title=stock_info['trans_title'],
            system_date=stock_info['system_date'],
            lot_mapped_id=stock_info['lot_data']['lot_id'] if len(stock_info['lot_data']) > 0 else None
        )

        # create/update general, save by base uom
        gre_general = GoodsRegistrationGeneral.objects.filter(
            gre_item=gre_item,
            warehouse=stock_info['warehouse']
        ).first()
        if gre_general:
            gre_general.quantity += stock_info['quantity'] * stock_info['stock_type']
            gre_general.save(update_fields=['quantity'])
        else:
            gre_general = GoodsRegistrationGeneral.objects.create(
                goods_registration=gre_item.goods_registration,
                gre_item=gre_item,
                warehouse=stock_info['warehouse'],
                quantity=stock_info['quantity']
            )
        return gre_item, gre_general

    @classmethod
    def for_goods_receipt(cls, stock_info, gre_item, goods_receipt_id):
        gre_item, gre_general = cls.update_gre_general(gre_item, stock_info)
        # create lot/sn data
        if stock_info['product'].general_traceability_method == 1:  # lot
            GoodsRegistrationLot.objects.create(
                goods_registration=gre_general.goods_registration,
                gre_general=gre_general,
                lot_registered_id=stock_info['lot_data']['lot_id']
            )
        if stock_info['product'].general_traceability_method == 2:  # sn
            bulk_info = []
            for serial in ProductWareHouseSerial.objects.filter(goods_receipt=goods_receipt_id):
                bulk_info.append(
                    GoodsRegistrationSerial(
                        goods_registration=gre_general.goods_registration,
                        gre_general=gre_general,
                        sn_registered=serial
                    )
                )
            GoodsRegistrationSerial.objects.bulk_create(bulk_info)
        return gre_item

    @classmethod
    def for_delivery(cls, stock_info, gre_item):
        gre_item, _ = cls.update_gre_general(gre_item, stock_info)
        return gre_item

    @classmethod
    def update_registered_quantity(cls, sale_order, stock_info, **kwargs):
        if sale_order.opportunity and stock_info.get('sale_order'):
            gre = sale_order.goods_registration_so.first()
            if gre:
                gre_item = GoodsRegistrationItem.objects.filter(
                    goods_registration=gre,
                    product=stock_info['product']
                ).first()
                if gre_item:
                    if 'goods_receipt_id' in kwargs:
                        gre_item = cls.for_goods_receipt(stock_info, gre_item, kwargs.get('goods_receipt_id'))
                    if 'delivery_id' in kwargs:
                        gre_item = cls.for_delivery(stock_info, gre_item)
                    gre_item.save(update_fields=[
                        'this_registered', 'this_registered_value',
                        'this_available', 'this_available_value',
                    ])
        return True


class GoodsRegistrationItem(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='gre_item'
    )
    so_item = models.ForeignKey(
        'saleorder.SaleOrderProduct', on_delete=models.CASCADE, related_name='gre_item_so_item'
    )
    product = models.ForeignKey(
        'saledata.Product', on_delete=models.CASCADE, related_name='gre_item_product', null=True
    )

    # số lượng hàng của dự án này
    this_registered = models.FloatField(default=0)
    this_registered_value = models.FloatField(default=0)
    this_registered_borrowed = models.FloatField(default=0)
    this_registered_value_borrowed = models.FloatField(default=0)
    this_available = models.FloatField(default=0)
    this_available_value = models.FloatField(default=0)

    # số lượng hàng mượn của dự án khác
    out_registered = models.FloatField(default=0)
    out_available = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Registration Item'
        verbose_name_plural = 'Goods Registration Item'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationItemSub(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, null=True
    )
    gre_item = models.ForeignKey(
        GoodsRegistrationItem, on_delete=models.CASCADE, related_name='gre_item_sub', null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse', on_delete=models.CASCADE, related_name="gre_item_sub_warehouse", null=True
    )

    quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    value = models.FloatField(default=0)

    stock_type = models.SmallIntegerField(choices=[(1, 'In'), (-1, 'Out')], default=1)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure', on_delete=models.CASCADE, related_name="gre_item_sub_uom", null=True
    )
    trans_id = models.CharField(blank=True, max_length=100, null=True)
    trans_code = models.CharField(blank=True, max_length=100, null=True)
    trans_title = models.CharField(blank=True, max_length=100, null=True)
    system_date = models.DateTimeField(null=True)
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = 'Goods Registration Item Sub'
        verbose_name_plural = 'Goods Registration Item Subs'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationGeneral(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, null=True
    )
    gre_item = models.ForeignKey(
        GoodsRegistrationItem, on_delete=models.CASCADE, related_name='gre_item_general', null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name="gre_item_general_warehouse",
        null=True
    )
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Registration General'
        verbose_name_plural = 'Goods Registration General'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationLot(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, null=True
    )
    gre_general = models.ForeignKey(
        GoodsRegistrationGeneral, on_delete=models.CASCADE, related_name='gre_general_lot', null=True
    )
    lot_registered = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, related_name='gre_lot_registered'
    )

    class Meta:
        verbose_name = 'Goods Registration Lot'
        verbose_name_plural = 'Goods Registration Lot'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationSerial(SimpleAbstractModel):
    goods_registration = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, null=True
    )
    gre_general = models.ForeignKey(
        GoodsRegistrationGeneral, on_delete=models.CASCADE, related_name='gre_general_serial', null=True
    )
    sn_registered = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, related_name='gre_sn_registered'
    )

    class Meta:
        verbose_name = 'Goods Registration Serial'
        verbose_name_plural = 'Goods Registration Serial'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsRegistrationItemBorrow(SimpleAbstractModel):
    """ Ghi lại dữ liệu mượn hàng giữa các dự án """

    goods_registration_source = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='gre_src', null=True
    )
    gre_item_source = models.ForeignKey(
        GoodsRegistrationItem, on_delete=models.CASCADE, related_name='gre_item_borrow_src', null=True
    )

    quantity = models.FloatField(default=0)
    available = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure', on_delete=models.CASCADE, related_name="gre_item_borrow_uom", null=True
    )

    goods_registration_destination = models.ForeignKey(
        GoodsRegistration, on_delete=models.CASCADE, related_name='gre_des', null=True
    )
    gre_item_destination = models.ForeignKey(
        GoodsRegistrationItem, on_delete=models.CASCADE, related_name='gre_item_borrow_des', null=True
    )

    class Meta:
        verbose_name = 'Goods Registration Item Borrow'
        verbose_name_plural = 'Goods Registration Item Borrow'
        ordering = ()
        default_permissions = ()
        permissions = ()
