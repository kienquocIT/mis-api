import logging
from django.db import transaction
from django.db.models import Sum
from apps.accounting.accountingsettings.models.account_determination import JEDocData
from apps.masterdata.saledata.models import Currency
from apps.sales.apinvoice.models import APInvoice
from apps.sales.financialcashflow.models import CashOutflow
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.report.models import ReportStockLog

logger = logging.getLogger(__name__)


class JEDocDataLogHandler:
    @classmethod
    def get_cost_from_stock_for_each_product(cls, transaction_obj):
        logs = ReportStockLog.objects.filter(
            trans_id=str(transaction_obj.id)
        ).values('product_id').annotate(total_cost=Sum('value'))
        return {str(item['product_id']): (item['total_cost'] or 0) for item in logs}

    @staticmethod
    def get_cost_from_stock_for_all(last_transaction_id_list):
        result = ReportStockLog.objects.filter(
            trans_id__in=[str(last_transaction_id) for last_transaction_id in last_transaction_id_list],
        ).aggregate(total_cost=Sum('value'))
        print(result['total_cost'])
        return result['total_cost'] or 0

    # Goods receipt
    @classmethod
    def push_for_goods_receipt(cls, gr_obj):
        try:
            with transaction.atomic():
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                cost_map = cls.get_cost_from_stock_for_each_product(gr_obj)
                JEDocData.objects.filter(doc_id=str(gr_obj.id), app_code=gr_obj.get_model_code()).delete()
                total_value = 0
                bulk_info = []
                for gr_prd_obj in gr_obj.goods_receipt_product_goods_receipt.all():
                    line_value = cost_map.get(str(gr_prd_obj.product_id), 0)
                    total_value += line_value
                    data_row = JEDocData.push_amount_source_doc_data(
                        company_id=gr_obj.company_id,
                        app_code=gr_obj.get_model_code(),
                        doc_id=gr_obj.id,
                        rule_level='LINE',
                        amount_source='COST',
                        value=line_value,
                        taxable_value=0,
                        currency_mapped=currency_mapped,
                        tracking_by='product',
                        tracking_id=gr_prd_obj.product_id
                    )
                    bulk_info.append(data_row)
                data_1 = JEDocData.push_amount_source_doc_data(
                    company_id=gr_obj.company_id,
                    app_code=gr_obj.get_model_code(),
                    doc_id=gr_obj.id,
                    rule_level='HEADER',
                    amount_source='COST',
                    value=total_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                bulk_info.append(data_1)
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return None

    # AP invoice
    @classmethod
    def push_for_ap_invoice(cls, ap_invoice_obj):
        try:
            with transaction.atomic():
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                JEDocData.objects.filter(doc_id=str(ap_invoice_obj.id), app_code=ap_invoice_obj.get_model_code()).delete()
                last_transaction_id_list = ap_invoice_obj.ap_invoice_goods_receipts.values_list(
                    'goods_receipt_mapped_id', flat=True
                )
                data_1 = JEDocData.push_amount_source_doc_data(
                    company_id=ap_invoice_obj.company_id,
                    app_code=ap_invoice_obj.get_model_code(),
                    doc_id=ap_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='COST',
                    value=cls.get_cost_from_stock_for_all(last_transaction_id_list),
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_2 = JEDocData.push_amount_source_doc_data(
                    company_id=ap_invoice_obj.company_id,
                    app_code=ap_invoice_obj.get_model_code(),
                    doc_id=ap_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TAX',
                    value=ap_invoice_obj.sum_tax_value,
                    taxable_value=ap_invoice_obj.sum_after_tax_value,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_3 = JEDocData.push_amount_source_doc_data(
                    company_id=ap_invoice_obj.company_id,
                    app_code=ap_invoice_obj.get_model_code(),
                    doc_id=ap_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TOTAL',
                    value=ap_invoice_obj.sum_after_tax_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by='account',
                    tracking_id=ap_invoice_obj.supplier_mapped_id
                )
                bulk_info = [data_1, data_2, data_3]
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return None

    # COF
    @classmethod
    def push_for_cof(cls, cof_obj):
        try:
            with transaction.atomic():
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                JEDocData.objects.filter(doc_id=str(cof_obj.id), app_code=cof_obj.get_model_code()).delete()
                data_1 = JEDocData.push_amount_source_doc_data(
                    company_id=cof_obj.company_id,
                    app_code=cof_obj.get_model_code(),
                    doc_id=cof_obj.id,
                    rule_level='HEADER',
                    amount_source='TOTAL',
                    value=cof_obj.total_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=[
                        'account', 'account', 'employee'
                    ][cof_obj.cof_type],
                    tracking_id=[
                        cof_obj.supplier_id, cof_obj.customer_id, cof_obj.employee_inherit_id
                    ][cof_obj.cof_type]
                )
                data_2 = JEDocData.push_amount_source_doc_data(
                    company_id=cof_obj.company_id,
                    app_code=cof_obj.get_model_code(),
                    doc_id=cof_obj.id,
                    rule_level='HEADER',
                    amount_source='CASH',
                    value=cof_obj.cash_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_3 = JEDocData.push_amount_source_doc_data(
                    company_id=cof_obj.company_id,
                    app_code=cof_obj.get_model_code(),
                    doc_id=cof_obj.id,
                    rule_level='HEADER',
                    amount_source='BANK',
                    value=cof_obj.bank_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                bulk_info = [data_1, data_2, data_3]
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return None

    @classmethod
    def run(cls, company_id):
        for transaction_obj in GoodsReceipt.objects.filter(company_id=company_id, system_status=3):
            cls.push_for_goods_receipt(transaction_obj)
            print(f"#run successfully {transaction_obj.code}!")
        for transaction_obj in APInvoice.objects.filter(company_id=company_id, system_status=3):
            cls.push_for_ap_invoice(transaction_obj)
            print(f"#run successfully {transaction_obj.code}!")
        for transaction_obj in CashOutflow.objects.filter(company_id=company_id, system_status=3):
            cls.push_for_cof(transaction_obj)
            print(f"#run successfully {transaction_obj.code}!")
        return True