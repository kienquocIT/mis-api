from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.sales.report.models import ReportStockLog, ReportInventoryCost, ReportInventorySubFunction


class InventoryCostLog:
    @classmethod
    def log(cls, doc_obj, doc_date, doc_data):
        try:
            tenant = doc_obj.tenant
            company = doc_obj.company
            with transaction.atomic():
                # lấy pp tính giá cost (0_FIFO, 1_CWA, 2_SIM)
                cost_cfg = InventoryCostLogFunc.get_cost_config(company.company_config)
                period_obj = Periods.objects.filter(tenant=tenant, company=company, fiscal_year=doc_date.year).first()
                if period_obj:
                    sub_period_order = doc_date.month - period_obj.space_month

                    # cho kiểm kê định kì
                    if company.company_config.definition_inventory_valuation == 1:
                        InventoryCostLogFunc.auto_calculate_for_periodic(tenant, company, period_obj, sub_period_order)

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


class InventoryCostLogFunc:
    @classmethod
    def cast_quantity_to_unit(cls, log_uom, log_quantity):
        return log_quantity * log_uom.ratio

    @classmethod
    def get_cost_config(cls, company_config):
        cost_per_warehouse = company_config.cost_per_warehouse
        cost_per_lot = company_config.cost_per_lot
        cost_per_project = company_config.cost_per_project
        config_inventory_management = []
        if cost_per_warehouse:
            config_inventory_management.append(1)
        if cost_per_lot:
            config_inventory_management.append(2)
        if cost_per_project:
            config_inventory_management.append(3)
        return config_inventory_management

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
            ReportInventorySubFunction.calculate_ending_balance_for_periodic(
                period_obj, sub_period_order, tenant, company
            )
        return True
