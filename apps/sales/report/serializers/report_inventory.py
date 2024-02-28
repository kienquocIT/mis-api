from rest_framework import serializers
from apps.sales.report.models import ReportInventory, ReportInventoryProductWarehouse


class ReportInventoryListSerializer(serializers.ModelSerializer):
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
        report_inventory_by_month = obj.report_inventory_by_month.all()
        set_warehouse = set(
            report_inventory_by_month.values_list(
                'warehouse__id', 'warehouse__code', 'warehouse__title'
            )
        )
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
