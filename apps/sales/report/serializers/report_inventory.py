from rest_framework import serializers
from apps.sales.delivery.models.delivery import OrderDeliveryLot
from apps.sales.inventory.models import GoodsReceiptLot, GoodsReturnProductDetail
from apps.sales.report.models import ReportInventory, ReportInventoryProductWarehouse


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

    def get_stock_activities(self, obj):
        result = []
        for warehouse_item in self.context.get('wh_list', []):
            wh_id, wh_code, wh_title = warehouse_item
            data_stock_activity = []
            rp_prd_wh_list = obj.product.report_inventory_product_warehouse_product.all()
            for prd_wh in rp_prd_wh_list:
                if all([
                    prd_wh.warehouse_id == wh_id,
                    prd_wh.period_mapped_id == obj.period_mapped_id,
                    prd_wh.sub_period_order == obj.sub_period_order
                ]):
                    for item in obj.report_inventory_by_month.filter(warehouse=wh_id).all():
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

                    data_stock_activity = sorted(data_stock_activity, key=lambda key: key['system_date'])
                    value_this_sub_period = prd_wh.get_value_this_sub_period(
                        data_stock_activity,
                        rp_prd_wh_list,
                        wh_id,
                        obj.period_mapped_id,
                        obj.sub_period_order
                    )
                    result.append({
                        'is_close': value_this_sub_period.get('is_close'),
                        'warehouse_id': wh_id,
                        'warehouse_code': wh_code,
                        'warehouse_title': wh_title,
                        'opening_balance_quantity': value_this_sub_period.get('opening_balance_quantity'),
                        'opening_balance_value': value_this_sub_period.get('opening_balance_value'),
                        'opening_balance_cost': value_this_sub_period.get('opening_balance_cost'),
                        'ending_balance_quantity': value_this_sub_period.get('ending_balance_quantity'),
                        'ending_balance_value': value_this_sub_period.get('ending_balance_value'),
                        'ending_balance_cost': value_this_sub_period.get('ending_balance_cost'),
                        'data_stock_activity': data_stock_activity
                    })
                    break
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
        rp_prd_wh_list = obj.product.report_inventory_product_warehouse_product.all()
        data_stock_activity = []
        sum_in_quantity = 0
        sum_out_quantity = 0
        sum_in_value = 0
        sum_out_value = 0

        for item in obj.product.report_inventory_by_month_product.all():
            if all([
                item.warehouse_id == obj.warehouse_id,
                item.report_inventory.period_mapped_id == obj.period_mapped_id,
                item.report_inventory.sub_period_order == obj.sub_period_order
            ]):
                if item.stock_type == 1:
                    sum_in_quantity += item.quantity
                    sum_in_value += item.value
                else:
                    sum_out_quantity += item.quantity
                    sum_out_value += item.value
                if item.trans_title == 'Goods receipt':
                    for lot_child in GoodsReceiptLot.objects.filter(
                        goods_receipt_id=item.trans_id,
                        goods_receipt_warehouse__goods_receipt_product__product_id=item.product_id,
                        goods_receipt_warehouse__warehouse_id=item.warehouse_id
                    ):
                        data_stock_activity.append({
                            'trans_id': item.trans_id,
                            'trans_code': item.trans_code,
                            'trans_title': item.trans_title,
                            'in_quantity': lot_child.quantity_import,
                            'in_value': item.cost * lot_child.quantity_import,
                            'out_quantity': 0,
                            'out_value': 0,
                            'current_quantity': item.current_quantity,
                            'current_cost': item.current_cost,
                            'current_value': item.current_value,
                            'system_date': item.system_date,
                            'lot_number': lot_child.lot_number,
                            'expire_date': lot_child.expire_date
                        })
                elif item.trans_title == 'Goods return':
                    for lot in GoodsReturnProductDetail.objects.filter(
                        goods_return_id=item.trans_id,
                        goods_return__product_id=item.product_id,
                        goods_return__return_to_warehouse_id=item.warehouse_id
                    ):
                        if lot.lot_no:
                            data_stock_activity.append({
                                'trans_id': item.trans_id,
                                'trans_code': item.trans_code,
                                'trans_title': item.trans_title,
                                'in_quantity': item.quantity,
                                'in_value': item.value,
                                'out_quantity': 0,
                                'out_value': 0,
                                'current_quantity': item.current_quantity,
                                'current_cost': item.current_cost,
                                'current_value': item.current_value,
                                'system_date': item.system_date,
                                'lot_number': lot.lot_no.lot_number,
                                'expire_date': lot.lot_no.expire_date
                            })
                elif item.trans_title == 'Delivery':
                    for lot_child in OrderDeliveryLot.objects.filter(
                        delivery_sub_id=item.trans_id,
                        delivery_product__product_id=item.product_id,
                        product_warehouse_lot__product_warehouse_id=item.warehouse_id
                    ):
                        if lot_child.product_warehouse_lot:
                            data_stock_activity.append({
                                'trans_id': item.trans_id,
                                'trans_code': item.trans_code,
                                'trans_title': item.trans_title,
                                'in_quantity': 0,
                                'in_value': 0,
                                'out_quantity': lot_child.quantity_delivery,
                                'out_value': item.cost * lot_child.quantity_delivery,
                                'current_quantity': item.current_quantity,
                                'current_cost': item.current_cost,
                                'current_value': item.current_value,
                                'system_date': item.system_date,
                                'lot_number': lot_child.product_warehouse_lot.lot_number,
                                'expire_date': lot_child.product_warehouse_lot.expire_date
                            })

        data_stock_activity = sorted(data_stock_activity, key=lambda key: key['system_date'])
        value_this_sub_period = obj.get_value_this_sub_period(
            data_stock_activity,
            rp_prd_wh_list,
            obj.warehouse_id,
            obj.period_mapped_id,
            obj.sub_period_order
        )

        result = {
            'is_close': value_this_sub_period.get('is_close'),
            'sum_in_quantity': sum_in_quantity,
            'sum_out_quantity': sum_out_quantity,
            'sum_in_value': sum_in_value,
            'sum_out_value': sum_out_value,
            'opening_balance_quantity': value_this_sub_period.get('opening_balance_quantity'),
            'opening_balance_value': value_this_sub_period.get('opening_balance_value'),
            'opening_balance_cost': value_this_sub_period.get('opening_balance_cost'),
            'ending_balance_quantity': value_this_sub_period.get('ending_balance_quantity'),
            'ending_balance_value': value_this_sub_period.get('ending_balance_value'),
            'ending_balance_cost': value_this_sub_period.get('ending_balance_cost'),
            'data_stock_activity': data_stock_activity
        }
        return result
