from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse
from apps.sales.report.models import (
    ReportStock, ReportInventoryCost, ReportInventorySubFunction
)


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    return (log_quantity / inventory_uom.ratio) if inventory_uom else 0


class ReportStockListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()

    class Meta:
        model = ReportStock
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
            'lot_number': obj.lot_mapped.lot_number if obj.lot_mapped else '',
            'serial_number': obj.serial_mapped.serial_number if obj.serial_mapped else '',
            'order_id': str(obj.sale_order_id) if obj.sale_order else str(
                obj.lease_order_id) if obj.lease_order else '',
            'order_code': obj.sale_order.code if obj.sale_order else obj.lease_order.code if obj.lease_order else '',
            'code': obj.product.code,
            'description': obj.product.description,
            'uom': {
                "id": obj.product.inventory_uom_id,
                "code": obj.product.inventory_uom.code,
                "title": obj.product.inventory_uom.title
            } if obj.product.inventory_uom else {},
            'valuation_method': obj.product.valuation_method
        } if obj.product else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id, 'title': obj.period_mapped.title, 'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_stock_activities_detail(cls, obj, all_logs_by_month, div, physical_warehouse_id, **kwargs):
        data_stock_activity = []
        # lấy các hoạt động nhập-xuất
        if 'sale_order_id' in kwargs:
            kwargs['physical_warehouse_id'] = physical_warehouse_id
        for log in all_logs_by_month.filter(product_id=obj.product_id, **kwargs):
            casted_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, log.quantity)
            casted_value = log.value
            casted_cost = (casted_value / casted_quantity) if casted_quantity else 0
            casted_current_quantity = [
                cast_unit_to_inv_quantity(obj.product.inventory_uom, log.perpetual_current_quantity),
                cast_unit_to_inv_quantity(obj.product.inventory_uom, log.periodic_current_quantity)
            ][div]
            casted_current_value = [log.perpetual_current_value, log.periodic_current_value][div]
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
        data_stock_activity = sorted(data_stock_activity, key=lambda key: (key['system_date'], key['log_order']))
        return data_stock_activity

    def get_stock_activities(self, obj):
        cost_cfg = self.context.get('cost_cfg')
        kw_parameter = {}
        if 2 in cost_cfg:
            kw_parameter['lot_mapped_id'] = obj.lot_mapped_id
        if 3 in cost_cfg:
            kw_parameter['sale_order_id'] = obj.sale_order_id
            kw_parameter['lease_order_id'] = obj.lease_order_id

        if obj.product.valuation_method == 2:
            kw_parameter['serial_mapped_id'] = obj.serial_mapped_id

        result = []
        for warehouse_item in self.context.get('wh_list', []):
            # warehouse_item: [id, code, title]
            if 1 in cost_cfg:
                kw_parameter['warehouse_id'] = warehouse_item[0] if len(warehouse_item) > 0 else None
            this_sub_period_cost = obj.product.report_inventory_cost_product.filter(
                period_mapped_id=obj.period_mapped_id,
                sub_period_order=obj.sub_period_order,
                **kw_parameter
            ).first()
            if this_sub_period_cost:
                this_balance = ReportInventorySubFunction.get_this_sub_period_cost_dict(
                    this_sub_period_cost, warehouse_item[0] if 'sale_order_id' in kw_parameter else None
                )
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
                    'warehouse_id': warehouse_item[0],
                    'warehouse_code': warehouse_item[1],
                    'warehouse_title': warehouse_item[2],
                    'opening_balance_quantity': casted_obq,
                    'opening_balance_cost': casted_obc,
                    'opening_balance_value': casted_obv,
                    'ending_balance_quantity': casted_ebq,
                    'ending_balance_cost': casted_ebc,
                    'ending_balance_value': casted_ebv,
                    'data_stock_activity': self.get_stock_activities_detail(
                        obj,
                        self.context.get('all_logs_by_month', []),
                        self.context.get('definition_inventory_valuation'),
                        warehouse_item[0],
                        **kw_parameter
                    ),
                    'periodic_closed': this_sub_period_cost.periodic_closed
                })
        return sorted(result, key=lambda key: key['warehouse_code'])


class ReportInventoryCostListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()
    warehouse_sub_list = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventoryCost
        fields = (
            'id',
            'product',
            'warehouse',
            'warehouse_sub_list',
            'period_mapped',
            'sub_period_order',
            'stock_activities',
            'for_balance_init',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'valuation_method': obj.product.valuation_method,
            'lot_number': obj.lot_mapped.lot_number if obj.lot_mapped else '',
            'serial_number': obj.serial_mapped.serial_number if obj.serial_mapped else '',
            'order_code': obj.sale_order.code if obj.sale_order else obj.lease_order.code if obj.lease_order else '',
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
            'id': obj.warehouse_id, 'title': obj.warehouse.title, 'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_warehouse_sub_list(cls, obj):
        return [{
            'id': wh_sub.warehouse_id,
            'title': wh_sub.warehouse.title,
            'code': wh_sub.warehouse.code,
            'opening_quantity': wh_sub.opening_quantity,
            'ending_quantity': wh_sub.ending_quantity
        } if wh_sub.warehouse else {} for wh_sub in obj.report_inventory_cost_wh.all().order_by('warehouse_id')]

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id, 'title': obj.period_mapped.title, 'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_data_stock_activity_for_in(cls, log, data_stock_activity, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity', 0))
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': lot.get('lot_value'),
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        if len(log.serial_data) > 0:
            serial = log.serial_data
            data_stock_activity.append({
                'in_quantity': 1,
                'in_value': log.value,
                'system_date': log.system_date,
                'serial_number': serial.get('serial_number'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        else:
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': log.value,
                'system_date': log.system_date,
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        return data_stock_activity

    @classmethod
    def get_data_stock_activity_for_out(cls, log, data_stock_activity, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity', 0))
            data_stock_activity.append({
                'out_quantity': casted_out_quantity,
                'out_value': lot.get('lot_value'),
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        if len(log.serial_data) > 0:
            serial = log.serial_data
            data_stock_activity.append({
                'out_quantity': 1,
                'out_value': log.value,
                'system_date': log.system_date,
                'serial_number': serial.get('serial_number'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        else:
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'out_quantity': casted_out_quantity,
                'out_value': log.value,
                'system_date': log.system_date,
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        return data_stock_activity

    @classmethod
    def for_project(cls, obj, date_range, div):
        result = []
        for wh_sub in obj.report_inventory_cost_wh.all().order_by('warehouse_id'):
            data_stock_activity = []
            sum_in_quantity = 0
            sum_out_quantity = 0
            sum_in_value = 0
            sum_out_value = 0
            kw_parameter = {
                'physical_warehouse_id': wh_sub.warehouse_id,
                'sale_order_id': obj.sale_order_id,
                'serial_mapped_id': obj.serial_mapped_id
            }

            for log in obj.product.report_stock_log_product.filter(
                    report_stock__period_mapped_id=obj.period_mapped_id,
                    report_stock__sub_period_order=obj.sub_period_order,
                    **kw_parameter
            ):
                if log.system_date.day in list(range(date_range[0], date_range[1] + 1)):
                    if log.stock_type == 1:
                        sum_in_quantity += log.quantity
                        sum_in_value += log.value
                    else:
                        sum_out_quantity += log.quantity
                        sum_out_value += log.value

                    # lấy detail cho từng TH
                    if log.trans_title in [
                        'Goods receipt', 'Goods receipt (IA)', 'Goods return',
                        'Goods transfer (in)', 'Balance init input'
                    ]:
                        data_stock_activity = cls.get_data_stock_activity_for_in(log, data_stock_activity, obj.product)
                    elif log.trans_title in [
                        'Delivery (sale)', 'Delivery (lease)',
                        'Goods issue', 'Goods transfer (out)'
                    ]:
                        data_stock_activity = cls.get_data_stock_activity_for_out(log, data_stock_activity, obj.product)
            data_stock_activity = sorted( data_stock_activity, key=lambda key: (key['system_date'], key['log_order']))

            # lấy inventory_cost_data của kì hiện tại
            this_sub_value = ReportInventorySubFunction.get_this_sub_period_cost_dict(obj)

            if div == 0:
                sum_in_quantity = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, sum_in_quantity
                )
                sum_out_quantity = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, sum_out_quantity
                )
            else:
                sum_in_quantity = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, obj.sum_input_quantity
                )
                sum_out_quantity = cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, obj.sum_output_quantity
                )
                sum_in_value = obj.sum_input_value
                sum_out_value = obj.sum_output_value

            result.append({
                'opening_balance_quantity': cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, wh_sub.opening_quantity
                ),
                'opening_balance_value': wh_sub.opening_quantity * this_sub_value['opening_balance_cost'],
                'sum_in_quantity': sum_in_quantity,
                'sum_in_value': sum_in_value,
                'sum_out_quantity': sum_out_quantity,
                'sum_out_value': sum_out_value,
                'ending_balance_quantity': cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, wh_sub.ending_quantity
                ),
                'ending_balance_value': wh_sub.ending_quantity * this_sub_value['ending_balance_cost'],
                'data_stock_activity': data_stock_activity,
                'periodic_closed': obj.periodic_closed
            })
        return result

    @classmethod
    def for_none_project(cls, obj, date_range, div, cost_cfg):
        data_stock_activity = []
        sum_in_quantity = 0
        sum_out_quantity = 0
        sum_in_value = 0
        sum_out_value = 0
        kw_parameter = {
            'physical_warehouse_id': obj.warehouse_id,
            'serial_mapped_id': obj.serial_mapped_id
        }
        if 1 in cost_cfg:
            kw_parameter['warehouse_id'] = obj.warehouse_id
        if 2 in cost_cfg:
            kw_parameter['lot_mapped_id'] = obj.lot_mapped_id
        if 3 in cost_cfg:
            kw_parameter['sale_order_id'] = obj.sale_order_id
            kw_parameter['lease_order_id'] = obj.lease_order_id

        for log in obj.product.report_stock_log_product.filter(
                report_stock__period_mapped_id=obj.period_mapped_id,
                report_stock__sub_period_order=obj.sub_period_order,
                **kw_parameter
        ):
            if log.system_date.day in list(range(date_range[0], date_range[1] + 1)):
                if log.stock_type == 1:
                    sum_in_quantity += log.quantity
                    sum_in_value += log.value
                else:
                    sum_out_quantity += log.quantity
                    sum_out_value += log.value

                # lấy detail cho từng TH
                if log.trans_title in [
                    'Goods receipt', 'Goods receipt (IA)', 'Goods return',
                    'Goods transfer (in)', 'Balance init input'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_in(log, data_stock_activity, obj.product)
                elif log.trans_title in [
                    'Delivery (sale)', 'Delivery (lease)',
                    'Goods issue', 'Goods transfer (out)'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_out(log, data_stock_activity, obj.product)

        data_stock_activity = sorted(
            data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
        )

        # lấy inventory_cost_data của kì hiện tại
        this_sub_value = ReportInventorySubFunction.get_this_sub_period_cost_dict(obj)

        if div == 0:
            sum_in_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_in_quantity)
            sum_out_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_out_quantity)
        else:
            sum_in_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_input_quantity)
            sum_out_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_output_quantity)
            sum_in_value = obj.sum_input_value
            sum_out_value = obj.sum_output_value

        result = {
            'opening_balance_quantity': cast_unit_to_inv_quantity(
                obj.product.inventory_uom, this_sub_value['opening_balance_quantity']
            ),
            'opening_balance_value': this_sub_value['opening_balance_value'],
            'sum_in_quantity': sum_in_quantity,
            'sum_in_value': sum_in_value,
            'sum_out_quantity': sum_out_quantity,
            'sum_out_value': sum_out_value,
            'ending_balance_quantity': cast_unit_to_inv_quantity(
                obj.product.inventory_uom, this_sub_value['ending_balance_quantity']
            ),
            'ending_balance_value': this_sub_value['ending_balance_value'],
            'data_stock_activity': data_stock_activity,
            'periodic_closed': obj.periodic_closed
        }
        return result

    def get_stock_activities(self, obj):
        div = self.context.get('definition_inventory_valuation')
        cost_cfg = self.context.get('cost_cfg')
        date_range = self.context.get('date_range', [])  # lấy tham số khoảng tg
        if not obj.warehouse_id:  # Project
            return self.for_project(obj, date_range, div)
        return self.for_none_project(obj, date_range, div, cost_cfg)


class WarehouseAvailableProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    stock_amount = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'stock_amount'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
            'general_traceability_method': obj.product.general_traceability_method,
            'uom': {
                "id": obj.product.inventory_uom_id,
                "code": obj.product.inventory_uom.code,
                "title": obj.product.inventory_uom.title
            } if obj.product.inventory_uom else {}
        } if obj.product else {}

    @classmethod
    def get_stock_amount(cls, obj):
        return cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.stock_amount)


class WarehouseAvailableProductDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    detail = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'detail'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
            'general_traceability_method': obj.product.general_traceability_method,
            'uom': {
                "id": obj.product.inventory_uom_id,
                "code": obj.product.inventory_uom.code,
                "title": obj.product.inventory_uom.title
            } if obj.product.inventory_uom else {}
        } if obj.product else {}

    @classmethod
    def get_detail(cls, obj):
        lot_data = []
        sn_data = []
        for item in obj.product_warehouse_lot_product_warehouse.filter(quantity_import__gt=0):
            gr_mapped = item.pw_lot_transact_pw_lot.first()
            goods_receipt_date = None
            if gr_mapped:
                goods_receipt_date = gr_mapped.goods_receipt.date_received if gr_mapped.goods_receipt else None
            lot_data.append({
                'id': item.id,
                'lot_number': item.lot_number,
                'expire_date': item.expire_date,
                'quantity_import': cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, item.quantity_import
                ),
                'goods_receipt_date': goods_receipt_date
            })
        for item in obj.product_warehouse_serial_product_warehouse.filter(serial_status=False):
            sn_data.append({
                'id': item.id,
                'vendor_serial_number': item.vendor_serial_number,
                'serial_number': item.serial_number,
                'goods_receipt_date': item.goods_receipt.date_received if item.goods_receipt else None
            })
        return {'lot_data': lot_data, 'sn_data': sn_data}
