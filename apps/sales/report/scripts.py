from apps.core.company.models import Company
from apps.masterdata.saledata.models import ProductWareHouse, Periods, SubPeriods
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import GoodsIssue, GoodsReceipt, GoodsReturn, GoodsTransfer
from apps.sales.report.models import ReportStockLog, ReportStock, BalanceInitialization, ReportInventoryCost
from apps.sales.report.serializers import BalanceInitializationCreateSerializer
from apps.sales.report.utils import IRForDeliveryHandler, IRForGoodsIssueHandler, IRForGoodsReceiptHandler, \
    IRForGoodsReturnHandler, IRForGoodsTransferHandler


class InventoryReportRun:
    @staticmethod
    def delete_inventory_report_data(company_id, this_period):
        print(f'#delete inventory report data in period [{this_period.code}]', end='')
        ReportStock.objects.filter(company_id=company_id, period_mapped=this_period).delete()
        ReportStockLog.objects.filter(company_id=company_id, report_stock__period_mapped=this_period).delete()
        ReportInventoryCost.objects.filter(company_id=company_id, period_mapped=this_period).delete()
        print('...done')
        return True

    @staticmethod
    def recreate_balance_init_data(company_id, this_period):
        print('#recreate balance init data', end='')
        company = Company.objects.filter(id=company_id).first()
        software_start_using_time = company.software_start_using_time if company else None
        if software_start_using_time:
            print(f'...log to {software_start_using_time.date()}')
            if this_period.start_date <= software_start_using_time.date() <= this_period.end_date:
                for balance_init in BalanceInitialization.objects.filter(company_id=company_id):
                    prd_wh_obj = ProductWareHouse.objects.filter(
                        product=balance_init.product, warehouse=balance_init.warehouse
                    ).first()
                    if prd_wh_obj:
                        print(f'{balance_init.product.code} {balance_init.warehouse.code} {balance_init.quantity}')
                        BalanceInitializationCreateSerializer.push_to_inventory_report(balance_init, prd_wh_obj)
                print('...done')
                return True
        print('...nothing is created')
        return True

    @staticmethod
    def get_all_delivery_this_period(company_id, this_period):
        print('...get all delivery this period', end='')
        all_delivery = OrderDeliverySub.objects.filter(
            company_id=company_id,
            state=2,
            date_done__date__lte=this_period.end_date,
            date_done__date__gte=this_period.start_date
        ).order_by('date_done')
        print(f'...found {all_delivery.count()} record(s) total')
        return all_delivery

    @staticmethod
    def get_all_goods_issue_this_period(company_id, this_period):
        print('...get all goods issue this period', end='')
        all_goods_issue = GoodsIssue.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_goods_issue.count()} record(s) total')
        return all_goods_issue

    @staticmethod
    def get_all_goods_receipt_this_period(company_id, this_period):
        print('...get all goods receipt this period', end='')
        all_goods_receipt = GoodsReceipt.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_goods_receipt.count()} record(s) total')
        return all_goods_receipt

    @staticmethod
    def get_all_goods_return_this_period(company_id, this_period):
        print('...get all goods return this period', end='')
        all_goods_return = GoodsReturn.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_goods_return.count()} record(s) total')
        return all_goods_return

    @staticmethod
    def get_all_goods_transfer_this_period(company_id, this_period):
        print('...get all goods transfer this period', end='')
        all_goods_transfer = GoodsTransfer.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_goods_transfer.count()} record(s) total')
        return all_goods_transfer

    @staticmethod
    def combine_data_all_docs(company_id, this_period):
        print('#combine data all docs')
        all_docs = []
        for delivery in InventoryReportRun.get_all_delivery_this_period(company_id, this_period):
            all_docs.append({
                'id': str(delivery.id),
                'code': str(delivery.code),
                'date_approved': delivery.date_done,
                'type': 'delivery'
            })
        for goods_issue in InventoryReportRun.get_all_goods_issue_this_period(company_id, this_period):
            all_docs.append({
                'id': str(goods_issue.id),
                'code': str(goods_issue.code),
                'date_approved': goods_issue.date_approved,
                'type': 'goods_issue'
            })
        for goods_receipt in InventoryReportRun.get_all_goods_receipt_this_period(company_id, this_period):
            all_docs.append({
                'id': str(goods_receipt.id),
                'code': str(goods_receipt.code),
                'date_approved': goods_receipt.date_approved,
                'type': 'goods_receipt'
            })
        for goods_return in InventoryReportRun.get_all_goods_return_this_period(company_id, this_period):
            all_docs.append({
                'id': str(goods_return.id),
                'code': str(goods_return.code),
                'date_approved': goods_return.date_approved,
                'type': 'goods_return'
            })
        for goods_transfer in InventoryReportRun.get_all_goods_transfer_this_period(company_id, this_period):
            all_docs.append({
                'id': str(goods_transfer.id),
                'code': str(goods_transfer.code),
                'date_approved': goods_transfer.date_approved,
                'type': 'goods_transfer'
            })
        return sorted(all_docs, key=lambda x: x['date_approved'])

    @staticmethod
    def log_docs(all_doc_sorted):
        print('#log docs')
        for doc in all_doc_sorted:
            print(f"> doc info: {doc['date_approved'].strftime('%d/%m/%Y')} - {doc['code']} ({doc['type']})")
            if doc['type'] == 'delivery':
                instance = OrderDeliverySub.objects.get(id=doc['id'])
                IRForDeliveryHandler.push_to_inventory_report(instance)
            if doc['type'] == 'goods_issue':
                instance = GoodsIssue.objects.get(id=doc['id'])
                IRForGoodsIssueHandler.push_to_inventory_report(instance)
            if doc['type'] == 'goods_receipt':
                instance = GoodsReceipt.objects.get(id=doc['id'])
                IRForGoodsReceiptHandler.push_to_inventory_report(instance)
            if doc['type'] == 'goods_return':
                instance = GoodsReturn.objects.get(id=doc['id'])
                IRForGoodsReturnHandler.push_to_inventory_report(instance)
            if doc['type'] == 'goods_transfer':
                instance = GoodsTransfer.objects.get(id=doc['id'])
                IRForGoodsTransferHandler.push_to_inventory_report(instance)
        return True

    @staticmethod
    def run(company_id, fiscal_year):
        """
        0. Cập nhập các sub_periods thành trạng thái 'chưa chạy báo cáo'
        1. Lấy dữ liệu các phiếu nhập - xuất kho
        2. Tạo lại Số dư đầu kì (nếu năm đó có setup 'Ngày bắt đầu sử dụng phần mềm')
        3. Xóa data inventory report data cũ
        4. Chạy log
        """
        this_period = Periods.objects.filter(company_id=company_id, fiscal_year=fiscal_year).first()
        if this_period:
            SubPeriods.objects.filter(period_mapped=this_period).update(run_report_inventory=False)

            all_doc_sorted = InventoryReportRun.combine_data_all_docs(company_id, this_period)

            InventoryReportRun.delete_inventory_report_data(company_id, this_period)
            InventoryReportRun.recreate_balance_init_data(company_id, this_period)
            InventoryReportRun.log_docs(all_doc_sorted)
            print('#run successfully!')
            return True
        print('#can not find any Period!')
        return False

    @staticmethod
    def run_tenant(tenant_id, fiscal_year):
        for company in Company.objects.filter(tenant_id=tenant_id):
            print(f'\n*** Run for {company.title}')
            InventoryReportRun.run(company.id, fiscal_year)
            print('...done')
        print('Done :))')
        return True