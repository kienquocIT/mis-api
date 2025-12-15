from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods, SubPeriods
from apps.sales.report.models import (
    ReportStockLog, ReportInventoryCost,
    ReportInventorySubFunction, ReportInventoryCostByWarehouse
)


class ReportInvLog:
    @classmethod
    def log(cls, doc_obj, doc_date, doc_data, for_balance_init=False):
        if not doc_obj or not doc_date or len(doc_data) == 0:
            print(f'*** NOT LOG (doc detail: {doc_obj.code}, {doc_date}, {len(doc_data)}) ***')
            return None
        try:
            with transaction.atomic():
                # lấy pp tính giá cost (0_FIFO, 1_WA, 2_SI)
                cost_cfg = ReportInvCommonFunc.get_cost_config(doc_obj.company)
                period_obj = Periods.get_period_by_doc_date(doc_obj.tenant_id, doc_obj.company_id, doc_date)
                if period_obj:
                    sub_period_obj = Periods.get_sub_period_by_doc_date(period_obj, doc_date)
                    if sub_period_obj:
                        sub_period_order = sub_period_obj.order

                        # cho kiểm kê định kì
                        if doc_obj.company.company_config.definition_inventory_valuation == 1:
                            ReportInvCommonFunc.auto_calculate_for_periodic(
                                doc_obj.tenant, doc_obj.company, period_obj, sub_period_order
                            )

                        # kiểm tra và chạy tổng kết (các) tháng trước đó, sau đó đẩy số dư qua đầu kì tháng tiếp theo
                        for order in range(1, sub_period_order + 1):
                            run_state = ReportInvCommonFunc.check_and_push_to_next_sub(
                                doc_obj.tenant,
                                doc_obj.company,
                                doc_obj.employee_created if doc_obj.employee_created else doc_obj.employee_inherit,
                                period_obj,
                                order
                            )
                            if run_state is False:
                                break

                        # tạo các log
                        new_logs = ReportStockLog.create_new_logs(
                            doc_obj, doc_data, period_obj, sub_period_order, cost_cfg
                        )

                        # cập nhập giá cost cho từng log
                        for log in new_logs:
                            ReportStockLog.update_log_cost(
                                log, period_obj, sub_period_order, cost_cfg, for_balance_init
                            )
                        print('# Add log for balance init successfully!\n'
                              if for_balance_init else f'# Write {doc_obj.code} to Inventory Report successfully!')
                        return new_logs
                    raise serializers.ValidationError({'sub_period_obj': 'Sub period order obj does not exist.'})
                raise serializers.ValidationError({'period_obj': f'Fiscal year {doc_date.year} does not exist.'})
        except Exception as err:
            print(err)
            return None


class ReportInvCommonFunc:
    @classmethod
    def cast_quantity_to_unit(cls, log_uom, log_quantity):
        return log_quantity * log_uom.ratio

    @classmethod
    def get_cost_config(cls, company):
        company_config = company.company_config
        cost_config = [
            1 if company_config.cost_per_warehouse else None,
            2 if company_config.cost_per_lot else None,
            3 if company_config.cost_per_project else None
        ]
        return [i for i in cost_config if i is not None]

    @classmethod
    def auto_calculate_for_periodic(cls, tenant, company, period_obj, sub_period_order):
        """ Tự động cập nhập giá cost cuối kì cho tháng trước """
        if int(sub_period_order) == 1:
            fiscal_year = period_obj.fiscal_year - 1
            period_obj = Periods.objects.filter(tenant=tenant, company=company, fiscal_year=fiscal_year).first()
            sub_period_order = 12

        if ReportInventoryCost.objects.filter(
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                periodic_closed=False
        ).exists():
            ReportInventorySubFunction.calculate_cost_dict_for_periodic(
                period_obj, sub_period_order, tenant, company
            )
        return True

    @classmethod
    def by_perpetual(cls, tenant, company, emp_current, last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh):
        item_parsed = {
            'tenant': tenant,
            'company': company,
            'employee_created': emp_current,
            'employee_inherit': emp_current,
            'product_id': last_sub_item.product_id,
            'serial_number': last_sub_item.serial_number,
            'lot_mapped_id': last_sub_item.lot_mapped_id,
            'warehouse_id': last_sub_item.warehouse_id,
            'sale_order_id': last_sub_item.sale_order_id,
            'lease_order_id': last_sub_item.lease_order_id,
            'service_order_id': last_sub_item.service_order_id,
            'period_mapped': this_period,
            'sub_period_order': this_sub.order,
            'sub_period': this_sub,
            'opening_balance_quantity': last_sub_item.ending_balance_quantity,
            'opening_balance_cost': last_sub_item.ending_balance_cost,
            'opening_balance_value': last_sub_item.ending_balance_value,
            'ending_balance_quantity': last_sub_item.ending_balance_quantity,
            'ending_balance_cost': last_sub_item.ending_balance_cost,
            'ending_balance_value': last_sub_item.ending_balance_value
        }
        rp_inv_cost = ReportInventoryCost(**item_parsed)
        bulk_info.append(rp_inv_cost)
        for report_inventory_cost in last_sub_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostByWarehouse(
                    report_inventory_cost=rp_inv_cost,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def by_periodic(cls, tenant, company, emp_current, last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh):
        item_parsed = {
            'tenant': tenant,
            'company': company,
            'employee_created': emp_current,
            'employee_inherit': emp_current,
            'product_id': last_sub_item.product_id,
            'serial_number': last_sub_item.serial_number,
            'lot_mapped_id': last_sub_item.lot_mapped_id,
            'warehouse_id': last_sub_item.warehouse_id,
            'sale_order_id': last_sub_item.sale_order_id,
            'lease_order_id': last_sub_item.lease_order_id,
            'service_order_id': last_sub_item.service_order_id,
            'period_mapped': this_period,
            'sub_period_order': this_sub.order,
            'sub_period': this_sub,
            'opening_balance_quantity': last_sub_item.periodic_ending_balance_quantity,
            'opening_balance_cost': last_sub_item.periodic_ending_balance_cost,
            'opening_balance_value': last_sub_item.periodic_ending_balance_value,
            'periodic_ending_balance_quantity': last_sub_item.periodic_ending_balance_quantity,
            'periodic_ending_balance_cost': last_sub_item.periodic_ending_balance_cost,
            'periodic_ending_balance_value': last_sub_item.periodic_ending_balance_value
        }
        rp_inv_cost = ReportInventoryCost(**item_parsed)
        bulk_info.append(rp_inv_cost)
        for report_inventory_cost in last_sub_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostByWarehouse(
                    report_inventory_cost=rp_inv_cost,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def push_to_next_sub(cls, tenant, company, emp_current, this_sub, last_sub):
        bulk_info = []
        bulk_info_wh = []
        for item in ReportInventoryCost.objects.filter(
                tenant=tenant, company=company, period_mapped=last_sub.period_mapped, sub_period=last_sub
        ):
            if not ReportInventoryCost.objects.filter(
                    tenant=tenant,
                    company=company,
                    period_mapped=this_sub.period_mapped,
                    sub_period=this_sub,
                    product_id=item.product_id,
                    warehouse_id=item.warehouse_id,
                    serial_number=item.serial_number,
                    lot_mapped_id=item.lot_mapped_id,
                    sale_order_id=item.sale_order_id,
                    lease_order_id=item.lease_order_id,
                    service_order_id=item.service_order_id,
            ).exists():
                bulk_info, bulk_info_wh = cls.by_perpetual(
                    tenant, company, emp_current, item, this_sub.period_mapped, this_sub, bulk_info, bulk_info_wh
                ) if company.company_config.definition_inventory_valuation == 0 else cls.by_periodic(
                    tenant, company, emp_current, item, this_sub.period_mapped, this_sub, bulk_info, bulk_info_wh
                )

        ReportInventoryCost.objects.bulk_create(bulk_info)
        ReportInventoryCostByWarehouse.objects.bulk_create(bulk_info_wh)
        return True

    @classmethod
    def check_and_push_to_next_sub(cls, tenant, company, emp_current, this_period, this_sub_order):
        """
        1. Lấy kỳ hiện tại + kỳ con hiện tại
        2. Nếu kỳ hiện tại chưa chạy report thì:
            2.1: Lấy kỳ trước + kỳ con trước
            2.2: Nếu kỳ con trước đã chạy report -> đẩy cuối kỳ trước qua đầu kỳ hiện tại -> cập nhập tt report kỳ này
                 Nếu không có kỳ con -> cập nhập tt report kỳ này
        """
        this_sub = SubPeriods.objects.filter(period_mapped=this_period, order=this_sub_order).first()
        if tenant and company and emp_current and this_period and this_sub:
            if not this_sub.run_report_inventory:
                last_period = Periods.objects.filter(
                    tenant=tenant, company=company, fiscal_year=this_period.fiscal_year - 1
                ).first() if int(this_sub_order) == 1 else this_period
                last_sub_order = 12 if int(this_sub_order) == 1 else int(this_sub_order) - 1
                last_sub = SubPeriods.objects.filter(period_mapped=last_period, order=last_sub_order).first()
                if last_period and last_sub:
                    if last_sub.run_report_inventory:
                        cls.push_to_next_sub(tenant, company, emp_current, this_sub, last_sub)
                this_sub.run_report_inventory = True
                this_sub.save(update_fields=['run_report_inventory'])
                print(f"Started {this_sub.start_date.month}/{this_period.fiscal_year}.")
            return True
        print('Error: Some objects are not exist (tenant, company, emp_current, this_period, this_sub).')
        return False
