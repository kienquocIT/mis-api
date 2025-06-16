from rest_framework import serializers

from apps.masterdata.saledata.models import WareHouse, ProductWareHouseLot
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.inventory.models import GoodsReceiptPurchaseRequest, GoodsReceiptProduct, GoodsReceiptRequestProduct, \
    GoodsReceiptWarehouse, GoodsReceiptLot, GoodsReceiptSerial, InventoryAdjustment, InventoryAdjustmentItem, \
    GoodsReceiptProductionReport
from apps.sales.production.models import ProductionOrder, ProductionReport, WorkOrder
from apps.sales.productmodification.models import ProductModification, RemovedComponent
from apps.sales.purchasing.models import PurchaseRequestProduct, PurchaseOrderProduct, PurchaseRequest, PurchaseOrder, \
    PurchaseOrderRequestProduct
from apps.shared import PurchaseRequestMsg, BaseMsg
from apps.shared.translations.sales import InventoryMsg, SaleMsg


class GoodsReceiptCommonCreate:
    @classmethod
    def create_m2m_goods_receipt_pr(cls, purchase_requests, instance):
        GoodsReceiptPurchaseRequest.objects.bulk_create([GoodsReceiptPurchaseRequest(
            goods_receipt=instance,
            purchase_request_id=purchase_request_id,
        ) for purchase_request_id in purchase_requests])
        return True

    @classmethod
    def create_m2m_goods_receipt_report(cls, instance):
        instance.goods_receipt_production_report_receipt.all().delete()
        GoodsReceiptProductionReport.objects.bulk_create([GoodsReceiptProductionReport(
            goods_receipt=instance,
            production_report_id=production_report_data.get('id', None),
        ) for production_report_data in instance.production_reports_data])
        return True

    @classmethod
    def create_goods_receipt_product(cls, goods_receipt_product, instance):
        for gr_product in goods_receipt_product:
            pr_products_data = gr_product.get('pr_products_data', [])
            gr_warehouse_data = gr_product.get('gr_warehouse_data', [])
            new_gr_product = GoodsReceiptProduct.objects.create(goods_receipt=instance, **gr_product)
            if new_gr_product.ia_item:
                new_gr_product.ia_item.action_status = True
                new_gr_product.ia_item.select_for_action = True
                new_gr_product.ia_item.save(update_fields=['action_status', 'select_for_action'])
            # If PO have PR
            # create sub model GoodsReceiptRequestProduct mapping goods_receipt_product
            if len(pr_products_data) > 0:
                for pr_product in pr_products_data:
                    gr_warehouse_data = pr_product.get('gr_warehouse_data', [])
                    new_pr_product = GoodsReceiptRequestProduct.objects.create(
                        goods_receipt=instance,
                        goods_receipt_product=new_gr_product,
                        **pr_product
                    )
                    # create sub model GoodsReceiptWarehouse mapping goods_receipt_request_product
                    cls.create_gr_warehouse_lot_serial(
                        warehouse_data=gr_warehouse_data,
                        instance=instance,
                        pr_product=new_pr_product,
                        gr_product=new_gr_product,
                    )
            else:
                # If PO doesn't have PR
                # create sub model GoodsReceiptWarehouse mapping goods_receipt_product
                cls.create_gr_warehouse_lot_serial(
                    warehouse_data=gr_warehouse_data,
                    instance=instance,
                    gr_product=new_gr_product
                )
        return True

    @classmethod
    def create_gr_warehouse_lot_serial(cls, warehouse_data, instance, pr_product=None, gr_product=None):
        for warehouse in warehouse_data:
            lot_data = warehouse.get('lot_data', [])
            serial_data = warehouse.get('serial_data', [])
            new_warehouse = GoodsReceiptWarehouse.objects.create(
                goods_receipt=instance,
                goods_receipt_request_product=pr_product,
                goods_receipt_product=gr_product,
                **warehouse
            )
            # create sub model GoodsReceiptLot + GoodsReceiptSerial mapping goods_receipt_warehouse
            GoodsReceiptLot.objects.bulk_create([
                GoodsReceiptLot(
                    goods_receipt=instance,
                    goods_receipt_warehouse=new_warehouse,
                    **lot
                ) for lot in lot_data
            ])
            GoodsReceiptSerial.objects.bulk_create([
                GoodsReceiptSerial(
                    goods_receipt=instance,
                    goods_receipt_warehouse=new_warehouse,
                    **serial
                ) for serial in serial_data
            ])
        return True

    @classmethod
    def delete_old_m2m_goods_receipt_pr(cls, instance):
        old_goods_receipt_pr = GoodsReceiptPurchaseRequest.objects.filter(goods_receipt=instance)
        if old_goods_receipt_pr:
            old_goods_receipt_pr.delete()
        return True

    @classmethod
    def delete_old_goods_receipt_product(cls, instance):
        old_gr_product = GoodsReceiptProduct.objects.filter(goods_receipt=instance)
        if old_gr_product:
            old_pr_product = GoodsReceiptRequestProduct.objects.filter(
                goods_receipt=instance,
                goods_receipt_product__in=old_gr_product
            )
            if old_pr_product:
                old_warehouse = GoodsReceiptWarehouse.objects.filter(
                    goods_receipt=instance,
                    goods_receipt_request_product__in=old_pr_product,
                )
                if old_warehouse:
                    old_lot = GoodsReceiptLot.objects.filter(
                            goods_receipt=instance,
                            goods_receipt_warehouse__in=old_warehouse,
                    )
                    if old_lot:
                        old_lot.delete()
                    old_serial = GoodsReceiptSerial.objects.filter(
                            goods_receipt=instance,
                            goods_receipt_warehouse__in=old_warehouse,
                    )
                    if old_serial:
                        old_serial.delete()
                    old_warehouse.delete()
                old_pr_product.delete()
            old_gr_product.delete()
        return True

    @classmethod
    def create_goods_receipt_sub_models(cls, purchase_requests, goods_receipt_product, instance, is_update=False):
        if purchase_requests:
            if is_update is True:
                cls.delete_old_m2m_goods_receipt_pr(instance=instance)
            cls.create_m2m_goods_receipt_pr(
                purchase_requests=purchase_requests,
                instance=instance
            )
        cls.create_m2m_goods_receipt_report(instance=instance)
        if goods_receipt_product:
            if is_update is True:
                cls.delete_old_goods_receipt_product(instance=instance)
            cls.create_goods_receipt_product(
                goods_receipt_product=goods_receipt_product,
                instance=instance
            )
        return True


class GoodsReceiptCommonValidate:

    @classmethod
    def validate_purchase_order_id(cls, value):
        if value is None:
            return value
        try:
            return str(PurchaseOrder.objects.get_on_company(
                id=value
            ).id)
        except PurchaseOrder.DoesNotExist:
            raise serializers.ValidationError({'purchase_order': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_inventory_adjustment_id(cls, value):
        if value is None:
            return value
        try:
            return str(InventoryAdjustment.objects.get_on_company(
                id=value
            ).id)
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError({'inventory_adjustment': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_supplier_id(cls, value):
        if value is None:
            return value
        try:
            return str(Account.objects.get_on_company(
                id=value
            ).id)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_purchase_requests(cls, value):
        if isinstance(value, list):
            if PurchaseRequest.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id__in=value
            ).count() == len(value):
                return value
            raise serializers.ValidationError({'detail': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST})
        raise serializers.ValidationError({'detail': PurchaseRequestMsg.PURCHASE_REQUEST_IS_ARRAY})

    @classmethod
    def validate_purchase_order_product_id(cls, value):
        try:
            return str(PurchaseOrderProduct.objects.get(id=value).id)
        except PurchaseOrderProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_order_product': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_ia_item_id(cls, value):
        try:
            return str(InventoryAdjustmentItem.objects.get(id=value).id)
        except InventoryAdjustmentItem.DoesNotExist:
            raise serializers.ValidationError({
                'ia_item': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_production_order_id(cls, value):
        try:
            if value is None:
                return value
            return str(ProductionOrder.objects.get(id=value).id)
        except ProductionOrder.DoesNotExist:
            raise serializers.ValidationError({
                'production_order_id': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_work_order_id(cls, value):
        try:
            if value is None:
                return value
            return str(WorkOrder.objects.get(id=value).id)
        except WorkOrder.DoesNotExist:
            raise serializers.ValidationError({
                'work_order_id': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_product_modification_id(cls, value):
        if value is None:
            return value
        try:
            return str(ProductModification.objects.get_on_company(
                id=value
            ).id)
        except ProductModification.DoesNotExist:
            raise serializers.ValidationError({'product_modification': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_product_modification_product_id(cls, value):
        try:
            return str(RemovedComponent.objects.get(id=value).id)
        except RemovedComponent.DoesNotExist:
            raise serializers.ValidationError({
                'product_modification_product': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_purchase_order_request_product_id(cls, value):
        try:
            if value is None:
                return value
            return str(PurchaseOrderRequestProduct.objects.get(id=value).id)
        except PurchaseOrderRequestProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_order_request_product': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_purchase_request_product_id(cls, value):
        try:
            if value is None:
                return value
            return str(PurchaseRequestProduct.objects.get(id=value).id)
        except PurchaseRequestProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_request_product': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_production_report_id(cls, value):
        try:
            if value is None:
                return value
            return str(ProductionReport.objects.get(id=value).id)
        except ProductionReport.DoesNotExist:
            raise serializers.ValidationError({
                'production_report_id': BaseMsg.NOT_EXIST
            })

    @classmethod
    def validate_product_id(cls, value):
        try:
            if value is None:
                return None
            return str(Product.objects.get(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_uom_id(cls, value):
        try:
            if value is None:
                return None
            return str(UnitOfMeasure.objects.get(id=value).id)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_tax_id(cls, value):
        try:
            return str(Tax.objects.get(id=value).id)
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_warehouse_id(cls, value):
        try:
            return str(WareHouse.objects.get(id=value).id)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_lot(cls, value):
        try:
            if value is None:
                return None
            return str(ProductWareHouseLot.objects.get(id=value).id)
        except ProductWareHouseLot.DoesNotExist:
            raise serializers.ValidationError({'lot': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_quantity_import(cls, value):
        if value <= 0:
            raise serializers.ValidationError({'quantity_import': InventoryMsg.GOODS_RECEIPT_QUANTITY})
        return value

    @classmethod
    def validate_price(cls, value):
        if isinstance(value, float):
            if value <= 0:
                raise serializers.ValidationError({'price': SaleMsg.PRICE_VALID})
        return value
