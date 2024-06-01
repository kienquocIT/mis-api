from rest_framework import serializers
from apps.sales.report.models import ReportInventory, ReportInventoryProductWarehouse, LoggingSubFunction


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    return (log_quantity / inventory_uom.ratio) if inventory_uom.ratio else 0


class ReportInventoryDetailListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    lot_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventory
        fields = (
            'id',
            'product',
            'lot_mapped',
            'period_mapped',
            'sub_period_order',
            'stock_activities'
        )

    @classmethod
    def get_product(cls, obj):
        title = f"{obj.product.title} ({obj.product.inventory_uom.title})"
        if obj.lot_mapped:
            title = f"{title} - {obj.lot_mapped.lot_number}"
        return {
            'id': obj.product_id,
            'title': title,
            'code': obj.product.code,
            'description': obj.product.description,
        } if obj.product else {}

    @classmethod
    def get_lot_mapped(cls, obj):
        return {
            'id': obj.lot_mapped_id,
            'lot_number': obj.lot_mapped.lot_number
        } if obj.lot_mapped else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_stock_activities_detail(cls, obj, all_logs_by_month, wh_id, div):
        data_stock_activity = []
        # lấy các hoạt động nhập-xuất
        for log in all_logs_by_month.filter(
            product_id=obj.product_id,
            lot_mapped=obj.lot_mapped,
            warehouse_id=wh_id,
        ):
            casted_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, log.quantity)
            casted_value = log.value
            casted_cost = (casted_value / casted_quantity) if casted_quantity else 0
            casted_current_quantity = [
                cast_unit_to_inv_quantity(obj.product.inventory_uom, log.current_quantity),
                cast_unit_to_inv_quantity(obj.product.inventory_uom, log.periodic_current_quantity)
            ][div]
            casted_current_value = [log.current_value, log.periodic_current_value][div]
            casted_current_cost = (casted_current_value / casted_current_quantity) if casted_current_quantity else 0

            data_stock_activity.append({
                'system_date': log.system_date,
                'posting_date': log.posting_date,
                'document_date': log.document_date,
                'stock_type': log.stock_type,
                'trans_code': log.trans_code,
                'trans_title': log.trans_title,
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_value,
                'current_quantity': casted_current_quantity,
                'current_cost': casted_current_cost,
                'current_value': casted_current_value,
                'log_order': log.log_order
            })
        # sắp xếp lại
        data_stock_activity = sorted(
            data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
        )
        return data_stock_activity

    def get_stock_activities(self, obj):
        #                                    SP
        #        Kho 1           -          Kho 2          -          Kho 3
        # (Các hđ nhập-xuất 1)   -   (Các hđ nhập-xuất 2)  -   (Các hđ nhập-xuất 3)
        result = []
        for warehouse_item in self.context.get('wh_list', []):
            wh_id, wh_code, wh_title = warehouse_item
            # lọc lấy cost_data của sp đó theo kho + theo kì
            inventory_cost_data = obj.product.report_inventory_product_warehouse_product.filter(
                lot_mapped=obj.lot_mapped,
                warehouse_id=wh_id,
                period_mapped_id=obj.period_mapped_id,
                sub_period_order=obj.sub_period_order
            ).first()
            if inventory_cost_data:
                # lấy inventory_cost_data của kì hiện tại
                this_balance = LoggingSubFunction.get_balance_data_this_sub(inventory_cost_data)
                casted_obq = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, this_balance['opening_balance_quantity']
                )
                casted_obv = this_balance['opening_balance_value']
                casted_obc = casted_obv / casted_obq if casted_obq else 0
                casted_ebq = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, this_balance['ending_balance_quantity']
                )
                casted_ebv = this_balance['ending_balance_value']
                casted_ebc = casted_ebv / casted_ebq if casted_ebq else 0

                result.append({
                    'warehouse_id': wh_id,
                    'warehouse_code': wh_code,
                    'warehouse_title': wh_title,
                    'opening_balance_quantity': casted_obq,
                    'opening_balance_cost': casted_obc,
                    'opening_balance_value': casted_obv,
                    'ending_balance_quantity': casted_ebq,
                    'ending_balance_cost': casted_ebc,
                    'ending_balance_value': casted_ebv,
                    'data_stock_activity': self.get_stock_activities_detail(
                        obj, self.context.get('all_logs_by_month', []), wh_id,
                        self.context.get('definition_inventory_valuation')
                    ),
                    'periodic_closed': inventory_cost_data.periodic_closed
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
            'for_balance',
        )

    @classmethod
    def get_product(cls, obj):
        title = obj.product.title
        if obj.lot_mapped:
            title = f"{title} - {obj.lot_mapped.lot_number}"
        return {
            'id': obj.product_id,
            'title': title,
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
    def get_data_stock_activity_for_in(cls, log, data_stock_activity, div, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity'))
            casted_current_quantity = [
                cast_unit_to_inv_quantity(product.inventory_uom, log.current_quantity),
                cast_unit_to_inv_quantity(product.inventory_uom, log.periodic_current_quantity)
            ][div]
            data_stock_activity.append({
                'trans_id': log.trans_id,
                'trans_code': log.trans_code,
                'trans_title': log.trans_title,
                'in_quantity': casted_in_quantity,
                'in_value': lot.get('lot_value'),
                'out_quantity': '',
                'out_value': '',
                'current_quantity': casted_current_quantity,
                'current_value': [log.current_value, log.periodic_current_value][div],
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order
            })
        else:
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            casted_current_quantity = [
                cast_unit_to_inv_quantity(product.inventory_uom, log.current_quantity),
                cast_unit_to_inv_quantity(product.inventory_uom, log.periodic_current_quantity)
            ][div]
            data_stock_activity.append({
                'trans_id': log.trans_id,
                'trans_code': log.trans_code,
                'trans_title': log.trans_title,
                'in_quantity': casted_in_quantity,
                'in_value': log.value,
                'out_quantity': '',
                'out_value': '',
                'current_quantity': casted_current_quantity,
                'current_value': [log.current_value, log.periodic_current_value][div],
                'system_date': log.system_date,
                'lot_id': '',
                'lot_number': '',
                'expire_date': '',
                'log_order': log.log_order
            })
        return data_stock_activity

    @classmethod
    def get_data_stock_activity_for_out(cls, log, data_stock_activity, div, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity'))
            casted_current_quantity = [
                cast_unit_to_inv_quantity(product.inventory_uom, log.current_quantity),
                cast_unit_to_inv_quantity(product.inventory_uom, log.periodic_current_quantity)
            ][div]
            data_stock_activity.append({
                'trans_id': log.trans_id,
                'trans_code': log.trans_code,
                'trans_title': log.trans_title,
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': lot.get('lot_value'),
                'current_quantity': casted_current_quantity,
                'current_value': [log.current_value, log.periodic_current_value][div],
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order
            })
        else:
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            casted_current_quantity = [
                cast_unit_to_inv_quantity(product.inventory_uom, log.current_quantity),
                cast_unit_to_inv_quantity(product.inventory_uom, log.periodic_current_quantity)
            ][div]
            data_stock_activity.append({
                'trans_id': log.trans_id,
                'trans_code': log.trans_code,
                'trans_title': log.trans_title,
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': log.value,
                'current_quantity': casted_current_quantity,
                'current_value': [log.current_value, log.periodic_current_value][div],
                'system_date': log.system_date,
                'lot_number': '',
                'expire_date': '',
                'log_order': log.log_order
            })
        return data_stock_activity

    def get_stock_activities(self, obj):
        div = self.context.get('definition_inventory_valuation')
        date_range = self.context.get('date_range', [])  # lấy tham số khoảng tg
        data_stock_activity = []
        sum_in_quantity = 0
        sum_out_quantity = 0
        sum_in_value = 0
        sum_out_value = 0
        for log in obj.product.report_inventory_by_month_product.filter(
            lot_mapped_id=obj.lot_mapped_id,
            warehouse_id=obj.warehouse_id,
            report_inventory__period_mapped_id=obj.period_mapped_id,
            report_inventory__sub_period_order=obj.sub_period_order,
        ):
            if log.date_created.day in list(range(date_range[0], date_range[1] + 1)):
                if log.stock_type == 1:
                    sum_in_quantity += log.quantity
                    sum_in_value += log.value
                else:
                    sum_out_quantity += log.quantity
                    sum_out_value += log.value
                # lấy detail cho từng TH
                if log.trans_title in ['Goods receipt', 'Goods receipt (IA)', 'Goods return', 'Goods transfer (in)']:
                    data_stock_activity = self.get_data_stock_activity_for_in(
                        log, data_stock_activity, div, obj.product
                    )
                elif log.trans_title in ['Delivery', 'Goods issue', 'Goods transfer (out)']:
                    data_stock_activity = self.get_data_stock_activity_for_out(
                        log, data_stock_activity, div, obj.product
                    )

        data_stock_activity = sorted(
            data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
        )
        # lấy inventory_cost_data của kì hiện tại
        this_sub_value = LoggingSubFunction.get_balance_data_this_sub(obj)

        if div:
            sum_out_value = sum_out_quantity * this_sub_value['ending_balance_cost']

        result = {
            'sum_in_quantity': cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_in_quantity),
            'sum_out_quantity': cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_out_quantity),
            'sum_in_value': sum_in_value,
            'sum_out_value': sum_out_value,
            'opening_balance_quantity': cast_unit_to_inv_quantity(
                obj.product.inventory_uom, this_sub_value['opening_balance_quantity']
            ),
            'opening_balance_value': this_sub_value['opening_balance_value'],
            'ending_balance_quantity': cast_unit_to_inv_quantity(
                obj.product.inventory_uom, this_sub_value['ending_balance_quantity']
            ),
            'ending_balance_value': this_sub_value['ending_balance_value'],
            'data_stock_activity': data_stock_activity,
            'periodic_closed': obj.periodic_closed
        }
        return result
