import logging
from django.db import transaction
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.accounting.journalentry.models import JournalEntry
from apps.sales.report.models import ReportStockLog


logger = logging.getLogger(__name__)


class JEForARInvoiceHandler:
    @classmethod
    def get_je_item_data(cls, ar_invoice_obj):
        debit_rows_data = []
        credit_rows_data = []
        sum_cost = 0
        for item in ar_invoice_obj.ar_invoice_deliveries.all():
            delivery_obj = item.delivery_mapped
            for deli_product in delivery_obj.delivery_product_delivery_sub.all():
                if deli_product.product:
                    for pw_data in deli_product.delivery_pw_delivery_product.all():
                        # lấy cost lúc giao của sp
                        stock_log_item = ReportStockLog.objects.filter(
                            product=deli_product.product,
                            trans_code=delivery_obj.code,
                            trans_id=str(delivery_obj.id)
                        ).first()
                        cost = stock_log_item.value if stock_log_item else 0
                        sum_cost += cost
                        for account in deli_product.product.get_product_account_deter_sub_data(
                            account_deter_foreign_title = 'Cost of goods sold',
                            warehouse_id=pw_data.warehouse_id
                        ):
                            debit_rows_data.append({
                                # (-) giá vốn hàng bán (mđ: 632)
                                'account': account,
                                'product_mapped': deli_product.product,
                                'business_partner': None,
                                'debit': cost,
                                'credit': 0,
                                'is_fc': False,
                                'taxable_value': 0,
                            })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=ar_invoice_obj.tenant_id,
            company_id=ar_invoice_obj.company_id,
            foreign_title='Customer underpayment'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) giao hàng chưa xuất hóa đơn (mđ: 13881)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': 0,
                'credit': sum_cost,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'ar-deli'
            })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=ar_invoice_obj.tenant_id,
            company_id=ar_invoice_obj.company_id,
            foreign_title='Receivables from customers'
        )
        if len(account_list) == 1:
            debit_rows_data.append({
                # (-) phải thu của khách hàng - trong nước (mđ: 131)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': ar_invoice_obj.customer_mapped,
                'debit': ar_invoice_obj.sum_after_tax_value,
                'credit': 0,
                'is_fc': False,
                'taxable_value': 0,
                'use_for_recon': True,
                'use_for_recon_type': 'ar-cif'
            })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=ar_invoice_obj.tenant_id,
            company_id=ar_invoice_obj.company_id,
            foreign_title='Sales revenue'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) doanh thu bán hàng hóa - trong nước (mđ: 511)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': 0,
                'credit': ar_invoice_obj.sum_after_tax_value - ar_invoice_obj.sum_tax_value,
                'is_fc': False,
                'taxable_value': 0,
            })

        account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
            tenant_id=ar_invoice_obj.tenant_id,
            company_id=ar_invoice_obj.company_id,
            foreign_title='Sales tax'
        )
        if len(account_list) == 1:
            credit_rows_data.append({
                # (+) thuế GTGT đầu ra (mđ: 3331)
                'account': account_list[0],
                'product_mapped': None,
                'business_partner': None,
                'debit': 0,
                'credit': ar_invoice_obj.sum_tax_value,
                'is_fc': False,
                'taxable_value': ar_invoice_obj.sum_after_tax_value,
            })

        return debit_rows_data, credit_rows_data

    @classmethod
    def push_to_journal_entry(cls, ar_invoice_obj):
        """ Chuẩn bị data để tự động tạo Bút Toán """
        try:
            with transaction.atomic():
                debit_rows_data, credit_rows_data = cls.get_je_item_data(ar_invoice_obj)
                kwargs = {
                    'je_transaction_app_code': ar_invoice_obj.get_model_code(),
                    'je_transaction_id': str(ar_invoice_obj.id),
                    'je_transaction_data': {
                        'id': str(ar_invoice_obj.id),
                        'code': ar_invoice_obj.code,
                        'title': ar_invoice_obj.title,
                        'date_created': str(ar_invoice_obj.date_created),
                        'date_approved': str(ar_invoice_obj.date_approved),
                    },
                    'tenant_id': str(ar_invoice_obj.tenant_id),
                    'company_id': str(ar_invoice_obj.company_id),
                    'employee_created_id': str(ar_invoice_obj.employee_created_id),
                    'employee_inherit_id': str(ar_invoice_obj.employee_inherit_id),
                    'date_created': str(ar_invoice_obj.date_created),
                    'date_approved': str(ar_invoice_obj.date_approved),
                    'je_item_data': {
                        'debit_rows': debit_rows_data,
                        'credit_rows': credit_rows_data
                    }
                }
                JournalEntry.auto_create_journal_entry(**kwargs)
                return True
        except Exception as err:
            logger.error(msg=f'[JE] Error while creating Journal Entry: {err}')
            return None
