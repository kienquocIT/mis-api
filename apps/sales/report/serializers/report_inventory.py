from django.db import transaction
from django.utils.datetime_safe import datetime
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, SubPeriods, Periods, Product, WareHouse,
    ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.report.inventory_log import ReportInvCommonFunc
from apps.sales.report.models import (
    ReportStock, ReportInventoryCost, ReportInventorySubFunction,
    ReportInventoryCostByWarehouse, ReportStockLog, ReportInventoryCostLatestLog
)


def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
    return (log_quantity / inventory_uom.ratio) if inventory_uom else 0


class ReportStockListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    lot_mapped = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    period_mapped = serializers.SerializerMethodField()
    stock_activities = serializers.SerializerMethodField()

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
            } if obj.product.inventory_uom else {},
            'valuation_method': obj.product.valuation_method
        } if obj.product else {}

    @classmethod
    def get_lot_mapped(cls, obj):
        return {'id': obj.lot_mapped_id, 'lot_number': obj.lot_mapped.lot_number} if obj.lot_mapped else {}

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id, 'code': obj.sale_order.code, 'title': obj.sale_order.title
        } if obj.sale_order else {}

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
        result = []
        for warehouse_item in self.context.get('wh_list', []):
            # warehouse_item: [id, code, title]
            if 1 in cost_cfg:
                kw_parameter['warehouse_id'] = warehouse_item[0]
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
            casted_out_quantity = cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity', 0))
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
            data_stock_activity = []
            sum_in_quantity = 0
            sum_out_quantity = 0
            sum_in_value = 0
            sum_out_value = 0
            kw_parameter = {
                'physical_warehouse_id': wh_sub.warehouse_id,
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
                    if log.trans_title in [
                        'Goods receipt', 'Goods receipt (IA)', 'Goods return',
                        'Goods transfer (in)', 'Balance init input'
                    ]:
                        data_stock_activity = cls.get_data_stock_activity_for_in(
                            log, data_stock_activity, obj.product
                        )
                    elif log.trans_title in ['Delivery', 'Goods issue', 'Goods transfer (out)']:
                        data_stock_activity = cls.get_data_stock_activity_for_out(
                            log, data_stock_activity, obj.product
                        )
            data_stock_activity = sorted( data_stock_activity, key=lambda key: (key['system_date'], key['log_order']))

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
        kw_parameter = {'physical_warehouse_id': obj.warehouse_id}
        if 1 in cost_cfg:
            kw_parameter['warehouse_id'] = obj.warehouse_id
        if 2 in cost_cfg:
            kw_parameter['lot_mapped_id'] = obj.lot_mapped_id
        if 3 in cost_cfg:
            kw_parameter['sale_order_id'] = obj.sale_order_id

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
                    'Goods receipt', 'Goods receipt (IA)', 'Goods return', 'Goods transfer (in)', 'Balance init input'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_in(
                        log, data_stock_activity, obj.product
                    )
                elif log.trans_title in ['Delivery', 'Goods issue', 'Goods transfer (out)']:
                    data_stock_activity = cls.get_data_stock_activity_for_out(
                        log, data_stock_activity, obj.product
                    )

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
            return {'id': obj.warehouse_id, 'title': obj.warehouse.title, 'code': obj.warehouse.code}
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


class BalanceInitializationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportInventoryCost
        fields = ()

    @classmethod
    def for_serial(cls, balance_data, periods, prd_obj, wh_obj):
        if float(balance_data.get('quantity')) == float(len(balance_data.get('data_sn', []))):
            if not ProductWareHouse.objects.filter(
                    tenant_id=periods.tenant_id,
                    company_id=periods.company_id,
                    product=prd_obj,
                    warehouse=wh_obj
            ).exists():
                prd_wh_obj = ProductWareHouse(
                    tenant_id=periods.tenant_id,
                    company_id=periods.company_id,
                    product=prd_obj,
                    warehouse=wh_obj,
                    uom=prd_obj.general_uom_group.uom_reference,
                    unit_price=float(balance_data.get('value')) / float(balance_data.get('quantity')),
                    tax=None,
                    stock_amount=float(balance_data.get('quantity')),
                    receipt_amount=float(balance_data.get('quantity')),
                    sold_amount=0,
                    picked_ready=0,
                    used_amount=0,
                    # backup data
                    product_data={"id": str(prd_obj.id), "code": prd_obj.code, "title": prd_obj.title},
                    warehouse_data={"id": str(wh_obj.id), "code": wh_obj.code, "title": wh_obj.title},
                    uom_data={
                        "id": str(prd_obj.general_uom_group.uom_reference_id),
                        "code": prd_obj.general_uom_group.uom_reference.code,
                        "title": prd_obj.general_uom_group.uom_reference.title
                    } if prd_obj.general_uom_group.uom_reference else {},
                    tax_data={}
                )
                bulk_info_sn = []
                for serial in balance_data.get('data_sn', []):
                    for key in serial:
                        if serial[key] == '':
                            serial[key] = None
                    bulk_info_sn.append(
                        ProductWareHouseSerial(
                            tenant_id=periods.tenant_id,
                            company_id=periods.company_id,
                            product_warehouse=prd_wh_obj,
                            **serial
                        )
                    )
                ProductWareHouseSerial.objects.bulk_create(bulk_info_sn)
                return True
            raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})
        raise serializers.ValidationError({"Invalid": 'Quantity is != num serial data.'})

    @classmethod
    def for_lot(cls, balance_data, periods, prd_obj, wh_obj):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=prd_obj,
                warehouse=wh_obj
        ).exists():
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=prd_obj,
                warehouse=wh_obj,
                uom=prd_obj.general_uom_group.uom_reference,
                unit_price=float(balance_data.get('value')) / float(balance_data.get('quantity')),
                tax=None,
                stock_amount=float(balance_data.get('quantity')),
                receipt_amount=float(balance_data.get('quantity')),
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                # backup data
                product_data={"id": str(prd_obj.id), "code": prd_obj.code, "title": prd_obj.title},
                warehouse_data={"id": str(wh_obj.id), "code": wh_obj.code, "title": wh_obj.title},
                uom_data={
                    "id": str(prd_obj.general_uom_group.uom_reference_id),
                    "code": prd_obj.general_uom_group.uom_reference.code,
                    "title": prd_obj.general_uom_group.uom_reference.title
                } if prd_obj.general_uom_group.uom_reference else {},
                tax_data={}
            )
            bulk_info_lot = []
            for lot in balance_data.get('data_lot', []):
                for key in lot:
                    if lot[key] == '':
                        lot[key] = None
                bulk_info_lot.append(
                    ProductWareHouseLot(
                        tenant_id=periods.tenant_id,
                        company_id=periods.company_id,
                        product_warehouse=prd_wh_obj,
                        lot_number=lot.get('lot_number'),
                        quantity_import=ReportInvCommonFunc.cast_quantity_to_unit(
                            prd_obj.inventory_uom, float(lot.get('quantity_import'))
                        )
                    )
                )
            ProductWareHouseLot.objects.bulk_create(bulk_info_lot)
            return True
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def for_none(cls, balance_data, periods, prd_obj, wh_obj):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=prd_obj,
                warehouse=wh_obj
        ).exists():
            ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=prd_obj,
                warehouse=wh_obj,
                uom=prd_obj.general_uom_group.uom_reference,
                unit_price=float(balance_data.get('value')) / float(balance_data.get('quantity')),
                tax=None,
                stock_amount=float(balance_data.get('quantity')),
                receipt_amount=float(balance_data.get('quantity')),
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                # backup data
                product_data={"id": str(prd_obj.id), "code": prd_obj.code, "title": prd_obj.title},
                warehouse_data={"id": str(wh_obj.id), "code": wh_obj.code, "title": wh_obj.title},
                uom_data={
                    "id": str(prd_obj.general_uom_group.uom_reference_id),
                    "code": prd_obj.general_uom_group.uom_reference.code,
                    "title": prd_obj.general_uom_group.uom_reference.title
                } if prd_obj.general_uom_group.uom_reference else {},
                tax_data={}
            )
            return True
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def check_valid_create(cls, periods, prd_obj, wh_obj, sub_period_order):
        if ReportStockLog.objects.filter(
                product=prd_obj,
                warehouse=wh_obj if not periods.company.company_config.cost_per_project else None
        ).exists():
            raise serializers.ValidationError(
                {"Has trans": f'{prd_obj.title} transactions are existed in {wh_obj.title}.'}
            )

        if ReportInventoryCost.objects.filter(
                product=prd_obj,
                warehouse=wh_obj if not periods.company.company_config.cost_per_project else None,
                period_mapped=periods,
                sub_period_order=sub_period_order
        ).exists():
            raise serializers.ValidationError(
                {"Existed": f"{prd_obj.title}'s opening balance has been created in {wh_obj.title}."}
            )
        return True

    @classmethod
    def create_balance_data_sub(
            cls, periods, prd_obj, wh_obj, sub_period_order, balance_data, emp_current, sub_period_obj
    ):
        cls.check_valid_create(periods, prd_obj, wh_obj, sub_period_order)
        balance_data['quantity'] = ReportInvCommonFunc.cast_quantity_to_unit(
            prd_obj.inventory_uom, float(balance_data.get('quantity', 0))
        )
        prd_obj.stock_amount += float(balance_data['quantity'])
        prd_obj.available_amount += float(balance_data['quantity'])
        prd_obj.save(update_fields=['stock_amount', 'available_amount'])

        rp_stock = ReportStock.objects.create(
            tenant=periods.tenant,
            company=periods.company,
            product=prd_obj,
            period_mapped=periods,
            sub_period_order=sub_period_order,
            sub_period=sub_period_obj,
            employee_created=emp_current,
            employee_inherit=emp_current,
        )

        if periods.company.company_config.definition_inventory_valuation == 0:
            log = ReportStockLog.objects.create(
                tenant=periods.tenant,
                company=periods.company,
                employee_created=emp_current,
                employee_inherit=emp_current,
                report_stock=rp_stock,
                product=prd_obj,
                physical_warehouse=wh_obj,
                system_date=datetime.now(),
                posting_date=datetime.now(),
                document_date=datetime.now(),
                stock_type=1,
                trans_id='',
                trans_code='',
                trans_title='Balance init input',
                quantity=float(balance_data['quantity']),
                cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                value=float(balance_data.get('value')),
                perpetual_current_quantity=float(balance_data['quantity']),
                perpetual_current_cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                perpetual_current_value=float(balance_data.get('value')),
                lot_data={},
                log_order=0,
            )
            cost_cfg = ReportInvCommonFunc.get_cost_config(periods.company.company_config)
            kw_parameter = {}
            if 1 in cost_cfg:
                kw_parameter['warehouse_id'] = log.warehouse_id
            if 2 in cost_cfg:
                kw_parameter['lot_mapped_id'] = log.lot_mapped_id
            if 3 in cost_cfg:
                pass
            if log.product.valuation_method == 0:
                ReportInventoryCostLatestLog.objects.create(product=log.product, fifo_flag_log=log, **kw_parameter)
            if log.product.valuation_method == 1:
                ReportInventoryCostLatestLog.objects.create(product=log.product, latest_log=log, **kw_parameter)
            rp_inv_cost = ReportInventoryCost.objects.create(
                tenant=periods.tenant,
                company=periods.company,
                employee_created=emp_current,
                employee_inherit=emp_current,
                product=prd_obj,
                warehouse=wh_obj if not periods.company.company_config.cost_per_project else None,
                period_mapped=periods,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                opening_balance_quantity=float(balance_data['quantity']),
                opening_balance_value=float(balance_data.get('value')),
                opening_balance_cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                ending_balance_quantity=float(balance_data['quantity']),
                ending_balance_value=float(balance_data.get('value')),
                ending_balance_cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                for_balance=True,
                sum_input_quantity=float(balance_data['quantity']),
                sum_input_value=float(balance_data.get('value')),
                sum_output_quantity=0,
                sum_output_value=0,
                sub_latest_log=log
            )
            if periods.company.company_config.cost_per_project:
                ReportInventoryCostByWarehouse.objects.create(
                    report_inventory_cost=rp_inv_cost,
                    warehouse=wh_obj,
                    opening_quantity=float(balance_data['quantity']),
                    ending_quantity=float(balance_data['quantity'])
                )
        else:
            log = ReportStockLog.objects.create(
                tenant=periods.tenant,
                company=periods.company,
                employee_created=emp_current,
                employee_inherit=emp_current,
                report_stock=rp_stock,
                product=prd_obj,
                physical_warehouse=wh_obj,
                system_date=datetime.now(),
                posting_date=datetime.now(),
                document_date=datetime.now(),
                stock_type=1,
                trans_id='',
                trans_code='',
                trans_title='Balance init input',
                quantity=float(balance_data['quantity']),
                cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                value=float(balance_data.get('value')),
                periodic_current_quantity=float(balance_data['quantity']),
                periodic_current_cost=0,
                periodic_current_value=0,
                lot_data={},
                log_order=0,
            )
            rp_inv_cost = ReportInventoryCost.objects.create(
                tenant=periods.tenant,
                company=periods.company,
                employee_created=emp_current,
                employee_inherit=emp_current,
                product=prd_obj,
                warehouse=wh_obj if not periods.company.company_config.cost_per_project else None,
                period_mapped=periods,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                opening_balance_quantity=float(balance_data['quantity']),
                opening_balance_value=float(balance_data.get('value')),
                opening_balance_cost=float(balance_data.get('value')) / float(balance_data['quantity']),
                periodic_ending_balance_quantity=float(balance_data['quantity']),
                periodic_ending_balance_value=0,
                periodic_ending_balance_cost=0,
                for_balance=True,
                sum_input_quantity=float(balance_data['quantity']),
                sum_input_value=float(balance_data.get('value')),
                sum_output_quantity=0,
                sum_output_value=0,
                periodic_closed=False,
                sub_latest_log=log
            )
            if periods.company.company_config.cost_per_project:
                ReportInventoryCostByWarehouse.objects.create(
                    report_inventory_cost=rp_inv_cost,
                    warehouse=wh_obj,
                    opening_quantity=float(balance_data['quantity']),
                    ending_quantity=float(balance_data['quantity'])
                )

        if len(balance_data.get('data_sn', [])) > 0:
            cls.for_serial(balance_data, periods, prd_obj, wh_obj)
        elif len(balance_data.get('data_lot', [])) > 0:
            cls.for_lot(balance_data, periods, prd_obj, wh_obj)
        elif len(balance_data.get('data_lot', [])) == 0 and len(balance_data.get('data_sn', [])) == 0:
            cls.for_none(balance_data, periods, prd_obj, wh_obj)
        return rp_inv_cost

    @classmethod
    def create_balance_data(cls, balance_data, periods, employee_current):
        with transaction.atomic():
            sub_period_order = periods.company.software_start_using_time.month - periods.space_month
            sub_period_obj = periods.sub_periods_period_mapped.filter(order=sub_period_order).first()
            prd_obj = Product.objects.filter(id=balance_data.get('product_id')).first()
            wh_obj = WareHouse.objects.filter(id=balance_data.get('warehouse_id')).first()
            if not all([sub_period_order, sub_period_obj, prd_obj, wh_obj, periods, employee_current]):
                raise serializers.ValidationError({'error': 'Some objects are not exist.'})
            return cls.create_balance_data_sub(
                periods,
                prd_obj,
                wh_obj,
                sub_period_order,
                balance_data,
                employee_current,
                sub_period_obj
            )

    def create(self, validated_data):
        periods = Periods.objects.filter(
            tenant=self.context.get('tenant_current'),
            company=self.context.get('company_current'),
            fiscal_year=datetime.now().year
        ).first()
        balance_data = self.initial_data.get('balance_data')
        employee_current = self.context.get('employee_current')

        instance = self.create_balance_data(balance_data, periods, employee_current)
        SubPeriods.objects.filter(period_mapped=periods).update(run_report_inventory=False)

        period_mapped = Periods.objects.filter(
            tenant=instance.tenant, company=instance.company
        ).order_by('fiscal_year').first()
        SubPeriods.objects.filter(
            period_mapped=period_mapped, period_mapped__company_id=instance.company
        ).update(run_report_inventory=False)
        return instance


class BalanceInitializationCreateSerializerImportDB(BalanceInitializationCreateSerializer):

    class Meta:
        model = ReportInventoryCost
        fields = ()

    @classmethod
    def create_balance_data_import_db(cls, balance_data, periods, employee_current, tenant_current, company_current):
        with transaction.atomic():
            sub_period_order = periods.company.software_start_using_time.month - periods.space_month
            sub_period_obj = periods.sub_periods_period_mapped.filter(order=sub_period_order).first()
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_data.get('product_code')
            ).first()
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_data.get('warehouse_code')
            ).first()
            if not all([sub_period_order, sub_period_obj, prd_obj, wh_obj, periods, employee_current]):
                raise serializers.ValidationError({'error': 'Some objects are not exist.'})
            return BalanceInitializationCreateSerializer.create_balance_data_sub(
                periods,
                prd_obj,
                wh_obj,
                sub_period_order,
                balance_data,
                employee_current,
                sub_period_obj
            )

    def create(self, validated_data):
        tenant_current = self.context.get('tenant_current')
        company_current = self.context.get('company_current')
        periods = Periods.objects.filter(
            tenant=tenant_current, company=company_current, fiscal_year=datetime.now().year
        ).first()
        balance_data = self.initial_data.get('balance_data')
        employee_current = self.context.get('employee_current')

        instance = self.create_balance_data_import_db(
            balance_data, periods, employee_current, tenant_current, company_current
        )
        SubPeriods.objects.filter(period_mapped=periods).update(run_report_inventory=False)
        return instance


class BalanceInitializationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportInventoryCost
        fields = ('id',)


class ReportInventoryCostWarehouseDetailSerializer(serializers.ModelSerializer):
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
            gr_mapped = item.pw_lot_transact_pw_lot.first()
            goods_receipt_date = None
            if gr_mapped:
                goods_receipt_date = gr_mapped.goods_receipt.date_received if gr_mapped.goods_receipt else None
            lot_data.append({
                'id': item.id,
                'lot_number': item.lot_number,
                'expire_date': item.expire_date,
                'quantity_import': cast_unit_to_inv_quantity(obj.product.inventory_uom, item.quantity_import),
                'goods_receipt_date': goods_receipt_date
            })
        for item in obj.product_warehouse_serial_product_warehouse.filter(is_delete=False):
            sn_data.append({
                'id': item.id,
                'vendor_serial_number': item.vendor_serial_number,
                'serial_number': item.serial_number,
                'goods_receipt_date': item.goods_receipt.date_received if item.goods_receipt else None
            })
        return {'lot_data': lot_data, 'sn_data': sn_data}
