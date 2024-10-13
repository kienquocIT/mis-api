from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods, SubPeriods
from apps.sales.report.models import (
    ReportStockLog, ReportInventoryCost,
    ReportInventorySubFunction, ReportInventoryCostByWarehouse
)


class InventoryCostLog:
    @classmethod
    def log(cls, doc_obj, doc_date, doc_data):
        try:
            tenant = doc_obj.tenant
            company = doc_obj.company
            employee = doc_obj.employee_created if doc_obj.employee_created else doc_obj.employee_inherit
            with transaction.atomic():
                # lấy pp tính giá cost (0_FIFO, 1_CWA, 2_SIM)
                cost_cfg = ReportInvCommonFunc.get_cost_config(company.company_config)
                period_obj = Periods.objects.filter(tenant=tenant, company=company, fiscal_year=doc_date.year).first()
                if period_obj:
                    sub_period_order = doc_date.month - period_obj.space_month

                    # cho kiểm kê định kì
                    if company.company_config.definition_inventory_valuation == 1:
                        ReportInvCommonFunc.auto_calculate_for_periodic(tenant, company, period_obj, sub_period_order)

                    # nếu đây GD đầu tiên, update các tháng trước đó (từ ngày bắt đầu sd phần mềm) -> "đã chạy báo cáo"
                    if not ReportStockLog.objects.filter(tenant=tenant, company=company).exists():
                        for order in range(
                                company.software_start_using_time.month - period_obj.space_month,
                                sub_period_order
                        ):
                            period_obj.sub_periods_period_mapped.filter(order=order).update(run_report_inventory=True)
                            print(f"Report inventory {order + period_obj.space_month}/{period_obj.fiscal_year} is run.")

                    # kiểm tra và chạy tổng kết tháng trước đó, sau đó đẩy số dư qua đầu kì tháng này
                    ReportInvCommonFunc.create_this_sub_inventory_cost_record(
                        tenant, company, employee, period_obj, sub_period_order
                    )

                    # tạo các log
                    new_logs = ReportStockLog.create_new_logs(doc_obj, doc_data, period_obj, sub_period_order, cost_cfg)

                    # cập nhập giá cost cho từng log
                    for log in new_logs:
                        ReportStockLog.update_log_cost(log, period_obj, sub_period_order, cost_cfg)
                    return True
                raise serializers.ValidationError({'period_obj': f'Fiscal year {doc_date.year} does not exist.'})
        except Exception as err:
            print(err)
            return False


class ReportInvCommonFunc:
    @classmethod
    def cast_quantity_to_unit(cls, log_uom, log_quantity):
        return log_quantity * log_uom.ratio

    @classmethod
    def get_cost_config(cls, company_config):
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
    def by_perpetual(
            cls, tenant, company, employee_current, last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh
    ):
        rp_prd_wh = ReportInventoryCost(
            tenant=tenant,
            company=company,
            employee_created=employee_current,
            employee_inherit=employee_current,
            product_id=last_sub_item.product_id,
            lot_mapped_id=last_sub_item.lot_mapped_id,
            warehouse_id=last_sub_item.warehouse_id,
            sale_order_id=last_sub_item.sale_order_id,
            period_mapped=this_period,
            sub_period_order=this_sub.order,
            sub_period=this_sub,
            opening_balance_quantity=last_sub_item.ending_balance_quantity,
            opening_balance_cost=last_sub_item.ending_balance_cost,
            opening_balance_value=last_sub_item.ending_balance_value,
            ending_balance_quantity=last_sub_item.ending_balance_quantity,
            ending_balance_cost=last_sub_item.ending_balance_cost,
            ending_balance_value=last_sub_item.ending_balance_value
        )
        bulk_info.append(rp_prd_wh)
        for report_inventory_cost in last_sub_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostByWarehouse(
                    report_inventory_cost=rp_prd_wh,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def by_periodic(
            cls, tenant, company, employee_current, last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh
    ):
        rp_prd_wh = ReportInventoryCost(
            tenant=tenant,
            company=company,
            employee_created=employee_current,
            employee_inherit=employee_current,
            product_id=last_sub_item.product_id,
            lot_mapped_id=last_sub_item.lot_mapped_id,
            warehouse_id=last_sub_item.warehouse_id,
            period_mapped=this_period,
            sub_period_order=this_sub.order,
            sub_period=this_sub,
            opening_balance_quantity=last_sub_item.periodic_ending_balance_quantity,
            opening_balance_cost=last_sub_item.periodic_ending_balance_cost,
            opening_balance_value=last_sub_item.periodic_ending_balance_value,
            periodic_ending_balance_quantity=last_sub_item.periodic_ending_balance_quantity,
            periodic_ending_balance_cost=last_sub_item.periodic_ending_balance_cost,
            periodic_ending_balance_value=last_sub_item.periodic_ending_balance_value
        )
        bulk_info.append(rp_prd_wh)
        for report_inventory_cost in last_sub_item.report_inventory_cost_wh.all():
            bulk_info_wh.append(
                ReportInventoryCostByWarehouse(
                    report_inventory_cost=rp_prd_wh,
                    warehouse=report_inventory_cost.warehouse,
                    opening_quantity=report_inventory_cost.ending_quantity,
                    ending_quantity=report_inventory_cost.ending_quantity
                )
            )
        return bulk_info, bulk_info_wh

    @classmethod
    def create_this_sub_inventory_cost_record(cls, tenant, company, employee_current, this_period, this_sub_order):
        if tenant and company and employee_current and this_period and this_sub_order:
            this_sub = SubPeriods.objects.filter(period_mapped=this_period, order=this_sub_order).first()
            if not this_sub.run_report_inventory:
                last_period = Periods.objects.filter(
                    fiscal_year=this_period.fiscal_year - 1
                ).first() if int(this_sub_order) == 1 else this_period
                last_sub_order = 12 if int(this_sub_order) == 1 else int(this_sub_order) - 1

                bulk_info = []
                bulk_info_wh = []
                for last_sub_item in ReportInventoryCost.objects.filter(
                        tenant=tenant,
                        company=company,
                        period_mapped=last_period,
                        sub_period_order=last_sub_order
                ):
                    if not ReportInventoryCost.objects.filter(
                            tenant=tenant,
                            company=company,
                            period_mapped=this_period,
                            sub_period_order=this_sub_order,
                            product_id=last_sub_item.product_id,
                            warehouse_id=last_sub_item.warehouse_id,
                            lot_mapped_id=last_sub_item.lot_mapped_id,
                            sale_order_id=last_sub_item.sale_order_id,
                    ).exists():
                        bulk_info, bulk_info_wh = cls.by_perpetual(
                            tenant, company, employee_current,
                            last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh
                        ) if company.company_config.definition_inventory_valuation == 0 else cls.by_periodic(
                            tenant, company, employee_current,
                            last_sub_item, this_period, this_sub, bulk_info, bulk_info_wh
                        )

                ReportInventoryCost.objects.bulk_create(bulk_info)
                ReportInventoryCostByWarehouse.objects.bulk_create(bulk_info_wh)
                last_sub = SubPeriods.objects.filter(period_mapped=last_period, order=last_sub_order).first()
                if any([
                    last_sub.run_report_inventory,
                    int(this_sub_order) == company.software_start_using_time.month - this_period.space_month
                ]):
                    this_sub.run_report_inventory = True
                    this_sub.save(update_fields=['run_report_inventory'])
                    print(f"Report inventory {this_sub.start_date.month}/{this_period.fiscal_year} is run.")
            return True
        raise serializers.ValidationError({'error': 'Some objects are not exist.'})
