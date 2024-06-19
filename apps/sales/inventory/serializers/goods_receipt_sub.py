from rest_framework import serializers

from apps.masterdata.saledata.models import WareHouse, ProductWareHouseLot
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.inventory.models import GoodsReceiptPurchaseRequest, GoodsReceiptProduct, GoodsReceiptRequestProduct, \
    GoodsReceiptWarehouse, GoodsReceiptLot, GoodsReceiptSerial, InventoryAdjustment
from apps.sales.purchasing.models import PurchaseRequestProduct, PurchaseOrderProduct, PurchaseRequest, PurchaseOrder, \
    PurchaseOrderRequestProduct
from apps.shared import AccountsMsg, ProductMsg, PurchaseRequestMsg, PurchasingMsg, WarehouseMsg
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
    def create_goods_receipt_product(cls, goods_receipt_product, instance):
        for gr_product in goods_receipt_product:
            purchase_request_products_data = []
            if 'purchase_request_products_data' in gr_product:
                purchase_request_products_data = gr_product['purchase_request_products_data']
                del gr_product['purchase_request_products_data']
            warehouse_gr_data = []
            if 'warehouse_data' in gr_product:
                warehouse_gr_data = gr_product['warehouse_data']
                del gr_product['warehouse_data']
            new_gr_product = GoodsReceiptProduct.objects.create(goods_receipt=instance, **gr_product)
            if new_gr_product.ia_item:
                new_gr_product.ia_item.action_status = True
                new_gr_product.ia_item.select_for_action = True
                new_gr_product.ia_item.save(update_fields=['action_status', 'select_for_action'])
            # If PO have PR
            # create sub model GoodsReceiptRequestProduct mapping goods_receipt_product
            for pr_product in purchase_request_products_data:
                warehouse_pr_data = []
                if 'warehouse_data' in pr_product:
                    warehouse_pr_data = pr_product['warehouse_data']
                    del pr_product['warehouse_data']
                new_pr_product = GoodsReceiptRequestProduct.objects.create(
                    goods_receipt=instance,
                    goods_receipt_product=new_gr_product,
                    **pr_product
                )
                # create sub model GoodsReceiptWarehouse mapping goods_receipt_request_product
                cls.create_gr_warehouse_lot_serial(
                    warehouse_data=warehouse_pr_data,
                    instance=instance,
                    pr_product=new_pr_product,
                    gr_product=new_gr_product,
                )
            # If PO doesn't have PR
            # create sub model GoodsReceiptWarehouse mapping goods_receipt_product
            cls.create_gr_warehouse_lot_serial(
                warehouse_data=warehouse_gr_data,
                instance=instance,
                gr_product=new_gr_product
            )
        return True

    @classmethod
    def create_gr_warehouse_lot_serial(cls, warehouse_data, instance, pr_product=None, gr_product=None):
        for warehouse in warehouse_data:
            lot_data = []
            serial_data = []
            if 'lot_data' in warehouse:
                lot_data = warehouse['lot_data']
                del warehouse['lot_data']
            if 'serial_data' in warehouse:
                serial_data = warehouse['serial_data']
                del warehouse['serial_data']
            new_warehouse = GoodsReceiptWarehouse.objects.create(
                goods_receipt=instance,
                goods_receipt_request_product=pr_product,
                goods_receipt_product=gr_product,
                **warehouse
            )
            # create sub model GoodsReceiptLot + GoodsReceiptSerial mapping goods_receipt_warehouse
            for lot in lot_data:
                GoodsReceiptLot.objects.create(
                    goods_receipt=instance,
                    goods_receipt_warehouse=new_warehouse,
                    **lot
                )
            for serial in serial_data:
                GoodsReceiptSerial.objects.create(
                    goods_receipt=instance,
                    goods_receipt_warehouse=new_warehouse,
                    **serial
                )
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
    def validate_purchase_order(cls, value):
        if value is None:
            return value
        try:
            return PurchaseOrder.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except PurchaseOrder.DoesNotExist:
            raise serializers.ValidationError({'purchase_order': PurchasingMsg.PURCHASE_ORDER_NOT_EXIST})

    @classmethod
    def validate_inventory_adjustment(cls, value):
        if value is None:
            return value
        try:
            return InventoryAdjustment.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError({'inventory_adjustment': InventoryMsg.INVENTORY_ADJUSTMENT_NOT_EXIST})

    @classmethod
    def validate_supplier(cls, value):
        if value is None:
            return value
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': AccountsMsg.ACCOUNT_NOT_EXIST})

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
    def validate_purchase_order_product(cls, value):
        try:
            return PurchaseOrderProduct.objects.get(id=value)
        except PurchaseOrderProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_order_product': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST
            })

    @classmethod
    def validate_purchase_order_request_product(cls, value):
        try:
            if value is None:
                return value
            return PurchaseOrderRequestProduct.objects.get(id=value)
        except PurchaseOrderRequestProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_order_request_product': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST
            })

    @classmethod
    def validate_purchase_request_product(cls, value):
        try:
            if value is None:
                return value
            return PurchaseRequestProduct.objects.get(id=value)
        except PurchaseRequestProduct.DoesNotExist:
            raise serializers.ValidationError({
                'purchase_request_product': PurchaseRequestMsg.PURCHASE_REQUEST_NOT_EXIST
            })

    @classmethod
    def validate_product(cls, value):
        try:
            if value is None:
                return None
            return Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_uom(cls, value):
        try:
            if value is None:
                return None
            return UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        try:
            return Tax.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_warehouse(cls, value):
        try:
            return WareHouse.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_lot(cls, value):
        try:
            if value is None:
                return None
            return ProductWareHouseLot.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except ProductWareHouseLot.DoesNotExist:
            raise serializers.ValidationError({'lot': WarehouseMsg.LOT_NOT_EXIST})

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
