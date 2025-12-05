import logging
from django.db import transaction
from django.db.models import Sum
from apps.accounting.accountingsettings.models.account_determination import JEDocData, JEDocumentType
from apps.accounting.journalentry.models import JournalEntry
from apps.accounting.journalentry.utils import JELogHandler
from apps.masterdata.saledata.models import Currency, Periods, SubPeriods
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
        logs = ReportStockLog.objects.filter(
            trans_id__in=[str(last_transaction_id) for last_transaction_id in last_transaction_id_list]
        ).values('product_id').annotate(total_cost=Sum('value'))
        return {str(item['product_id']): (item['total_cost'] or 0) for item in logs}

    # Goods receipt
    @classmethod
    def push_goods_receipt_doc_data(cls, gr_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=gr_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                cost_map = cls.get_cost_from_stock_for_each_product(gr_obj)
                JEDocData.objects.filter(doc_id=str(gr_obj.id), app_code=app_code).delete()
                bulk_info = []
                for gr_prd_obj in gr_obj.goods_receipt_product_goods_receipt.all():
                    line_value = cost_map.get(str(gr_prd_obj.product_id), 0)
                    data_row = JEDocData.make_doc_data_obj(
                        company_id=gr_obj.company_id,
                        app_code=app_code,
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
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return False

    # AP invoice
    @classmethod
    def push_ap_invoice_doc_data(cls, ap_invoice_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=ap_invoice_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                last_transaction_id_list = ap_invoice_obj.ap_invoice_goods_receipts.values_list(
                    'goods_receipt_mapped_id', flat=True
                )
                cost_map = cls.get_cost_from_stock_for_all(last_transaction_id_list)
                JEDocData.objects.filter(
                    doc_id=str(ap_invoice_obj.id), app_code=app_code
                ).delete()
                data_1 = JEDocData.make_doc_data_obj(
                    company_id=ap_invoice_obj.company_id,
                    app_code=app_code,
                    doc_id=ap_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TAX',
                    value=ap_invoice_obj.sum_tax_value,
                    taxable_value=ap_invoice_obj.sum_after_tax_value,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_2 = JEDocData.make_doc_data_obj(
                    company_id=ap_invoice_obj.company_id,
                    app_code=app_code,
                    doc_id=ap_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TOTAL',
                    value=ap_invoice_obj.sum_after_tax_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by='account',
                    tracking_id=ap_invoice_obj.supplier_mapped_id
                )
                bulk_info = [data_1, data_2]
                for item in ap_invoice_obj.ap_invoice_items.all():
                    line_value = cost_map.get(str(item.product_id), 0)
                    data_row = JEDocData.make_doc_data_obj(
                        company_id=ap_invoice_obj.company_id,
                        app_code=app_code,
                        doc_id=ap_invoice_obj.id,
                        rule_level='LINE',
                        amount_source='COST',
                        value=line_value,
                        taxable_value=0,
                        currency_mapped=currency_mapped,
                        tracking_by='product',
                        tracking_id=item.product_id
                    )
                    bulk_info.append(data_row)
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return False

    # COF
    @classmethod
    def push_cof_doc_data(cls, cof_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=cof_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                JEDocData.objects.filter(doc_id=str(cof_obj.id), app_code=app_code).delete()
                data_1 = JEDocData.make_doc_data_obj(
                    company_id=cof_obj.company_id,
                    app_code=app_code,
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
                data_2 = JEDocData.make_doc_data_obj(
                    company_id=cof_obj.company_id,
                    app_code=app_code,
                    doc_id=cof_obj.id,
                    rule_level='HEADER',
                    amount_source='CASH',
                    value=cof_obj.cash_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_3 = JEDocData.make_doc_data_obj(
                    company_id=cof_obj.company_id,
                    app_code=app_code,
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
            return False

    # Delivery
    @classmethod
    def push_delivery_doc_data(cls, delivery_sub_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=delivery_sub_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                cost_map = cls.get_cost_from_stock_for_each_product(delivery_sub_obj)
                currency_exchange_rate = 1
                if delivery_sub_obj.order_delivery.sale_order:
                    currency_exchange_rate = delivery_sub_obj.order_delivery.sale_order.currency_exchange_rate
                JEDocData.objects.filter(
                    doc_id=str(delivery_sub_obj.id), app_code=app_code
                ).delete()
                bulk_info = []
                for deli_product in delivery_sub_obj.delivery_product_delivery_sub.all():
                    line_value = cost_map.get(str(deli_product.product_id), 0)
                    data_row_cost = JEDocData.make_doc_data_obj(
                        company_id=delivery_sub_obj.company_id,
                        app_code=app_code,
                        doc_id=delivery_sub_obj.id,
                        rule_level='LINE',
                        amount_source='COST',
                        value=line_value,
                        taxable_value=0,
                        currency_mapped=currency_mapped,
                        tracking_by='product',
                        tracking_id=deli_product.product_id
                    )
                    data_row_sales = JEDocData.make_doc_data_obj(
                        company_id=delivery_sub_obj.company_id,
                        app_code=app_code,
                        doc_id=delivery_sub_obj.id,
                        rule_level='LINE',
                        amount_source='SALES',
                        value=deli_product.product_subtotal_cost * currency_exchange_rate,
                        taxable_value=0,
                        currency_mapped=currency_mapped,
                        tracking_by='product',
                        tracking_id=deli_product.product_id
                    )
                    bulk_info.append(data_row_cost)
                    bulk_info.append(data_row_sales)
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return False

    # AR invoice
    @classmethod
    def push_ar_invoice_doc_data(cls, ar_invoice_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=ar_invoice_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                JEDocData.objects.filter(
                    doc_id=str(ar_invoice_obj.id), app_code=app_code
                ).delete()
                data_1 = JEDocData.make_doc_data_obj(
                    company_id=ar_invoice_obj.company_id,
                    app_code=app_code,
                    doc_id=ar_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TAX',
                    value=ar_invoice_obj.sum_tax_value,
                    taxable_value=ar_invoice_obj.sum_after_tax_value,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_2 = JEDocData.make_doc_data_obj(
                    company_id=ar_invoice_obj.company_id,
                    app_code=app_code,
                    doc_id=ar_invoice_obj.id,
                    rule_level='HEADER',
                    amount_source='TOTAL',
                    value=ar_invoice_obj.sum_after_tax_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by='account',
                    tracking_id=ar_invoice_obj.customer_mapped_id
                )
                bulk_info = [data_1, data_2]
                for item in ar_invoice_obj.ar_invoice_items.all():
                    currency_exchange_rate = 1
                    delivery_mapped_obj = item.ar_invoice.ar_invoice_deliveries.first()
                    if delivery_mapped_obj.delivery_mapped.sale_order:
                        currency_exchange_rate = delivery_mapped_obj.delivery_mapped.sale_order.currency_exchange_rate
                    line_value = item.product_subtotal * currency_exchange_rate
                    data_row = JEDocData.make_doc_data_obj(
                        company_id=ar_invoice_obj.company_id,
                        app_code=app_code,
                        doc_id=ar_invoice_obj.id,
                        rule_level='LINE',
                        amount_source='SALES',
                        value=line_value,
                        taxable_value=0,
                        currency_mapped=currency_mapped,
                        tracking_by='product',
                        tracking_id=item.product_id
                    )
                    bulk_info.append(data_row)
                JEDocData.objects.bulk_create(bulk_info)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while push to JEDocData: {err}')
            return False

    # CIF
    @classmethod
    def push_cif_doc_data(cls, cif_obj, app_code):
        try:
            with transaction.atomic():
                if not JEDocumentType.objects.filter(
                    company_id=cif_obj.company_id, app_code=app_code, is_auto_je=True
                ).exists():
                    return False
                currency_mapped = Currency.objects.filter_on_company(is_primary=True).first()
                JEDocData.objects.filter(doc_id=str(cif_obj.id), app_code=app_code).delete()
                data_1 = JEDocData.make_doc_data_obj(
                    company_id=cif_obj.company_id,
                    app_code=app_code,
                    doc_id=cif_obj.id,
                    rule_level='HEADER',
                    amount_source='TOTAL',
                    value=cif_obj.total_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by='account',
                    tracking_id=cif_obj.customer_id
                )
                data_2 = JEDocData.make_doc_data_obj(
                    company_id=cif_obj.company_id,
                    app_code=app_code,
                    doc_id=cif_obj.id,
                    rule_level='HEADER',
                    amount_source='CASH',
                    value=cif_obj.cash_value,
                    taxable_value=0,
                    currency_mapped=currency_mapped,
                    tracking_by=None,
                    tracking_id=None
                )
                data_3 = JEDocData.make_doc_data_obj(
                    company_id=cif_obj.company_id,
                    app_code=app_code,
                    doc_id=cif_obj.id,
                    rule_level='HEADER',
                    amount_source='BANK',
                    value=cif_obj.bank_value,
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
            return False

    @classmethod
    def push_data_to_je_doc_data(cls, transaction_obj):
        app_code = transaction_obj.get_model_code()
        if app_code == 'inventory.goodsreceipt':
            is_auto_je = cls.push_goods_receipt_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        if app_code == 'apinvoice.apinvoice':
            is_auto_je = cls.push_ap_invoice_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        if app_code == 'financialcashflow.cashoutflow':
            is_auto_je = cls.push_cof_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        if app_code == 'delivery.orderdeliverysub':
            is_auto_je = cls.push_delivery_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        if app_code == 'arinvoice.arinvoice':
            is_auto_je = cls.push_ar_invoice_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        if app_code == 'financialcashflow.cashinflow':
            is_auto_je = cls.push_cif_doc_data(transaction_obj, app_code)
            if is_auto_je:
                JELogHandler.push_to_journal_entry(transaction_obj)
        return True
