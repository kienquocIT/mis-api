from apps.accounting.journalentry.models import JournalEntry, JE_ALLOWED_APP, AllowedAppAutoJournalEntry
from apps.accounting.journalentry.utils import (
    JEForAPInvoiceHandler, JEForARInvoiceHandler, JEForCIFHandler,
    JEForCOFHandler, JEForDeliveryHandler, JEForGoodsReceiptHandler
)
from apps.masterdata.saledata.models.periods import Periods, SubPeriods
from apps.sales.apinvoice.models import APInvoice
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.delivery.models.delivery import OrderDelivery
from apps.sales.financialcashflow.models.cif_models import CashInflow
from apps.sales.financialcashflow.models.cof_models import CashOutflow
from apps.sales.inventory.models.goods_receipt import GoodsReceipt


class JournalEntryInitData:
    @staticmethod
    def create_app_supported(tenant_id, company_id):
        """ Hàm khởi tạo các app hỗ trợ bút toán tự động """
        for key, value in JE_ALLOWED_APP.items():
            AllowedAppAutoJournalEntry.update_or_create_app(tenant_id, company_id, key, False)
        return True

class JournalEntryRun:
    @staticmethod
    def delete_journal_entry_data(company_id, this_period):
        print(f'#delete journal entry data in period [{this_period.code}]', end='')
        JournalEntry.objects.filter(company_id=company_id, period_mapped=this_period).delete()
        print('...done')
        return True

    @staticmethod
    def get_all_ap_invoice_this_period(company_id, this_period):
        print('...get all AP invoice this period', end='')
        all_ap_invoice = APInvoice.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_ap_invoice.count()} record(s) total')
        return all_ap_invoice

    @staticmethod
    def get_all_ar_invoice_this_period(company_id, this_period):
        print('...get all AR invoice this period', end='')
        all_ar_invoice = ARInvoice.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_ar_invoice.count()} record(s) total')
        return all_ar_invoice

    @staticmethod
    def get_all_cif_this_period(company_id, this_period):
        print('...get all cif this period', end='')
        all_cif = CashInflow.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_cif.count()} record(s) total')
        return all_cif

    @staticmethod
    def get_all_cof_this_period(company_id, this_period):
        print('...get all goods receipt this period', end='')
        all_cof = CashOutflow.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_cof.count()} record(s) total')
        return all_cof

    @staticmethod
    def get_all_delivery_this_period(company_id, this_period):
        print('...get all delivery this period', end='')
        all_delivery = OrderDelivery.objects.filter(
            company_id=company_id,
            system_status=3,
            date_approved__date__lte=this_period.end_date,
            date_approved__date__gte=this_period.start_date
        ).order_by('date_approved')
        print(f'...found {all_delivery.count()} record(s) total')
        return all_delivery

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
    def combine_data_all_docs(company_id, this_period):
        print('#combine data all docs')
        all_docs = []
        for ap_invoice in JournalEntryRun.get_all_ap_invoice_this_period(company_id, this_period):
            all_docs.append({
                'id': str(ap_invoice.id),
                'code': str(ap_invoice.code),
                'date_approved': ap_invoice.date_approved,
                'type': 'ap_invoice'
            })
        for ar_invoice in JournalEntryRun.get_all_ar_invoice_this_period(company_id, this_period):
            all_docs.append({
                'id': str(ar_invoice.id),
                'code': str(ar_invoice.code),
                'date_approved': ar_invoice.date_approved,
                'type': 'ar_invoice'
            })
        for cif in JournalEntryRun.get_all_cif_this_period(company_id, this_period):
            all_docs.append({
                'id': str(cif.id),
                'code': str(cif.code),
                'date_approved': cif.date_approved,
                'type': 'cif'
            })
        for cof in JournalEntryRun.get_all_cof_this_period(company_id, this_period):
            all_docs.append({
                'id': str(cof.id),
                'code': str(cof.code),
                'date_approved': cof.date_approved,
                'type': 'cof'
            })
        for delivery in JournalEntryRun.get_all_delivery_this_period(company_id, this_period):
            all_docs.append({
                'id': str(delivery.id),
                'code': str(delivery.code),
                'date_approved': delivery.date_approved,
                'type': 'delivery'
            })
        for goods_receipt in JournalEntryRun.get_all_goods_receipt_this_period(company_id, this_period):
            all_docs.append({
                'id': str(goods_receipt.id),
                'code': str(goods_receipt.code),
                'date_approved': goods_receipt.date_approved,
                'type': 'goods_receipt'
            })
        return sorted(all_docs, key=lambda x: x['date_approved'])

    @staticmethod
    def log_docs(all_doc_sorted):
        print('#log docs')
        for doc in all_doc_sorted:
            print(f"> doc info: {doc['date_approved'].strftime('%d/%m/%Y')} - {doc['code']} ({doc['type']})")
            if doc['type'] == 'ap_invoice':
                instance = APInvoice.objects.get(id=doc['id'])
                JEForAPInvoiceHandler.push_to_journal_entry(instance)
            if doc['type'] == 'ar_invoice':
                instance = ARInvoice.objects.get(id=doc['id'])
                JEForARInvoiceHandler.push_to_journal_entry(instance)
            if doc['type'] == 'cif':
                instance = CashInflow.objects.get(id=doc['id'])
                JEForCIFHandler.push_to_journal_entry(instance)
            if doc['type'] == 'cof':
                instance = CashOutflow.objects.get(id=doc['id'])
                JEForCOFHandler.push_to_journal_entry(instance)
            if doc['type'] == 'delivery':
                instance = OrderDelivery.objects.get(id=doc['id'])
                JEForDeliveryHandler.push_to_journal_entry(instance)
            if doc['type'] == 'goods_receipt':
                instance = GoodsReceipt.objects.get(id=doc['id'])
                JEForGoodsReceiptHandler.push_to_journal_entry(instance)
        return True

    @staticmethod
    def run(company_id, fiscal_year):
        this_period = Periods.objects.filter(company_id=company_id, fiscal_year=fiscal_year).first()
        if this_period:
            SubPeriods.objects.filter(period_mapped=this_period).update(run_report_inventory=False)

            all_doc_sorted = JournalEntryRun.combine_data_all_docs(company_id, this_period)

            JournalEntryRun.delete_journal_entry_data(company_id, this_period)
            JournalEntryRun.log_docs(all_doc_sorted)
            print('#run successfully!')
            return True
        print('#can not find any Period!')
        return False
