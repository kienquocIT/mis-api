from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse
from apps.sales.report.models import ReportStock, ReportInventoryCost, ReportInventorySubFunction


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    return (log_quantity / inventory_uom.ratio) if inventory_uom.ratio else 0


class ReportStockListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    lot_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = ReportStock
        fields = (
            'id',
            'product',
            'lot_mapped',
            'sale_order',
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
            'sale_order_code': obj.sale_order.code if obj.sale_order else '',
            'code': obj.product.code,
            'description': obj.product.description,
            'uom': {
                "id": obj.product.inventory_uom_id,
                "code": obj.product.inventory_uom.code,
                "title": obj.product.inventory_uom.title
            } if obj.product.inventory_uom else {}
        } if obj.product else {}

    @classmethod
    def get_lot_mapped(cls, obj):
        return {
            'id': obj.lot_mapped_id,
            'lot_number': obj.lot_mapped.lot_number
        } if obj.lot_mapped else {}

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title
        } if obj.sale_order else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_stock_activities_detail(cls, obj, all_logs_by_month, div, **kwargs):
        data_stock_activity = []
        # lấy các hoạt động nhập-xuất
        for log in all_logs_by_month.filter(
            product_id=obj.product_id,
            **kwargs
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
        config_inventory_management = self.context.get('config_inventory_management')
        kw_parameter = {}
        if 2 in config_inventory_management:
            kw_parameter['lot_mapped_id'] = obj.lot_mapped_id
        if 3 in config_inventory_management:
            kw_parameter['sale_order_id'] = obj.sale_order_id
        result = []
        for warehouse_item in self.context.get('wh_list', []):
            # warehouse_item: [id, code, title]
            if 1 in config_inventory_management:
                kw_parameter['warehouse_id'] = warehouse_item[0]
            rp_inventory_cost = obj.product.report_inventory_cost_product.filter(
                period_mapped_id=obj.period_mapped_id,
                sub_period_order=obj.sub_period_order,
                **kw_parameter
            ).first()
            if rp_inventory_cost:
                this_balance = ReportInventorySubFunction.get_balance_data_this_sub_period(rp_inventory_cost)
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
                        **kw_parameter
                    ),
                    'periodic_closed': rp_inventory_cost.periodic_closed
                })
        return sorted(result, key=lambda key: key['warehouse_code'])


class BalanceInitializationListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    opening_balance_quantity = serializers.SerializerMethodField()
    opening_balance_cost = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventoryCost
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
        if obj.warehouse:
            return {
                'id': obj.warehouse_id,
                'title': obj.warehouse.title,
                'code': obj.warehouse.code,
            }
        warehouse_sub = obj.report_inventory_cost_wh.first()
        return {
            'id': warehouse_sub.warehouse.id,
            'title': warehouse_sub.warehouse.title,
            'code': warehouse_sub.warehouse.code,
        } if warehouse_sub else {}

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
            'space_month': obj.period_mapped.space_month,
            'fiscal_year': obj.period_mapped.fiscal_year,
        } if obj.period_mapped else {}

    @classmethod
    def get_opening_balance_quantity(cls, obj):
        return cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.opening_balance_quantity)

    @classmethod
    def get_opening_balance_cost(cls, obj):
        return obj.opening_balance_value / cast_unit_to_inv_quantity(
            obj.product.inventory_uom, obj.opening_balance_quantity
        )


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
            'for_balance',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'lot_number': obj.lot_mapped.lot_number if obj.lot_mapped else '',
            'sale_order_code': obj.sale_order.code if obj.sale_order else '',
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
            'id': obj.period_mapped_id,
            'title': obj.period_mapped.title,
            'code': obj.period_mapped.code,
        } if obj.period_mapped else {}

    @classmethod
    def get_data_stock_activity_for_in(cls, log, data_stock_activity, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity'))
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': lot.get('lot_value'),
                'out_quantity': '',
                'out_value': '',
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title
            })
        else:
            casted_in_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': log.value,
                'out_quantity': '',
                'out_value': '',
                'system_date': log.system_date,
                'lot_number': '',
                'expire_date': '',
                'log_order': log.log_order,
                'trans_title': log.trans_title
            })
        return data_stock_activity

    @classmethod
    def get_data_stock_activity_for_out(cls, log, data_stock_activity, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity'))
            data_stock_activity.append({
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': lot.get('lot_value'),
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title
            })
        else:
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': log.value,
                'system_date': log.system_date,
                'lot_number': '',
                'expire_date': '',
                'log_order': log.log_order,
                'trans_title': log.trans_title
            })
        return data_stock_activity

    @classmethod
    def for_project(cls, obj, date_range, div):
        result = []
        for wh_sub in obj.report_inventory_cost_wh.all().order_by('warehouse_id'):
            sub_warehouse_id = wh_sub.warehouse_id
            data_stock_activity = []
            sum_in_quantity = 0
            sum_out_quantity = 0
            sum_in_value = 0
            sum_out_value = 0
            kw_parameter = {
                'physical_warehouse_id': sub_warehouse_id,
                'sale_order_id': obj.sale_order_id
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
                    if log.trans_title in ['Goods receipt', 'Goods receipt (IA)', 'Goods return',
                                           'Goods transfer (in)']:
                        data_stock_activity = cls.get_data_stock_activity_for_in(log, data_stock_activity,
                                                                                  obj.product)
                    elif log.trans_title in ['Delivery', 'Goods issue', 'Goods transfer (out)']:
                        data_stock_activity = cls.get_data_stock_activity_for_out(log, data_stock_activity,
                                                                                   obj.product)
            data_stock_activity = sorted(
                data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
            )

            # lấy inventory_cost_data của kì hiện tại
            this_sub_value = ReportInventorySubFunction.get_balance_data_this_sub_period(obj)

            if div == 0:
                sum_in_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_in_quantity)
                sum_out_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_out_quantity)
            else:
                sum_in_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_input_quantity)
                sum_out_quantity = cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_output_quantity)
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
    def for_none_project(cls, obj, date_range, div, config_inventory_management):
        data_stock_activity = []
        sum_in_quantity = 0
        sum_out_quantity = 0
        sum_in_value = 0
        sum_out_value = 0
        kw_parameter = {'physical_warehouse_id': obj.warehouse_id}
        if 1 in config_inventory_management:
            kw_parameter['warehouse_id'] = obj.warehouse_id
        if 2 in config_inventory_management:
            kw_parameter['lot_mapped_id'] = obj.lot_mapped_id
        if 3 in config_inventory_management:
            kw_parameter['sale_order_id'] = obj.sale_order_id

        print(kw_parameter)
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
                    'Goods receipt', 'Goods receipt (IA)', 'Goods return', 'Goods transfer (in)'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_in(
                        log, data_stock_activity, obj.product
                    )
                elif log.trans_title in [
                    'Delivery', 'Goods issue', 'Goods transfer (out)'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_out(
                        log, data_stock_activity, obj.product
                    )

        data_stock_activity = sorted(
            data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
        )

        # lấy inventory_cost_data của kì hiện tại
        this_sub_value = ReportInventorySubFunction.get_balance_data_this_sub_period(obj)

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
                obj.product.inventory_uom,
                this_sub_value['opening_balance_quantity']
            ),
            'opening_balance_value': this_sub_value['opening_balance_value'],
            'sum_in_quantity': sum_in_quantity,
            'sum_in_value': sum_in_value,
            'sum_out_quantity': sum_out_quantity,
            'sum_out_value': sum_out_value,
            'ending_balance_quantity': cast_unit_to_inv_quantity(
                obj.product.inventory_uom,
                this_sub_value['ending_balance_quantity']
            ),
            'ending_balance_value': this_sub_value['ending_balance_value'],
            'data_stock_activity': data_stock_activity,
            'periodic_closed': obj.periodic_closed
        }
        return result

    def get_stock_activities(self, obj):
        div = self.context.get('definition_inventory_valuation')
        config_inventory_management = self.context.get('config_inventory_management')
        date_range = self.context.get('date_range', [])  # lấy tham số khoảng tg
        if not obj.warehouse_id:  # Project
            return self.for_project(obj, date_range, div)
        return self.for_none_project(obj, date_range, div, config_inventory_management)


class ProductWarehouseViewListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    detail = serializers.SerializerMethodField()
    stock_amount = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'stock_amount',
            'detail'
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
    def get_stock_amount(cls, obj):
        return cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.stock_amount)

    @classmethod
    def get_detail(cls, obj):
        lot_data = []
        sn_data = []
        for item in obj.product_warehouse_lot_product_warehouse.filter(quantity_import__gt=0):
            lot_data.append({
                'id': item.id,
                'lot_number': item.lot_number,
                'expire_date': item.expire_date,
                'quantity_import': cast_unit_to_inv_quantity(obj.product.inventory_uom, item.quantity_import)
            })
        for item in obj.product_warehouse_serial_product_warehouse.filter(is_delete=False):
            sn_data.append({
                'id': item.id,
                'vendor_serial_number': item.vendor_serial_number,
                'serial_number': item.serial_number
            })
        return {
            'lot_data': lot_data,
            'sn_data': sn_data
        }
