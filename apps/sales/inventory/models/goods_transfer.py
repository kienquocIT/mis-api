from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouseLot,
    ProductWareHouse,
    ProductWareHouseSerial,
    SubPeriods
)
from apps.sales.inventory.models.goods_registration import GReItemSub, GReItemProductWarehouse
from apps.sales.report.utils.log_for_goods_transfer import IRForGoodsTransferHandler
from apps.shared import DataAbstractModel, GOODS_TRANSFER_TYPE, MasterDataAbstractModel, AutoDocumentAbstractModel, \
    SimpleAbstractModel

__all__ = ['GoodsTransfer', 'GoodsTransferProduct']


class GoodsTransfer(DataAbstractModel, AutoDocumentAbstractModel):
    goods_transfer_type = models.SmallIntegerField(
        default=0,
        choices=GOODS_TRANSFER_TYPE,
        help_text='choices= ' + str(GOODS_TRANSFER_TYPE),
    )
    equipment_loan = models.ForeignKey(
        'equipmentloan.EquipmentLoan',
        on_delete=models.CASCADE,
        related_name='goods_transfer_el',
        null=True,
    )
    note = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    agency = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name='goods_transfer_agency',
        null=True,
    )
    date_transfer = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Goods Transfer'
        verbose_name_plural = 'Goods Transfer'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def update_product_warehouse(cls, item, tenant_id, company_id):
        src_prd_wh = item.product.product_warehouse_product.filter_on_company(
            warehouse=item.warehouse
        ).first() if item.product.product_warehouse_product else None
        des_prd_wh = item.product.product_warehouse_product.filter_on_company(
            warehouse=item.end_warehouse
        ).first() if item.product.product_warehouse_product else None

        if src_prd_wh:
            src_prd_wh.receipt_amount -= item.quantity
            src_prd_wh.stock_amount = src_prd_wh.receipt_amount - src_prd_wh.sold_amount
            src_prd_wh.save(update_fields=['receipt_amount', 'stock_amount'])

        if des_prd_wh:
            des_prd_wh.receipt_amount += item.quantity
            des_prd_wh.stock_amount = des_prd_wh.receipt_amount - des_prd_wh.sold_amount
            des_prd_wh.save(update_fields=['receipt_amount', 'stock_amount'])
        else:
            data_item = {
                'tenant_id': tenant_id,
                'company_id': company_id,
                'product': item.product,
                'uom': item.uom,
                'warehouse': item.end_warehouse,
                'unit_price': item.unit_cost,
                'stock_amount': item.quantity,
                'receipt_amount': item.quantity,
                'sold_amount': 0,
                'picked_ready': 0,
                'product_data': {
                    'id': item.product_id,
                    'code': item.product.code,
                    'title': item.product.title
                },
                'warehouse_data': {
                    'id': item.end_warehouse_id,
                    'code': item.end_warehouse.code,
                    'title': item.end_warehouse.title
                },
                'uom_data': {
                    'id': item.uom_id,
                    'code': item.uom.code,
                    'title': item.uom.title
                },
            }
            des_prd_wh = ProductWareHouse.objects.create(**data_item)
        return src_prd_wh, des_prd_wh

    @classmethod
    def update_prd_wh_lot(cls, src_prd_wh, des_prd_wh, lot_data, tenant_id, company_id):
        all_lot_src = src_prd_wh.product_warehouse_lot_product_warehouse.all()
        all_lot_des = des_prd_wh.product_warehouse_lot_product_warehouse.all()
        bulk_info = []
        for lot_item in lot_data:
            lot_src_obj = all_lot_src.filter(id=lot_item['lot_id']).first()
            if lot_src_obj and lot_src_obj.quantity_import >= lot_item['quantity']:
                lot_src_obj.quantity_import -= lot_item['quantity']
                lot_src_obj.save(update_fields=['quantity_import'])
                lot_des_obj = all_lot_des.filter(lot_number=lot_src_obj.lot_number).first()
                if lot_des_obj:
                    lot_des_obj.quantity_import += lot_item['quantity']
                    lot_des_obj.save(update_fields=['quantity_import'])
                else:
                    bulk_info.append(
                        ProductWareHouseLot(
                            tenant_id=tenant_id,
                            company_id=company_id,
                            product_warehouse=des_prd_wh,
                            lot_number=lot_src_obj.lot_number,
                            quantity_import=lot_item['quantity'],
                            expire_date=lot_src_obj.expire_date,
                            manufacture_date=lot_src_obj.manufacture_date
                        )
                    )
            else:
                print('Update Lot failed.')
        ProductWareHouseLot.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def update_prd_wh_serial(cls, src_prd_wh, des_prd_wh, sn_data, tenant_id, company_id):
        all_sn_src = src_prd_wh.product_warehouse_serial_product_warehouse.all()
        bulk_info = []
        for sn_id in sn_data:
            sn_src_obj = all_sn_src.filter(id=sn_id).first()
            if sn_src_obj and not sn_src_obj.serial_status:
                sn_src_obj.serial_status = 1
                sn_src_obj.save(update_fields=['serial_status'])
                bulk_info.append(
                    ProductWareHouseSerial(
                        tenant_id=tenant_id,
                        company_id=company_id,
                        product_warehouse=des_prd_wh,
                        vendor_serial_number=sn_src_obj.vendor_serial_number,
                        serial_number=sn_src_obj.serial_number,
                        expire_date=sn_src_obj.expire_date,
                        manufacture_date=sn_src_obj.manufacture_date,
                        warranty_start=sn_src_obj.warranty_start,
                        warranty_end=sn_src_obj.warranty_end,
                        use_for_modification=sn_src_obj.use_for_modification
                    )
                )
            else:
                print('Update Serial failed.')
        ProductWareHouseSerial.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def update_data_warehouse(cls, goods_transfer_obj):
        tenant_id = goods_transfer_obj.tenant_id
        company_id = goods_transfer_obj.company_id
        for item in goods_transfer_obj.goods_transfer.all():
            src_prd_wh, des_prd_wh = cls.update_product_warehouse(item, tenant_id, company_id)
            if item.product.general_traceability_method == 1:  # lot
                cls.update_prd_wh_lot(src_prd_wh, des_prd_wh, item.lot_data, tenant_id, company_id)
            elif item.product.general_traceability_method == 2:  # sn
                cls.update_prd_wh_serial(src_prd_wh, des_prd_wh, item.sn_data, tenant_id, company_id)
        return True

    @classmethod
    def check_and_create_gre_item_sub_if_transfer_in_project(cls, goods_transfer, goods_transfer_item):
        goods_registration = goods_transfer_item.sale_order.goods_registration_so.first()
        gre_item = goods_registration.gre_item.filter(product=goods_transfer_item.product).first()

        # update gre_item_prd_wh
        gre_item_prd_wh = gre_item.gre_item_prd_wh.all()
        gre_item_prd_wh_out_warehouse = gre_item_prd_wh.filter(warehouse=goods_transfer_item.warehouse).first()
        gre_item_prd_wh_in_warehouse = gre_item_prd_wh.filter(warehouse=goods_transfer_item.end_warehouse).first()
        if gre_item_prd_wh_out_warehouse:
            gre_item_prd_wh_out_warehouse.quantity -= goods_transfer_item.quantity
            gre_item_prd_wh_out_warehouse.save(update_fields=['quantity'])
        if gre_item_prd_wh_in_warehouse:
            gre_item_prd_wh_in_warehouse.quantity += goods_transfer_item.quantity
            gre_item_prd_wh_in_warehouse.save(update_fields=['quantity'])
        else:
            GReItemProductWarehouse.objects.create(
                goods_registration=goods_registration,
                gre_item=gre_item,
                warehouse=goods_transfer_item.end_warehouse,
                quantity=goods_transfer_item.quantity
            )

        casted_quantity = (
                goods_transfer_item.quantity / goods_transfer_item.product.inventory_uom.ratio
        ) if goods_transfer_item.product.inventory_uom.ratio else 0
        GReItemSub.objects.bulk_create(
            [
                GReItemSub(
                    goods_registration=goods_registration,
                    gre_item=gre_item,
                    warehouse=goods_transfer_item.warehouse,
                    quantity=casted_quantity,
                    cost=goods_transfer_item.unit_cost,
                    value=casted_quantity * goods_transfer_item.unit_cost,
                    stock_type=-1,
                    uom=goods_transfer_item.uom,
                    trans_id=goods_transfer.id,
                    trans_code=goods_transfer.code,
                    trans_title='Goods transfer (out)',
                    system_date=goods_transfer.date_approved
                ),
                GReItemSub(
                    goods_registration=goods_registration,
                    gre_item=gre_item,
                    warehouse=goods_transfer_item.end_warehouse,
                    quantity=casted_quantity,
                    cost=goods_transfer_item.unit_cost,
                    value=casted_quantity * goods_transfer_item.unit_cost,
                    stock_type=1,
                    uom=goods_transfer_item.uom,
                    trans_id=goods_transfer.id,
                    trans_code=goods_transfer.code,
                    trans_title='Goods transfer (in)',
                    system_date=goods_transfer.date_approved
                )
            ]
        )

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_check_period', False):
            SubPeriods.check_period(self.tenant_id, self.company_id)

        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'GT[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                if self.system_status == 3:
                    self.update_data_warehouse(self)
                    for item in self.goods_transfer.filter(sale_order__isnull=False):
                        self.check_and_create_gre_item_sub_if_transfer_in_project(self, item)
                    IRForGoodsTransferHandler.push_to_inventory_report(self)

        # hit DB
        super().save(*args, **kwargs)


class GoodsTransferProduct(SimpleAbstractModel):
    goods_transfer = models.ForeignKey(
        GoodsTransfer,
        on_delete=models.CASCADE,
        related_name='goods_transfer',
    )
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_warehouse_goods_transfer',
    )

    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_transfer',
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="product_goods_transfer",
    )

    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="sale_order_goods_transfer",
        null=True
    )

    end_warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='end_warehouse_goods_transfer',
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_transfer',
    )

    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]
    quantity = models.FloatField(default=0)
    unit_cost = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Transfer Product'
        verbose_name_plural = 'Goods Transfer Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
