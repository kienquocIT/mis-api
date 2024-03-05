from rest_framework import serializers

from apps.masterdata.saledata.models import WareHouse
from apps.sales.delivery.models.delivery import OrderDeliveryLot
from apps.sales.inventory.models import GoodsReceiptLot, GoodsReturnProductDetail
from apps.sales.report.models import ReportInventory, ReportInventoryProductWarehouse, ReportInventorySub


class ReportInventoryDetailListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventory
        fields = (
            'id',
            'product',
            'period_mapped',
            'sub_period_order',
            'stock_activities'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
        } if obj.product else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_stock_activities(cls, obj):
        set_warehouse = set(WareHouse.objects.all().values_list('id', 'code', 'title'))
        result = []
        for warehouse_item in set_warehouse:
            wh_id, wh_code, wh_title = warehouse_item
            data_stock_activity = []
            obj_by_warehouse = ReportInventoryProductWarehouse.objects.filter(
                product=obj.product,
                warehouse_id=wh_id,
                sub_period_order=obj.sub_period_order
            ).first()
            if obj_by_warehouse:
                for item in obj.report_inventory_by_month.all().filter(warehouse_id=wh_id):
                    data_stock_activity.append({
                        'system_date': item.system_date,
                        'posting_date': item.posting_date,
                        'document_date': item.document_date,
                        'stock_type': item.stock_type,
                        'trans_code': item.trans_code,
                        'trans_title': item.trans_title,
                        'quantity': item.quantity,
                        'cost': item.cost,
                        'value': item.value,
                        'current_quantity': item.current_quantity,
                        'current_cost': item.current_cost,
                        'current_value': item.current_value,
                    })
                result.append({
                    'warehouse_id': wh_id,
                    'warehouse_code': wh_code,
                    'warehouse_title': wh_title,
                    'opening_balance_quantity': obj_by_warehouse.opening_balance_quantity,
                    'opening_balance_cost': obj_by_warehouse.opening_balance_cost,
                    'opening_balance_value': obj_by_warehouse.opening_balance_value,
                    'ending_balance_quantity': obj_by_warehouse.ending_balance_quantity,
                    'ending_balance_cost': obj_by_warehouse.ending_balance_cost,
                    'ending_balance_value': obj_by_warehouse.ending_balance_value,
                    'data_stock_activity': sorted(data_stock_activity, key=lambda key: key['system_date'])
                })
        return sorted(result, key=lambda key: key['warehouse_code'])


class BalanceInitializationListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventoryProductWarehouse
        fields = (
            'id',
            'product',
            'warehouse',
            'period_mapped',
            'sub_period_order',
            'opening_balance_quantity',
            'opening_balance_cost',
            'opening_balance_value',
            'ending_balance_quantity',
            'ending_balance_cost',
            'ending_balance_value'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
            'uom': {
                'id': obj.product.inventory_uom_id,
                'title': obj.product.inventory_uom.title,
                'code': obj.product.inventory_uom.code,
            }
        } if obj.product else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
            'space_month': obj.period_mapped.space_month,
            'fiscal_year': obj.period_mapped.fiscal_year,
        } if obj.period_mapped else {}


class ReportInventoryListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventoryProductWarehouse
        fields = (
            'id',
            'product',
            'warehouse',
            'period_mapped',
            'sub_period_order',
            'stock_activities',
            'opening_balance_quantity',
            'opening_balance_value',
            'ending_balance_quantity',
            'ending_balance_value',
            'for_balance',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
            'uom': {
                "id": obj.product.inventory_uom_id,
                "code": obj.product.inventory_uom.code,
                "title": obj.product.inventory_uom.title
            } if obj.product.inventory_uom else {}
        } if obj.product else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_stock_activities(cls, obj):
        in_out_data = []
        sum_in_quantity = 0
        sum_out_quantity = 0
        sum_in_value = 0
        sum_out_value = 0
        for item in ReportInventorySub.objects.filter(
            product=obj.product,
            warehouse=obj.warehouse,
            report_inventory__period_mapped=obj.period_mapped,
            report_inventory__sub_period_order=obj.sub_period_order
        ):

            sum_in_quantity += item.quantity
            sum_in_value += item.value
            lot_number = ''
            expire_date = ''
            if item.trans_title == 'Goods receipt':
                lot = GoodsReceiptLot.objects.filter(
                    goods_receipt_id=item.trans_id,
                    goods_receipt_warehouse__goods_receipt_product__product=item.product,
                    goods_receipt_warehouse__warehouse=item.warehouse
                ).first()
                if lot:
                    lot_number = lot.lot_number
                    expire_date = lot.expire_date
            elif item.trans_title == 'Goods return':
                lot = GoodsReturnProductDetail.objects.filter(
                    goods_return_id=item.trans_id,
                    goods_return__product=item.product,
                    goods_return__return_to_warehouse=item.warehouse,
                ).first()
                if lot:
                    if lot.lot_no:
                        lot_number = lot.lot_no.lot_number
                        expire_date = lot.lot_no.expire_date
            elif item.trans_title == 'Delivery':
                lot = OrderDeliveryLot.objects.filter(
                    delivery_sub_id=item.trans_id,
                    delivery_product__product=item.product,
                    product_warehouse_lot__product_warehouse__warehouse=item.warehouse
                ).first()
                if lot:
                    if lot.product_warehouse_lot:
                        lot_number = lot.product_warehouse_lot.lot_number
                        expire_date = lot.product_warehouse_lot.expire_date
            in_out_data.append({
                'trans_id': item.trans_id,
                'trans_code': item.trans_code,
                'trans_title': item.trans_title,
                'in_quantity': item.quantity if item.stock_type == 1 else '',
                'in_value': item.value if item.stock_type == 1 else '',
                'out_quantity': item.quantity if item.stock_type == -1 else '',
                'out_value': item.value if item.stock_type == -1 else '',
                'system_date': item.system_date,
                'lot_number': lot_number,
                'expire_date': expire_date
            })

        result = {
            'sum_in_quantity': sum_in_quantity,
            'sum_out_quantity': sum_out_quantity,
            'sum_in_value': sum_in_value,
            'sum_out_value': sum_out_value,
            'in_out_data': sorted(in_out_data, key=lambda key: key['system_date'])
        }
        return result
