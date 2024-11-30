from django.db import models
from rest_framework import serializers
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking
)
from apps.sales.inventory.utils import ReturnFinishHandler, ReturnHandler
from apps.sales.report.inventory_log import ReportInvLog, ReportInvCommonFunc
from apps.sales.report.models import ReportStockLog
from apps.shared import DataAbstractModel


class GoodsDetail(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='goods_detail_product',
    )
    product_data = models.JSONField(default=dict)
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='goods_detail_warehouse',
    )
    warehouse_data = models.JSONField(default=dict)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='goods_detail_uom',
    )
    uom_data = models.JSONField(default=dict)
    goods_receipt = models.ForeignKey(
        'inventory.GoodsReceipt',
        on_delete=models.CASCADE,
        related_name='goods_detail_goods_receipt',
    )
    goods_receipt_data = models.JSONField(default=dict)
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        related_name='goods_detail_purchase_request',
        null=True
    )
    purchase_request_data = models.JSONField(default=dict)
    lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        related_name='goods_detail_lot',
        null=True
    )
    lot_data = models.JSONField(default=dict)
    imported_sn_quantity = models.FloatField(default=0)
    receipt_quantity = models.FloatField(default=0)
    status = models.BooleanField(default=False)

    @staticmethod
    def count_created_serial_data(good_receipt_obj, gr_prd_obj, gr_wh_obj, pr_data):
        count = 0
        for serial in good_receipt_obj.pw_serial_goods_receipt.filter(
                product_warehouse__product=gr_prd_obj.product,
                product_warehouse__warehouse=gr_wh_obj.warehouse,
        ).order_by('date_created'):
            if serial.purchase_request_id:
                if str(serial.purchase_request_id) == pr_data.get('id'):
                    count += 1
            else:
                count += 1
        return count

    @classmethod
    def push_goods_receipt_data_to_goods_detail(cls, goods_receipt_obj):
        print(f'* Push goods receipt data ({goods_receipt_obj.code}) to_goods detail.')
        for gr_prd_obj in goods_receipt_obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                pr_data = gr_wh_obj.goods_receipt_request_product.purchase_request_data if (
                    gr_wh_obj.goods_receipt_request_product) else {}
                gr_wh_lot_obj = gr_wh_obj.goods_receipt_lot_gr_warehouse.first()
                count_serial_data = cls.count_created_serial_data(
                    goods_receipt_obj, gr_prd_obj, gr_wh_obj, pr_data
                )
                GoodsDetail.objects.create(
                    product=gr_prd_obj.product,
                    product_data={
                        'id': str(gr_prd_obj.product_id),
                        'code': gr_prd_obj.product.code,
                        'title': gr_prd_obj.product.title,
                        'category': str(gr_prd_obj.product.general_product_category_id),
                        'general_traceability_method': gr_prd_obj.product.general_traceability_method
                    } if gr_prd_obj.product else {},
                    warehouse=gr_wh_obj.warehouse,
                    warehouse_data={
                        'id': str(gr_wh_obj.warehouse_id),
                        'code': gr_wh_obj.warehouse.code,
                        'title': gr_wh_obj.warehouse.title
                    } if gr_wh_obj.warehouse else {},
                    uom=gr_prd_obj.uom,
                    uom_data=gr_prd_obj.uom_data,
                    goods_receipt=goods_receipt_obj,
                    goods_receipt_data={
                        'id': str(goods_receipt_obj.id),
                        'code': goods_receipt_obj.code,
                        'title': goods_receipt_obj.title,
                        'date_approved': str(goods_receipt_obj.date_approved),
                        'pic': {
                            'id': str(goods_receipt_obj.employee_inherit_id),
                            'code': goods_receipt_obj.employee_inherit.code,
                            'fullname': goods_receipt_obj.employee_inherit.get_full_name(2),
                            'group': {
                                'id': str(goods_receipt_obj.employee_inherit.group_id),
                                'code': goods_receipt_obj.employee_inherit.group.code,
                                'title': goods_receipt_obj.employee_inherit.group.title,
                            } if goods_receipt_obj.employee_inherit.group else {},
                        } if goods_receipt_obj.employee_inherit else {},
                    } if goods_receipt_obj else {},
                    purchase_request_id=pr_data.get('id'),
                    purchase_request_data=pr_data,
                    lot=gr_wh_lot_obj.lot if gr_wh_lot_obj else None,
                    lot_data={
                        'id': str(gr_wh_lot_obj.lot_id),
                        'lot_number': gr_wh_lot_obj.lot.lot_number,
                        'expire_date': str(gr_wh_lot_obj.lot.expire_date),
                        'manufacture_date': str(gr_wh_lot_obj.lot.manufacture_date)
                    } if gr_wh_lot_obj else {},
                    imported_sn_quantity=count_serial_data,
                    receipt_quantity=gr_wh_obj.quantity_import,
                    status=int(count_serial_data == gr_wh_obj.quantity_import),
                    tenant=goods_receipt_obj.tenant,
                    company=goods_receipt_obj.company,
                    employee_inherit=goods_receipt_obj.employee_inherit,
                    employee_created=goods_receipt_obj.employee_created
                )
        print('Done')
        return True

    class Meta:
        verbose_name = 'Goods Detail'
        verbose_name_plural = 'Goods Detail'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
