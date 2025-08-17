from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import (
    ProductWareHouse, SubPeriods, Periods, Product, WareHouse,
    ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.report.utils.inventory_log import ReportInvCommonFunc, ReportInvLog
from apps.sales.report.models import (
    ReportStock, ReportInventoryCost, ReportInventorySubFunction,
    ReportStockLog, BalanceInitialization, BalanceInitializationSerial, BalanceInitializationLot
)


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
            casted_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, log.quantity)
            casted_value = log.value
            casted_cost = (casted_value / casted_quantity) if casted_quantity else 0
            casted_current_quantity = [
                BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, log.perpetual_current_quantity),
                BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, log.periodic_current_quantity)
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
                casted_obq = BalanceInitCommonFunction.cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, this_balance['opening_balance_quantity']
                )
                casted_obv = this_balance['opening_balance_value']
                casted_obc = casted_obv / casted_obq if casted_obq else 0
                casted_ebq = BalanceInitCommonFunction.cast_unit_to_inv_quantity(
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
            casted_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity', 0))
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': lot.get('lot_value'),
                'out_quantity': '',
                'out_value': '',
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        else:
            casted_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'in_quantity': casted_in_quantity,
                'in_value': log.value,
                'out_quantity': '',
                'out_value': '',
                'system_date': log.system_date,
                'lot_number': '',
                'expire_date': '',
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        return data_stock_activity

    @classmethod
    def get_data_stock_activity_for_out(cls, log, data_stock_activity, product):
        if len(log.lot_data) > 0:
            lot = log.lot_data
            casted_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(product.inventory_uom, lot.get('lot_quantity', 0))
            data_stock_activity.append({
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': lot.get('lot_value'),
                'system_date': log.system_date,
                'lot_number': lot.get('lot_number'),
                'expire_date': lot.get('lot_expire_date'),
                'log_order': log.log_order,
                'trans_title': log.trans_title,
                'trans_code': log.trans_code,
            })
        else:
            casted_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(product.inventory_uom, log.quantity)
            data_stock_activity.append({
                'in_quantity': '',
                'in_value': '',
                'out_quantity': casted_out_quantity,
                'out_value': log.value,
                'system_date': log.system_date,
                'lot_number': '',
                'expire_date': '',
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
                    elif log.trans_title in [
                        'Delivery (sale)', 'Delivery (lease)',
                        'Goods issue', 'Goods transfer (out)'
                    ]:
                        data_stock_activity = cls.get_data_stock_activity_for_out(
                            log, data_stock_activity, obj.product
                        )
            data_stock_activity = sorted( data_stock_activity, key=lambda key: (key['system_date'], key['log_order']))

            # lấy inventory_cost_data của kì hiện tại
            this_sub_value = ReportInventorySubFunction.get_this_sub_period_cost_dict(obj)

            if div == 0:
                sum_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_in_quantity)
                sum_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_out_quantity)
            else:
                sum_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_input_quantity)
                sum_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_output_quantity)
                sum_in_value = obj.sum_input_value
                sum_out_value = obj.sum_output_value

            result.append({
                'opening_balance_quantity': BalanceInitCommonFunction.cast_unit_to_inv_quantity(
                    obj.product.inventory_uom, wh_sub.opening_quantity
                ),
                'opening_balance_value': wh_sub.opening_quantity * this_sub_value['opening_balance_cost'],
                'sum_in_quantity': sum_in_quantity,
                'sum_in_value': sum_in_value,
                'sum_out_quantity': sum_out_quantity,
                'sum_out_value': sum_out_value,
                'ending_balance_quantity': BalanceInitCommonFunction.cast_unit_to_inv_quantity(
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
                    data_stock_activity = cls.get_data_stock_activity_for_in(
                        log, data_stock_activity, obj.product
                    )
                elif log.trans_title in [
                    'Delivery (sale)', 'Delivery (lease)',
                    'Goods issue', 'Goods transfer (out)'
                ]:
                    data_stock_activity = cls.get_data_stock_activity_for_out(
                        log, data_stock_activity, obj.product
                    )

        data_stock_activity = sorted(
            data_stock_activity, key=lambda key: (key['system_date'], key['log_order'])
        )

        # lấy inventory_cost_data của kì hiện tại
        this_sub_value = ReportInventorySubFunction.get_this_sub_period_cost_dict(obj)

        if div == 0:
            sum_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_in_quantity)
            sum_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, sum_out_quantity)
        else:
            sum_in_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_input_quantity)
            sum_out_quantity = BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.sum_output_quantity)
            sum_in_value = obj.sum_input_value
            sum_out_value = obj.sum_output_value

        result = {
            'opening_balance_quantity': BalanceInitCommonFunction.cast_unit_to_inv_quantity(
                obj.product.inventory_uom, this_sub_value['opening_balance_quantity']
            ),
            'opening_balance_value': this_sub_value['opening_balance_value'],
            'sum_in_quantity': sum_in_quantity,
            'sum_in_value': sum_in_value,
            'sum_out_quantity': sum_out_quantity,
            'sum_out_value': sum_out_value,
            'ending_balance_quantity': BalanceInitCommonFunction.cast_unit_to_inv_quantity(
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
        return BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, obj.stock_amount)


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
                'quantity_import': BalanceInitCommonFunction.cast_unit_to_inv_quantity(obj.product.inventory_uom, item.quantity_import),
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


# balance init
class BalanceInitializationListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    class Meta:
        model = BalanceInitialization
        fields = (
            'id',
            'product',
            'uom',
            'warehouse',
            'quantity',
            'value',
            'data_sn',
            'data_lot'
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
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
        } if obj.uom else {}

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


class BalanceInitializationCreateSerializer(serializers.ModelSerializer):
    balance_init_data = serializers.JSONField(default=dict)

    class Meta:
        model = BalanceInitialization
        fields = ('balance_init_data',)

    def validate(self, validate_data):
        tenant_current = self.context.get('tenant_current')
        company_current = self.context.get('company_current')
        if not tenant_current or not company_current:
            raise serializers.ValidationError({"error": "Tenant or Company is missing."})

        balance_init_data = validate_data.get('balance_init_data', {})
        validate_data = BalanceInitCommonFunction.validate_balance_init_data(
            balance_init_data, tenant_current, company_current
        )
        return validate_data

    @classmethod
    def for_serial(cls, periods, instance, quantity, data_sn):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).exists():
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            bulk_info_sn = []
            for serial in data_sn:
                for key in serial:
                    if serial[key] == '':
                        serial[key] = None
                bulk_info_sn.append(
                    ProductWareHouseSerial(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product_warehouse=prd_wh_obj,
                        **serial
                    )
                )
            ProductWareHouseSerial.objects.bulk_create(bulk_info_sn)
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def for_lot(cls, periods, instance, quantity, data_lot):
        if not ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).exists():
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            bulk_info_lot = []
            for lot in data_lot:
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
                            instance.product.inventory_uom, float(lot.get('quantity_import', 0))
                        )
                    )
                )
            ProductWareHouseLot.objects.bulk_create(bulk_info_lot)
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def for_none(cls, periods, instance, quantity):
        prd_wh = ProductWareHouse.objects.filter(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse
        ).first()
        if not prd_wh:
            prd_wh_obj = ProductWareHouse.objects.create(
                tenant_id=periods.tenant_id,
                company_id=periods.company_id,
                product=instance.product,
                warehouse=instance.warehouse,
                uom=instance.product.general_uom_group.uom_reference,
                unit_price=instance.value/quantity,
                tax=None,
                stock_amount=quantity,
                receipt_amount=quantity,
                sold_amount=0,
                picked_ready=0,
                used_amount=0,
                product_data={
                    "id": str(instance.product_id),
                    "code": instance.product.code,
                    "title": instance.product.title
                },
                warehouse_data={
                    "id": str(instance.warehouse_id),
                    "code": instance.warehouse.code,
                    "title": instance.warehouse.title
                },
                uom_data={
                    "id": str(instance.product.general_uom_group.uom_reference_id),
                    "code": instance.product.general_uom_group.uom_reference.code,
                    "title": instance.product.general_uom_group.uom_reference.title
                } if instance.product.general_uom_group.uom_reference else {},
                tax_data={}
            )
            return prd_wh_obj
        raise serializers.ValidationError({"Existed": 'This Product-Warehouse already exists.'})

    @classmethod
    def create_product_warehouse_data(cls, instance, validated_data):
        with transaction.atomic():
            period_obj = validated_data['period_obj']
            data_lot = instance.data_lot
            data_sn = instance.data_sn
            quantity = ReportInvCommonFunc.cast_quantity_to_unit(instance.product.inventory_uom, instance.quantity)

            instance.product.stock_amount += quantity
            instance.product.available_amount += quantity
            instance.product.save(update_fields=['stock_amount', 'available_amount'])

            if len(data_sn) > 0:
                return cls.for_serial(period_obj, instance, quantity, data_sn)
            if len(data_lot) > 0:
                return cls.for_lot(period_obj, instance, quantity, data_lot)
            if len(data_lot) == 0 and len(data_sn) == 0:
                return cls.for_none(period_obj, instance, quantity)
            return True

    @classmethod
    def push_to_inventory_report(cls, instance, prd_wh_obj):
        """ Khởi tạo số dư đầu kì """
        doc_data = []
        if len(instance.data_lot) > 0:
            all_lots = prd_wh_obj.product_warehouse_lot_product_warehouse.all()
            for lot in instance.data_lot:
                lot_mapped = all_lots.filter(lot_number=lot.get('lot_number')).first()
                if lot_mapped:
                    unit_price_by_inventory_uom = instance.value/instance.quantity
                    casted_cost = unit_price_by_inventory_uom/instance.product.inventory_uom.ratio
                    doc_data.append({
                        'product': instance.product,
                        'warehouse': instance.warehouse,
                        'system_date': instance.date_created,
                        'posting_date': instance.date_created,
                        'document_date': instance.date_created,
                        'stock_type': 1,
                        'trans_id': '',
                        'trans_code': '',
                        'trans_title': 'Balance init input',
                        'quantity': lot_mapped.quantity_import,
                        'cost': casted_cost,
                        'value': casted_cost * lot_mapped.quantity_import,
                        'lot_data': {
                            'lot_id': str(lot_mapped.id),
                            'lot_number': lot_mapped.lot_number,
                            'lot_expire_date': str(lot_mapped.expire_date) if lot_mapped.expire_date else None
                        }
                    })
        else:
            casted_quantity = ReportInvCommonFunc.cast_quantity_to_unit(
                instance.product.inventory_uom,
                instance.quantity
            )
            doc_data.append({
                'product': instance.product,
                'warehouse': instance.warehouse,
                'system_date': instance.date_created,
                'posting_date': instance.date_created,
                'document_date': instance.date_created,
                'stock_type': 1,
                'trans_id': '',
                'trans_code': '',
                'trans_title': 'Balance init input',
                'quantity': casted_quantity,
                'cost': instance.value / casted_quantity,
                'value': instance.value,
                'lot_data': {}
            })
        ReportInvLog.log(instance, instance.company.software_start_using_time, doc_data, True)
        return True

    @classmethod
    def create_m2m_balance_init_data(cls, instance):
        bulk_info_sn = []
        for serial in instance.data_sn:
            serial_obj = ProductWareHouseSerial.objects.filter(
                product_warehouse__product=instance.product,
                serial_number=serial.get('serial_number')
            ).first()
            if serial_obj:
                bulk_info_sn.append(BalanceInitializationSerial(
                    balance_init=instance,
                    serial_mapped=serial_obj
                ))
        BalanceInitializationSerial.objects.bulk_create(bulk_info_sn)

        bulk_info_lot = []
        for lot in instance.data_lot:
            lot_obj = ProductWareHouseLot.objects.filter(
                product_warehouse__product=instance.product,
                lot_number=lot.get('lot_number')
            ).first()
            if lot_obj:
                bulk_info_lot.append(BalanceInitializationLot(
                    balance_init=instance,
                    lot_mapped=lot_obj,
                    quantity=lot.get('quantity_import')
                ))
        BalanceInitializationLot.objects.bulk_create(bulk_info_lot)
        return True

    def create(self, validated_data):
        instance = BalanceInitialization.objects.create(
            product=validated_data.get('product'),
            warehouse=validated_data.get('warehouse'),
            uom=validated_data.get('uom'),
            quantity=validated_data.get('quantity', 0),
            value=validated_data.get('value', 0),
            data_lot=validated_data.get('data_lot', []),
            data_sn=validated_data.get('data_sn', []),
            tenant=self.context.get('tenant_current'),
            company=self.context.get('company_current'),
            employee_created=self.context.get('employee_current'),
            employee_inherit=self.context.get('employee_current'),
        )
        prd_wh_obj = self.create_product_warehouse_data(instance, validated_data)
        self.create_m2m_balance_init_data(instance)
        self.push_to_inventory_report(instance, prd_wh_obj)
        SubPeriods.objects.filter(period_mapped=validated_data['period_obj']).update(run_report_inventory=False)
        return instance


class BalanceInitializationCreateSerializerImportDB(BalanceInitializationCreateSerializer):
    balance_init_data = serializers.JSONField(default=dict)

    class Meta:
        model = BalanceInitialization
        fields = ('balance_init_data',)

    def validate(self, validate_data):
        tenant_current = self.context.get('tenant_current')
        company_current = self.context.get('company_current')
        if not tenant_current or not company_current:
            raise serializers.ValidationError({"error": "Tenant or Company is missing."})

        balance_init_data = validate_data.get('balance_init_data', {})
        validate_data = BalanceInitCommonFunction.validate_balance_init_data(
            balance_init_data, tenant_current, company_current
        )
        return validate_data

    def create(self, validated_data):
        instance = BalanceInitialization.objects.create(
            product=validated_data.get('product'),
            warehouse=validated_data.get('warehouse'),
            uom=validated_data.get('uom'),
            quantity=validated_data.get('quantity', 0),
            value=validated_data.get('value', 0),
            data_lot=validated_data.get('data_lot', []),
            data_sn=validated_data.get('data_sn', []),
            tenant=self.context.get('tenant_current'),
            company=self.context.get('company_current'),
            employee_created=self.context.get('employee_current'),
            employee_inherit=self.context.get('employee_current'),
        )
        prd_wh_obj = self.create_product_warehouse_data(instance, validated_data)
        self.create_m2m_balance_init_data(instance)
        self.push_to_inventory_report(instance, prd_wh_obj)
        SubPeriods.objects.filter(period_mapped=validated_data['period_obj']).update(run_report_inventory=False)
        return instance


class BalanceInitializationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportInventoryCost
        fields = ('id',)


class BalanceInitCommonFunction:
    @staticmethod
    def cast_unit_to_inv_quantity(inventory_uom, log_quantity):
        return (log_quantity / inventory_uom.ratio) if inventory_uom else 0

    @staticmethod
    def get_product_from_balance_init_data(balance_init_data, tenant_current, company_current):
        if 'product_id' not in balance_init_data and 'product_code' not in balance_init_data:
            raise serializers.ValidationError({"error": "Balance data is missing product information."})

        prd_obj = None
        if 'product_id' in balance_init_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, id=balance_init_data.get('product_id')
            ).first()
        if 'product_code' in balance_init_data:
            prd_obj = Product.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_init_data.get('product_code')
            ).first()
        return prd_obj

    @staticmethod
    def get_warehouse_from_balance_init_data(balance_init_data, tenant_current, company_current):
        if 'warehouse_id' not in balance_init_data and 'warehouse_code' not in balance_init_data:
            raise serializers.ValidationError({"error": "Balance data is missing warehouse information."})

        wh_obj = None
        if 'warehouse_id' in balance_init_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, id=balance_init_data.get('warehouse_id')
            ).first()
        if 'product_code' in balance_init_data:
            wh_obj = WareHouse.objects.filter(
                tenant=tenant_current, company=company_current, code=balance_init_data.get('warehouse_code')
            ).first()
        return wh_obj

    @staticmethod
    def validate_balance_init_data(balance_init_data, tenant_obj, company_obj):
        prd_obj = BalanceInitCommonFunction.get_product_from_balance_init_data(balance_init_data, tenant_obj, company_obj)
        if not prd_obj:
            raise serializers.ValidationError({'prd_obj': 'Product is not found.'})

        wh_obj = BalanceInitCommonFunction.get_warehouse_from_balance_init_data(balance_init_data, tenant_obj, company_obj)
        if not wh_obj:
            raise serializers.ValidationError({'wh_obj': 'Warehouse is not found.'})

        this_period = Periods.get_current_period(tenant_obj.id, company_obj.id)
        if not this_period:
            raise serializers.ValidationError({'this_period': 'Period is not found.'})

        if not prd_obj.inventory_uom:
            raise serializers.ValidationError({'inventory_uom': 'Inventory UOM is not found.'})

        if BalanceInitialization.objects.filter(product=prd_obj, warehouse=wh_obj).exists():
            raise serializers.ValidationError(
                {"Existed": f"{prd_obj.title}'s opening balance has been created in {wh_obj.title}."}
            )

        if prd_obj.is_used_in_inventory_activities(warehouse_obj=wh_obj):
            raise serializers.ValidationError(
                {"Has trans": f'{prd_obj.title} transactions are existed in {wh_obj.title}.'}
            )

        sub_period_order = company_obj.software_start_using_time.month - this_period.space_month
        this_sub_period = this_period.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if not this_sub_period:
            raise serializers.ValidationError({"this_sub_period": 'This sub period is not found.'})

        validate_data = {
            'product': prd_obj,
            'uom': prd_obj.inventory_uom,
            'warehouse': wh_obj,
            'period_obj': this_period,
            'sub_period_obj': this_sub_period,
            'quantity': float(balance_init_data.get('quantity', 0)),
            'value': float(balance_init_data.get('value', 0)),
            'data_lot': balance_init_data.get('data_lot', []),
            'data_sn': balance_init_data.get('data_sn', [])
        }
        return validate_data
