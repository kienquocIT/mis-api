from django.db import transaction
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.sales.report.models import ReportStockLog, ReportInventoryCost, ReportInventorySubFunction


class InventoryCostLog:
    @classmethod
    def log(cls, stock_obj, stock_obj_date, stock_data):
        return cls.weighted_average_log(stock_obj, stock_obj_date, stock_data)

    @classmethod
    def weighted_average_log(cls, stock_obj, stock_obj_date, stock_data):
        print('*** WEIGHTED AVERAGE LOG')
        try:
            tenant = stock_obj.tenant
            company = stock_obj.company
            with transaction.atomic():
                # lấy pp tính giá cost
                cost_calculate_cfg = InventoryCostLogFunc.get_cost_calculate_config(company.company_config)
                period_obj = Periods.objects.filter(
                    tenant=tenant,
                    company=company,
                    fiscal_year=stock_obj_date.year
                ).first()
                if period_obj:
                    sub_period_order = stock_obj_date.month - period_obj.space_month

                    # cho kiểm kê định kì
                    if int(sub_period_order) == 1:
                        last_period_obj = Periods.objects.filter(
                            tenant=tenant,
                            company=company,
                            fiscal_year=period_obj.fiscal_year - 1
                        ).first()
                        last_sub_cost = ReportInventoryCost.objects.filter(
                            period_mapped=last_period_obj,
                            sub_period_order=12,
                            periodic_closed=False
                        ).exists()
                        if last_sub_cost:
                            ReportInventorySubFunction.calculate_ending_balance_for_periodic(
                                last_period_obj, 12, tenant, company
                            )
                    else:
                        last_sub_cost = ReportInventoryCost.objects.filter(
                            period_mapped=period_obj,
                            sub_period_order=int(sub_period_order) - 1,
                            periodic_closed=False
                        ).exists()
                        if last_sub_cost:
                            ReportInventorySubFunction.calculate_ending_balance_for_periodic(
                                period_obj, int(sub_period_order) - 1, tenant, company
                            )

                    # tạo các log
                    new_log_list = ReportStockLog.create_new_log_list(
                        stock_obj, stock_data, period_obj, sub_period_order, cost_calculate_cfg
                    )
                    # cập nhập giá cost hiện tại
                    for log in new_log_list:
                        ReportStockLog.update_current_cost(log, period_obj, sub_period_order, cost_calculate_cfg)
                    return True
                raise serializers.ValidationError({'period_obj': f'Fiscal year {stock_obj_date.year} does not exist.'})
        except Exception as err:
            print(err)
        return False


class InventoryCostLogFunc:
    @classmethod
    def cast_quantity_to_unit(cls, log_uom, log_quantity):
        return log_quantity * log_uom.ratio

    @classmethod
    def get_cost_calculate_config(cls, company_config):
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
